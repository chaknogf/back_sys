from sqlalchemy import Column, Integer, String, Date, Time, TIMESTAMP, ForeignKey, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.database.db import Base

class ConsultaModel(Base):
    __tablename__ = 'consultas'

    id = Column(Integer, primary_key=True, autoincrement=True)
    paciente_id = Column(Integer, ForeignKey('pacientes.id', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    tipo_consulta = Column(Integer)
    especialidad = Column(Integer)
    servicio = Column(Integer)
    documento = Column(String(20))
    fecha_consulta = Column(Date)
    hora_consulta = Column(Time)
    ciclo = Column(JSONB)
    indicadores = Column(JSONB)
    detalle_clinico = Column(JSONB)
    sistema = Column(JSONB)
    signos_vitales = Column(JSONB)
    ansigmas = Column(JSONB)
    antecedentes = Column(JSONB)
    ordenes = Column(JSONB)
    estudios = Column(JSONB)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    paciente = relationship("PacienteModel", back_populates="consultas")
    eventos = relationship("EventoConsultaModel", back_populates="consulta", cascade="all, delete-orphan")