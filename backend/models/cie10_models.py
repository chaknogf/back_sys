# coding: utf-8
from sqlalchemy import CHAR, Column, ForeignKey, Integer, String, TIMESTAMP, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Especialidad(Base):
    __tablename__ = 'especialidad'

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    especialista = Column(String(100))


class Cie10(Base):
    __tablename__ = 'cie10'

    cod = Column(String(7), primary_key=True)
    grupo = Column(CHAR(1), index=True)
    dx = Column(String(250), nullable=False)
    abreviatura = Column(String(10))
    especialidad_id = Column(ForeignKey('especialidad.id'), index=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    especialidad = relationship('Especialidad')
