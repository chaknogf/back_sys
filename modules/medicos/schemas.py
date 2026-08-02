from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime


class MedicoBase(BaseModel):
    nombre: str = Field(..., max_length=200)
    colegiado: Optional[str] = Field(None, max_length=20)
    pasaporte: Optional[str] = Field(None, max_length=20)
    dpi: Optional[int] = None
    sexo: Optional[str] = Field(None, max_length=1)
    especialidad_id: Optional[int] = None
    activo: Optional[bool] = True


class MedicoCreate(MedicoBase):
    pass


class MedicoUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=200)
    colegiado: Optional[str] = Field(None, max_length=20)
    pasaporte: Optional[str] = Field(None, max_length=20)
    dpi: Optional[int] = None
    sexo: Optional[str] = Field(None, max_length=1)
    especialidad_id: Optional[int] = None
    activo: Optional[bool] = None


class MedicoOut(MedicoBase):
    id: int
    created_at: datetime
    especialidad_nombre: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class MedicoListResponse(BaseModel):
    total: int
    medicos: list[MedicoOut]

    model_config = ConfigDict(from_attributes=True)
