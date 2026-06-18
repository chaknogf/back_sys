from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class EncamamientoBase(BaseModel):
    nombre_servicio: str = Field(..., max_length=100)
    descripcion: Optional[str] = None
    camas_censables: int = Field(..., ge=0)
    activo: Optional[bool] = True


class EncamamientoCreate(EncamamientoBase):
    pass


class EncamamientoUpdate(BaseModel):
    nombre_servicio: Optional[str] = Field(None, max_length=100)
    descripcion: Optional[str] = None
    camas_censables: Optional[int] = Field(None, ge=0)
    activo: Optional[bool]


class EncamamientoOut(EncamamientoBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
