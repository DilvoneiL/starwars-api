from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

class BadRequestError(Exception):
    def __init__(self, message: str):
        self.message = message

class UpstreamError(Exception):
    def __init__(self, message: str, status_code: int = 502):
        self.message = message
        self.status_code = status_code

class NotFoundError(Exception):
    def __init__(self, message: str):
        self.message = message

def add_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(BadRequestError)
    async def bad_request_handler(_: Request, exc: BadRequestError):
        return JSONResponse(status_code=400, content={"error": exc.message})

    @app.exception_handler(NotFoundError)
    async def not_found_handler(_: Request, exc: NotFoundError):
        return JSONResponse(status_code=404, content={"error": exc.message})

    @app.exception_handler(UpstreamError)
    async def upstream_handler(_: Request, exc: UpstreamError):
        return JSONResponse(status_code=exc.status_code, content={"error": exc.message})
