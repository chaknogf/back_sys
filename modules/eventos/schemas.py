# modules/eventos/schemas.py

from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class DatosExtra(BaseModel):
    clave: str
    valor: str | int | float | bool | None = None

    model_config = ConfigDict(extra="allow")


class Responsable(BaseModel):
    nombre: str
    registro: str
    nota: Optional[str] = None
    cargo: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class EventoConsultaBase(BaseModel):
    consulta_id: int
    tipo_evento: int
    datos: Optional[Dict[str, Any]] | None = None
    responsable: Optional[Responsable] = None
    estado: Optional[str] = "A"

    model_config = ConfigDict(from_attributes=True)


class EventoConsultaCreate(EventoConsultaBase):
    pass


class EventoConsultaUpdate(BaseModel):
    tipo_evento: Optional[int] = None
    datos: Optional[Dict[str, Any]] = None
    responsable: Optional[Responsable] = None
    estado: Optional[str] = None

    model_config = ConfigDict(extra="ignore")


class EventoConsultaOut(EventoConsultaBase):
    id: int
    creado_en: datetime
    actualizado_en: datetime

    model_config = ConfigDict(from_attributes=True)


class EventoConsultaList(BaseModel):
    total: int
    eventos: list[EventoConsultaOut]

    model_config = ConfigDict(from_attributes=True)
