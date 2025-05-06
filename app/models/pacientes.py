from sqlalchemy import Column, Integer, String, Date, TIMESTAMP, JSON
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class PacienteModel(Base):
    __tablename__ = "pacientes"

    id = Column(Integer, primary_key=True, index=True)
    identificadores = Column(JSON, nullable=False)

    primer_nombre = Column(String(50))
    segundo_nombre = Column(String(50))
    otros_nombres = Column(String(100))
    primer_apellido = Column(String(50))
    segundo_apellido = Column(String(50))
    sexo = Column(String(2))
    fecha_nacimiento = Column(Date)

    contacto = Column(JSON)
    referencias = Column(JSON)
    datos_extra = Column(JSON)

    estado = Column(String(2), default='A')
    creado_por = Column(String(50))
    actualizado_por = Column(String(50))
    # creado_en = Column(TIMESTAMP, server_default=func.now())
    # actualizado_en = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())