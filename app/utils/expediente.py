# app/utils/expediente.py

from datetime import datetime
from sqlalchemy import Column, Integer, SmallInteger, DateTime
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.database.db import Base

# ======================
# MODELOS DE CONTROL DE CORRELATIVOS
# ======================
class ExpedienteControl(Base):
    __tablename__ = "expediente_control"

    anio = Column(SmallInteger, primary_key=True)
    ultimo_correlativo = Column(Integer, nullable=False, default=0)
    actualizado_en = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
class EmergenciaControl(Base):
    __tablename__ = "emergencia_control"

    anio = Column(SmallInteger, primary_key=True)
    ultimo_correlativo = Column(Integer, nullable=False, default=0)
    actualizado_en = Column(DateTime, server_default=func.now(), onupdate=func.now())

class ConstanciaNacimientoControl(Base):
    __tablename__ = "constancia_nacimiento_control"

    anio = Column(SmallInteger, primary_key=True)
    ultimo_correlativo = Column(Integer, nullable=False, default=0)
    actualizado_en = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
class DefuncionControl(Base):
    __tablename__ = "defuncion_control"

    anio = Column(SmallInteger, primary_key=True)
    ultimo_correlativo = Column(Integer, nullable=False, default=0)
    actualizado_en = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
class ConstanciaMedicaControl(Base):
    __tablename__ = "constancia_medica_control"

    anio = Column(SmallInteger, primary_key=True)
    ultimo_correlativo = Column(Integer, nullable=False, default=0)
    actualizado_en = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
# ======================
# FUNCIONES PARA GENERAR CORRELATIVOS
# ======================

def generar_expediente(db: Session) -> str:
    anio_actual = int(datetime.now().strftime("%y"))  # 25 para 2025

    control = (
        db.query(ExpedienteControl)
        .filter(ExpedienteControl.anio == anio_actual)
        .with_for_update()
        .first()
    )

    if not control:
        # Año nuevo o tabla vacía → iniciar en 0
        control = ExpedienteControl(
            anio=anio_actual,
            ultimo_correlativo=0
        )
        db.add(control)
        db.flush()  # asegura persistencia sin commit

    # Incremento SIEMPRE después
    control.ultimo_correlativo += 1
    correlativo = control.ultimo_correlativo

    return f"{anio_actual}A-{correlativo}"

def generar_emergencia(db: Session) -> str:
    anio_actual = int(datetime.now().strftime("%y"))  # 25 para 2025

    control = (
        db.query(EmergenciaControl)
        .filter(EmergenciaControl.anio == anio_actual)
        .with_for_update()
        .first()
    )

    if not control:
        control = EmergenciaControl(
            anio=anio_actual,
            ultimo_correlativo=0
        )
        db.add(control)
        db.flush()

    control.ultimo_correlativo += 1
    correlativo = control.ultimo_correlativo

    return f"{correlativo}-E{anio_actual}"

def generar_constancia_nacimiento(db: Session) -> str:
    anio_actual = int(datetime.now().strftime("%y"))  # 25 para 2025

    control = (
        db.query(ConstanciaNacimientoControl)
        .filter(ConstanciaNacimientoControl.anio == anio_actual)
        .with_for_update()
        .first()
    )

    if not control:
        # Año nuevo o tabla vacía → iniciar en 0
        control = ConstanciaNacimientoControl(
            anio=anio_actual,
            ultimo_correlativo=0
        )
        db.add(control)
        db.flush()  # asegura persistencia sin commit

    # Incremento SIEMPRE después
    control.ultimo_correlativo += 1
    correlativo = control.ultimo_correlativo

    return f"CN-{correlativo}-{anio_actual}"

def generar_constancia_medica(db: Session) -> str:
    anio_actual = int(datetime.now().strftime("%y"))  # 25 para 2025

    control = (
        db.query(ConstanciaMedicaControl)
        .filter(ConstanciaMedicaControl.anio == anio_actual)
        .with_for_update()
        .first()
    )

    if not control:
        # Año nuevo o tabla vacía → iniciar en 0
        control = ConstanciaMedicaControl(
            anio=anio_actual,
            ultimo_correlativo=0
        )
        db.add(control)
        db.flush()  # asegura persistencia sin commit

    # Incremento SIEMPRE después
    control.ultimo_correlativo += 1
    correlativo = control.ultimo_correlativo

    return f"CM-{correlativo}-{anio_actual}"

def generar_defuncion(db: Session) -> str:
    anio_actual = int(datetime.now().strftime("%y"))  # 25 para 2025

    control = (
        db.query(DefuncionControl)
        .filter(DefuncionControl.anio == anio_actual)
        .with_for_update()
        .first()
    )

    if not control:
        # Año nuevo o tabla vacía → iniciar en 0
        control = DefuncionControl(
            anio=anio_actual,
            ultimo_correlativo=0
        )
        db.add(control)
        db.flush()  # asegura persistencia sin commit

    # Incremento SIEMPRE después
    control.ultimo_correlativo += 1
    correlativo = control.ultimo_correlativo

    return f"DF-{correlativo}-{anio_actual}"