"""Convierte errores de validación, integridad y ejecución en respuestas HTTP."""

from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, DataError
from starlette.formparsers import FormData


def _serializable_body(body):
    """Aplana FormData para que el cuerpo de validación pueda serializarse a JSON."""
    if isinstance(body, FormData):
        return {k: v for k, v in body.items()}
    return body


def register_exception_handlers(app):
    """Registra respuestas comunes; las violaciones de integridad se exponen como 409."""
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

    @app.exception_handler(DataError)
    async def data_error_handler(request: Request, exc: DataError):
        mensaje = str(exc.orig) if hasattr(exc, 'orig') else str(exc)
        # Extraer información útil del mensaje de PostgreSQL
        msg_lower = mensaje.lower()
        if 'length' in msg_lower or 'too long' in msg_lower:
            detalle = 'El valor supera la longitud permitida para ese campo (máx. 10 caracteres en Especialidad/Lugar/Responsable, o 200 en nombre del procedimiento).'
        elif 'null' in msg_lower or 'not null' in msg_lower:
            detalle = 'El campo es obligatorio y no puede ser nulo.'
        elif 'violates check constraint' in msg_lower:
            detalle = 'El valor no cumple la restricción del check constraint (ej. cantidad >= 1).'
        else:
            detalle = 'Error de datos: ' + mensaje
        return JSONResponse(
            status_code=400,
            content={"detail": detalle},
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
