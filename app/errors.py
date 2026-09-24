"""Format d'erreur unique : {"error": "<code>", "message": "<texte>", ...}"""
import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

log = logging.getLogger("app")


class AppError(Exception):
    def __init__(self, status: int, error: str, message: str, headers: dict | None = None, **extra):
        self.status, self.error, self.message, self.headers, self.extra = status, error, message, headers, extra


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _app_error(_: Request, exc: AppError):
        return JSONResponse({"error": exc.error, "message": exc.message, **exc.extra},
                            status_code=exc.status, headers=exc.headers)

    @app.exception_handler(RequestValidationError)
    async def _validation(_: Request, exc: RequestValidationError):
        details = [{"field": ".".join(str(p) for p in e["loc"][1:]), "message": e["msg"]} for e in exc.errors()]
        return JSONResponse({"error": "validation_error", "message": "Paramètres invalides", "details": details},
                            status_code=422)

    @app.exception_handler(StarletteHTTPException)
    async def _http(_: Request, exc: StarletteHTTPException):
        codes = {404: "not_found", 405: "method_not_allowed"}
        return JSONResponse({"error": codes.get(exc.status_code, "http_error"), "message": str(exc.detail)},
                            status_code=exc.status_code)

    @app.exception_handler(Exception)
    async def _unexpected(_: Request, exc: Exception):
        log.exception("Erreur inattendue")
        return JSONResponse({"error": "internal_error", "message": "Erreur interne"}, status_code=500)
