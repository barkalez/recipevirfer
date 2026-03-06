from pathlib import Path
from tempfile import TemporaryDirectory

from django.core.management import call_command
from django.test import TestCase

from apps.recipes.models import CulinaryAction


class ImportCulinaryActionsCommandTests(TestCase):
    def test_imports_actions_from_markdown(self):
        with TemporaryDirectory() as tmpdir:
            md_path = Path(tmpdir) / "acciones.md"
            md_path.write_text(
                "# Acciones\n\n1. cortar\n2. mezclar\n3. hornear\n",
                encoding="utf-8",
            )

            call_command("import_culinary_actions", path=str(md_path))

        self.assertEqual(CulinaryAction.objects.count(), 3)
        self.assertTrue(CulinaryAction.objects.filter(name="cortar").exists())
        self.assertTrue(CulinaryAction.objects.filter(name="mezclar").exists())
        self.assertTrue(CulinaryAction.objects.filter(name="hornear").exists())
