from django.urls import path

from .views import home, ingredient_suggestions, ingredients_list, landing, recipes_create_placeholder

urlpatterns = [
    path("", landing, name="landing"),
    path("home/", home, name="home"),
    path("ingredients/", ingredients_list, name="ingredients-list"),
    path("recipes/create/", recipes_create_placeholder, name="recipes-create"),
    path("ingredients/suggestions/", ingredient_suggestions, name="ingredient-suggestions"),
]
