from fastapi import FastAPI
from app.routers.resources import router as resources_router
from app.routers.relations import router as relations_router
from app.core.logging import setup_logging
from app.core.errors import add_exception_handlers

setup_logging()

app = FastAPI(
    title="StarWars API",
    version="1.0.0",
    description="API intermediária para consultas na SWAPI com filtros, ordenação e relações.",
)

# Routers
app.include_router(resources_router, prefix="/v1")
app.include_router(relations_router, prefix="/v1")

# Exception handlers
add_exception_handlers(app)

@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
