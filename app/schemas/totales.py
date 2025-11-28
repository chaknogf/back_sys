# app/schemas/totales.py
"""
Schemas para respuestas de conteos y estadísticas.
Usado en dashboard, reportes y monitoreo.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List


class TotalesItem(BaseModel):
    """Un solo ítem de conteo (ej: pacientes, consultas, usuarios)"""
    entidad: str = Field(..., description="Nombre de la entidad contada")
    total: int = Field(..., ge=0, description="Cantidad total")
    icono: str | None = Field(None, description="Icono para frontend (ej: 'users', 'file-medical')")
    color: str | None = Field(None, description="Color del card (ej: 'blue', 'green')")


class TotalesResponse(BaseModel):
    """Respuesta completa del dashboard con múltiples conteos"""
    totales: List[TotalesItem] = Field(..., description="Lista de conteos")
    generado_en: str = Field(..., description="Timestamp de generación")

    model_config = ConfigDict(from_attributes=False)