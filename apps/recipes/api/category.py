from django.db.models import Q

CATEGORY_KEYWORDS = {
    "vegetal": ["tomat", "ceboll", "ajo", "patata", "papa", "zanahoria", "lechuga", "espinaca", "pepino", "calab", "brocoli", "coliflor", "berenjena"],
    "fruta": ["manzana", "platano", "banana", "pera", "naranja", "limon", "fresa", "mango", "uva", "melon", "sandia", "piña", "kiwi"],
    "legumbre": ["lenteja", "garbanzo", "frijol", "alubia", "judia", "soja", "habas"],
    "cereal": ["arroz", "trigo", "avena", "maiz", "cebada", "centeno", "quinoa", "mijo"],
    "proteina_animal": ["pollo", "res", "ternera", "cerdo", "pavo", "cordero", "pescado", "atun", "salmon", "huevo", "marisco"],
    "lacteo": ["leche", "queso", "yogur", "yogurt", "mantequilla", "nata"],
    "grasa_aceite": ["aceite", "oliva", "manteca", "sebo"],
    "frutos_secos_semillas": ["almendra", "nuez", "avellana", "pistacho", "cacahu", "mani", "sesamo", "chia", "linaza", "semilla"],
    "especia_hierba": ["pimienta", "comino", "oregano", "canela", "perejil", "albahaca", "laurel", "curry", "pimenton"],
}


def infer_category(alimento: str) -> str:
    text = (alimento or "").lower()
    for category, words in CATEGORY_KEYWORDS.items():
        if any(w in text for w in words):
            return category
    return "otro"


def apply_category_filter(queryset, categoria: str):
    words = CATEGORY_KEYWORDS.get(categoria)
    if not words:
        return queryset.none()

    condition = Q()
    for word in words:
        condition |= Q(alimento__icontains=word)
    return queryset.filter(condition)
