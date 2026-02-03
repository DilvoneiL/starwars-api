import respx
from httpx import Response

SWAPI = "https://swapi.dev/api"


def _people_page_1():
    return {
        "count": 2,
        "next": None,
        "previous": None,
        "results": [
            {
                "name": "Luke Skywalker",
                "height": "172",
                "gender": "male",
                "eye_color": "blue",
                "hair_color": "blond",
                "homeworld": f"{SWAPI}/planets/1/",
                "films": [f"{SWAPI}/films/1/"],
                "starships": [],
            },
            {
                "name": "Leia Organa",
                "height": "150",
                "gender": "female",
                "eye_color": "brown",
                "hair_color": "brown",
                "homeworld": f"{SWAPI}/planets/2/",
                "films": [f"{SWAPI}/films/1/"],
                "starships": [],
            },
        ],
    }


@respx.mock
def test_list_people_basic(client):
    # Mock SWAPI: GET https://swapi.dev/api/people/?page=1
    respx.get(f"{SWAPI}/people/").mock(
        return_value=Response(200, json=_people_page_1())
    )

    r = client.get("/v1/resources/people?page=1")
    assert r.status_code == 200

    data = r.json()
    assert data["resource"] == "people"
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert len(data["results"]) == 2


@respx.mock
def test_list_people_filter_gender(client):
    respx.get(f"{SWAPI}/people/").mock(
        return_value=Response(200, json=_people_page_1())
    )

    r = client.get("/v1/resources/people?gender=female")
    assert r.status_code == 200

    data = r.json()
    assert data["page_size"] == 1
    assert data["results"][0]["name"] == "Leia Organa"
    assert data["meta"]["filters_applied"]["gender"] == "female"


@respx.mock
def test_list_people_sort_name_desc(client):
    respx.get(f"{SWAPI}/people/").mock(
        return_value=Response(200, json=_people_page_1())
    )

    r = client.get("/v1/resources/people?sort=name&order=desc")
    assert r.status_code == 200

    data = r.json()
    names = [x["name"] for x in data["results"]]
    assert names == ["Luke Skywalker", "Leia Organa"]  # desc: Luke > Leia
    assert data["meta"]["sort"] == "name"
    assert data["meta"]["order"] == "desc"


@respx.mock
def test_list_people_fields_projection(client):
    respx.get(f"{SWAPI}/people/").mock(
        return_value=Response(200, json=_people_page_1())
    )

    r = client.get("/v1/resources/people?fields=name,gender")
    assert r.status_code == 200

    data = r.json()
    first = data["results"][0]
    assert set(first.keys()) == {"name", "gender"}  # só os campos pedidos


@respx.mock
def test_list_people_include_homeworld(client):
    respx.get(f"{SWAPI}/people/").mock(
        return_value=Response(200, json=_people_page_1())
    )

    # Mock do homeworld do Luke (planets/1)
    respx.get(f"{SWAPI}/planets/1/").mock(
        return_value=Response(200, json={"name": "Tatooine", "climate": "arid"})
    )
    # Mock do homeworld da Leia (planets/2)
    respx.get(f"{SWAPI}/planets/2/").mock(
        return_value=Response(200, json={"name": "Alderaan", "climate": "temperate"})
    )

    r = client.get("/v1/resources/people?include=homeworld")
    assert r.status_code == 200

    data = r.json()
    assert isinstance(data["results"][0]["homeworld"], dict)
    assert data["results"][0]["homeworld"]["name"] in ["Tatooine", "Alderaan"]
    assert "homeworld" in data["meta"]["included"]


@respx.mock
def test_invalid_resource_returns_400(client):
    r = client.get("/v1/resources/vehicles")
    assert r.status_code == 400
    assert "Unsupported resource" in r.json()["error"]


@respx.mock
def test_swapi_upstream_error_returns_502(client):
    # Simula SWAPI retornando erro
    respx.get(f"{SWAPI}/people/").mock(
        return_value=Response(500, json={"detail": "boom"})
    )

    r = client.get("/v1/resources/people")
    assert r.status_code == 502
    assert "SWAPI error" in r.json()["error"]
