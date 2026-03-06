from pathlib import Path
import re

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.recipes.models import CulinaryAction


class Command(BaseCommand):
    help = "Importa acciones culinarias desde acciones_culinarias/acciones_culinarias.md"

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            default=str(Path(settings.BASE_DIR) / "acciones_culinarias" / "acciones_culinarias.md"),
            help="Ruta al archivo markdown de acciones culinarias",
        )

    def handle(self, *args, **options):
        path = Path(options["path"]).expanduser().resolve()
        if not path.exists():
            raise CommandError(f"No existe el archivo: {path}")

        created = 0
        updated = 0
        ignored = 0
        parsed = 0

        pattern = re.compile(r"^\s*\d+\.\s+(.*?)\s*$")

        for line in path.read_text(encoding="utf-8").splitlines():
            match = pattern.match(line)
            if not match:
                continue

            parsed += 1
            name = match.group(1).strip()
            if not name:
                ignored += 1
                continue

            action, was_created = CulinaryAction.objects.get_or_create(
                name=name,
                defaults={"source": CulinaryAction.SOURCE_SEED},
            )
            if was_created:
                created += 1
                continue

            if action.source != CulinaryAction.SOURCE_SEED:
                action.source = CulinaryAction.SOURCE_SEED
                action.save(update_fields=["source", "normalized_name", "updated_at"])
                updated += 1
            else:
                ignored += 1

        self.stdout.write(self.style.SUCCESS("Importacion de acciones culinarias completada"))
        self.stdout.write(f"- Lineas parseadas: {parsed}")
        self.stdout.write(f"- Creadas: {created}")
        self.stdout.write(f"- Actualizadas: {updated}")
        self.stdout.write(f"- Ignoradas: {ignored}")
