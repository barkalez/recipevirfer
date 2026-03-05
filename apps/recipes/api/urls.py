from django.urls import path

from .views import HealthCheckView, IngredientDetailAPIView, IngredientListAPIView

urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health-check"),
    path("ingredients/", IngredientListAPIView.as_view(), name="ingredients-list-api"),
    path("ingredients/<int:fdc_id>/", IngredientDetailAPIView.as_view(), name="ingredient-detail-api"),
]
