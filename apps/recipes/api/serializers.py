from rest_framework import serializers

from apps.recipes.models import NutritionalInfoIngredient


class HealthSerializer(serializers.Serializer):
    status = serializers.CharField()


class NutritionalInfoIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = NutritionalInfoIngredient
        fields = [
            "source_id",
            "fdc_id",
            "name",
            "normalized_name",
            "scientific_name",
            "source_name_en",
            "source",
            "edible_portion",
            "energy_total",
            "protein_total",
            "nutrients",
        ]
