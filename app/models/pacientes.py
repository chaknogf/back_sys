from sqlalchemy import Column, Integer, String, Date, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.database.db import Base

class PacienteModel(Base):
    __tablename__ = 'pacientes'

    id = Column(Integer, primary_key=True)
    identificadores = Column(JSONB, nullable=False)
    nombre = Column(JSONB)
    sexo = Column(String(2))
    fecha_nacimiento = Column(Date)
    contacto = Column(JSONB)
    referencias = Column(JSONB)
    datos_extra = Column(JSONB)
    estado = Column(String(2), default='A')
    metadatos = Column(JSONB)
    creado_en = Column(TIMESTAMP(timezone=True), server_default=text("NOW()"))
    actualizado_en = Column(TIMESTAMP(timezone=True), server_default=text("NOW()"))

    # relación con ConsultaModel
    consultas = relationship("ConsultaModel", back_populates="paciente", cascade="all, delete-orphan")