from django.contrib import admin

from apps.recipes.models import CsvIngredient


@admin.register(CsvIngredient)
class CsvIngredientAdmin(admin.ModelAdmin):
    list_display = ("fdc_id", "alimento", "created_at")
    search_fields = ("alimento", "fdc_id")
    list_per_page = 50
