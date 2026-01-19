# app/utils/expediente.py

from datetime import datetime
from sqlalchemy import Column, Integer, SmallInteger, DateTime
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.database.db import Base


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


def generar_expediente(db: Session) -> str:
    anio_actual = int(datetime.now().strftime("%y"))  # 25 para 2025

    control = db.query(ExpedienteControl).filter_by(anio=anio_actual).first()

    if control:
        control.ultimo_correlativo += 1
    else:
        control = ExpedienteControl(anio=anio_actual, ultimo_correlativo=1)
        db.add(control)

    # ❌ NO commit aquí
    correlativo = control.ultimo_correlativo  # sin ceros
    return f"{anio_actual}A-{correlativo}"     # 25A-11

def generar_emergencia(db: Session) -> str:
    anio_actual = int(datetime.now().strftime("%y"))  # 25 para 2025

    control = db.query(EmergenciaControl).filter_by(anio=anio_actual).first()

    if control:
        control.ultimo_correlativo += 1
    else:
        control = EmergenciaControl(anio=anio_actual, ultimo_correlativo=1)
        db.add(control)

    # ❌ NO commit aquí
    correlativo = control.ultimo_correlativo
    return f"{correlativo}-E{anio_actual}"  # 16-E25