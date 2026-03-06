import json

from django.core.paginator import Paginator
from django.db.models import Case, IntegerField, Q, Value, When
from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from apps.recipes.models import CulinaryAction, CulinaryParticiple, CulinaryUnit, NutritionalInfoIngredient
from apps.recipes.services import normalize_spanish_term
from apps.recipes.services.usda_client import USDAClientError, USDANoResultsError
from apps.recipes.services.usda_import import USDAImportService


def landing(request):
    return render(request, "landing.html")


def home(request):
    total = NutritionalInfoIngredient.objects.count()
    return render(request, "home.html", {"total_ingredients": total})


def recipes_create_placeholder(request):
    return render(request, "recipes_placeholder.html")


def _ingredient_payload(ingredient: NutritionalInfoIngredient) -> dict:
    return {
        "source_id": ingredient.source_id,
        "name": ingredient.name,
        "source": ingredient.source,
        "fdc_id": ingredient.fdc_id,
    }


@require_GET
def ingredient_suggestions(request):
    query = (request.GET.get("q") or "").strip()
    if len(query) < 1:
        return JsonResponse([], safe=False)

    normalized_query = normalize_spanish_term(query)
    rows = (
        NutritionalInfoIngredient.objects.filter(
            Q(normalized_name__startswith=normalized_query) | Q(name__istartswith=query)
        )
        .annotate(
            prefix_rank=Case(
                When(normalized_name__startswith=normalized_query, then=Value(0)),
                default=Value(1),
                output_field=IntegerField(),
            )
        )
        .order_by("prefix_rank", "name")
        .values_list("source_id", "name", "source")[:5]
    )
    payload = [
        {"id": source_id, "name": name, "source": source}
        for source_id, name, source in rows
    ]
    return JsonResponse(payload, safe=False)


@require_GET
def culinary_unit_suggestions(request):
    query = (request.GET.get("q") or "").strip()
    if len(query) < 1:
        return JsonResponse([], safe=False)

    normalized_query = normalize_spanish_term(query)
    rows = (
        CulinaryUnit.objects.filter(
            Q(normalized_name__startswith=normalized_query) | Q(name__istartswith=query)
        )
        .annotate(
            prefix_rank=Case(
                When(normalized_name__startswith=normalized_query, then=Value(0)),
                default=Value(1),
                output_field=IntegerField(),
            )
        )
        .order_by("prefix_rank", "name")
        .values_list("id", "name")[:5]
    )
    payload = [{"id": unit_id, "name": name} for unit_id, name in rows]
    return JsonResponse(payload, safe=False)


@require_GET
def culinary_action_suggestions(request):
    query = (request.GET.get("q") or "").strip()
    if len(query) < 1:
        return JsonResponse([], safe=False)

    normalized_query = normalize_spanish_term(query)
    rows = (
        CulinaryAction.objects.filter(
            Q(normalized_name__startswith=normalized_query) | Q(name__istartswith=query)
        )
        .annotate(
            prefix_rank=Case(
                When(normalized_name__startswith=normalized_query, then=Value(0)),
                default=Value(1),
                output_field=IntegerField(),
            )
        )
        .order_by("prefix_rank", "name")
        .values_list("id", "name")[:5]
    )
    payload = [{"id": action_id, "name": name} for action_id, name in rows]
    return JsonResponse(payload, safe=False)


@require_GET
def culinary_participle_suggestions(request):
    query = (request.GET.get("q") or "").strip()
    if len(query) < 1:
        return JsonResponse([], safe=False)

    normalized_query = normalize_spanish_term(query)
    rows = (
        CulinaryParticiple.objects.filter(
            Q(normalized_name__startswith=normalized_query) | Q(name__istartswith=query)
        )
        .annotate(
            prefix_rank=Case(
                When(normalized_name__startswith=normalized_query, then=Value(0)),
                default=Value(1),
                output_field=IntegerField(),
            )
        )
        .order_by("prefix_rank", "name")
        .values_list("id", "name")[:5]
    )
    payload = [{"id": participle_id, "name": name} for participle_id, name in rows]
    return JsonResponse(payload, safe=False)


@require_POST
def add_culinary_unit(request: HttpRequest):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({"detail": "Solicitud invalida"}, status=400)
    if not isinstance(payload, dict):
        return JsonResponse({"detail": "Solicitud invalida"}, status=400)

    name = str(payload.get("name") or "").strip()
    if not name:
        return JsonResponse({"detail": "Debes escribir una medida culinaria"}, status=400)

    normalized_name = normalize_spanish_term(name)
    existing = CulinaryUnit.objects.filter(normalized_name=normalized_name).first()
    if existing:
        return JsonResponse({"status": "exists", "unit": {"id": existing.id, "name": existing.name}}, status=200)

    unit = CulinaryUnit.objects.create(name=name, source=CulinaryUnit.SOURCE_MANUAL)
    return JsonResponse(
        {"status": "created", "unit": {"id": unit.id, "name": unit.name}},
        status=201,
    )


@require_POST
def add_culinary_action(request: HttpRequest):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({"detail": "Solicitud invalida"}, status=400)
    if not isinstance(payload, dict):
        return JsonResponse({"detail": "Solicitud invalida"}, status=400)

    name = str(payload.get("name") or "").strip()
    if not name:
        return JsonResponse({"detail": "Debes escribir una accion culinaria"}, status=400)

    normalized_name = normalize_spanish_term(name)
    existing = CulinaryAction.objects.filter(normalized_name=normalized_name).first()
    if existing:
        return JsonResponse({"status": "exists", "action": {"id": existing.id, "name": existing.name}}, status=200)

    action = CulinaryAction.objects.create(name=name, source=CulinaryAction.SOURCE_MANUAL)
    return JsonResponse(
        {"status": "created", "action": {"id": action.id, "name": action.name}},
        status=201,
    )


@require_POST
def add_culinary_participle(request: HttpRequest):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({"detail": "Solicitud invalida"}, status=400)
    if not isinstance(payload, dict):
        return JsonResponse({"detail": "Solicitud invalida"}, status=400)

    name = str(payload.get("name") or "").strip()
    if not name:
        return JsonResponse({"detail": "Debes escribir un participio"}, status=400)

    normalized_name = normalize_spanish_term(name)
    existing = CulinaryParticiple.objects.filter(normalized_name=normalized_name).first()
    if existing:
        return JsonResponse(
            {"status": "exists", "participle": {"id": existing.id, "name": existing.name}},
            status=200,
        )

    participle = CulinaryParticiple.objects.create(name=name, source=CulinaryParticiple.SOURCE_MANUAL)
    return JsonResponse(
        {"status": "created", "participle": {"id": participle.id, "name": participle.name}},
        status=201,
    )


@require_POST
def import_ingredient_from_api(request: HttpRequest):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({"detail": "Solicitud invalida"}, status=400)

    user_query = str(payload.get("query") or "").strip()
    normalized = normalize_spanish_term(user_query)
    if not normalized:
        return JsonResponse({"detail": "Debes escribir un ingrediente"}, status=400)

    local = NutritionalInfoIngredient.objects.filter(
        Q(normalized_name=normalized) | Q(name__iexact=user_query)
    ).first()
    if local:
        return JsonResponse({"status": "exists", "ingredient": _ingredient_payload(local)}, status=200)

    service = USDAImportService()
    try:
        ingredient, created = service.import_from_user_query(user_query)
    except USDANoResultsError:
        return JsonResponse(
            {"detail": "No se encontraron resultados en USDA para este termino."},
            status=404,
        )
    except USDAClientError as error:
        return JsonResponse(
            {"detail": f"No fue posible importar desde USDA: {error}"},
            status=502,
        )

    return JsonResponse(
        {
            "status": "created" if created else "exists",
            "ingredient": _ingredient_payload(ingredient),
        },
        status=201 if created else 200,
    )


@require_GET
def ingredient_detail_local(request: HttpRequest, source_id: int):
    ingredient = get_object_or_404(NutritionalInfoIngredient, source_id=source_id)
    return JsonResponse(
        {
            "source_id": ingredient.source_id,
            "name": ingredient.name,
            "scientific_name": ingredient.scientific_name,
            "source_name_en": ingredient.source_name_en,
            "source": ingredient.source,
            "fdc_id": ingredient.fdc_id,
            "energy_total": ingredient.energy_total,
            "protein_total": ingredient.protein_total,
            "nutrients": ingredient.nutrients or {},
        }
    )


def ingredient_detail_page(request: HttpRequest, source_id: int):
    ingredient = get_object_or_404(NutritionalInfoIngredient, source_id=source_id)

    if request.method == "POST":
        ingredient.search_aliases.all().delete()
        ingredient.delete()
        return redirect("ingredients-list")

    return render(
        request,
        "ingredient_detail.html",
        {
            "ingredient": ingredient,
            "nutrients": ingredient.nutrients or {},
        },
    )


def ingredients_list(request):
    query = (request.GET.get("q") or "").strip()
    qs = NutritionalInfoIngredient.objects.all()
    if query:
        if query.isdigit():
            qs = qs.filter(
                Q(source_id=int(query))
                | Q(name__icontains=query)
                | Q(scientific_name__icontains=query)
            )
        else:
            qs = qs.filter(Q(name__icontains=query) | Q(scientific_name__icontains=query))

    paginator = Paginator(qs, 50)
    page_obj = paginator.get_page(request.GET.get("page", 1))

    return render(
        request,
        "ingredients_list.html",
        {
            "page_obj": page_obj,
            "query": query,
            "total_filtered": paginator.count,
        },
    )
