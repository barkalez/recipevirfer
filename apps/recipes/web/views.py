from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from apps.recipes.models import Ingredient

from .forms import IngredientForm, RecipeForm, WeeklyMenuForm


def _ingredient_sections(form):
    sections = [
        (
            "General",
            [
                "nombre",
                "categoria",
                "descripcion",
                "imagen_modo",
                "imagen_url",
                "imagen_archivo",
                "temporada",
            ],
        ),
        (
            "Nutricion",
            [
                "calorias_100g",
                "proteinas_100g",
                "grasas_100g",
                "carbohidratos_100g",
                "alergenos",
            ],
        ),
        (
            "Dieta",
            [
                "apto_vegetariano",
                "apto_vegano",
                "apto_celiacos",
            ],
        ),
        (
            "Cocina",
            [
                "sabor_predominante",
                "tipo_ingrediente",
                "metodos_cocinado",
                "recetas_relacionadas",
            ],
        ),
        (
            "Conservacion y Compra",
            [
                "forma_conservacion",
                "unidad_compra",
                "precio_aproximado",
                "fuente_informacion",
            ],
        ),
    ]

    return [{"title": title, "fields": [form[name] for name in names]} for title, names in sections]


def landing(request):
    return render(request, "landing.html")


def home(request):
    return render(request, "home.html")


def add_ingredient_placeholder(request):
    ingredient_id = request.GET.get("id")
    instance = None
    if ingredient_id:
        instance = get_object_or_404(Ingredient, pk=ingredient_id)

    if request.method == "POST":
        form = IngredientForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            obj = form.save()
            messages.success(request, "Ingrediente guardado en PostgreSQL.")
            return redirect(f"{redirect('add-ingredient').url}?id={obj.id}")
    else:
        form = IngredientForm(instance=instance)

    return render(
        request,
        "ingredient_form.html",
        {
            "title": "Anadir ingrediente",
            "description": "Formulario esencial de ingrediente.",
            "form": form,
            "sections": _ingredient_sections(form),
            "wide_fields": [
                "descripcion",
                "imagen_archivo",
                "alergenos",
                "metodos_cocinado",
                "recetas_relacionadas",
            ],
            "submit_label": "Guardar ingrediente",
            "entity": instance,
        },
    )


def add_recipe_placeholder(request):
    if request.method == "POST":
        form = RecipeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Receta guardada en PostgreSQL.")
            return redirect("add-recipe")
    else:
        form = RecipeForm()

    return render(
        request,
        "entity_form.html",
        {
            "title": "Anadir receta",
            "description": "Guarda una receta base para ampliarla despues.",
            "form": form,
            "submit_label": "Guardar receta",
        },
    )


def weekly_menu_placeholder(request):
    if request.method == "POST":
        form = WeeklyMenuForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Menu semanal guardado en PostgreSQL.")
            return redirect("create-weekly-menu")
    else:
        form = WeeklyMenuForm()

    return render(
        request,
        "entity_form.html",
        {
            "title": "Crear menu semanal",
            "description": "Registra una planificacion semanal de referencia.",
            "form": form,
            "submit_label": "Guardar menu",
        },
    )
