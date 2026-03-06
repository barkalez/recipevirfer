from django.test import TestCase

from apps.recipes.models import IngredientSearchAlias, NutritionalInfoIngredient
from apps.recipes.services.usda_client import USDANoResultsError
from apps.recipes.services.usda_import import USDAImportService


class FakeUSDAClient:
    def __init__(self, candidates=None, detail=None):
        self.candidates = candidates or []
        self.detail = detail or {}
        self.search_calls = 0
        self.detail_calls = 0

    def search_foods(self, query_en: str, page_size: int = 12):
        self.search_calls += 1
        return self.candidates

    def get_food_detail(self, fdc_id: int):
        self.detail_calls += 1
        return self.detail


class USDAImportServiceTests(TestCase):
    def test_local_first_returns_existing_without_api(self):
        ingredient = NutritionalInfoIngredient.objects.create(source_id=10, name="Pimiento verde")
        fake_client = FakeUSDAClient()

        service = USDAImportService(client=fake_client)
        result, created = service.import_from_user_query("pimiento verde")

        self.assertFalse(created)
        self.assertEqual(result.id, ingredient.id)
        self.assertEqual(fake_client.search_calls, 0)
        self.assertEqual(fake_client.detail_calls, 0)

    def test_import_uses_alias_and_persists_new_ingredient(self):
        IngredientSearchAlias.objects.update_or_create(
            alias_normalized="curcuma",
            defaults={
                "alias_es": "cúrcuma",
                "usda_query_en": "turmeric",
            },
        )

        fake_client = FakeUSDAClient(
            candidates=[
                {
                    "fdcId": 999,
                    "description": "Turmeric powder, branded",
                    "dataType": "Branded",
                    "brandOwner": "Brand",
                    "foodNutrients": [{"value": 1}] * 3,
                },
                {
                    "fdcId": 1000,
                    "description": "Turmeric, ground spice",
                    "dataType": "Foundation",
                    "foodNutrients": [{"value": 1}] * 12,
                },
            ],
            detail={
                "fdcId": 1000,
                "description": "Turmeric, ground spice",
                "foodNutrients": [
                    {"nutrient": {"name": "Energy"}, "amount": 312},
                    {"nutrient": {"name": "Protein"}, "amount": 9.7},
                    {"nutrient": {"name": "Vitamin C, total ascorbic acid"}, "amount": 0.7},
                ],
            },
        )

        service = USDAImportService(client=fake_client)
        ingredient, created = service.import_from_user_query("cúrcuma")

        self.assertTrue(created)
        self.assertEqual(fake_client.search_calls, 1)
        self.assertEqual(fake_client.detail_calls, 1)
        self.assertEqual(ingredient.name, "cúrcuma")
        self.assertEqual(ingredient.fdc_id, 1000)
        self.assertEqual(ingredient.source, NutritionalInfoIngredient.SOURCE_USDA)
        self.assertEqual(ingredient.source_name_en, "Turmeric, ground spice")
        self.assertEqual(ingredient.energy_total, 312.0)
        self.assertEqual(ingredient.protein_total, 9.7)
        self.assertEqual(ingredient.nutrients.get("vitamina_c_mg"), 0.7)

        alias = IngredientSearchAlias.objects.get(alias_normalized="curcuma")
        self.assertEqual(alias.ingredient_id, ingredient.id)

    def test_reuses_existing_by_fdc_id(self):
        existing = NutritionalInfoIngredient.objects.create(
            source_id=1_000_001_000,
            fdc_id=1000,
            name="Cúrcuma ya importada",
            source=NutritionalInfoIngredient.SOURCE_USDA,
        )
        fake_client = FakeUSDAClient(
            candidates=[{"fdcId": 1000, "description": "Turmeric", "dataType": "Foundation"}],
            detail={"fdcId": 1000, "description": "Turmeric"},
        )

        service = USDAImportService(client=fake_client)
        ingredient, created = service.import_from_user_query("cúrcuma")

        self.assertFalse(created)
        self.assertEqual(ingredient.id, existing.id)
        self.assertEqual(fake_client.search_calls, 1)
        self.assertEqual(fake_client.detail_calls, 0)

    def test_raises_when_usda_returns_no_candidates(self):
        service = USDAImportService(client=FakeUSDAClient(candidates=[]))

        with self.assertRaises(USDANoResultsError):
            service.import_from_user_query("ingrediente inexistente")
