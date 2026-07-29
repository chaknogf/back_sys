from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class PersonalSaludCreate(BaseModel):
    nombre: str = Field(..., max_length=200)
    especialidad: Optional[str] = Field(None, max_length=100)
    especialidad_id: Optional[int] = None
    medico_id: Optional[int] = None


class PersonalSaludUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=200)
    especialidad: Optional[str] = Field(None, max_length=100)
    especialidad_id: Optional[int] = None
    medico_id: Optional[int] = None


class PersonalSaludOut(BaseModel):
    id: int
    nombre: str
    especialidad: Optional[str] = None
    especialidad_id: Optional[int] = None
    medico_id: Optional[int] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
