from django import forms

from apps.recipes.models import Ingredient, Recipe, WeeklyMenu


def _to_choice_tuples(options):
    return [(opt, opt) for opt in options]


class StyledModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for _, field in self.fields.items():
            css_class = field.widget.attrs.get("class", "")
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = (css_class + " form-check-input").strip()
            elif isinstance(field.widget, forms.SelectMultiple):
                field.widget.attrs["class"] = (css_class + " form-select").strip()
                field.widget.attrs.setdefault("size", 5)
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs["class"] = (css_class + " form-select").strip()
            else:
                field.widget.attrs["class"] = (css_class + " form-control").strip()


class IngredientForm(StyledModelForm):
    alergenos = forms.MultipleChoiceField(
        required=False,
        choices=_to_choice_tuples(Ingredient.ALERGENOS_CHOICES),
        widget=forms.SelectMultiple,
    )
    metodos_cocinado = forms.MultipleChoiceField(
        required=False,
        choices=_to_choice_tuples(Ingredient.METODOS_COCINADO_CHOICES),
        widget=forms.SelectMultiple,
    )

    class Meta:
        model = Ingredient
        fields = [
            "nombre",
            "categoria",
            "descripcion",
            "imagen_modo",
            "imagen_url",
            "imagen_archivo",
            "temporada",
            "calorias_100g",
            "proteinas_100g",
            "grasas_100g",
            "carbohidratos_100g",
            "alergenos",
            "apto_vegetariano",
            "apto_vegano",
            "apto_celiacos",
            "sabor_predominante",
            "tipo_ingrediente",
            "metodos_cocinado",
            "forma_conservacion",
            "unidad_compra",
            "precio_aproximado",
            "recetas_relacionadas",
            "fuente_informacion",
        ]
        labels = {
            "nombre": "nombre",
            "categoria": "categoria",
            "descripcion": "descripcion",
            "imagen_modo": "imagen",
            "imagen_url": "url",
            "imagen_archivo": "archivo subido",
            "temporada": "temporada",
            "calorias_100g": "calorias_100g",
            "proteinas_100g": "proteinas_100g",
            "grasas_100g": "grasas_100g",
            "carbohidratos_100g": "carbohidratos_100g",
            "alergenos": "alergenos",
            "apto_vegetariano": "apto_vegetariano",
            "apto_vegano": "apto_vegano",
            "apto_celiacos": "apto_celiacos",
            "sabor_predominante": "sabor_predominante",
            "tipo_ingrediente": "tipo_ingrediente",
            "metodos_cocinado": "metodos_cocinado",
            "forma_conservacion": "forma_conservacion",
            "unidad_compra": "unidad_compra",
            "precio_aproximado": "precio_aproximado",
            "recetas_relacionadas": "recetas_relacionadas",
            "fuente_informacion": "fuente_informacion",
        }
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 3}),
            "calorias_100g": forms.NumberInput(attrs={"step": "0.01"}),
            "proteinas_100g": forms.NumberInput(attrs={"step": "0.01"}),
            "grasas_100g": forms.NumberInput(attrs={"step": "0.01"}),
            "carbohidratos_100g": forms.NumberInput(attrs={"step": "0.01"}),
            "precio_aproximado": forms.NumberInput(attrs={"step": "0.01"}),
            "recetas_relacionadas": forms.TextInput(attrs={"placeholder": "IDs o nombres separados por coma"}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.alergenos = self.cleaned_data.get("alergenos", [])
        instance.metodos_cocinado = self.cleaned_data.get("metodos_cocinado", [])
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class RecipeForm(StyledModelForm):
    class Meta:
        model = Recipe
        fields = [
            "title",
            "description",
            "servings",
            "prep_minutes",
            "cook_minutes",
            "difficulty",
            "ingredients_text",
            "steps",
            "tips",
            "is_public",
        ]
        labels = {
            "title": "Titulo",
            "description": "Descripcion",
            "servings": "Porciones",
            "prep_minutes": "Minutos de preparacion",
            "cook_minutes": "Minutos de coccion",
            "difficulty": "Dificultad",
            "ingredients_text": "Ingredientes",
            "steps": "Pasos",
            "tips": "Consejos",
            "is_public": "Visible para otros",
        }


class WeeklyMenuForm(StyledModelForm):
    class Meta:
        model = WeeklyMenu
        fields = [
            "name",
            "week_start",
            "monday_recipe",
            "tuesday_recipe",
            "wednesday_recipe",
            "thursday_recipe",
            "friday_recipe",
            "saturday_recipe",
            "sunday_recipe",
            "notes",
        ]
        labels = {
            "name": "Nombre del menu",
            "week_start": "Semana (fecha de inicio)",
            "monday_recipe": "Lunes",
            "tuesday_recipe": "Martes",
            "wednesday_recipe": "Miercoles",
            "thursday_recipe": "Jueves",
            "friday_recipe": "Viernes",
            "saturday_recipe": "Sabado",
            "sunday_recipe": "Domingo",
            "notes": "Notas",
        }
        widgets = {
            "week_start": forms.DateInput(attrs={"type": "date"}),
        }
