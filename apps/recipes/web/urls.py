from django.urls import path

from .views import (
    add_ingredient_placeholder,
    add_recipe_placeholder,
    home,
    landing,
    weekly_menu_placeholder,
)

urlpatterns = [
    path("", landing, name="landing"),
    path("home/", home, name="home"),
    path("ingredients/new/", add_ingredient_placeholder, name="add-ingredient"),
    path("recipes/new/", add_recipe_placeholder, name="add-recipe"),
    path("weekly-menu/create/", weekly_menu_placeholder, name="create-weekly-menu"),
]
