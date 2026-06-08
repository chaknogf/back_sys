from datetime import datetime
from sqlalchemy.orm import Session
from modules.expediente.models import (
    ExpedienteControl, EmergenciaControl,
    ConstanciaNacimientoControl, DefuncionControl, ConstanciaMedicaControl
)


def generar_expediente(db: Session) -> str:
    anio_actual = int(datetime.now().strftime("%y"))

    control = (
        db.query(ExpedienteControl)
        .filter(ExpedienteControl.anio == anio_actual)
        .with_for_update()
        .first()
    )

    if not control:
        control = ExpedienteControl(anio=anio_actual, ultimo_correlativo=0)
        db.add(control)
        db.flush()

    control.ultimo_correlativo += 1
    correlativo = control.ultimo_correlativo
    db.commit()
    return f"{anio_actual}A-{correlativo}"


def generar_emergencia(db: Session) -> str:
    anio_actual = int(datetime.now().strftime("%y"))

    control = (
        db.query(EmergenciaControl)
        .filter(EmergenciaControl.anio == anio_actual)
        .with_for_update()
        .first()
    )

    if not control:
        control = EmergenciaControl(anio=anio_actual, ultimo_correlativo=0)
        db.add(control)
        db.flush()

    control.ultimo_correlativo += 1
    correlativo = control.ultimo_correlativo
    db.commit()
    return f"{correlativo}-E{anio_actual}"


def generar_constancia_nacimiento(db: Session) -> str:
    anio_actual = int(datetime.now().strftime("%y"))

    control = (
        db.query(ConstanciaNacimientoControl)
        .filter(ConstanciaNacimientoControl.anio == anio_actual)
        .with_for_update()
        .first()
    )

    if not control:
        control = ConstanciaNacimientoControl(anio=anio_actual, ultimo_correlativo=0)
        db.add(control)
        db.flush()

    control.ultimo_correlativo += 1
    correlativo = control.ultimo_correlativo
    db.commit()
    return f"CN-{correlativo}-{anio_actual}"


def generar_constancia_medica(db: Session) -> str:
    anio_actual = int(datetime.now().strftime("%y"))

    control = (
        db.query(ConstanciaMedicaControl)
        .filter(ConstanciaMedicaControl.anio == anio_actual)
        .with_for_update()
        .first()
    )

    if not control:
        control = ConstanciaMedicaControl(anio=anio_actual, ultimo_correlativo=0)
        db.add(control)
        db.flush()

    control.ultimo_correlativo += 1
    correlativo = control.ultimo_correlativo
    db.commit()
    return f"CM-{correlativo}-{anio_actual}"


def generar_defuncion(db: Session) -> str:
    anio_actual = int(datetime.now().strftime("%y"))

    control = (
        db.query(DefuncionControl)
        .filter(DefuncionControl.anio == anio_actual)
        .with_for_update()
        .first()
    )

    if not control:
        control = DefuncionControl(anio=anio_actual, ultimo_correlativo=0)
        db.add(control)
        db.flush()

    control.ultimo_correlativo += 1
    correlativo = control.ultimo_correlativo
    db.commit()
    return f"DF-{correlativo}-{anio_actual}"
