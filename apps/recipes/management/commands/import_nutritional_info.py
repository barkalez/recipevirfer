import csv
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.recipes.models import NutritionalInfoIngredient
from apps.recipes.services import (
    OPTIONAL_BASE_COLUMN_ALIASES,
    REQUIRED_COLUMNS,
    extract_base_values,
    extract_nutrients,
    normalize_spanish_term,
    resolve_column_name,
)


class Command(BaseCommand):
    help = "Importa csv/nutritional-info.csv al modelo NutritionalInfoIngredient."

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            default=str(Path(settings.BASE_DIR) / "csv" / "nutritional-info.csv"),
            help="Ruta al CSV nutricional",
        )
        parser.add_argument("--batch-size", type=int, default=500)

    def _open_reader(self, csv_path: Path):
        last_error = None
        for encoding in ("utf-8-sig", "latin-1", "cp1252"):
            try:
                handle = csv_path.open("r", newline="", encoding=encoding)
                reader = csv.DictReader(handle)
                headers = reader.fieldnames or []
                if not all(column in headers for column in REQUIRED_COLUMNS):
                    handle.close()
                    continue
                return handle, reader
            except UnicodeDecodeError as error:
                last_error = error

        if last_error:
            raise CommandError(f"No se pudo leer el CSV por codificacion: {last_error}")
        raise CommandError(f"CSV invalido. Se esperaban columnas: {', '.join(REQUIRED_COLUMNS)}")

    @transaction.atomic
    def handle(self, *args, **options):
        csv_path = Path(options["path"]).expanduser().resolve()
        batch_size = max(1, options["batch_size"])

        if not csv_path.exists():
            raise CommandError(f"No existe el archivo: {csv_path}")

        handle, reader = self._open_reader(csv_path)
        headers = reader.fieldnames or []

        for column in REQUIRED_COLUMNS:
            if column not in headers:
                handle.close()
                raise CommandError(f"Columna obligatoria ausente: {column}")

        column_map = {
            key: resolve_column_name(headers, aliases)
            for key, aliases in OPTIONAL_BASE_COLUMN_ALIASES.items()
        }

        processed = 0
        created = 0
        updated = 0
        ignored = 0
        errors = 0
        seen_ids = set()

        existing = NutritionalInfoIngredient.objects.in_bulk(field_name="source_id")
        to_create = []
        to_update = []

        for row in reader:
            processed += 1

            source_raw = (row.get("f_id") or "").strip()
            name = (row.get("f_ori_name") or "").strip()

            if not source_raw or not name:
                ignored += 1
                continue

            try:
                source_id = int(source_raw)
            except ValueError:
                errors += 1
                continue

            if source_id in seen_ids:
                ignored += 1
                continue
            seen_ids.add(source_id)

            base_values = extract_base_values(row, column_map)
            nutrients = extract_nutrients(row, headers)

            current = existing.get(source_id)
            if current is None:
                to_create.append(
                    NutritionalInfoIngredient(
                        source_id=source_id,
                        fdc_id=None,
                        name=name,
                        normalized_name=normalize_spanish_term(name),
                        scientific_name=base_values["scientific_name"],
                        source_name_en="",
                        source=NutritionalInfoIngredient.SOURCE_CSV,
                        edible_portion=base_values["edible_portion"],
                        energy_total=base_values["energy_total"],
                        protein_total=base_values["protein_total"],
                        nutrients=nutrients,
                        source_payload={},
                    )
                )
                created += 1
            else:
                changed = False
                if current.name != name:
                    current.name = name
                    changed = True
                if current.scientific_name != base_values["scientific_name"]:
                    current.scientific_name = base_values["scientific_name"]
                    changed = True
                if current.edible_portion != base_values["edible_portion"]:
                    current.edible_portion = base_values["edible_portion"]
                    changed = True
                if current.energy_total != base_values["energy_total"]:
                    current.energy_total = base_values["energy_total"]
                    changed = True
                if current.protein_total != base_values["protein_total"]:
                    current.protein_total = base_values["protein_total"]
                    changed = True
                if current.nutrients != nutrients:
                    current.nutrients = nutrients
                    changed = True
                if current.source != NutritionalInfoIngredient.SOURCE_CSV:
                    current.source = NutritionalInfoIngredient.SOURCE_CSV
                    changed = True
                if current.normalized_name != normalize_spanish_term(name):
                    current.normalized_name = normalize_spanish_term(name)
                    changed = True

                if changed:
                    to_update.append(current)
                    updated += 1
                else:
                    ignored += 1

            if len(to_create) >= batch_size:
                NutritionalInfoIngredient.objects.bulk_create(to_create, batch_size=batch_size)
                to_create = []

            if len(to_update) >= batch_size:
                NutritionalInfoIngredient.objects.bulk_update(
                    to_update,
                    [
                        "name",
                        "normalized_name",
                        "scientific_name",
                        "source",
                        "edible_portion",
                        "energy_total",
                        "protein_total",
                        "nutrients",
                    ],
                    batch_size=batch_size,
                )
                to_update = []

        if to_create:
            NutritionalInfoIngredient.objects.bulk_create(to_create, batch_size=batch_size)

        if to_update:
            NutritionalInfoIngredient.objects.bulk_update(
                to_update,
                [
                    "name",
                    "normalized_name",
                    "scientific_name",
                    "source",
                    "edible_portion",
                    "energy_total",
                    "protein_total",
                    "nutrients",
                ],
                batch_size=batch_size,
            )

        handle.close()

        self.stdout.write(self.style.SUCCESS("Importacion completada"))
        self.stdout.write(f"- Filas procesadas: {processed}")
        self.stdout.write(f"- Creadas: {created}")
        self.stdout.write(f"- Actualizadas: {updated}")
        self.stdout.write(f"- Ignoradas: {ignored}")
        self.stdout.write(f"- Errores: {errors}")
