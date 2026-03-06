from __future__ import annotations

from typing import Any

MISSING_TOKENS = {"", "NA", "N/A", "NULL", "NONE", "TR"}

REQUIRED_COLUMNS = ("f_id", "f_ori_name")
OPTIONAL_BASE_COLUMN_ALIASES = {
    "scientific_name": ("sci_name",),
    "edible_portion": ("edible_portion",),
    "energy_total": ("energía, total", "energ�a, total"),
    "protein_total": ("proteina, total",),
}


def is_missing(value: Any) -> bool:
    raw = "" if value is None else str(value).strip()
    return raw.upper() in MISSING_TOKENS


def parse_float(value: Any) -> float | None:
    if is_missing(value):
        return None

    raw = str(value).strip().replace(",", ".")
    try:
        return float(raw)
    except ValueError:
        return None


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def resolve_column_name(headers: list[str], aliases: tuple[str, ...]) -> str | None:
    for alias in aliases:
        if alias in headers:
            return alias
    return None


def extract_base_values(row: dict[str, Any], column_map: dict[str, str]) -> dict[str, Any]:
    scientific_name = clean_text(row.get(column_map.get("scientific_name", "")))
    edible_portion = parse_float(row.get(column_map.get("edible_portion", "")))
    energy_total = parse_float(row.get(column_map.get("energy_total", "")))
    protein_total = parse_float(row.get(column_map.get("protein_total", "")))
    return {
        "scientific_name": scientific_name,
        "edible_portion": edible_portion,
        "energy_total": energy_total,
        "protein_total": protein_total,
    }


def extract_nutrients(row: dict[str, Any], headers: list[str]) -> dict[str, Any]:
    all_optional = {name for aliases in OPTIONAL_BASE_COLUMN_ALIASES.values() for name in aliases}
    skip = set(REQUIRED_COLUMNS) | all_optional
    nutrients: dict[str, Any] = {}

    for header in headers:
        if header in skip:
            continue

        raw_value = row.get(header)
        if is_missing(raw_value):
            continue

        numeric_value = parse_float(raw_value)
        nutrients[header] = numeric_value if numeric_value is not None else clean_text(raw_value)

    return nutrients
