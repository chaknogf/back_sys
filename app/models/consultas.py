from sqlalchemy import Column, Integer, String, Date, Time, TIMESTAMP, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Consulta(Base):
    __tablename__ = "consultas"

    id = Column(Integer, primary_key=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id"), nullable=False)
    tipo_consulta = Column(Integer)
    especialidad = Column(Integer)
    servicio = Column(Integer)
    documento = Column(String(20))
    fecha_consulta = Column(Date)
    hora_consulta = Column(Time)
    ciclo = Column(JSON)  # JSONB para eventos de estado
    indicadores = Column(JSON)  # JSONB con indicadores varios
    detalle_clinico = Column(JSON)  # JSONB con información médica detallada
    sistema = Column(JSON)  # JSONB con información de sistema (creador/modificador)
    signos_vitales = Column(JSON)  # JSONB con signos vitales
    asigmas = Column(JSON)  # JSONB con asigmas
    antecedentes = Column(JSON)  # JSONB con antecedentes
    ordenes = Column(JSON)  # JSONB con ordenes
    # created_at = Column(TIMESTAMP, default=datetime.utcnow)
    # updated_at = Column(TIMESTAMP, default=datetime.utcnow)
