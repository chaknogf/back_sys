"""Esquemas Pydantic para el catálogo maestro de procedimientos."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class CatalogoProcedimientoBase(BaseModel):
    abreviatura: Optional[str] = Field(None, max_length=10)
    nombre: str = Field(..., max_length=200)
    descripcion: Optional[str] = None
    anestesia: Optional[int] = Field(0, ge=0)
    especialidad_ref: Optional[int] = None
    activo: Optional[bool] = True


class CatalogoProcedimientoCreate(CatalogoProcedimientoBase):
    pass


class CatalogoProcedimientoUpdate(BaseModel):
    abreviatura: Optional[str] = Field(None, max_length=10)
    nombre: Optional[str] = Field(None, max_length=200)
    descripcion: Optional[str] = None
    anestesia: Optional[int] = Field(None, ge=0)
    especialidad_ref: Optional[int] = None
    activo: Optional[bool] = None


class CatalogoProcedimientoOut(CatalogoProcedimientoBase):
    id: int
    especialidad_nombre: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AreaCuerpoOut(BaseModel):
    id: int
    codigo: str
    nombre: str
    region: Optional[str] = None
    descripcion: Optional[str] = None
    activo: Optional[bool] = True

    model_config = ConfigDict(from_attributes=True)


class AreaCuerpoCreate(BaseModel):
    codigo: str = Field(..., max_length=20)
    nombre: str = Field(..., max_length=100)
    region: Optional[str] = Field(None, max_length=50)
    descripcion: Optional[str] = None
    activo: Optional[bool] = True


class AreaCuerpoUpdate(BaseModel):
    codigo: Optional[str] = Field(None, max_length=20)
    nombre: Optional[str] = Field(None, max_length=100)
    region: Optional[str] = Field(None, max_length=50)
    descripcion: Optional[str] = None
    activo: Optional[bool] = None