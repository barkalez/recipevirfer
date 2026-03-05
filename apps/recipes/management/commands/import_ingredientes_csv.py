import csv
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.recipes.models import CsvIngredient


class Command(BaseCommand):
    help = "Importa ingredientes_reales_usda_es.csv a PostgreSQL (tabla CsvIngredient)."

    def add_arguments(self, parser):
        parser.add_argument("--path", required=True, help="Ruta al CSV de entrada")
        parser.add_argument("--batch-size", type=int, default=1000)
        parser.add_argument("--keep-existing", action="store_true")

    @transaction.atomic
    def handle(self, *args, **options):
        csv_path = Path(options["path"]).expanduser().resolve()
        batch_size = options["batch_size"]
        keep_existing = options["keep_existing"]

        if not csv_path.exists():
            raise CommandError(f"No existe el archivo: {csv_path}")

        with csv_path.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                raise CommandError("CSV sin encabezados")

            fdc_col = "fdc_id" if "fdc_id" in reader.fieldnames else None
            food_col = "alimento" if "alimento" in reader.fieldnames else ("food" if "food" in reader.fieldnames else None)

            if not fdc_col or not food_col:
                raise CommandError(
                    f"CSV invalido. Se esperaba fdc_id y alimento/food. Header: {reader.fieldnames}"
                )

            nutrient_cols = [c for c in reader.fieldnames if c not in {fdc_col, food_col}]

            if not keep_existing:
                deleted, _ = CsvIngredient.objects.all().delete()
                self.stdout.write(self.style.WARNING(f"Registros previos eliminados: {deleted}"))

            to_create = []
            total = 0

            for row in reader:
                fdc_raw = (row.get(fdc_col) or "").strip()
                food = (row.get(food_col) or "").strip()
                if not fdc_raw or not food:
                    continue

                try:
                    fdc_id = int(fdc_raw)
                except ValueError:
                    continue

                nutrients = {}
                for col in nutrient_cols:
                    val = (row.get(col) or "").strip()
                    if val != "":
                        nutrients[col] = val

                to_create.append(
                    CsvIngredient(
                        fdc_id=fdc_id,
                        alimento=food,
                        nutrientes=nutrients,
                    )
                )

                if len(to_create) >= batch_size:
                    CsvIngredient.objects.bulk_create(
                        to_create,
                        batch_size=batch_size,
                        ignore_conflicts=True,
                    )
                    total += len(to_create)
                    self.stdout.write(f"Insertados: {total}")
                    to_create = []

            if to_create:
                CsvIngredient.objects.bulk_create(
                    to_create,
                    batch_size=batch_size,
                    ignore_conflicts=True,
                )
                total += len(to_create)

        self.stdout.write(self.style.SUCCESS(f"Importacion completada. Filas procesadas: {total}"))
