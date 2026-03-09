# app/schemas/citas.py

from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, Dict, Any


class CitaBase(BaseModel):
    fecha: Optional[date] = None
    expediente: Optional[str] = None
    paciente_id: Optional[int] = None
    especialidad: Optional[str] = None
    agenda: Optional[date] = None
    datos_extra: Optional[Dict[str, Any]] = None
    created_by: Optional[str] = None


class CitaCreate(CitaBase):
    pass


class CitaUpdate(BaseModel):
    fecha: Optional[date] = None
    paciente_id: Optional[int] = None
    especialidad: Optional[str] = None
    agenda: Optional[date] = None
    datos_extra: Optional[Dict[str, Any]] = None
    created_by: Optional[str] = None


class CitaResponse(CitaBase):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True