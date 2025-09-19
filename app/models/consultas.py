from sqlalchemy import Column, Integer, String, Date, Time, TIMESTAMP, ForeignKey, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.database.db import Base

class ConsultaModel(Base):
    __tablename__ = 'consultas'

    id = Column(Integer, primary_key=True, autoincrement=True)
    expediente = Column(String(20), nullable=False)
    paciente_id = Column(Integer, ForeignKey('pacientes.id', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    tipo_consulta = Column(Integer)
    especialidad = Column(Integer)
    servicio = Column(Integer)
    documento = Column(String(20))
    fecha_consulta = Column(Date)
    hora_consulta = Column(Time)

    # JSONB con valores por defecto para evitar NULL
    ciclo = Column(JSONB, server_default=text("'{}'::jsonb"))
    indicadores = Column(JSONB, server_default=text("'[]'::jsonb"))
    detalle_clinico = Column(JSONB, server_default=text("'{}'::jsonb"))
    sistema = Column(JSONB, server_default=text("'{}'::jsonb"))
    signos_vitales = Column(JSONB, server_default=text("'{}'::jsonb"))
    antecedentes = Column(JSONB, server_default=text("'{}'::jsonb"))
    ordenes = Column(JSONB, server_default=text("'{}'::jsonb"))
    estudios = Column(JSONB, server_default=text("'{}'::jsonb"))
    comentario = Column(JSONB, server_default=text("'{}'::jsonb"))
    impresion_clinica = Column(JSONB, server_default=text("'{}'::jsonb"))
    tratamiento = Column(JSONB, server_default=text("'{}'::jsonb"))
    examen_fisico = Column(JSONB, server_default=text("'{}'::jsonb"))
    nota_enfermeria = Column(JSONB, server_default=text("'{}'::jsonb"))
    egreso = Column(JSONB, server_default=text("'{}'::jsonb"))
    presa_quirurgica = Column(JSONB, server_default=text("'{}'::jsonb"))
    contraindicado = Column(Text)

    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), onupdate=text("CURRENT_TIMESTAMP"), nullable=False)

    # Relaciones
    paciente = relationship("PacienteModel", back_populates="consultas")
    eventos = relationship("EventoConsultaModel", back_populates="consulta", cascade="all, delete-orphan")