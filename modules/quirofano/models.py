from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from core.database import Base


class FormatoProcedimientoModel(Base):
    __tablename__ = "formato_procedimiento"

    formato_procedimiento_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigo = Column(String(5), unique=True, nullable=False, index=True)
    nombre = Column(String(100), nullable=False)
    activo = Column(Boolean, default=True)


class EstadoCirugiaModel(Base):
    __tablename__ = "estado_cirugia"

    estado_cirugia_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigo = Column(String(5), unique=True, nullable=False, index=True)
    nombre = Column(String(50), nullable=False)
    activo = Column(Boolean, default=True)


class RangoEspecialistaModel(Base):
    __tablename__ = "rango_especialista"

    rango_especialista_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigo = Column(String(5), unique=True, nullable=False, index=True)
    nombre = Column(String(50), nullable=False)
    activo = Column(Boolean, default=True)


class ProcedenciaProcedimientoModel(Base):
    __tablename__ = "procedencia_procedimiento"

    procedencia_procedimiento_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigo = Column(String(5), unique=True, nullable=False, index=True)
    nombre = Column(String(50), nullable=False)
    activo = Column(Boolean, default=True)


class CategoriaProcedimientoModel(Base):
    __tablename__ = "categoria_procedimiento"

    categoria_procedimiento_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigo = Column(String(10), unique=True, nullable=False, index=True)
    nombre = Column(String(150), nullable=False)
    activo = Column(Boolean, default=True)

    tipos = relationship("TipoProcedimientoModel", back_populates="categoria")


class TipoProcedimientoModel(Base):
    __tablename__ = "tipo_procedimiento"

    tipo_procedimiento_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigo = Column(String(10), unique=True, nullable=False, index=True)
    nombre = Column(String(200), nullable=False)
    categoria_procedimiento_id = Column(Integer, ForeignKey("categoria_procedimiento.categoria_procedimiento_id"), nullable=False)
    activo = Column(Boolean, default=True)

    categoria = relationship("CategoriaProcedimientoModel", back_populates="tipos")