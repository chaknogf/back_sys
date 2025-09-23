from pydantic import ConfigDict
from sqlalchemy import Column, Index, Integer, String, Date, Time, TIMESTAMP, ForeignKey, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.database.db import Base
from app.database.db import engine

class ConsultaModel(Base):
    __tablename__ = "consultas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    expediente = Column(String(20), nullable=False)
    paciente_id = Column(Integer, ForeignKey("pacientes.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    tipo_consulta = Column(Integer, nullable=False)
    especialidad = Column(Integer, nullable=False)
    servicio = Column(Integer, nullable=False)
    documento = Column(String(255), nullable=False)
    fecha_consulta = Column(Date, nullable=False)
    hora_consulta = Column(Time, nullable=False)
    indicadores = Column(JSONB, nullable=True)
    ciclo = Column(JSONB, nullable=True)
    creado_en = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    actualizado_en = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), onupdate=text("CURRENT_TIMESTAMP"), nullable=False)

    # Relaciones
    paciente = relationship("PacienteModel", back_populates="consultas")
    eventos = relationship("EventoConsultaModel", back_populates="consulta", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_consulta_paciente", "paciente_id"),
        Index("idx_consulta_fecha", "fecha_consulta"),
        Index("idx_consulta_tipo", "tipo_consulta"),
    )
    
class VistaConsultasModel(Base):
    __tablename__ = "vista_consultas"
    __table_args__ = {"autoload_with": engine}

    id_paciente = Column(Integer, primary_key=True)
    identificadores = Column(JSONB, nullable=True)
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
    especialidad = Column(Integer)
    servicio = Column(Integer)
    documento = Column(String)
    fecha_consulta = Column(Date)
    hora_consulta = Column(Time)
    ciclo = Column(JSONB, nullable=True)