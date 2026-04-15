# app/schemas/citas.py

from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, Dict, Any
from app.schemas.paciente import PacientesNombre


class CitaBase(BaseModel):
    fecha_registro: Optional[date] = None
    expediente: Optional[str] = None
    paciente_id: Optional[int] = None
    especialidad: Optional[str] = None
    fecha_cita: Optional[date] = None
    datos_extra: Optional[Dict[str, Any]] = None
   


class CitaCreate(CitaBase):
    pass


class CitaUpdate(BaseModel):
    id: int
    fecha_registro: Optional[date] = None
    paciente_id: Optional[int] = None
    expediente: Optional[str] = None
    especialidad: Optional[str] = None
    fecha_cita: Optional[date] = None
    datos_extra: Optional[Dict[str, Any]] = None



class CitaResponse(CitaBase):
    id: int
    created_by: str
    paciente: PacientesNombre
   

    class Config:
        from_attributes = True