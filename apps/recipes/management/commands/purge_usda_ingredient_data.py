from django.core.management.base import BaseCommand
from django.db import connection
from django.db.utils import OperationalError, ProgrammingError

from apps.recipes.models import NutritionalInfoIngredient


class Command(BaseCommand):
    help = "Elimina datos legacy USDA y vacia ingredientes nutricionales para recarga limpia."

    def handle(self, *args, **options):
        try:
            deleted_current, _ = NutritionalInfoIngredient.objects.all().delete()
        except (OperationalError, ProgrammingError):
            deleted_current = 0

        legacy_tables = [
            "recipes_csvingredient",
            "recipes_ingredient",
        ]
        existing_tables = set(connection.introspection.table_names())

        deleted_legacy = []
        with connection.cursor() as cursor:
            for table_name in legacy_tables:
                if table_name not in existing_tables:
                    continue
                cursor.execute(f'TRUNCATE TABLE "{table_name}" RESTART IDENTITY CASCADE;')
                deleted_legacy.append(table_name)

        self.stdout.write(self.style.SUCCESS("Purgado completado"))
        self.stdout.write(f"- Registros eliminados en modelo activo: {deleted_current}")
        self.stdout.write(
            f"- Tablas legacy purgadas: {', '.join(deleted_legacy) if deleted_legacy else 'ninguna'}"
        )
