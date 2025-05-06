from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import date, time, datetime

class ConsultaBase(BaseModel):
    paciente_id: int
    tipo_consulta: Optional[int] = None
    especialidad: Optional[int] = None
    servicio: Optional[int] = None
    documento: Optional[str] = None
    fecha_consulta: Optional[date] = None
    hora_consulta: Optional[time] = None
    ciclo: Optional[Dict[str, datetime]] = None
    indicadores: Optional[Dict[str, Any]] = None
    detalle_clinico: Optional[Dict[str, Any]] = None
    sistema: Optional[Dict[str, Any]] = None

class ConsultaCreate(ConsultaBase):
    pass

class ConsultaUpdate(ConsultaBase):
    pass

class ConsultaOut(ConsultaBase):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True