from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from django.db import transaction

from apps.recipes.models import IngredientSearchAlias, NutritionalInfoIngredient
from apps.recipes.services.text_normalization import normalize_query_tokens, normalize_spanish_term

from .usda_client import USDAFoodDataClient, USDAClientError, USDANoResultsError

logger = logging.getLogger(__name__)

ES_TO_EN_FALLBACK = {
    "pimiento verde": "green bell pepper",
    "pimiento rojo": "red bell pepper",
    "curcuma": "turmeric",
    "cúrcuma": "turmeric",
    "calabacin": "zucchini",
    "calabacín": "zucchini",
    "cebolla morada": "red onion",
    "judias verdes": "green beans",
    "judías verdes": "green beans",
}

NUTRIENT_NAME_MAP = {
    "energy": "energia_kcal",
    "protein": "proteina_g",
    "total lipid (fat)": "grasas_g",
    "carbohydrate, by difference": "carbohidratos_g",
    "fiber, total dietary": "fibra_g",
    "sugars, total including nlea": "azucares_g",
    "sodium, na": "sodio_mg",
    "calcium, ca": "calcio_mg",
    "iron, fe": "hierro_mg",
    "magnesium, mg": "magnesio_mg",
    "phosphorus, p": "fosforo_mg",
    "potassium, k": "potasio_mg",
    "zinc, zn": "zinc_mg",
    "copper, cu": "cobre_mg",
    "manganese, mn": "manganeso_mg",
    "selenium, se": "selenio_ug",
    "vitamin c, total ascorbic acid": "vitamina_c_mg",
    "vitamin a, rae": "vitamina_a_ug_rae",
    "vitamin e (alpha-tocopherol)": "vitamina_e_mg",
    "vitamin k (phylloquinone)": "vitamina_k_ug",
    "thiamin": "vitamina_b1_mg",
    "riboflavin": "vitamina_b2_mg",
    "niacin": "vitamina_b3_mg",
    "vitamin b-6": "vitamina_b6_mg",
    "folate, total": "folato_ug",
    "vitamin b-12": "vitamina_b12_ug",
}


@dataclass
class ResolvedQuery:
    requested_es: str
    normalized_es: str
    usda_query_en: str


class USDAImportService:
    def __init__(self, client: USDAFoodDataClient | None = None):
        self.client = client or USDAFoodDataClient()

    def _resolve_query(self, user_query: str) -> ResolvedQuery:
        normalized = normalize_spanish_term(user_query)
        alias = IngredientSearchAlias.objects.filter(alias_normalized=normalized).first()
        if alias:
            return ResolvedQuery(
                requested_es=alias.alias_es,
                normalized_es=alias.alias_normalized,
                usda_query_en=alias.usda_query_en,
            )

        fallback = ES_TO_EN_FALLBACK.get(normalized)
        if fallback:
            return ResolvedQuery(
                requested_es=user_query.strip(),
                normalized_es=normalized,
                usda_query_en=fallback,
            )

        return ResolvedQuery(
            requested_es=user_query.strip(),
            normalized_es=normalized,
            usda_query_en=normalized,
        )

    def _score_candidate(self, item: dict[str, Any], query_en: str) -> int:
        description = (item.get("description") or "").lower()
        query_tokens = normalize_query_tokens(query_en)

        score = 0
        if description.startswith(query_en.lower()):
            score += 35

        token_hits = sum(1 for token in query_tokens if token in description)
        score += token_hits * 7

        data_type = (item.get("dataType") or "").lower()
        type_priority = {
            "foundation": 40,
            "sr legacy": 35,
            "survey (fndds)": 25,
            "branded": 5,
        }
        score += type_priority.get(data_type, 0)

        if item.get("brandOwner"):
            score -= 15

        nutrients = item.get("foodNutrients") or []
        score += min(len(nutrients), 20)

        return score

    def _rank_candidates(self, candidates: list[dict[str, Any]], query_en: str) -> list[dict[str, Any]]:
        if not candidates:
            raise USDANoResultsError("USDA no devolvio ingredientes")

        return sorted(
            candidates,
            key=lambda item: self._score_candidate(item, query_en),
            reverse=True,
        )

    def _extract_nutrients(self, detail: dict[str, Any]) -> tuple[dict[str, float], float | None, float | None]:
        nutrients: dict[str, float] = {}

        for item in detail.get("foodNutrients") or []:
            nutrient_info = item.get("nutrient") or {}
            name = (
                nutrient_info.get("name")
                or item.get("nutrientName")
                or item.get("name")
                or ""
            ).lower().strip()
            amount = item.get("amount", item.get("value"))
            if amount is None:
                continue

            try:
                value = float(amount)
            except (TypeError, ValueError):
                continue

            mapped_key = NUTRIENT_NAME_MAP.get(name)
            if mapped_key:
                nutrients[mapped_key] = value

        energy = nutrients.get("energia_kcal")
        protein = nutrients.get("proteina_g")
        return nutrients, energy, protein

    @staticmethod
    def _has_enough_search_nutrients(nutrients: dict[str, float], energy: float | None, protein: float | None) -> bool:
        if energy is not None and protein is not None and len(nutrients) >= 6:
            return True
        return len(nutrients) >= 10

    def _find_local_match(self, normalized_query: str) -> NutritionalInfoIngredient | None:
        return (
            NutritionalInfoIngredient.objects.filter(normalized_name=normalized_query)
            .order_by("id")
            .first()
        )

    @staticmethod
    def _source_id_from_fdc(fdc_id: int) -> int:
        return 1_000_000_000 + fdc_id

    @transaction.atomic
    def import_from_user_query(self, user_query: str) -> tuple[NutritionalInfoIngredient, bool]:
        resolved = self._resolve_query(user_query)
        if not resolved.normalized_es:
            raise USDAClientError("Debes escribir un ingrediente valido")

        local_match = self._find_local_match(resolved.normalized_es)
        if local_match:
            return local_match, False

        candidates = self.client.search_foods(resolved.usda_query_en)
        ranked_candidates = self._rank_candidates(candidates, resolved.usda_query_en)

        detail = None
        selected = None
        last_error: USDAClientError | None = None
        for candidate in ranked_candidates:
            candidate_fdc = candidate.get("fdcId")
            if not candidate_fdc:
                continue

            fdc_id = int(candidate_fdc)
            existing_by_fdc = NutritionalInfoIngredient.objects.filter(fdc_id=fdc_id).first()
            if existing_by_fdc:
                IngredientSearchAlias.objects.update_or_create(
                    alias_normalized=resolved.normalized_es,
                    defaults={
                        "alias_es": resolved.requested_es,
                        "usda_query_en": resolved.usda_query_en,
                        "ingredient": existing_by_fdc,
                    },
                )
                return existing_by_fdc, False

            candidate_nutrients, candidate_energy, candidate_protein = self._extract_nutrients(
                {"foodNutrients": candidate.get("foodNutrients") or []}
            )
            if self._has_enough_search_nutrients(
                candidate_nutrients,
                candidate_energy,
                candidate_protein,
            ):
                detail = {
                    "fdcId": fdc_id,
                    "description": candidate.get("description"),
                    "foodNutrients": candidate.get("foodNutrients") or [],
                }
                selected = candidate
                break

            try:
                detail = self.client.get_food_detail(fdc_id)
                selected = candidate
                break
            except USDAClientError as error:
                last_error = error
                continue

        if detail is None or selected is None:
            if last_error:
                raise last_error
            raise USDANoResultsError("USDA no devolvio detalle util para el termino")

        fdc_id = int(selected.get("fdcId"))
        nutrients, energy, protein = self._extract_nutrients(detail)

        description_en = (detail.get("description") or selected.get("description") or "").strip()
        ingredient = NutritionalInfoIngredient.objects.create(
            source_id=self._source_id_from_fdc(fdc_id),
            fdc_id=fdc_id,
            name=resolved.requested_es,
            scientific_name="",
            source_name_en=description_en,
            source=NutritionalInfoIngredient.SOURCE_USDA,
            edible_portion=1.0,
            energy_total=energy,
            protein_total=protein,
            nutrients=nutrients,
            source_payload={
                "search_candidate": selected,
                "detail": detail,
            },
        )

        IngredientSearchAlias.objects.update_or_create(
            alias_normalized=resolved.normalized_es,
            defaults={
                "alias_es": resolved.requested_es,
                "usda_query_en": resolved.usda_query_en,
                "ingredient": ingredient,
            },
        )

        logger.info("Ingrediente importado desde USDA", extra={"fdc_id": fdc_id, "name": ingredient.name})
        return ingredient, True
