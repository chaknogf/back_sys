# modules/medicos/schemas.py

from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import datetime

class MedicoBase(BaseModel):
    nombre: str = Field(..., max_length=200)
    colegiado: Optional[int] = None
    dpi: Optional[int]
    sexo: Optional[str] = Field(None, max_length=1)
    especialidad: Optional[str] = Field(None, max_length=100)
    activo: Optional[bool] = True


class MedicoCreate(MedicoBase):
    pass


class MedicoUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=200)
    colegiado: Optional[int] = None
    dpi: Optional[int] = None
    sexo: Optional[str] = Field(None, max_length=1)
    especialidad: Optional[str] = Field(None, max_length=100)
    activo: Optional[bool] = None


class MedicoOut(MedicoBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MedicoListResponse(BaseModel):
    total: int
    medicos: List[MedicoOut]

    model_config = ConfigDict(from_attributes=True)
