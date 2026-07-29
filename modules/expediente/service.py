from datetime import datetime
from sqlalchemy.orm import Session
from modules.expediente.models import CorrelativoControl


def _generar_correlativo(db: Session, tipo: str, formato: str) -> str:
    anio_actual = int(datetime.now().strftime("%y"))
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
    db.commit()
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
