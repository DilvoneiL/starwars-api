import respx
from httpx import Response

SWAPI = "https://swapi.dev/api"


@respx.mock
def test_film_not_found_returns_404(client):
    respx.get(f"{SWAPI}/films/999/").mock(
        return_value=Response(404, json={"detail": "Not found"})
    )

    r = client.get("/v1/films/999/characters")
    assert r.status_code == 404


@respx.mock
def test_film_characters_pagination(client):
    film_id = 1

    respx.get(f"{SWAPI}/films/{film_id}/").mock(
        return_value=Response(
            200,
            json={
                "title": "A New Hope",
                "characters": [
                    f"{SWAPI}/people/1/",
                    f"{SWAPI}/people/2/",
                    f"{SWAPI}/people/3/",
                ],
            },
        )
    )

    respx.get(f"{SWAPI}/people/1/").mock(return_value=Response(200, json={"name": "Luke"}))
    respx.get(f"{SWAPI}/people/2/").mock(return_value=Response(200, json={"name": "Leia"}))
    respx.get(f"{SWAPI}/people/3/").mock(return_value=Response(200, json={"name": "Han"}))

    r = client.get("/v1/films/1/characters?sort=name&order=asc&page=2&page_size=1")
    assert r.status_code == 200

    data = r.json()
    assert data["count"] == 3
    assert data["page"] == 2
    assert data["page_size"] == 1
    assert data["results"][0]["name"] == "Leia"


@respx.mock
def test_film_characters_bad_page_returns_400(client):
    film_id = 1
    # mock do filme para garantir que se o handler passar pela validação, existe upstream
    respx.get(f"{SWAPI}/films/{film_id}/").mock(
        return_value=Response(200, json={"title": "A New Hope", "characters": []})
    )

    r = client.get("/v1/films/1/characters?page=0")
    assert r.status_code == 400
    assert "page must be" in r.json()["error"]
