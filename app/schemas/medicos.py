# app/schemas/medicos.py

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class MedicoBase(BaseModel):
    nombre: str = Field(..., max_length=200)
    colegiado: Optional[int] 
    dpi: Optional[int]
    sexo: Optional[str] = Field(None, max_length=1)
    especialidad: Optional[str] = Field(None, max_length=100)
    activo: Optional[bool] = True


class MedicoCreate(MedicoBase):
    pass


class MedicoUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=200)
    colegiado: Optional[int]
    dpi: Optional[int]
    sexo: Optional[str] = Field(None, max_length=1)
    especialidad: Optional[str] = Field(None, max_length=100)
    activo: Optional[bool]


class MedicoOut(MedicoBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True