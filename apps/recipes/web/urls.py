from django.urls import path

from .views import (
    add_culinary_action,
    add_culinary_participle,
    add_culinary_unit,
    culinary_action_suggestions,
    culinary_participle_suggestions,
    culinary_unit_suggestions,
    home,
    ingredient_detail_page,
    import_ingredient_from_api,
    ingredient_detail_local,
    ingredient_suggestions,
    ingredients_list,
    landing,
    recipes_create_placeholder,
)

urlpatterns = [
    path("", landing, name="landing"),
    path("home/", home, name="home"),
    path("ingredients/", ingredients_list, name="ingredients-list"),
    path("ingredients/<int:source_id>/", ingredient_detail_page, name="ingredient-detail"),
    path("ingredients/<int:source_id>/json/", ingredient_detail_local, name="ingredient-detail-local"),
    path("recipes/create/", recipes_create_placeholder, name="recipes-create"),
    path("ingredients/suggestions/", ingredient_suggestions, name="ingredient-suggestions"),
    path("ingredients/import-from-api/", import_ingredient_from_api, name="ingredient-import-from-api"),
    path("culinary-units/suggestions/", culinary_unit_suggestions, name="culinary-unit-suggestions"),
    path("culinary-units/add/", add_culinary_unit, name="culinary-unit-add"),
    path("culinary-actions/suggestions/", culinary_action_suggestions, name="culinary-action-suggestions"),
    path("culinary-actions/add/", add_culinary_action, name="culinary-action-add"),
    path("culinary-participles/suggestions/", culinary_participle_suggestions, name="culinary-participle-suggestions"),
    path("culinary-participles/add/", add_culinary_participle, name="culinary-participle-add"),
]
