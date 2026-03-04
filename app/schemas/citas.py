# app/schemas/citas.py

from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


class CitaBase(BaseModel):
    fecha: Optional[date] = None
    paciente_id: Optional[int] = None
    especialidad: Optional[int] = None
    fecha_cita: Optional[date] = None
    nota: Optional[str] = None
    tipo: Optional[int] = None
    lab: Optional[int] = None
    fecha_lab: Optional[date] = None
    created_by: Optional[str] = None


class CitaCreate(CitaBase):
    pass


class CitaUpdate(CitaBase):
    pass


class CitaResponse(CitaBase):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True