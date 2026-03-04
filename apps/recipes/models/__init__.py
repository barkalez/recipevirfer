from django.db import models


class Ingredient(models.Model):
    CATEGORIA_CHOICES = [
        ("verdura", "verdura"),
        ("fruta", "fruta"),
        ("carne", "carne"),
        ("pescado", "pescado"),
        ("marisco", "marisco"),
        ("cereal", "cereal"),
        ("legumbre", "legumbre"),
        ("lacteo", "lacteo"),
        ("huevo", "huevo"),
        ("especia", "especia"),
        ("hierba_aromatica", "hierba aromatica"),
        ("fruto_seco", "fruto seco"),
        ("semilla", "semilla"),
        ("grasa_aceite", "grasa / aceite"),
        ("azucar_endulzante", "azucar / endulzante"),
        ("bebida", "bebida"),
        ("hongo", "hongo"),
    ]

    SUBCATEGORIA_CHOICES = [
        ("pescado_azul", "pescado azul"),
        ("pescado_blanco", "pescado blanco"),
        ("carne_roja", "carne roja"),
        ("carne_blanca", "carne blanca"),
        ("legumbre_seca", "legumbre seca"),
        ("legumbre_fresca", "legumbre fresca"),
        ("cereal_integral", "cereal integral"),
        ("cereal_refinado", "cereal refinado"),
        ("lacteo_fermentado", "lacteo fermentado"),
        ("lacteo_fresco", "lacteo fresco"),
        ("fruto_seco_tostado", "fruto seco tostado"),
        ("fruto_seco_crudo", "fruto seco crudo"),
    ]

    IMAGEN_MODO_CHOICES = [
        ("ruta", "ruta de imagen"),
        ("url", "url"),
        ("archivo", "archivo subido"),
    ]

    TIPO_ORIGEN_CHOICES = [
        ("vegetal", "vegetal"),
        ("animal", "animal"),
        ("mineral", "mineral"),
        ("fungico", "fungico"),
        ("sintetico", "sintetico"),
    ]

    ORIGEN_GEOGRAFICO_CHOICES = [
        ("pais", "pais"),
        ("region", "region"),
        ("denominacion_origen", "denominacion de origen"),
        ("continente", "continente"),
    ]

    PARTE_UTILIZADA_CHOICES = [
        ("raiz", "raiz"),
        ("hoja", "hoja"),
        ("tallo", "tallo"),
        ("fruto", "fruto"),
        ("semilla", "semilla"),
        ("flor", "flor"),
        ("bulbo", "bulbo"),
        ("tuberculo", "tuberculo"),
        ("musculo", "musculo"),
        ("organo", "organo"),
    ]

    TEMPORADA_CHOICES = [
        ("primavera", "primavera"),
        ("verano", "verano"),
        ("otono", "otono"),
        ("invierno", "invierno"),
        ("todo_el_ano", "todo el ano"),
    ]

    VITAMINAS_CHOICES = [
        "vitamina A",
        "vitamina B1",
        "vitamina B2",
        "vitamina B3",
        "vitamina B6",
        "vitamina B9",
        "vitamina B12",
        "vitamina C",
        "vitamina D",
        "vitamina E",
        "vitamina K",
    ]

    MINERALES_CHOICES = [
        "calcio",
        "hierro",
        "magnesio",
        "fosforo",
        "potasio",
        "sodio",
        "zinc",
        "cobre",
        "selenio",
        "manganeso",
    ]

    INDICE_GLUCEMICO_CHOICES = [
        ("bajo", "bajo (0-55)"),
        ("medio", "medio (56-69)"),
        ("alto", "alto (70+)"),
    ]

    BENEFICIOS_CHOICES = [
        "antioxidante",
        "antiinflamatorio",
        "alto en fibra",
        "alto en proteina",
        "fuente de energia",
        "rico en vitaminas",
        "rico en minerales",
        "mejora digestion",
    ]

    CONTRAINDICACIONES_CHOICES = [
        "alergias",
        "intolerancias",
        "alto en sodio",
        "alto en azucar",
        "no recomendado en embarazo",
        "interaccion con medicamentos",
    ]

    SI_NO_CHOICES = [
        ("si", "si"),
        ("no", "no"),
    ]

    CELIACOS_CHOICES = [
        ("si", "si"),
        ("no", "no"),
        ("puede_contener_gluten", "puede contener gluten"),
    ]

    ALERGENOS_CHOICES = [
        "gluten",
        "huevo",
        "leche",
        "soja",
        "frutos secos",
        "cacahuete",
        "pescado",
        "marisco",
        "mostaza",
        "apio",
        "sesamo",
        "sulfitos",
    ]

    SABOR_CHOICES = [
        ("dulce", "dulce"),
        ("salado", "salado"),
        ("acido", "acido"),
        ("amargo", "amargo"),
        ("umami", "umami"),
        ("picante", "picante"),
    ]

    TEXTURA_CHOICES = [
        ("crujiente", "crujiente"),
        ("blando", "blando"),
        ("cremoso", "cremoso"),
        ("fibroso", "fibroso"),
        ("gelatinoso", "gelatinoso"),
        ("jugoso", "jugoso"),
        ("seco", "seco"),
    ]

    TIPO_INGREDIENTE_CHOICES = [
        ("principal", "principal"),
        ("secundario", "secundario"),
        ("condimento", "condimento"),
        ("espesante", "espesante"),
        ("aromatizante", "aromatizante"),
        ("guarnicion", "guarnicion"),
    ]

    METODOS_COCINADO_CHOICES = [
        "crudo",
        "hervido",
        "al vapor",
        "frito",
        "salteado",
        "al horno",
        "a la parrilla",
        "asado",
        "confitado",
        "fermentado",
    ]

    COMBINACIONES_CHOICES = [
        "tomate + albahaca",
        "patata + huevo",
        "arroz + pollo",
        "pasta + queso",
        "chocolate + avellana",
        "limon + pescado",
    ]

    FORMA_CONSERVACION_CHOICES = [
        ("refrigerado", "refrigerado"),
        ("congelado", "congelado"),
        ("seco", "seco"),
        ("en_salmuera", "en salmuera"),
        ("en_aceite", "en aceite"),
        ("al_vacio", "al vacio"),
    ]

    TEMPERATURA_CONSERVACION_CHOICES = [
        ("ambiente", "ambiente"),
        ("4c", "4C refrigeracion"),
        ("-18c", "-18C congelacion"),
    ]

    DURACION_CONSERVACION_CHOICES = [
        ("horas", "horas"),
        ("dias", "dias"),
        ("semanas", "semanas"),
        ("meses", "meses"),
        ("anos", "anos"),
    ]

    UNIDAD_COMPRA_CHOICES = [
        ("gramo", "gramo"),
        ("kilogramo", "kilogramo"),
        ("mililitro", "mililitro"),
        ("litro", "litro"),
        ("unidad", "unidad"),
        ("pieza", "pieza"),
        ("cucharada", "cucharada"),
        ("cucharadita", "cucharadita"),
    ]

    LUGAR_COMPRA_CHOICES = [
        ("supermercado", "supermercado"),
        ("mercado", "mercado"),
        ("pescaderia", "pescaderia"),
        ("carniceria", "carniceria"),
        ("fruteria", "fruteria"),
        ("herbolario", "herbolario"),
        ("tienda_online", "tienda online"),
    ]

    ETIQUETAS_CHOICES = [
        "ecologico",
        "organico",
        "artesanal",
        "premium",
        "local",
        "importado",
    ]

    FUENTE_INFO_CHOICES = [
        ("base_nutricional", "base de datos nutricional"),
        ("literatura_cientifica", "literatura cientifica"),
        ("wikipedia", "wikipedia"),
        ("etiqueta_producto", "etiqueta de producto"),
        ("usuario_editor", "usuario / editor"),
    ]

    nombre = models.CharField(max_length=120, default="")
    nombre_cientifico = models.CharField(max_length=160, blank=True)
    categoria = models.CharField(max_length=40, choices=CATEGORIA_CHOICES, blank=True)
    subcategoria = models.CharField(max_length=40, choices=SUBCATEGORIA_CHOICES, blank=True)
    descripcion = models.TextField(blank=True)

    imagen_modo = models.CharField(max_length=20, choices=IMAGEN_MODO_CHOICES, default="ruta")
    imagen_ruta = models.CharField(max_length=255, blank=True)
    imagen_url = models.URLField(blank=True)
    imagen_archivo = models.FileField(upload_to="ingredients/", blank=True, null=True)

    tipo_origen = models.CharField(max_length=20, choices=TIPO_ORIGEN_CHOICES, blank=True)
    origen_geografico = models.CharField(max_length=30, choices=ORIGEN_GEOGRAFICO_CHOICES, blank=True)
    parte_utilizada = models.CharField(max_length=20, choices=PARTE_UTILIZADA_CHOICES, blank=True)
    temporada = models.CharField(max_length=20, choices=TEMPORADA_CHOICES, blank=True)

    calorias_100g = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    proteinas_100g = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    grasas_100g = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    grasas_saturadas_100g = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    carbohidratos_100g = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    azucares_100g = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    fibra_100g = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    sal_100g = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    sodio_100g = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    vitaminas = models.JSONField(default=list, blank=True)
    minerales = models.JSONField(default=list, blank=True)

    indice_glucemico = models.CharField(max_length=10, choices=INDICE_GLUCEMICO_CHOICES, blank=True)
    beneficios_nutricionales = models.JSONField(default=list, blank=True)
    contraindicaciones = models.JSONField(default=list, blank=True)

    apto_vegetariano = models.CharField(max_length=3, choices=SI_NO_CHOICES, blank=True)
    apto_vegano = models.CharField(max_length=3, choices=SI_NO_CHOICES, blank=True)
    apto_celiacos = models.CharField(max_length=30, choices=CELIACOS_CHOICES, blank=True)
    apto_keto = models.CharField(max_length=3, choices=SI_NO_CHOICES, blank=True)
    apto_halal = models.CharField(max_length=3, choices=SI_NO_CHOICES, blank=True)
    apto_kosher = models.CharField(max_length=3, choices=SI_NO_CHOICES, blank=True)

    alergenos = models.JSONField(default=list, blank=True)

    sabor_predominante = models.CharField(max_length=15, choices=SABOR_CHOICES, blank=True)
    textura = models.CharField(max_length=20, choices=TEXTURA_CHOICES, blank=True)
    tipo_ingrediente = models.CharField(max_length=20, choices=TIPO_INGREDIENTE_CHOICES, blank=True)
    metodos_cocinado = models.JSONField(default=list, blank=True)
    combinaciones_habituales = models.JSONField(default=list, blank=True)

    recetas_relacionadas = models.CharField(max_length=300, blank=True)

    forma_conservacion = models.CharField(max_length=20, choices=FORMA_CONSERVACION_CHOICES, blank=True)
    temperatura_conservacion = models.CharField(max_length=20, choices=TEMPERATURA_CONSERVACION_CHOICES, blank=True)
    duracion_conservacion = models.CharField(max_length=20, choices=DURACION_CONSERVACION_CHOICES, blank=True)

    unidad_compra = models.CharField(max_length=20, choices=UNIDAD_COMPRA_CHOICES, blank=True)
    precio_aproximado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    lugar_compra = models.CharField(max_length=20, choices=LUGAR_COMPRA_CHOICES, blank=True)

    etiquetas = models.JSONField(default=list, blank=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True, null=True, blank=True)
    fuente_informacion = models.CharField(max_length=30, choices=FUENTE_INFO_CHOICES, blank=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self) -> str:
        return self.nombre


class Recipe(models.Model):
    DIFFICULTY_CHOICES = [
        ("easy", "Facil"),
        ("medium", "Media"),
        ("hard", "Dificil"),
    ]

    title = models.CharField(max_length=180)
    description = models.TextField(blank=True)
    servings = models.PositiveSmallIntegerField(default=1)
    prep_minutes = models.PositiveIntegerField(default=0)
    cook_minutes = models.PositiveIntegerField(default=0)
    difficulty = models.CharField(max_length=12, choices=DIFFICULTY_CHOICES, default="medium")
    ingredients_text = models.TextField(blank=True)
    steps = models.TextField(blank=True)
    tips = models.TextField(blank=True)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["title"]

    def __str__(self) -> str:
        return self.title


class WeeklyMenu(models.Model):
    name = models.CharField(max_length=120, default="Menu semanal")
    week_start = models.DateField()
    monday_recipe = models.ForeignKey(
        Recipe,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="menus_monday",
    )
    tuesday_recipe = models.ForeignKey(
        Recipe,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="menus_tuesday",
    )
    wednesday_recipe = models.ForeignKey(
        Recipe,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="menus_wednesday",
    )
    thursday_recipe = models.ForeignKey(
        Recipe,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="menus_thursday",
    )
    friday_recipe = models.ForeignKey(
        Recipe,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="menus_friday",
    )
    saturday_recipe = models.ForeignKey(
        Recipe,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="menus_saturday",
    )
    sunday_recipe = models.ForeignKey(
        Recipe,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="menus_sunday",
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-week_start"]

    def __str__(self) -> str:
        return f"{self.name} ({self.week_start})"
