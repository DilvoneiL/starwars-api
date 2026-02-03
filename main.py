from a2wsgi import ASGIMiddleware
from app.main import app as fastapi_app

# Exporta um WSGI callable que o Functions Framework consegue servir
app = ASGIMiddleware(fastapi_app)
