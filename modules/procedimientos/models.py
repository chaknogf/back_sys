"""Modelos del catálogo de procedimientos y sus realizaciones clínicas."""

from sqlalchemy import Boolean, Column, Integer, String, Text, Date, CHAR, TIMESTAMP, CheckConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base


class Procedimiento(Base):
    """Catálogo con nombres y abreviaturas únicos para procedimientos clínicos."""
    __tablename__ = "procedimientos"
    __table_args__ = {"schema": "public"}
    
    id = Column(Integer, primary_key=True, index=True)
    abreviatura = Column(String(10), unique=True, nullable=True)
    nombre = Column(String(200), unique=True, nullable=False)
    descripcion = Column(Text, nullable=True)
    anestesia = Column(Integer, nullable=True, default=0)
    
    proce_medicos = relationship("ProceMedico", back_populates="procedimiento")


class ProceMedico(Base):
    """Procedimiento realizado con el desglose de cantidades por grupo de edad y sexo.

    `grupo_edad_detalle` es un JSONB {"NEO": {"m": 2, "f": 1}, ...} y `cantidad`
    guarda su suma, para no recalcularla en cada reporte. La columna `sexo` se
    conserva únicamente para los registros históricos, que nunca tuvieron grupo
    etario; los registros nuevos la dejan en NULL.
    """
    __tablename__ = "proce_medicos"
    __table_args__ = (
        CheckConstraint("cantidad >= 1", name="proce_medicos_cantidad_check"),
        {"schema": "public"}
    )

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, nullable=True)
    lugar_servicio = Column(String(10), nullable=True)
    sexo = Column(CHAR(1), nullable=True)
    id_procedimiento = Column(Integer, ForeignKey("public.procedimientos.id", ondelete="SET NULL"), nullable=True)
    id_catalogo_procedimiento = Column(Integer, ForeignKey("public.catalogo_procedimientos.id", ondelete="SET NULL"), nullable=True)
    id_area_cuerpo_intervenida = Column(Integer, ForeignKey("public.area_cuerpo_intervenida.id", ondelete="SET NULL"), nullable=True)
    especialidad = Column(String(10), nullable=True)
    especialidad_id = Column(Integer, ForeignKey("especialidades.id", ondelete="SET NULL"), nullable=True)
    cantidad = Column(Integer, nullable=False, default=1)
    responsable = Column(String(20), nullable=True)
    anestesia = Column(Integer, nullable=True, default=0)
    grupo_edad_detalle = Column(JSONB, nullable=True)
    created_by = Column(String(10), nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())

    procedimiento = relationship("Procedimiento", back_populates="proce_medicos")
    catalogo = relationship("CatalogoProcedimiento", back_populates="proce_medicos")
    area_cuerpo = relationship("AreaCuerpoIntervenida", back_populates="proce_medicos")


class CatalogoProcedimiento(Base):
    """Catálogo maestro de procedimientos estandarizados."""
    __tablename__ = "catalogo_procedimientos"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    abreviatura = Column(String(10), unique=True, nullable=True)
    nombre = Column(String(200), unique=True, nullable=False)
    descripcion = Column(Text, nullable=True)
    anestesia = Column(Integer, nullable=True, default=0)
    especialidad_ref = Column(Integer, ForeignKey("especialidades.id", ondelete="SET NULL"), nullable=True)
    activo = Column(Boolean, nullable=True, default=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())

    proce_medicos = relationship("ProceMedico", back_populates="catalogo")


class AreaCuerpoIntervenida(Base):
    """Catálogo de áreas del cuerpo donde se realiza el procedimiento."""
    __tablename__ = "area_cuerpo_intervenida"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(20), unique=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    region = Column(String(50), nullable=True)
    descripcion = Column(Text, nullable=True)
    activo = Column(Boolean, nullable=True, default=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())

    proce_medicos = relationship("ProceMedico", back_populates="area_cuerpo")
