from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Query
from app.core.config import SUPPORTED_RESOURCES
from app.core.errors import BadRequestError
from app.models.schemas import PaginatedResponse, Meta
from app.services.swapi_client import get_json
from app.services.filters import apply_filters
from app.services.sorting import sort_items
from app.services.enrich import enrich_item

router = APIRouter(tags=["resources"])

def _parse_csv(value: Optional[str]) -> List[str]:
    if not value:
        return []
    return [x.strip() for x in value.split(",") if x.strip()]

def _select_fields(item: Dict[str, Any], fields: List[str]) -> Dict[str, Any]:
    if not fields:
        return item
    return {k: item.get(k) for k in fields if k in item}

@router.get("/resources/{resource}", response_model=PaginatedResponse)
async def list_resource(
    resource: str,
    search: Optional[str] = None,
    page: int = 1,
    sort: Optional[str] = None,
    order: str = "asc",
    fields: Optional[str] = None,
    include: Optional[str] = None,
    # filtros genéricos (você pode expandir conforme o recurso)
    gender: Optional[str] = None,
    eye_color: Optional[str] = None,
    hair_color: Optional[str] = None,
    climate: Optional[str] = None,
    terrain: Optional[str] = None,
    starship_class: Optional[str] = None,
    min_height: Optional[int] = None,
    max_height: Optional[int] = None,
    min_population: Optional[int] = None,
    max_population: Optional[int] = None,
):
    resource = resource.lower()
    if resource not in SUPPORTED_RESOURCES:
        raise BadRequestError(f"Unsupported resource: {resource}. Use one of {sorted(SUPPORTED_RESOURCES)}")

    params: Dict[str, Any] = {"page": page}
    if search:
        params["search"] = search

    swapi_data = await get_json(f"{resource}/", params=params)

    results: List[Dict[str, Any]] = swapi_data.get("results", [])
    filters_dict = {
        "gender": gender,
        "eye_color": eye_color,
        "hair_color": hair_color,
        "climate": climate,
        "terrain": terrain,
        "starship_class": starship_class,
        "min_height": min_height,
        "max_height": max_height,
        "min_population": min_population,
        "max_population": max_population,
    }

    # filtros locais (porque SWAPI não suporta tudo)
    filtered = apply_filters(results, {k: v for k, v in filters_dict.items() if v is not None})

    # ordenação local
    sorted_items = sort_items(filtered, sort=sort, order=order)

    include_list = _parse_csv(include)
    fields_list = _parse_csv(fields)

    # enrich + field selection
    final_results: List[Dict[str, Any]] = []
    for item in sorted_items:
        enriched = await enrich_item(item, include_list)
        projected = _select_fields(enriched, fields_list) if fields_list else enriched
        final_results.append(projected)

    meta = Meta(
        sort=sort,
        order=order,
        filters_applied={k: v for k, v in filters_dict.items() if v is not None},
        included=include_list,
    )

    return PaginatedResponse(
        resource=resource,
        count=swapi_data.get("count", len(final_results)),
        page=page,
        page_size=len(final_results),
        next=swapi_data.get("next"),
        previous=swapi_data.get("previous"),
        results=final_results,
        meta=meta,
    )
