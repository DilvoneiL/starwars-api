import functions_framework
from a2wsgi import ASGIMiddleware
from werkzeug.wrappers import Response as WzResponse

from app.main import app as fastapi_app

wsgi_app = ASGIMiddleware(fastapi_app)

@functions_framework.http
def handler(request):
    return WzResponse.from_app(wsgi_app, request.environ)
