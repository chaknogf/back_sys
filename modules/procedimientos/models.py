"""Modelos del catálogo de procedimientos y sus realizaciones clínicas."""

from sqlalchemy import Boolean, Column, Integer, String, Text, Date, TIMESTAMP, CheckConstraint, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base


class ProceMedico(Base):
    """Procedimiento realizado con su desglose por grupo etario (niño/adulto) y sexo.

    El desglose se guarda en seis columnas enteras:
    `nino_m/nino_f` (menores de 18 años), `adulto_m/adulto_f` (18 años o más) y
    `sin_edad_m/sin_edad_f` (registros históricos sin edad ni grupo etario).
    `cantidad` guarda la suma de las seis, para no recalcularla en cada reporte.
    """
    __tablename__ = "proce_medicos"
    __table_args__ = (
        CheckConstraint("cantidad >= 1", name="proce_medicos_cantidad_check"),
        {"schema": "public"}
    )

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, nullable=True)
    lugar_servicio = Column(String(10), nullable=True)
    id_catalogo_procedimiento = Column(Integer, ForeignKey("public.catalogo_procedimientos.id", ondelete="SET NULL"), nullable=True)
    id_area_cuerpo_intervenida = Column(Integer, ForeignKey("public.area_cuerpo_intervenida.id", ondelete="SET NULL"), nullable=True)
    especialidad = Column(String(10), nullable=True)
    especialidad_id = Column(Integer, ForeignKey("especialidades.id", ondelete="SET NULL"), nullable=True)
    cantidad = Column(Integer, nullable=False, default=1)
    responsable = Column(String(20), nullable=True)
    anestesia = Column(Integer, nullable=True, default=0)
    nino_m = Column(Integer, nullable=False, default=0, server_default="0")
    nino_f = Column(Integer, nullable=False, default=0, server_default="0")
    adulto_m = Column(Integer, nullable=False, default=0, server_default="0")
    adulto_f = Column(Integer, nullable=False, default=0, server_default="0")
    sin_edad_m = Column(Integer, nullable=False, default=0, server_default="0")
    sin_edad_f = Column(Integer, nullable=False, default=0, server_default="0")
    created_by = Column(String(10), nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())

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


class CatalogoProcedimientoEspecialidad(Base):
    """Tabla puente: especialidades habilitadas para un procedimiento del catálogo.

    Un procedimiento puede quedar habilitado para varias especialidades; la
    columna `especialidad_ref` de `CatalogoProcedimiento` se conserva como
    referencia principal (la primera de la lista) por compatibilidad.
    """
    __tablename__ = "catalogo_procedimientos_especialidades"
    __table_args__ = (
        UniqueConstraint("id_catalogo_procedimiento", "id_especialidad", name="uq_cat_proc_esp"),
        {"schema": "public"},
    )

    id = Column(Integer, primary_key=True, index=True)
    id_catalogo_procedimiento = Column(
        Integer,
        ForeignKey("public.catalogo_procedimientos.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    id_especialidad = Column(
        Integer,
        ForeignKey("especialidades.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())


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
