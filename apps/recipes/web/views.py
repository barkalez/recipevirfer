from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render

from apps.recipes.models import CsvIngredient


def landing(request):
    return render(request, "landing.html")


def home(request):
    total = CsvIngredient.objects.count()
    return render(request, "home.html", {"total_ingredients": total})


def recipes_create_placeholder(request):
    return render(request, "recipes_placeholder.html")


def ingredient_suggestions(request):
    query = (request.GET.get("q") or "").strip()
    if len(query) < 1:
        return JsonResponse({"results": []})

    rows = (
        CsvIngredient.objects.filter(alimento__istartswith=query)
        .order_by("alimento")
        .values("fdc_id", "alimento")[:5]
    )
    return JsonResponse({"results": list(rows)})


def ingredients_list(request):
    query = (request.GET.get("q") or "").strip()
    qs = CsvIngredient.objects.all()
    if query:
        if query.isdigit():
            qs = qs.filter(Q(fdc_id=int(query)) | Q(alimento__icontains=query))
        else:
            qs = qs.filter(alimento__icontains=query)

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
