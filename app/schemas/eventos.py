# app/schemas/eventos.py
"""
Schemas para eventos de consulta.
Totalmente compatibles con Pydantic v2, FastAPI y OpenAPI.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import datetime


# ===================================================================
# Modelos anidados (reutilizables)
# ===================================================================
class DatosExtra(BaseModel):
    """Datos clave-valor flexibles (ej: presión, temperatura, etc.)"""
    clave: str
    valor: str | int | float | bool | None = None

    model_config = ConfigDict(extra="allow")  # Permite campos extras si llegan


class Responsable(BaseModel):
    """Persona que realiza el evento"""
    nombre: str
    registro: str                            # Número de colegiado, DPI, etc.
    nota: Optional[str] = None
    cargo: Optional[str] = None               # médico, enfermera, etc.

    model_config = ConfigDict(from_attributes=True)


# ===================================================================
# Schema base (común a creación y respuesta)
# ===================================================================
class EventoConsultaBase(BaseModel):
    consulta_id: int
    tipo_evento: int
    datos: Optional[Dict[str, Any]] | None = None       # JSON flexible
    responsable: Optional[Responsable] = None
    estado: Optional[str] = "A"                         # A=activo, I=inactivo

    model_config = ConfigDict(from_attributes=True)


# ===================================================================
# Para crear un evento (entrada)
# ===================================================================
class EventoConsultaCreate(EventoConsultaBase):
    """Schema usado al crear un nuevo evento"""
    pass  # Hereda todo de Base


# ===================================================================
# Para actualizar (parcial)
# ===================================================================
class EventoConsultaUpdate(BaseModel):
    """Schema para actualización parcial (PATCH)"""
    tipo_evento: Optional[int] = None
    datos: Optional[Dict[str, Any]] = None
    responsable: Optional[Responsable] = None
    estado: Optional[str] = None

    model_config = ConfigDict(extra="ignore")


# ===================================================================
# Respuesta completa (salida al frontend)
# ===================================================================
class EventoConsultaOut(EventoConsultaBase):
    """Schema devuelto al cliente"""
    id: int
    creado_en: datetime
    actualizado_en: datetime

    model_config = ConfigDict(from_attributes=True)


# ===================================================================
# Lista de eventos (para respuestas múltiples)
# ===================================================================
class EventoConsultaList(BaseModel):
    total: int
    eventos: list[EventoConsultaOut]

    model_config = ConfigDict(from_attributes=True)