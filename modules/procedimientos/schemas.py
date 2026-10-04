"""Validación de entradas y respuestas del catálogo y registro de procedimientos."""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import date, datetime
from typing import Optional


class ProcedimientoBase(BaseModel):
    abreviatura: Optional[str] = Field(None, max_length=10)
    nombre: str = Field(..., max_length=200)
    descripcion: Optional[str] = None
    anestesia: Optional[int] = Field(0, ge=0)

class ProcedimientoCreate(ProcedimientoBase):
    pass

class ProcedimientoUpdate(BaseModel):
    abreviatura: Optional[str] = Field(None, max_length=10)
    nombre: Optional[str] = Field(None, max_length=200)
    descripcion: Optional[str] = None
    anestesia: Optional[int] = Field(None, ge=0)

class ProcedimientoOut(ProcedimientoBase):
    id: int

    model_config = ConfigDict(
        from_attributes=True
    )

class ProcedimientoResponse(ProcedimientoOut):
    pass


class ProceMedicoBase(BaseModel):
    """Datos clínicos del procedimiento; valida sexo y cantidades/anestesia no negativas."""
    fecha: Optional[date] = None
    lugar_servicio: Optional[str] = None
    sexo: Optional[str] = Field(None, pattern="^[MF]$")
    id_procedimiento: Optional[int] = None
    id_catalogo_procedimiento: Optional[int] = None
    id_area_cuerpo_intervenida: Optional[int] = None
    especialidad: Optional[str] = None
    especialidad_id: Optional[int] = None
    cantidad: int = Field(1, ge=1)
    responsable: Optional[str] = Field(None, max_length=20)
    anestesia: Optional[int] = Field(0, ge=0)
    created_by: Optional[str] = Field(None, max_length=10)
    
    @field_validator('sexo')
    @classmethod
    def validate_sexo(cls, v):
        if v is not None and v not in ['M', 'F']:
            raise ValueError('sexo debe ser "M" o "F"')
        return v

class ProceMedicoCreate(ProceMedicoBase):
    pass

class ProceMedicoUpdate(BaseModel):
    fecha: Optional[date] = None
    lugar_servicio: Optional[str] = None
    sexo: Optional[str] = Field(None, pattern="^[MF]$")
    id_procedimiento: Optional[int] = None
    id_catalogo_procedimiento: Optional[int] = None
    id_area_cuerpo_intervenida: Optional[int] = None
    especialidad: Optional[str] = None
    especialidad_id: Optional[int] = None
    cantidad: Optional[int] = Field(None, ge=1)
    responsable: Optional[str] = Field(None, max_length=20)
    anestesia: Optional[int] = Field(None, ge=0)
    created_by: Optional[str] = Field(None, max_length=10)
    
    @field_validator('sexo')
    @classmethod
    def validate_sexo(cls, v):
        if v is not None and v not in ['M', 'F']:
            raise ValueError('sexo debe ser "M" o "F"')
        return v
    
class ProceMedicoOut(ProceMedicoBase):
    id: int
    procedimiento: Optional[ProcedimientoOut] = None
    catalogo: Optional["CatalogoProcedimientoOut"] = None
    area_cuerpo: Optional["AreaCuerpoOut"] = None

    model_config = ConfigDict(
        from_attributes=True
    )

class ProceMedicoInDB(ProceMedicoBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True
    )

class ProceMedicoResponse(ProceMedicoInDB):
    procedimiento_info: Optional[ProcedimientoResponse] = None
    
class ProcedimientosListResponse(BaseModel):
    total: int
    procedimientos: list[ProceMedicoOut]


class CatalogoProcedimientoBase(BaseModel):
    abreviatura: Optional[str] = Field(None, max_length=10)
    nombre: str = Field(..., max_length=200)
    descripcion: Optional[str] = None
    anestesia: Optional[int] = Field(0, ge=0)
    especialidad_ref: Optional[int] = None
    activo: Optional[bool] = True


class CatalogoProcedimientoOut(CatalogoProcedimientoBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class CatalogoProcedimientoCreate(CatalogoProcedimientoBase):
    pass


class CatalogoProcedimientoUpdate(BaseModel):
    abreviatura: Optional[str] = Field(None, max_length=10)
    nombre: Optional[str] = Field(None, max_length=200)
    descripcion: Optional[str] = None
    anestesia: Optional[int] = Field(None, ge=0)
    especialidad_ref: Optional[int] = None
    activo: Optional[bool] = None


class AreaCuerpoOut(BaseModel):
    id: int
    codigo: str
    nombre: str
    region: Optional[str] = None
    descripcion: Optional[str] = None
    activo: Optional[bool] = True

    model_config = ConfigDict(from_attributes=True)


ProceMedicoOut.model_rebuild()
