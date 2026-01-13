# app/schemas/paises.py
"""
Schemas para países ISO (paises_iso).
Usado en selects, formularios de pacientes, reportes internacionales.
"""

from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class PaisOut(BaseModel):
    """
    Representación completa de un país según estándar ISO 3166.
    """
    id: int = Field(..., description="ID interno en la base de datos")
    nombre: str = Field(..., max_length=100, description="Nombre oficial del país")
   
    codigo_iso3: Optional[str] = Field(
        None,
        max_length=3,
        pattern=r"^[A-Z]{3}$",
        description="Código ISO 3166-1 alpha-3 (ej: GTM, USA, MEX)"
    )

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


# ===================================================================
# Versión ligera para <select> y autocomplete
# ===================================================================
class PaisSelect(BaseModel):
    """Ideal para dropdowns en frontend"""
    value: int = Field(..., description="ID del país (value del option)")
    label: str = Field(..., description="Texto visible (ej: Guatemala (GTM))")

    @staticmethod
    def from_orm(pais) -> "PaisSelect":
        iso = pais.codigo_iso3 or pais.codigo_iso2 or ""
        label = f"{pais.nombre}"
        if iso:
            label += f" ({iso})"
        return PaisSelect(value=pais.id, label=label)


# ===================================================================
# Respuesta para listas
# ===================================================================
class PaisListResponse(BaseModel):
    total: int = Field(..., ge=0)
    paises: List[PaisOut]

    model_config = ConfigDict(from_attributes=True)