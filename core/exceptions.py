"""Convierte errores de validación, integridad y ejecución en respuestas HTTP.

Nunca se envían al cliente detalles internos (mensajes de psycopg2, SQL,
nombres de restricciones, trazas ni el cuerpo crudo de la petición). El
diagnóstico completo se registra en el log del servidor junto con un
`request_id` de correlación; el cliente solo recibe el `request_id` para
reportarlo a soporte.
"""

import logging
import uuid

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import DataError, IntegrityError

logger = logging.getLogger("core.exceptions")

# SQLSTATE -> mensaje orientado al usuario (sin nombres de tabla/columna).
_SQLSTATE_DETALLE = {
    "23505": "Ya existe un registro con ese valor único.",
    "23503": "La operación afecta registros relacionados inexistentes o aún referenciados.",
    "23514": "El valor no cumple una restricción de datos del sistema.",
    "22001": "El valor supera la longitud permitida para ese campo.",
}

_DETALLE_GENERICO_409 = "Conflicto al guardar los datos."


def _sanear_errors(errors):
    """Deja solo ubicación/tipo/mensaje; elimina `input` (PHI) y `ctx` no serializable."""
    limpios = []
    for err in errors:
        loc = [str(x) for x in err.get("loc", ()) if x not in ("body", "form")]
        item = {
            "loc": loc,
            "type": str(err.get("type", "")),
            "msg": str(err.get("msg", "")),
        }
        for clave in ("loc_ms", "url"):
            if clave in err:
                item[clave] = err[clave]
        limpios.append(item)
    return limpios


def _log_error(request: Request, request_id: str, exc, *, nivel="exception"):
    log = logger.exception if nivel == "exception" else logger.error
    log(
        "unhandled_error request_id=%s method=%s path=%s exc=%s: %s",
        request_id,
        request.method,
        request.url.path,
        type(exc).__name__,
        exc,
    )


def _request_id() -> str:
    return uuid.uuid4().hex[:12]


def register_exception_handlers(app):
    """Registra respuestas comunes; las violaciones de integridad se exponen como 409."""

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        request_id = _request_id()
        logger.warning(
            "validation_error request_id=%s method=%s path=%s errors=%s",
            request_id,
            request.method,
            request.url.path,
            _sanear_errors(exc.errors()),
        )
        return JSONResponse(
            status_code=422,
            content={
                "detail": "Error de validación",
                "errors": _sanear_errors(exc.errors()),
                "request_id": request_id,
            },
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        request_id = _request_id()
        _log_error(request, request_id, exc)
        sqlstate = getattr(getattr(exc, "orig", None), "sqlstate", "")
        detalle = _SQLSTATE_DETALLE.get(sqlstate, _DETALLE_GENERICO_409)
        return JSONResponse(
            status_code=409,
            content={"detail": detalle, "request_id": request_id},
        )

    @app.exception_handler(DataError)
    async def data_error_handler(request: Request, exc: DataError):
        request_id = _request_id()
        _log_error(request, request_id, exc)
        # Clasificación orientativa; el mensaje crudo de PostgreSQL NO se expone.
        mensaje = str(getattr(exc, "orig", None) or exc).lower()
        if "length" in mensaje or "too long" in mensaje:
            detalle = (
                "El valor supera la longitud permitida para ese campo "
                "(máx. 10 caracteres en Especialidad/Lugar/Responsable, "
                "o 200 en nombre del procedimiento)."
            )
        elif "null" in mensaje:
            detalle = "El campo es obligatorio y no puede ser nulo."
        elif "check constraint" in mensaje:
            detalle = "El valor no cumple la restricción de validación del campo."
        else:
            detalle = "Los datos enviados no cumplen el formato esperado."
        return JSONResponse(
            status_code=400,
            content={"detail": detalle, "request_id": request_id},
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        request_id = _request_id()
        _log_error(request, request_id, exc)
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Error interno del servidor",
                "request_id": request_id,
            },
        )
