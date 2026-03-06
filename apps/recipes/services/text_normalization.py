from __future__ import annotations

import re
import unicodedata


def strip_accents(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def normalize_spanish_term(value: str) -> str:
    text = (value or "").strip().lower()
    text = strip_accents(text)
    text = re.sub(r"\s+", " ", text)
    return text


def normalize_query_tokens(value: str) -> list[str]:
    normalized = normalize_spanish_term(value)
    return [token for token in normalized.split(" ") if token]
