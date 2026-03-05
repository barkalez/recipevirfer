#!/usr/bin/env python3
import csv
import os
import re
from collections import Counter, OrderedDict
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

PROGRESS_EVERY = 2_000_000
OUTPUT_FILE = "ingredientes_reales_usda.csv"

INPUT_FILES = {
    "food": "food.csv",
    "food_nutrient": "food_nutrient.csv",
    "nutrient": "nutrient.csv",
    "measure_unit": "measure_unit.csv",  # No es obligatorio usarlo, pero se valida existencia.
    "sr_legacy_food": "sr_legacy_food.csv",
    "food_category": "food_category.csv",  # No es obligatorio usarlo, pero se valida existencia.
}

EXCLUDE_TERMS = [
    "pillsbury", "kraft", "bakeries", "mcdonald", "nestle", "heinz", "campbell",
    "pizza", "burger", "sandwich", "muffin", "biscuit", "roll", "icing", "shake n bake",
    "soup", "stew", "cereal", "cookie", "cake", "chips", "candy", "chocolate", "ice cream",
    "ketchup", "mayonnaise", "dressing", "sauce", "seasoned", "breaded", "battered", "stuffed",
    "frozen", "prepared", "ready-to-eat", "rte", "restaurant", "fast food", "with ",
    # Marcas/comerciales detectadas en SR Legacy
    "goya", "gamesa", "la moderna", "crunchmaster", "pepperidge farm", "goldfish",
    "cracker barrel", "mars snackfood", "abbott", "ensure", "twizzlers", "milky way",
    # Alimentos claramente procesados/no ingrediente base
    "snack", "candies", "candy", "babyfood", "baby food", "beverage", "beverages", "drink",
    "canned", "syrup", "pie filling", "pie crust", "crackers", "cracker",
    "granola bar", "popcorn", "pretzels", "trail mix", "dessert",
    # Formas de cocción/preparación para evitar platos y versiones listas
    "cooked", "roasted", "broiled", "braised", "steamed", "fried", "baked", "grilled", "smoked",
]

MACROS = [
    "Energy",
    "Protein",
    "Total lipid (fat)",
    "Carbohydrate, by difference",
    "Fiber, total dietary",
    "Sugars, total including NLEA",
]

MICROS = [
    "Calcium, Ca", "Iron, Fe", "Magnesium, Mg", "Phosphorus, P", "Potassium, K", "Sodium, Na",
    "Zinc, Zn", "Copper, Cu", "Manganese, Mn", "Selenium, Se",
    "Iodine, I", "Chromium, Cr", "Molybdenum, Mo", "Chloride, Cl", "Fluoride, F",
    "Vitamin A, RAE", "Vitamin C, total ascorbic acid", "Vitamin D (D2 + D3)",
    "Vitamin E (alpha-tocopherol)", "Vitamin K (phylloquinone)",
    "Thiamin", "Riboflavin", "Niacin", "Pantothenic acid", "Vitamin B-6", "Folate, total",
    "Vitamin B-12", "Choline, total", "Biotin", "Vitamin A, IU",
]

SELECTED_NUTRIENTS = MACROS + MICROS

# Fallback mínimo para mantener sufijo de unidad en el nombre de columna si faltara en nutrient.csv.
FALLBACK_UNITS = {
    "Energy": "kcal",
    "Protein": "g",
    "Total lipid (fat)": "g",
    "Carbohydrate, by difference": "g",
    "Fiber, total dietary": "g",
    "Sugars, total including NLEA": "g",
    "Calcium, Ca": "mg",
    "Iron, Fe": "mg",
    "Magnesium, Mg": "mg",
    "Phosphorus, P": "mg",
    "Potassium, K": "mg",
    "Sodium, Na": "mg",
    "Zinc, Zn": "mg",
    "Copper, Cu": "mg",
    "Manganese, Mn": "mg",
    "Selenium, Se": "ug",
    "Iodine, I": "ug",
    "Chromium, Cr": "ug",
    "Molybdenum, Mo": "ug",
    "Chloride, Cl": "mg",
    "Fluoride, F": "ug",
    "Vitamin A, RAE": "ug",
    "Vitamin C, total ascorbic acid": "mg",
    "Vitamin D (D2 + D3)": "ug",
    "Vitamin E (alpha-tocopherol)": "mg",
    "Vitamin K (phylloquinone)": "ug",
    "Thiamin": "mg",
    "Riboflavin": "mg",
    "Niacin": "mg",
    "Pantothenic acid": "mg",
    "Vitamin B-6": "mg",
    "Folate, total": "ug",
    "Vitamin B-12": "ug",
    "Choline, total": "mg",
    "Biotin": "ug",
    "Vitamin A, IU": "iu",
}


def ensure_files_exist(paths: Dict[str, str]) -> None:
    missing = [p for p in paths.values() if not os.path.exists(p)]
    if missing:
        raise FileNotFoundError(f"Faltan archivos requeridos: {', '.join(missing)}")


def normalize_text(s: str) -> str:
    return (s or "").strip().lower()


def normalize_unit(unit: str) -> str:
    u = normalize_text(unit).replace("μ", "u").replace("µ", "u")
    u = u.replace("mcg", "ug")
    u = u.replace(" ", "")
    return u


def slugify(text: str) -> str:
    t = (text or "").strip().lower()
    t = t.replace("μ", "u").replace("µ", "u")
    t = t.replace("+", " plus ")
    t = re.sub(r"[^a-z0-9]+", "_", t)
    t = re.sub(r"_+", "_", t).strip("_")
    return t


def detect_column(fieldnames: Sequence[str], candidates: Sequence[str], file_name: str) -> str:
    name_map = {f.strip().lower(): f for f in fieldnames}
    for c in candidates:
        found = name_map.get(c.strip().lower())
        if found:
            return found
    raise RuntimeError(
        f"No se encontró columna esperada en {file_name}. Candidatas: {candidates}. "
        f"Header real: {list(fieldnames)}"
    )


def should_exclude_description(description: str) -> bool:
    d = normalize_text(description)
    return any(term in d for term in EXCLUDE_TERMS)


def read_sr_legacy_ids(path: str) -> Set[str]:
    with open(path, "r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise RuntimeError(f"{path} no tiene header")
        fdc_col = detect_column(reader.fieldnames, ["fdc_id", "id", "food_id"], path)

        ids = set()
        for row in reader:
            value = (row.get(fdc_col) or "").strip()
            if value:
                ids.add(value)
    return ids


def read_and_filter_foods(path: str, sr_ids: Set[str]) -> Tuple[Dict[str, str], Counter]:
    included: Dict[str, str] = {}
    excluded_counter: Counter = Counter()

    with open(path, "r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise RuntimeError(f"{path} no tiene header")

        fdc_col = detect_column(reader.fieldnames, ["fdc_id", "id", "food_id"], path)
        desc_col = detect_column(reader.fieldnames, ["description", "food_description", "desc"], path)

        for row in reader:
            fdc_id = (row.get(fdc_col) or "").strip()
            if not fdc_id or fdc_id not in sr_ids:
                continue

            desc = (row.get(desc_col) or "").strip()
            if should_exclude_description(desc):
                excluded_counter[desc] += 1
                continue

            included[fdc_id] = desc

    return included, excluded_counter


def read_nutrient_catalog(path: str) -> Tuple[Dict[str, str], Dict[str, str], Dict[str, str], List[str]]:
    """
    Devuelve:
    - nutrient_id_by_name: nombre nutriente -> nutrient_id
    - unit_by_name: nombre nutriente -> unidad normalizada
    - col_by_name: nombre nutriente -> nombre de columna de salida
    - missing_names: nutrientes objetivo no encontrados en nutrient.csv
    """
    selected_lc = {n.lower(): n for n in SELECTED_NUTRIENTS}
    nutrient_id_by_name: Dict[str, str] = {}
    unit_by_name: Dict[str, str] = {}

    with open(path, "r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise RuntimeError(f"{path} no tiene header")

        id_col = detect_column(reader.fieldnames, ["id", "nutrient_id"], path)
        name_col = detect_column(reader.fieldnames, ["name", "nutrient_name", "description"], path)
        unit_col = detect_column(reader.fieldnames, ["unit_name", "unit", "units"], path)

        for row in reader:
            n_id = (row.get(id_col) or "").strip()
            n_name = (row.get(name_col) or "").strip()
            unit = normalize_unit(row.get(unit_col) or "")
            if not n_id or not n_name:
                continue

            key = n_name.lower()
            if key in selected_lc and selected_lc[key] not in nutrient_id_by_name:
                canonical_name = selected_lc[key]
                nutrient_id_by_name[canonical_name] = n_id
                unit_by_name[canonical_name] = unit or FALLBACK_UNITS.get(canonical_name, "")

    col_by_name: Dict[str, str] = {}
    missing_names: List[str] = []
    used_cols = set()

    for n_name in SELECTED_NUTRIENTS:
        unit = unit_by_name.get(n_name) or FALLBACK_UNITS.get(n_name, "")
        base = slugify(n_name)
        col = f"{base}_{unit}" if unit else base

        # Evitar colisiones raras de nombres de columna.
        if col in used_cols:
            i = 2
            new_col = f"{col}_{i}"
            while new_col in used_cols:
                i += 1
                new_col = f"{col}_{i}"
            col = new_col

        used_cols.add(col)
        col_by_name[n_name] = col

        if n_name not in nutrient_id_by_name:
            missing_names.append(n_name)

    return nutrient_id_by_name, unit_by_name, col_by_name, missing_names


def stream_food_nutrients(
    path: str,
    included_food_ids: Set[str],
    nutrient_id_by_name: Dict[str, str],
) -> Dict[str, Dict[str, str]]:
    values_by_food: Dict[str, Dict[str, str]] = {}
    selected_nutrient_ids = set(nutrient_id_by_name.values())

    with open(path, "r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise RuntimeError(f"{path} no tiene header")

        food_col = detect_column(reader.fieldnames, ["food_id", "fdc_id", "id"], path)
        nutrient_col = detect_column(reader.fieldnames, ["nutrient_id", "id"], path)
        amount_col = detect_column(reader.fieldnames, ["amount", "value"], path)

        for i, row in enumerate(reader, start=1):
            if i % PROGRESS_EVERY == 0:
                print(f"[progreso] food_nutrient.csv: {i:,} líneas leídas...")

            fdc_id = (row.get(food_col) or "").strip()
            if not fdc_id or fdc_id not in included_food_ids:
                continue

            n_id = (row.get(nutrient_col) or "").strip()
            if not n_id or n_id not in selected_nutrient_ids:
                continue

            amount = (row.get(amount_col) or "").strip()
            if amount == "":
                continue

            bucket = values_by_food.setdefault(fdc_id, {})
            if n_id not in bucket:
                bucket[n_id] = amount

    return values_by_food


def write_output(
    out_path: str,
    foods: Dict[str, str],
    values_by_food: Dict[str, Dict[str, str]],
    nutrient_id_by_name: Dict[str, str],
    col_by_name: Dict[str, str],
) -> int:
    header = ["fdc_id", "food"] + [col_by_name[n] for n in SELECTED_NUTRIENTS]
    written = 0

    # Orden reproducible por fdc_id numérico si es posible.
    def sort_key(x: str):
        return (0, int(x)) if x.isdigit() else (1, x)

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()

        for fdc_id in sorted(foods.keys(), key=sort_key):
            row = {"fdc_id": fdc_id, "food": foods[fdc_id]}
            nutrient_values = values_by_food.get(fdc_id, {})

            for n_name in SELECTED_NUTRIENTS:
                col = col_by_name[n_name]
                n_id = nutrient_id_by_name.get(n_name)
                row[col] = nutrient_values.get(n_id, "") if n_id else ""

            writer.writerow(row)
            written += 1

    return written


def print_excluded_top20(excluded_counter: Counter) -> None:
    print("\nTop 20 descripciones excluidas por heurística:")
    if not excluded_counter:
        print("(sin exclusiones heurísticas)")
        return

    for idx, (desc, count) in enumerate(excluded_counter.most_common(20), start=1):
        print(f"{idx:2d}. [{count}] {desc}")


def main() -> None:
    ensure_files_exist(INPUT_FILES)

    print("Cargando IDs SR Legacy...")
    sr_ids = read_sr_legacy_ids(INPUT_FILES["sr_legacy_food"])
    print(f"SR Legacy IDs cargados: {len(sr_ids):,}")

    print("Filtrando foods (SR Legacy + heurística por descripción)...")
    foods, excluded_counter = read_and_filter_foods(INPUT_FILES["food"], sr_ids)
    print(f"Foods incluidos tras filtro: {len(foods):,}")

    print("Cargando catálogo de nutrientes objetivo...")
    nutrient_id_by_name, unit_by_name, col_by_name, missing_names = read_nutrient_catalog(INPUT_FILES["nutrient"])

    print("Nutrientes objetivo (macros + micros):")
    print(f"- solicitados: {len(SELECTED_NUTRIENTS)}")
    print(f"- encontrados en nutrient.csv: {len(nutrient_id_by_name)}")
    if missing_names:
        print("- no encontrados (se dejarán columnas vacías):")
        for n in missing_names:
            print(f"  * {n}")

    print("Procesando food_nutrient.csv en streaming...")
    values_by_food = stream_food_nutrients(
        INPUT_FILES["food_nutrient"],
        included_food_ids=set(foods.keys()),
        nutrient_id_by_name=nutrient_id_by_name,
    )

    print(f"Escribiendo CSV de salida: {OUTPUT_FILE}")
    written_rows = write_output(
        OUTPUT_FILE,
        foods=foods,
        values_by_food=values_by_food,
        nutrient_id_by_name=nutrient_id_by_name,
        col_by_name=col_by_name,
    )

    print("\nResumen final:")
    print(f"- total de foods incluidos: {len(foods):,}")
    print(f"- total de filas escritas: {written_rows:,}")
    print_excluded_top20(excluded_counter)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}")
        raise
