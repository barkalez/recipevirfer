from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.recipes.models import CsvIngredient

from .serializers import CsvIngredientSerializer

from .category import apply_category_filter


def _safe_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def apply_nutrient_range_filters(queryset, protein_min, protein_max, calories_min, calories_max):
    if all(v is None for v in [protein_min, protein_max, calories_min, calories_max]):
        return queryset

    valid_ids = []
    for pk, nutrients in queryset.values_list("id", "nutrientes"):
        nutrients = nutrients or {}
        protein = _safe_float(nutrients.get("protein_g"))
        calories = _safe_float(nutrients.get("energy_kcal"))

        if protein_min is not None and (protein is None or protein < protein_min):
            continue
        if protein_max is not None and (protein is None or protein > protein_max):
            continue
        if calories_min is not None and (calories is None or calories < calories_min):
            continue
        if calories_max is not None and (calories is None or calories > calories_max):
            continue

        valid_ids.append(pk)

    return queryset.filter(id__in=valid_ids)


class HealthCheckView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        return Response({"status": "ok"})


class IngredientListAPIView(generics.ListAPIView):
    serializer_class = CsvIngredientSerializer
    authentication_classes = []
    permission_classes = []

    def get_queryset(self):
        queryset = CsvIngredient.objects.all().order_by("alimento")

        query = (self.request.query_params.get("q") or "").strip()
        categoria = (self.request.query_params.get("categoria") or "").strip().lower()

        protein_min = _safe_float(self.request.query_params.get("protein_min"))
        protein_max = _safe_float(self.request.query_params.get("protein_max"))
        calories_min = _safe_float(self.request.query_params.get("calories_min"))
        calories_max = _safe_float(self.request.query_params.get("calories_max"))

        if query:
            if query.isdigit():
                queryset = queryset.filter(Q(fdc_id=int(query)) | Q(alimento__icontains=query))
            else:
                queryset = queryset.filter(alimento__icontains=query)

        if categoria:
            queryset = apply_category_filter(queryset, categoria)

        queryset = apply_nutrient_range_filters(
            queryset,
            protein_min=protein_min,
            protein_max=protein_max,
            calories_min=calories_min,
            calories_max=calories_max,
        )

        return queryset


class IngredientDetailAPIView(generics.RetrieveAPIView):
    serializer_class = CsvIngredientSerializer
    authentication_classes = []
    permission_classes = []

    def get_object(self):
        return get_object_or_404(CsvIngredient, fdc_id=self.kwargs["fdc_id"])
