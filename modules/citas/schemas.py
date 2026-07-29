# modules/citas/schemas.py

from pydantic import BaseModel, ConfigDict, field_validator
from datetime import date, datetime
from typing import Optional, Dict, Any
from modules.pacientes.schemas import PacientesNombre


class CitaBase(BaseModel):
    fecha_registro: Optional[date] = None
    expediente: Optional[str] = None
    paciente_id: Optional[int] = None
    especialidad: Optional[str] = None
    especialidad_id: Optional[int] = None
    fecha_cita: Optional[date] = None
    razon_consulta: Optional[str] = None
    notas: Optional[str] = None
    datos_extra: Optional[Dict[str, Any]] = None
   

class CitaCreate(CitaBase):
    pass


class CitaUpdate(BaseModel):
    paciente_id: Optional[int] = None
    expediente: Optional[str] = None
    especialidad: Optional[str] = None
    especialidad_id: Optional[int] = None
    fecha_cita: Optional[date] = None
    razon_consulta: Optional[str] = None
    notas: Optional[str] = None
    datos_extra: Optional[Dict[str, Any]] = None


class CitasPorFechaRazon(BaseModel):
    fecha_cita: date
    razon_consulta: Optional[str]
    dia_semana: Optional[str]
    total: int

class CitaResponse(CitaBase):
    id: int
    created_by: str
    paciente: Optional[PacientesNombre] = None

    @field_validator("created_by", mode="before")
    @classmethod
    def coerce_created_by(cls, v):
        if isinstance(v, int):
            return str(v)
        return v

    model_config = ConfigDict(from_attributes=True)
        
class CitaListResponse(BaseModel):
    total: int
    citas: list[CitaResponse]
    model_config = ConfigDict(from_attributes=True)
