from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.recipes.models import NutritionalInfoIngredient
from apps.recipes.services import normalize_spanish_term

from .serializers import NutritionalInfoIngredientSerializer


def _safe_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


class HealthCheckView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        return Response({"status": "ok"})


class IngredientListAPIView(generics.ListAPIView):
    serializer_class = NutritionalInfoIngredientSerializer
    authentication_classes = []
    permission_classes = []

    def get_queryset(self):
        queryset = NutritionalInfoIngredient.objects.all().order_by("name")

        query = (self.request.query_params.get("q") or "").strip()

        protein_min = _safe_float(self.request.query_params.get("protein_min"))
        protein_max = _safe_float(self.request.query_params.get("protein_max"))
        calories_min = _safe_float(self.request.query_params.get("calories_min"))
        calories_max = _safe_float(self.request.query_params.get("calories_max"))

        if query:
            normalized_query = normalize_spanish_term(query)
            if query.isdigit():
                queryset = queryset.filter(
                    Q(source_id=int(query))
                    | Q(name__icontains=query)
                    | Q(normalized_name__icontains=normalized_query)
                    | Q(scientific_name__icontains=query)
                )
            else:
                queryset = queryset.filter(
                    Q(name__icontains=query)
                    | Q(normalized_name__icontains=normalized_query)
                    | Q(scientific_name__icontains=query)
                )

        if protein_min is not None:
            queryset = queryset.filter(protein_total__gte=protein_min)
        if protein_max is not None:
            queryset = queryset.filter(protein_total__lte=protein_max)
        if calories_min is not None:
            queryset = queryset.filter(energy_total__gte=calories_min)
        if calories_max is not None:
            queryset = queryset.filter(energy_total__lte=calories_max)

        return queryset


class IngredientDetailAPIView(generics.RetrieveAPIView):
    serializer_class = NutritionalInfoIngredientSerializer
    authentication_classes = []
    permission_classes = []

    def get_object(self):
        return get_object_or_404(NutritionalInfoIngredient, source_id=self.kwargs["source_id"])
