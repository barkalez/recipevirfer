from django.contrib import admin

from apps.recipes.models import CulinaryAction, CulinaryParticiple, CulinaryUnit, IngredientSearchAlias, NutritionalInfoIngredient


@admin.register(NutritionalInfoIngredient)
class NutritionalInfoIngredientAdmin(admin.ModelAdmin):
    list_display = (
        "source_id",
        "fdc_id",
        "name",
        "source",
        "scientific_name",
        "source_name_en",
        "energy_total",
        "protein_total",
        "updated_at",
    )
    search_fields = ("name", "normalized_name", "scientific_name", "source_name_en", "source_id", "fdc_id")
    list_filter = ("source", "created_at", "updated_at")
    ordering = ("name",)
    list_per_page = 50


@admin.register(IngredientSearchAlias)
class IngredientSearchAliasAdmin(admin.ModelAdmin):
    list_display = ("alias_es", "usda_query_en", "ingredient", "updated_at")
    search_fields = ("alias_es", "alias_normalized", "usda_query_en", "ingredient__name")
    list_per_page = 50


@admin.register(CulinaryUnit)
class CulinaryUnitAdmin(admin.ModelAdmin):
    list_display = ("name", "source", "updated_at")
    search_fields = ("name", "normalized_name")
    list_filter = ("source",)
    ordering = ("name",)
    list_per_page = 50


@admin.register(CulinaryAction)
class CulinaryActionAdmin(admin.ModelAdmin):
    list_display = ("name", "source", "updated_at")
    search_fields = ("name", "normalized_name")
    list_filter = ("source",)
    ordering = ("name",)
    list_per_page = 50


@admin.register(CulinaryParticiple)
class CulinaryParticipleAdmin(admin.ModelAdmin):
    list_display = ("name", "source", "updated_at")
    search_fields = ("name", "normalized_name")
    list_filter = ("source",)
    ordering = ("name",)
    list_per_page = 50
