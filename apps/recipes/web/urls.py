from django.urls import path

from .views import home, ingredients_list, landing

urlpatterns = [
    path("", landing, name="landing"),
    path("home/", home, name="home"),
    path("ingredients/", ingredients_list, name="ingredients-list"),
]
