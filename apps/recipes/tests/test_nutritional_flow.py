import csv
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from django.core.management import call_command, get_commands
from django.test import TestCase
from rest_framework.test import APIClient

from apps.recipes.models import (
    CulinaryAction,
    CulinaryParticiple,
    CulinaryUnit,
    IngredientSearchAlias,
    NutritionalInfoIngredient,
)


class NutritionalInfoModelTests(TestCase):
    def test_model_uses_new_schema_without_usda_fields(self):
        ingredient = NutritionalInfoIngredient.objects.create(
            source_id=1,
            name="Tomate",
            scientific_name="Solanum lycopersicum",
            edible_portion=0.95,
            energy_total=18.0,
            protein_total=0.9,
            nutrients={"sodio": 5.0},
        )

        self.assertEqual(str(ingredient), "1 - Tomate")
        self.assertTrue(hasattr(ingredient, "fdc_id"))
        self.assertIsNone(ingredient.fdc_id)
        self.assertFalse(hasattr(ingredient, "alimento"))


class ImportNutritionalInfoCommandTests(TestCase):
    def setUp(self):
        self.csv_path = Path("/tmp/test_nutritional_info.csv")

    def tearDown(self):
        if self.csv_path.exists():
            self.csv_path.unlink()

    def _write_csv(self, rows):
        headers = [
            "f_id",
            "f_ori_name",
            "sci_name",
            "edible_portion",
            "energía, total",
            "proteina, total",
            "sodio",
        ]
        with self.csv_path.open("w", newline="", encoding="latin-1") as handle:
            writer = csv.DictWriter(handle, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)

    def test_import_is_idempotent_and_updates_existing_rows(self):
        self._write_csv(
            [
                {
                    "f_id": 10,
                    "f_ori_name": "Avena",
                    "sci_name": "Avena sativa",
                    "edible_portion": "1",
                    "energía, total": "389",
                    "proteina, total": "16.9",
                    "sodio": "2",
                }
            ]
        )

        out = StringIO()
        call_command("import_nutritional_info", path=str(self.csv_path), stdout=out)
        self.assertIn("Creadas: 1", out.getvalue())
        self.assertEqual(NutritionalInfoIngredient.objects.count(), 1)

        self._write_csv(
            [
                {
                    "f_id": 10,
                    "f_ori_name": "Avena",
                    "sci_name": "Avena sativa",
                    "edible_portion": "1",
                    "energía, total": "389",
                    "proteina, total": "17.5",
                    "sodio": "2",
                }
            ]
        )

        out = StringIO()
        call_command("import_nutritional_info", path=str(self.csv_path), stdout=out)
        self.assertIn("Actualizadas: 1", out.getvalue())
        self.assertEqual(
            NutritionalInfoIngredient.objects.get(source_id=10).protein_total,
            17.5,
        )


class NutritionalInfoApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        NutritionalInfoIngredient.objects.create(
            source_id=100,
            name="Tomate",
            scientific_name="Solanum lycopersicum",
            energy_total=18.0,
            protein_total=0.9,
            nutrients={"sodio": 5.0},
        )
        NutritionalInfoIngredient.objects.create(
            source_id=101,
            name="Atun",
            scientific_name="Thunnus thynnus",
            energy_total=132.0,
            protein_total=28.0,
            nutrients={"sodio": 47.0},
        )

    def test_list_filters_by_query_and_ranges(self):
        response = self.client.get("/api/v1/ingredients/", {"q": "Atun", "protein_min": 20})

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["results"][0]["source_id"], 101)
        self.assertIn("nutrients", payload["results"][0])
        self.assertIn("fdc_id", payload["results"][0])

    def test_detail_uses_source_id(self):
        response = self.client.get("/api/v1/ingredients/100/")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["source_id"], 100)
        self.assertEqual(payload["name"], "Tomate")

    def test_suggestions_returns_top_5_prefix_matches(self):
        extra_names = [
            "Pepino",
            "Pepinillo",
            "Pera",
            "Perejil",
            "Pechuga de pollo",
            "Pecan",
        ]
        for index, name in enumerate(extra_names, start=200):
            NutritionalInfoIngredient.objects.create(source_id=index, name=name)

        response = self.client.get("/ingredients/suggestions/", {"q": "pe"})

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIsInstance(payload, list)
        self.assertEqual(len(payload), 5)
        for item in payload:
            self.assertEqual(set(item.keys()), {"id", "name", "source"})
            self.assertTrue(item["name"].lower().startswith("pe"))

    def test_import_endpoint_returns_existing_without_calling_usda(self):
        with patch("apps.recipes.web.views.USDAImportService.import_from_user_query") as mocked_import:
            response = self.client.post(
                "/ingredients/import-from-api/",
                data='{\"query\": \"Tomate\"}',
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "exists")
        self.assertEqual(payload["ingredient"]["name"], "Tomate")
        mocked_import.assert_not_called()

    def test_old_import_command_is_removed(self):
        commands = get_commands()
        self.assertNotIn("import_ingredientes_csv", commands)

    def test_culinary_unit_suggestions_and_add(self):
        CulinaryUnit.objects.create(name="cucharada", source=CulinaryUnit.SOURCE_SEED)
        CulinaryUnit.objects.create(name="cucharadita", source=CulinaryUnit.SOURCE_SEED)
        CulinaryUnit.objects.create(name="cucharon", source=CulinaryUnit.SOURCE_SEED)
        CulinaryUnit.objects.create(name="cuenco", source=CulinaryUnit.SOURCE_SEED)
        CulinaryUnit.objects.create(name="cubo", source=CulinaryUnit.SOURCE_SEED)
        CulinaryUnit.objects.create(name="cucharada sopera", source=CulinaryUnit.SOURCE_SEED)

        response = self.client.get("/culinary-units/suggestions/", {"q": "cuch"})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertGreaterEqual(len(payload), 1)
        self.assertLessEqual(len(payload), 5)
        self.assertEqual(set(payload[0].keys()), {"id", "name"})

        add_response = self.client.post(
            "/culinary-units/add/",
            data='{\"name\": \"medida personal\"}',
            content_type="application/json",
        )
        self.assertEqual(add_response.status_code, 201)
        self.assertTrue(CulinaryUnit.objects.filter(name="medida personal").exists())

        add_again = self.client.post(
            "/culinary-units/add/",
            data='{\"name\": \"medida personal\"}',
            content_type="application/json",
        )
        self.assertEqual(add_again.status_code, 200)
        self.assertEqual(add_again.json()["status"], "exists")

    def test_culinary_action_suggestions_and_add(self):
        CulinaryAction.objects.create(name="cortar", source=CulinaryAction.SOURCE_SEED)
        CulinaryAction.objects.create(name="cocer", source=CulinaryAction.SOURCE_SEED)
        CulinaryAction.objects.create(name="calentar", source=CulinaryAction.SOURCE_SEED)
        CulinaryAction.objects.create(name="caramelizar", source=CulinaryAction.SOURCE_SEED)
        CulinaryAction.objects.create(name="colar", source=CulinaryAction.SOURCE_SEED)
        CulinaryAction.objects.create(name="combinar", source=CulinaryAction.SOURCE_SEED)

        response = self.client.get("/culinary-actions/suggestions/", {"q": "co"})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertGreaterEqual(len(payload), 1)
        self.assertLessEqual(len(payload), 5)
        self.assertEqual(set(payload[0].keys()), {"id", "name"})

        add_response = self.client.post(
            "/culinary-actions/add/",
            data='{\"name\": \"glasear test\"}',
            content_type="application/json",
        )
        self.assertEqual(add_response.status_code, 201)
        self.assertTrue(CulinaryAction.objects.filter(name="glasear test").exists())

        add_again = self.client.post(
            "/culinary-actions/add/",
            data='{\"name\": \"glasear test\"}',
            content_type="application/json",
        )
        self.assertEqual(add_again.status_code, 200)
        self.assertEqual(add_again.json()["status"], "exists")

    def test_culinary_participle_suggestions_and_add(self):
        CulinaryParticiple.objects.create(name="picado", source=CulinaryParticiple.SOURCE_SEED)
        CulinaryParticiple.objects.create(name="picada", source=CulinaryParticiple.SOURCE_SEED)
        CulinaryParticiple.objects.create(name="troceado", source=CulinaryParticiple.SOURCE_SEED)
        CulinaryParticiple.objects.create(name="troceada", source=CulinaryParticiple.SOURCE_SEED)
        CulinaryParticiple.objects.create(name="rallado", source=CulinaryParticiple.SOURCE_SEED)
        CulinaryParticiple.objects.create(name="rallada", source=CulinaryParticiple.SOURCE_SEED)

        response = self.client.get("/culinary-participles/suggestions/", {"q": "pi"})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertGreaterEqual(len(payload), 1)
        self.assertLessEqual(len(payload), 5)
        self.assertEqual(set(payload[0].keys()), {"id", "name"})

        add_response = self.client.post(
            "/culinary-participles/add/",
            data='{\"name\": \"fileteado\"}',
            content_type="application/json",
        )
        self.assertEqual(add_response.status_code, 201)
        self.assertTrue(CulinaryParticiple.objects.filter(name="fileteado").exists())

        add_again = self.client.post(
            "/culinary-participles/add/",
            data='{\"name\": \"fileteado\"}',
            content_type="application/json",
        )
        self.assertEqual(add_again.status_code, 200)
        self.assertEqual(add_again.json()["status"], "exists")

    def test_ingredient_detail_page_and_delete_related_data(self):
        ingredient = NutritionalInfoIngredient.objects.create(
            source_id=301,
            name="Calabacin",
            source="usda_api",
            nutrients={"fibra": 1.2},
        )
        IngredientSearchAlias.objects.create(
            alias_es="calabacin test",
            alias_normalized="calabacin test",
            usda_query_en="zucchini",
            ingredient=ingredient,
        )

        detail_response = self.client.get(f"/ingredients/{ingredient.source_id}/")
        self.assertEqual(detail_response.status_code, 200)
        self.assertIn("Calabacin", detail_response.content.decode("utf-8"))

        delete_response = self.client.post(
            f"/ingredients/{ingredient.source_id}/",
            {},
            follow=True,
        )
        self.assertEqual(delete_response.status_code, 200)
        self.assertFalse(NutritionalInfoIngredient.objects.filter(source_id=301).exists())
        self.assertFalse(IngredientSearchAlias.objects.filter(alias_normalized="calabacin test").exists())
