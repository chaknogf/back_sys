# app/schemas/procedimientos.py
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import date, datetime
from typing import Optional

#================================================
# Schemas para Procedimiento
#================================================
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


#===============================================
# Schemas para ProceMedico
#===============================================

class ProceMedicoBase(BaseModel):
    fecha: Optional[date] = None
    lugar_servicio: Optional[str] = None
    sexo: Optional[str] = Field(None, pattern="^[MF]$")
    id_procedimiento: Optional[int] = None
    especialidad: Optional[str] = None
    cantidad: int = Field(1, ge=1)
    responsable: Optional[str] = None
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
    especialidad: Optional[str] = None
    cantidad: Optional[int] = Field(None, ge=1)
    responsable: Optional[str] = None
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
    # Opcional: incluir datos relacionados
    procedimiento_info: Optional[ProcedimientoResponse] = None
    
class ProcedimientosListResponse(BaseModel):
    total: int
    procedimientos: list[ProceMedicoOut]