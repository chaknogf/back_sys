from sqlalchemy import (
    Column, Integer, String, Boolean, ForeignKey, UniqueConstraint, Date, Time, Text, TIMESTAMP
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base


class IntervencionQuirurgicaModel(Base):
    __tablename__ = "intervenciones_quirurgicas"

    intervencion_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id", ondelete="SET NULL"), nullable=False, index=True)
    expediente = Column(String(20), index=True)
    procedimiento_principal = Column(String(200), nullable=True)
    procedimiento_2 = Column(String(200), nullable=True)
    procedimiento_3 = Column(String(200), nullable=True)
    procedimiento_4 = Column(String(200), nullable=True)
    procedimiento_5 = Column(String(200), nullable=True)
    area_cuerpo_intervenida = Column(String(100), nullable=True)
    estado_cirugia_id = Column(Integer, ForeignKey("estado_cirugia.estado_cirugia_id", ondelete="SET NULL"), index=True)
    formato_procedimiento_id = Column(Integer, ForeignKey("formato_procedimiento.formato_procedimiento_id", ondelete="SET NULL"))
    procedencia_procedimiento_id = Column(Integer, ForeignKey("procedencia_procedimiento.procedencia_procedimiento_id", ondelete="SET NULL"))
    rango_especialista_id = Column(Integer, ForeignKey("rango_especialista.rango_especialista_id", ondelete="SET NULL"))
    quirofano_numero_id = Column(Integer, ForeignKey("quirofano_numero.quirofano_numero_id", ondelete="SET NULL"), index=True)
    medico_id = Column(Integer, ForeignKey("medicos.id", ondelete="SET NULL"), index=True)
    fecha = Column(Date, nullable=False, index=True)
    hora_inicio_anestesia = Column(Time, nullable=True)
    hora_inicio_intervencion = Column(Time, nullable=True)
    hora_finaliza_intervencion = Column(Time, nullable=True)
    hora_finaliza_limpieza_prepara_quirofano = Column(Time, nullable=True)
    observaciones = Column(Text, nullable=True)
    activo = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    paciente = relationship("PacienteModel")
    estado_cirugia = relationship("EstadoCirugiaModel")
    formato_procedimiento = relationship("FormatoProcedimientoModel")
    procedencia_procedimiento = relationship("ProcedenciaProcedimientoModel")
    rango_especialista = relationship("RangoEspecialistaModel")
    quirofano_numero = relationship("QuirofanoNumeroModel")
    medico = relationship("MedicoModel")


class QuirofanoNumeroModel(Base):
    __tablename__ = "quirofano_numero"

    quirofano_numero_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    numero = Column(Integer, unique=True, nullable=False, index=True)
    nombre = Column(String(50), nullable=False)
    activo = Column(Boolean, default=True)


class FormatoProcedimientoModel(Base):
    __tablename__ = "formato_procedimiento"

    formato_procedimiento_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigo = Column(String(5), unique=True, nullable=False, index=True)
    nombre = Column(String(100), nullable=False)
    activo = Column(Boolean, default=True)


class EstadoCirugiaModel(Base):
    __tablename__ = "estado_cirugia"

    estado_cirugia_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigo = Column(String(5), unique=True, nullable=False, index=True)
    nombre = Column(String(50), nullable=False)
    activo = Column(Boolean, default=True)


class RangoEspecialistaModel(Base):
    __tablename__ = "rango_especialista"

    rango_especialista_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigo = Column(String(5), unique=True, nullable=False, index=True)
    nombre = Column(String(50), nullable=False)
    activo = Column(Boolean, default=True)


class ProcedenciaProcedimientoModel(Base):
    __tablename__ = "procedencia_procedimiento"

    procedencia_procedimiento_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigo = Column(String(5), unique=True, nullable=False, index=True)
    nombre = Column(String(50), nullable=False)
    activo = Column(Boolean, default=True)


class ProcedimientoQuirofanoModel(Base):
    __tablename__ = "procedimiento_quirofano"

    procedimiento_quirofano_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigo = Column(String(10), unique=True, nullable=False, index=True)
    nombre = Column(String(200), nullable=False)
    especialidad_id = Column(
        Integer, ForeignKey("especialidades.id", ondelete="RESTRICT"), nullable=True, index=True
    )
    activo = Column(Boolean, default=True)

    especialidad = relationship("EspecialidadModel", lazy="joined")

    @property
    def especialidad_nombre(self):
        return self.especialidad.nombre if self.especialidad else None