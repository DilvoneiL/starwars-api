from typing import Any, Dict, List, Optional
from fastapi import APIRouter
from app.core.errors import BadRequestError
from app.services.swapi_client import get_json
from app.services.sorting import sort_items

router = APIRouter(tags=["relations"])

@router.get("/films/{film_id}/characters")
async def film_characters(
    film_id: int,
    sort: Optional[str] = "name",
    order: str = "asc",
    fields: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
):
    if page < 1:
        raise BadRequestError("page must be >= 1")
    if page_size < 1 or page_size > 100:
        raise BadRequestError("page_size must be between 1 and 100")

    film = await get_json(f"films/{film_id}/")

    characters_urls: List[str] = film.get("characters", [])
    characters: List[Dict[str, Any]] = []
    for url in characters_urls:
        characters.append(await get_json(url))

    characters = sort_items(characters, sort=sort, order=order)

    if fields:
        wanted = [x.strip() for x in fields.split(",") if x.strip()]
        characters = [{k: c.get(k) for k in wanted if k in c} for c in characters]

    total = len(characters)
    start = (page - 1) * page_size
    end = start + page_size
    paged = characters[start:end]

    return {
        "film_id": film_id,
        "film_title": film.get("title"),
        "count": total,
        "page": page,
        "page_size": len(paged),
        "results": paged,
    }
