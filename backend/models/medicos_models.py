# coding: utf-8
from sqlalchemy import BigInteger, Column, Enum, ForeignKey, Integer, String, TIMESTAMP, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Especialidad(Base):
    __tablename__ = 'especialidad'

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    especialista = Column(String(100))


class Medico(Base):
    __tablename__ = 'medicos'

    id = Column(Integer, primary_key=True)
    colegiado = Column(Integer, nullable=False, unique=True)
    nombre = Column(String(200))
    dpi = Column(BigInteger)
    especialidad = Column(ForeignKey('especialidad.id'), index=True)
    pasaporte = Column(String(30))
    sexo = Column(Enum('M', 'F'))
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    especialidad1 = relationship('Especialidad')
