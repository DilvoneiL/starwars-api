from app.services.filters import apply_filters
from app.services.sorting import sort_items

def test_apply_filters_gender():
    items = [{"name": "A", "gender": "male"}, {"name": "B", "gender": "female"}]
    out = apply_filters(items, {"gender": "female"})
    assert len(out) == 1
    assert out[0]["name"] == "B"

def test_sort_items_asc():
    items = [{"name": "Leia"}, {"name": "Anakin"}]
    out = sort_items(items, "name", "asc")
    assert [x["name"] for x in out] == ["Anakin", "Leia"]

def test_sort_items_desc():
    items = [{"name": "Leia"}, {"name": "Anakin"}]
    out = sort_items(items, "name", "desc")
    assert [x["name"] for x in out] == ["Leia", "Anakin"]
