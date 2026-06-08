from datetime import datetime
from sqlalchemy import Column, Integer, SmallInteger, DateTime
from sqlalchemy.sql import func
from core.database import Base


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
