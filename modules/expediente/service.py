"""Generación de correlativos anuales para expedientes y documentos clínicos."""

from datetime import datetime
from zoneinfo import ZoneInfo
from sqlalchemy.orm import Session
from modules.expediente.models import CorrelativoControl
from core.config import APP_TIMEZONE


def _generar_correlativo(db: Session, tipo: str, formato: str) -> str:
    """Incrementa el contador anual bajo bloqueo de fila.

    No confirma la transacción: el llamador hace commit (o rollback) junto con
    el resto de su operación, para que el correlativo y el documento que lo usa
    sean atómicos."""
    anio_actual = int(datetime.now(APP_TIMEZONE).strftime("%y"))
    control = (
        db.query(CorrelativoControl)
        .filter(
            CorrelativoControl.tipo == tipo,
            CorrelativoControl.anio == anio_actual,
        )
        .with_for_update()
        .first()
    )
    if not control:
        control = CorrelativoControl(tipo=tipo, anio=anio_actual, ultimo_correlativo=0)
        db.add(control)
        db.flush()
    control.ultimo_correlativo += 1
    correlativo = control.ultimo_correlativo
    db.flush()
    return formato.format(correlativo=correlativo, anio=anio_actual)


def generar_expediente(db: Session) -> str:
    return _generar_correlativo(db, "expediente", "{anio}A-{correlativo}")


def generar_emergencia(db: Session) -> str:
    return _generar_correlativo(db, "emergencia", "{correlativo}-E{anio}")


def generar_constancia_nacimiento(db: Session) -> str:
    return _generar_correlativo(db, "constancia_nacimiento", "CN-{correlativo}-{anio}")


def generar_constancia_medica(db: Session) -> str:
    return _generar_correlativo(db, "constancia_medica", "CM-{correlativo}-{anio}")


def generar_defuncion(db: Session) -> str:
    return _generar_correlativo(db, "defuncion", "DF-{correlativo}-{anio}")
