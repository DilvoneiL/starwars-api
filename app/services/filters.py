from typing import Any, Dict, List
from app.core.errors import BadRequestError

def _to_int(value: Any, field_name: str) -> int:
    try:
        return int(str(value))
    except Exception:
        raise BadRequestError(f"Invalid integer for {field_name}: {value}")

def apply_filters(items: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    filters: dict com chaves como:
      gender, eye_color, climate, starship_class, min_height, max_height, min_population, max_population, etc.
    """
    if not filters:
        return items

    result = items

    # filtros de igualdade (strings)
    eq_fields = ["gender", "eye_color", "hair_color", "climate", "terrain", "starship_class"]
    for f in eq_fields:
        if f in filters and filters[f] is not None:
            val = str(filters[f]).lower()
            result = [x for x in result if str(x.get(f, "")).lower() == val]

    # range: height
    if "min_height" in filters and filters["min_height"] is not None:
        mn = _to_int(filters["min_height"], "min_height")
        result = [x for x in result if str(x.get("height", "0")).isdigit() and int(x["height"]) >= mn]

    if "max_height" in filters and filters["max_height"] is not None:
        mx = _to_int(filters["max_height"], "max_height")
        result = [x for x in result if str(x.get("height", "0")).isdigit() and int(x["height"]) <= mx]

    # range: population (planets)
    if "min_population" in filters and filters["min_population"] is not None:
        mn = _to_int(filters["min_population"], "min_population")
        result = [x for x in result if str(x.get("population", "0")).isdigit() and int(x["population"]) >= mn]

    if "max_population" in filters and filters["max_population"] is not None:
        mx = _to_int(filters["max_population"], "max_population")
        result = [x for x in result if str(x.get("population", "0")).isdigit() and int(x["population"]) <= mx]

    return result
