from sqlalchemy import Column, Integer, String, Date, Time, TIMESTAMP, ForeignKey, JSON, text
from sqlalchemy import Column, Integer, String, Text, JSON, CHAR
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.database.db import Base


# 🧍‍♂️ Modelo: Paciente
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
    consultas = relationship("Consulta", back_populates="paciente")
    