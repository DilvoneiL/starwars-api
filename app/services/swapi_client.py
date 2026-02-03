import httpx
from typing import Any, Dict, Optional
from app.core.config import SWAPI_BASE_URL, HTTP_TIMEOUT_SECONDS, CACHE_TTL_SECONDS
from app.core.errors import UpstreamError, NotFoundError
from app.services.cache import TTLCache

_cache = TTLCache(ttl_seconds=CACHE_TTL_SECONDS)

def _full_url(path: str) -> str:
    if path.startswith("http://") or path.startswith("https://"):
        return path
    return f"{SWAPI_BASE_URL.rstrip('/')}/{path.lstrip('/')}"

async def get_json(path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    url = _full_url(path)

    # chave simples (boa o suficiente pro case)
    cache_key = url + (
        "?" + "&".join([f"{k}={v}" for k, v in (params or {}).items()])
        if params else ""
    )

    cached = _cache.get(cache_key)
    if cached is not None:
        return cached

    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT_SECONDS) as client:
            resp = await client.get(url, params=params)

            # ✅ Mapeamento correto de 404
            if resp.status_code == 404:
                raise NotFoundError(f"SWAPI resource not found: {url}")

            # ✅ Outros erros upstream viram 502
            if resp.status_code >= 400:
                raise UpstreamError(f"SWAPI error {resp.status_code} for {url}", status_code=502)

            data = resp.json()
            _cache.set(cache_key, data)
            return data

    except httpx.RequestError as e:
        raise UpstreamError(f"SWAPI request failed: {str(e)}", status_code=502)

def clear_cache() -> None:
    # limpa cache entre testes para evitar falsos positivos/negativos
    _cache._store.clear()
