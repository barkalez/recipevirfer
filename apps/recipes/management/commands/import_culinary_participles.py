from django.core.management.base import BaseCommand

from apps.recipes.models import CulinaryParticiple


DEFAULT_PARTICIPLES = [
    "picado",
    "picada",
    "troceado",
    "troceada",
    "cortado",
    "cortada",
    "laminado",
    "laminada",
    "rallado",
    "rallada",
    "triturado",
    "triturada",
    "molido",
    "molida",
    "machacado",
    "machacada",
    "pelado",
    "pelada",
    "en rodajas",
    "en dados",
    "en juliana",
    "en tiras",
    "desmenuzado",
    "desmenuzada",
    "batido",
    "batida",
    "salteado",
    "salteada",
    "sofreido",
    "sofreida",
    "asado",
    "asada",
    "hervido",
    "hervida",
]


class Command(BaseCommand):
    help = "Carga una lista semilla de participios culinarios"

    def handle(self, *args, **options):
        created = 0
        updated = 0
        ignored = 0

        for name in DEFAULT_PARTICIPLES:
            participle, was_created = CulinaryParticiple.objects.get_or_create(
                name=name,
                defaults={"source": CulinaryParticiple.SOURCE_SEED},
            )
            if was_created:
                created += 1
                continue

            if participle.source != CulinaryParticiple.SOURCE_SEED:
                participle.source = CulinaryParticiple.SOURCE_SEED
                participle.save(update_fields=["source", "normalized_name", "updated_at"])
                updated += 1
            else:
                ignored += 1

        self.stdout.write(self.style.SUCCESS("Importacion de participios culinarios completada"))
        self.stdout.write(f"- Creados: {created}")
        self.stdout.write(f"- Actualizados: {updated}")
        self.stdout.write(f"- Ignorados: {ignored}")
