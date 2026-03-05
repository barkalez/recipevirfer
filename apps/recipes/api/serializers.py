from rest_framework import serializers

from apps.recipes.models import CsvIngredient

from .category import infer_category


class HealthSerializer(serializers.Serializer):
    status = serializers.CharField()


class CsvIngredientSerializer(serializers.ModelSerializer):
    categoria_inferida = serializers.SerializerMethodField()
    calorias_100g = serializers.SerializerMethodField()
    proteinas_100g = serializers.SerializerMethodField()

    class Meta:
        model = CsvIngredient
        fields = [
            "fdc_id",
            "alimento",
            "categoria_inferida",
            "calorias_100g",
            "proteinas_100g",
            "nutrientes",
        ]

    def _to_float(self, value):
        if value in (None, ""):
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def get_calorias_100g(self, obj):
        return self._to_float((obj.nutrientes or {}).get("energy_kcal"))

    def get_proteinas_100g(self, obj):
        return self._to_float((obj.nutrientes or {}).get("protein_g"))

    def get_categoria_inferida(self, obj):
        return infer_category(obj.alimento)
