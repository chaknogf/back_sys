from datetime import datetime
from sqlalchemy import Column, Integer, SmallInteger, String, DateTime, PrimaryKeyConstraint
from sqlalchemy.sql import func
from core.database import Base


class CorrelativoControl(Base):
    __tablename__ = "correlativos_control"

    tipo = Column(String(30), primary_key=True)
    anio = Column(SmallInteger, primary_key=True)
    ultimo_correlativo = Column(Integer, nullable=False, default=0)
    actualizado_en = Column(DateTime, server_default=func.now(), onupdate=func.now())


# Mantener modelos legacy para no romper imports existentes
class ExpedienteControl(Base):
    __tablename__ = "expediente_control"
    __table_args__ = {"extend_existing": True}

    anio = Column(SmallInteger, primary_key=True)
    ultimo_correlativo = Column(Integer, nullable=False, default=0)
    actualizado_en = Column(DateTime, server_default=func.now(), onupdate=func.now())


class EmergenciaControl(Base):
    __tablename__ = "emergencia_control"
    __table_args__ = {"extend_existing": True}

    anio = Column(SmallInteger, primary_key=True)
    ultimo_correlativo = Column(Integer, nullable=False, default=0)
    actualizado_en = Column(DateTime, server_default=func.now(), onupdate=func.now())


class ConstanciaNacimientoControl(Base):
    __tablename__ = "constancia_nacimiento_control"
    __table_args__ = {"extend_existing": True}

    anio = Column(SmallInteger, primary_key=True)
    ultimo_correlativo = Column(Integer, nullable=False, default=0)
    actualizado_en = Column(DateTime, server_default=func.now(), onupdate=func.now())


class DefuncionControl(Base):
    __tablename__ = "defuncion_control"
    __table_args__ = {"extend_existing": True}

    anio = Column(SmallInteger, primary_key=True)
    ultimo_correlativo = Column(Integer, nullable=False, default=0)
    actualizado_en = Column(DateTime, server_default=func.now(), onupdate=func.now())


class ConstanciaMedicaControl(Base):
    __tablename__ = "constancia_medica_control"
    __table_args__ = {"extend_existing": True}

    anio = Column(SmallInteger, primary_key=True)
    ultimo_correlativo = Column(Integer, nullable=False, default=0)
    actualizado_en = Column(DateTime, server_default=func.now(), onupdate=func.now())
