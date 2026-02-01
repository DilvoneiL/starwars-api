from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class Meta(BaseModel):
    sort: Optional[str] = None
    order: Optional[str] = None
    filters_applied: Dict[str, Any] = Field(default_factory=dict)
    included: List[str] = Field(default_factory=list)

class PaginatedResponse(BaseModel):
    resource: str
    count: int
    page: int
    page_size: int
    next: Optional[str] = None
    previous: Optional[str] = None
    results: List[Dict[str, Any]]
    meta: Meta = Field(default_factory=Meta)
