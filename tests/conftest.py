import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services import swapi_client

@pytest.fixture(autouse=True)
def _clear_swapi_cache():
    swapi_client.clear_cache()
    yield

@pytest.fixture()
def client():
    return TestClient(app)
