from pydantic import BaseModel, Field, ConfigDict
from typing import List


class TotalesItem(BaseModel):
    entidad: str = Field(..., description="Nombre de la entidad contada")
    total: int = Field(..., ge=0, description="Cantidad total")
    icono: str | None = Field(None, description="Icono para frontend (ej: 'users', 'file-medical')")
    color: str | None = Field(None, description="Color del card (ej: 'blue', 'green')")


class TotalesResponse(BaseModel):
    totales: List[TotalesItem] = Field(..., description="Lista de conteos")
    generado_en: str = Field(..., description="Timestamp de generación")

    model_config = ConfigDict(from_attributes=False)
