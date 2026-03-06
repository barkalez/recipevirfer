from django.core.management import call_command
from django.test import TestCase

from apps.recipes.models import CulinaryParticiple


class ImportCulinaryParticiplesCommandTests(TestCase):
    def test_imports_default_participles(self):
        call_command("import_culinary_participles")

        self.assertGreaterEqual(CulinaryParticiple.objects.count(), 10)
        self.assertTrue(CulinaryParticiple.objects.filter(name="picado").exists())
        self.assertTrue(CulinaryParticiple.objects.filter(name="troceada").exists())
