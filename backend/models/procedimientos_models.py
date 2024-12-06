# coding: utf-8
from sqlalchemy import BigInteger, Column, Date, Enum, ForeignKey, Integer, String, TIMESTAMP, Text, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class CodigoProcedimiento(Base):
    __tablename__ = 'codigo_procedimientos'

    id = Column(Integer, primary_key=True)
    abreviatura = Column(String(10), nullable=False)
    procedimiento = Column(String(200), nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))


class Especialidad(Base):
    __tablename__ = 'especialidad'

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    especialista = Column(String(100))


class Servicio(Base):
    __tablename__ = 'servicios'

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False, unique=True)
    descripcion = Column(Text)


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


class ProceMedico(Base):
    __tablename__ = 'proce_medicos'

    id = Column(Integer, primary_key=True)
    fecha = Column(Date)
    servicio_id = Column(ForeignKey('servicios.id'), index=True)
    sexo = Column(Enum('M', 'F'))
    codigo_procedimiento_id = Column(ForeignKey('codigo_procedimientos.id'), nullable=False, index=True)
    especialidad_id = Column(ForeignKey('especialidad.id'), index=True)
    cantidad = Column(Integer)
    medico_id = Column(ForeignKey('medicos.colegiado'), index=True)
    grupo_edad = Column(Enum('N', 'A'))
    created_by = Column(String(10))
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    codigo_procedimiento = relationship('CodigoProcedimiento')
    especialidad = relationship('Especialidad')
    medico = relationship('Medico')
    servicio = relationship('Servicio')
