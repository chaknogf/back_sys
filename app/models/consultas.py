# app/models/consultas.py → solo cambia __table_args__
from sqlalchemy import Column, Integer, String, Date, Time, ForeignKey, Index, text, desc
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP
from sqlalchemy.orm import relationship
from app.database.db import Base


class ConsultaModel(Base):
    __tablename__ = "consultas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    expediente = Column(String(20), nullable=True, index=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id", ondelete="CASCADE"), nullable=False, index=True)
    tipo_consulta = Column(Integer, nullable=False, index=True)
    especialidad = Column(String(50), nullable=False)
    servicio = Column(String(50), nullable=False)
    documento = Column(String(20), nullable=False)
    fecha_consulta = Column(Date, nullable=False, index=True)
    hora_consulta = Column(Time, nullable=False)
    indicadores = Column(JSONB, nullable=True)
    ciclo = Column(JSONB, nullable=True)
    orden = Column(Integer, nullable=True)
    #creado_en = Column(TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    #actualizado_en = Column(TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"), onupdate=text("CURRENT_TIMESTAMP"), nullable=False)

    paciente = relationship("PacienteModel", back_populates="consultas")
    eventos = relationship("EventoConsultaModel", back_populates="consulta", cascade="all, delete-orphan", passive_deletes=True)

    __table_args__ = (
        # Los índices más importantes para el sistema
        Index("idx_consulta_paciente_fecha", "paciente_id", "fecha_consulta"),
        Index("idx_consulta_fecha_desc", desc("fecha_consulta")),        # ← CORREGIDO
        Index("idx_consulta_tipo", "tipo_consulta"),
        Index("idx_consulta_servicio", "servicio"),
        Index("idx_consulta_documento", "documento"),
    )


# =============================================================================
# VISTA MATERIALIZADA (solo lectura) - NO se usa para INSERT/UPDATE/DELETE
# =============================================================================
class VistaConsultasModel(Base):
    """
    Representa una vista materializada en PostgreSQL (vista_consultas).
    Solo lectura. Ideal para reportes y búsquedas rápidas.
    """
    __tablename__ = "vista_consultas"
    __table_args__ = {"schema": "public"}  # Ajusta si tu vista está en otro schema

    # Campos de la vista (exactamente como están en PostgreSQL)
    id_paciente = Column(Integer, primary_key=True)
    otro_id = Column(JSONB, nullable=True)
    expediente = Column(String)
    cui = Column(Integer, nullable=True)
    nombre = Column(JSONB, nullable=True)
    primer_nombre = Column(String)
    segundo_nombre = Column(String)
    otro_nombre = Column(String)
    primer_apellido = Column(String)
    segundo_apellido = Column(String)
    apellido_casada = Column(String)
    sexo = Column(String)
    fecha_nacimiento = Column(Date)
    estado = Column(String)

    id_consulta = Column(Integer)
    tipo_consulta = Column(Integer)
    especialidad = Column(String)
    servicio = Column(String)
    documento = Column(String)
    fecha_consulta = Column(Date)
    hora_consulta = Column(Time)
    ciclo = Column(JSONB, nullable=True)
    orden = Column(Integer, nullable=True)

    # Esta clase NO tiene relaciones ni métodos de escritura
    # Solo se usa para SELECT rápidas