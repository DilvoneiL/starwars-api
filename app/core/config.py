import os

SWAPI_BASE_URL = os.getenv("SWAPI_BASE_URL", "https://swapi.dev/api")
HTTP_TIMEOUT_SECONDS = float(os.getenv("HTTP_TIMEOUT_SECONDS", "10"))
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "120"))

SUPPORTED_RESOURCES = {"people", "planets", "starships", "films"}
MAX_INCLUDE_DEPTH = int(os.getenv("MAX_INCLUDE_DEPTH", "1"))  # evita explosão de requests
