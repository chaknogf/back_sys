from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from starlette.formparsers import FormData


def _serializable_body(body):
    if isinstance(body, FormData):
        return {k: v for k, v in body.items()}
    return body


def register_exception_handlers(app):
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "detail": "Error de validación",
                "errors": exc.errors(),
                "body": _serializable_body(exc.body),
            },
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        return JSONResponse(
            status_code=409,
            content={
                "detail": "Conflicto de integridad de datos",
                "error": str(exc.orig) if hasattr(exc, 'orig') else str(exc),
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Error interno del servidor",
                "error": str(exc) if __debug__ else "Contacte al administrador",
            },
        )
