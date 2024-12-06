# coding: utf-8
from sqlalchemy import BigInteger, Column, ForeignKey, Integer, String, TIMESTAMP, Text, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False, unique=True)
    descripcion = Column(Text)
    permisos = Column(String(250))


class Usuario(Base):
    __tablename__ = 'usuarios'

    id = Column(Integer, primary_key=True)
    username = Column(String(10), nullable=False, unique=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100))
    dpi = Column(BigInteger, unique=True)
    contraseña = Column(String(255))
    rol = Column(ForeignKey('roles.id'), index=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    role = relationship('Role')
