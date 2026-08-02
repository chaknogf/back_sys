from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class PersonalSaludCreate(BaseModel):
    nombre: str = Field(..., max_length=200)
    especialidad_id: Optional[int] = None
    medico_id: Optional[int] = None


class PersonalSaludUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=200)
    especialidad_id: Optional[int] = None
    medico_id: Optional[int] = None


class PersonalSaludOut(BaseModel):
    id: int
    nombre: str
    especialidad_id: Optional[int] = None
    especialidad_nombre: Optional[str] = None
    medico_id: Optional[int] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
