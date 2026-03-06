from pathlib import Path
from tempfile import TemporaryDirectory

from django.core.management import call_command
from django.test import TestCase

from apps.recipes.models import CulinaryUnit


class ImportCulinaryUnitsCommandTests(TestCase):
    def test_imports_units_from_markdown(self):
        with TemporaryDirectory() as tmpdir:
            md_path = Path(tmpdir) / "medidas.md"
            md_path.write_text(
                "# Unidades\n\n1. cucharada\n2. cucharadita\n3. taza\n",
                encoding="utf-8",
            )

            call_command("import_culinary_units", path=str(md_path))

        self.assertEqual(CulinaryUnit.objects.count(), 3)
        self.assertTrue(CulinaryUnit.objects.filter(name="cucharada").exists())
        self.assertTrue(CulinaryUnit.objects.filter(name="cucharadita").exists())
        self.assertTrue(CulinaryUnit.objects.filter(name="taza").exists())
