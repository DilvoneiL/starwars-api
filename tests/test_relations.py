from typing import Any, Dict, List, Optional
from fastapi import APIRouter
from app.core.errors import NotFoundError
from app.services.swapi_client import get_json
from app.services.sorting import sort_items

router = APIRouter(tags=["relations"])

@router.get("/films/{film_id}/characters")
async def film_characters(
    film_id: int,
    sort: Optional[str] = "name",
    order: str = "asc",
    fields: Optional[str] = None,
):
    film = await get_json(f"films/{film_id}/")
    if not film:
        raise NotFoundError("Film not found")

    characters_urls: List[str] = film.get("characters", [])
    characters: List[Dict[str, Any]] = []
    for url in characters_urls:
        characters.append(await get_json(url))

    # ordenação local
    characters = sort_items(characters, sort=sort, order=order)

    # seleção de campos
    if fields:
        wanted = [x.strip() for x in fields.split(",") if x.strip()]
        characters = [{k: c.get(k) for k in wanted if k in c} for c in characters]

    return {
        "film_id": film_id,
        "film_title": film.get("title"),
        "count": len(characters),
        "results": characters,
    }
