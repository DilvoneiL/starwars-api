from typing import Any, Dict, List, Optional
from app.core.errors import BadRequestError

def sort_items(items: List[Dict[str, Any]], sort: Optional[str], order: str = "asc") -> List[Dict[str, Any]]:
    if not sort:
        return items

    if not items:
        return items

    if sort not in items[0]:
        # pode ser que nem todos tenham, mas pelo menos valida no primeiro
        raise BadRequestError(f"Invalid sort field: {sort}")

    reverse = (order or "asc").lower() == "desc"

    def key_fn(x: Dict[str, Any]) -> Any:
        v = x.get(sort)
        # tenta converter números quando fizer sentido
        if isinstance(v, str) and v.isdigit():
            return int(v)
        return v

    return sorted(items, key=key_fn, reverse=reverse)
