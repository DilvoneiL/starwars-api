from typing import Any, Dict, List, Set
from app.core.config import MAX_INCLUDE_DEPTH
from app.services.swapi_client import get_json

RELATION_FIELDS = {
    # people
    "homeworld": "homeworld",
    "films": "films",
    "starships": "starships",
    # planets
    "residents": "residents",
    # films
    "characters": "characters",
    "planets": "planets",
    "starships": "starships",
}

async def enrich_item(item: Dict[str, Any], include: List[str], _depth: int = 0, _seen: Set[str] | None = None) -> Dict[str, Any]:
    if not include:
        return item
    if _depth >= MAX_INCLUDE_DEPTH:
        return item

    seen = _seen or set()
    out = dict(item)

    for inc in include:
        field = RELATION_FIELDS.get(inc)
        if not field:
            continue

        value = out.get(field)
        if not value:
            continue

        # value pode ser string(url) ou lista de urls
        if isinstance(value, str):
            if value in seen:
                continue
            seen.add(value)
            out[field] = await get_json(value)
        elif isinstance(value, list):
            enriched = []
            for url in value:
                if url in seen:
                    continue
                seen.add(url)
                enriched.append(await get_json(url))
            out[field] = enriched

    return out
