from __future__ import annotations

import json
import logging
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from django.conf import settings

logger = logging.getLogger(__name__)


class USDAClientError(Exception):
    pass


class USDANoResultsError(USDAClientError):
    pass


class USDAFoodDataClient:
    def __init__(self, api_key: str | None = None, timeout: int = 10):
        self.api_key = api_key or getattr(settings, "USDA_API_KEY", "")
        self.timeout = timeout
        self.base_url = getattr(settings, "USDA_API_BASE_URL", "https://api.nal.usda.gov/fdc/v1")

    def _get_json(self, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        if not self.api_key:
            raise USDAClientError("USDA_API_KEY no configurada")

        query = {"api_key": self.api_key}
        if params:
            query.update(params)

        url = f"{self.base_url}{endpoint}?{urllib.parse.urlencode(query)}"

        request = urllib.request.Request(url=url, method="GET")
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                raw = response.read().decode("utf-8")
                return json.loads(raw)
        except urllib.error.HTTPError as error:
            if error.code == 429:
                if self.api_key == "DEMO_KEY":
                    raise USDAClientError(
                        "USDA rate limit alcanzado para DEMO_KEY. Configura USDA_API_KEY propia."
                    ) from error
                raise USDAClientError("USDA rate limit alcanzado") from error
            raise USDAClientError(f"USDA devolvio HTTP {error.code}") from error
        except urllib.error.URLError as error:
            raise USDAClientError("Error de red al consultar USDA") from error
        except json.JSONDecodeError as error:
            raise USDAClientError("Respuesta USDA invalida") from error

    def search_foods(self, query_en: str, page_size: int = 12) -> list[dict[str, Any]]:
        payload = self._get_json(
            "/foods/search",
            {
                "query": query_en,
                "pageSize": page_size,
            },
        )
        foods = payload.get("foods") or []
        return foods

    def get_food_detail(self, fdc_id: int) -> dict[str, Any]:
        return self._get_json(f"/food/{fdc_id}")
