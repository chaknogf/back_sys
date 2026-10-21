"""Validación de entradas y respuestas del catálogo y registro de procedimientos."""

from pydantic import BaseModel, Field, ConfigDict, model_validator
from datetime import date, datetime
from typing import Optional, Self


# Categorías etarias admitidas en el registro de procedimientos (corte a los 18 años)
CATEGORIAS_EDAD = {
    "nino": "PEDIA",
    "adulto": "ADULTO",
}

# Columnas del desglose niño/adulto × sexo (sin_edad_* es exclusivo de históricos)
CAMPOS_CATEGORIA = ("nino_m", "nino_f", "adulto_m", "adulto_f")


class ProceMedicoBase(BaseModel):
    """Datos clínicos del procedimiento con el desglose niño/adulto × sexo.

    `nino_*` son los procedimientos sobre menores de 18 años y `adulto_*` los de
    18 años o más, cada uno separado por sexo (`m`/`f`). `sin_edad_*` solo lo
    llenan los registros históricos migrados y no se captura desde el formulario.
    """
    fecha: Optional[date] = None
    lugar_servicio: Optional[str] = None
    id_catalogo_procedimiento: Optional[int] = None
    id_area_cuerpo_intervenida: Optional[int] = None
    especialidad: Optional[str] = None
    especialidad_id: Optional[int] = None
    responsable: Optional[str] = Field(None, max_length=20)
    anestesia: Optional[int] = Field(0, ge=0)
    created_by: Optional[str] = Field(None, max_length=10)
    nino_m: int = Field(0, ge=0)
    nino_f: int = Field(0, ge=0)
    adulto_m: int = Field(0, ge=0)
    adulto_f: int = Field(0, ge=0)
    sin_edad_m: int = Field(0, ge=0)
    sin_edad_f: int = Field(0, ge=0)

    @property
    def total_cantidad(self) -> int:
        return (
            self.nino_m + self.nino_f + self.adulto_m + self.adulto_f
            + self.sin_edad_m + self.sin_edad_f
        )


class ProceMedicoCreate(ProceMedicoBase):
    """Alta de un procedimiento realizado; exige al menos una persona capturada."""

    @model_validator(mode="after")
    def _validar_cantidad(self) -> Self:
        if self.total_cantidad <= 0:
            raise ValueError(
                "debe registrar al menos una persona (niño, adulto o no especificado)"
            )
        return self


class ProceMedicoUpdate(BaseModel):
    fecha: Optional[date] = None
    lugar_servicio: Optional[str] = None
    id_catalogo_procedimiento: Optional[int] = None
    id_area_cuerpo_intervenida: Optional[int] = None
    especialidad: Optional[str] = None
    especialidad_id: Optional[int] = None
    responsable: Optional[str] = Field(None, max_length=20)
    anestesia: Optional[int] = Field(None, ge=0)
    created_by: Optional[str] = Field(None, max_length=10)
    nino_m: Optional[int] = Field(None, ge=0)
    nino_f: Optional[int] = Field(None, ge=0)
    adulto_m: Optional[int] = Field(None, ge=0)
    adulto_f: Optional[int] = Field(None, ge=0)
    sin_edad_m: Optional[int] = Field(None, ge=0)
    sin_edad_f: Optional[int] = Field(None, ge=0)


class ProceMedicoOut(ProceMedicoBase):
    id: int
    cantidad: int = 0
    catalogo: Optional["CatalogoProcedimientoOut"] = None
    area_cuerpo: Optional["AreaCuerpoOut"] = None

    model_config = ConfigDict(from_attributes=True)


class ProceMedicoInDB(ProceMedicoBase):
    id: int
    cantidad: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProceMedicoResponse(ProceMedicoInDB):
    catalogo: Optional["CatalogoProcedimientoOut"] = None
    area_cuerpo: Optional["AreaCuerpoOut"] = None


class ProcedimientosListResponse(BaseModel):
    total: int
    procedimientos: list[ProceMedicoOut]


class CatalogoProcedimientoBase(BaseModel):
    abreviatura: Optional[str] = Field(None, max_length=10)
    nombre: str = Field(..., max_length=200)
    descripcion: Optional[str] = None
    anestesia: Optional[int] = Field(0, ge=0)
    especialidad_ref: Optional[int] = None
    activo: Optional[bool] = True


class CatalogoProcedimientoOut(CatalogoProcedimientoBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class CatalogoProcedimientoCreate(CatalogoProcedimientoBase):
    pass


class CatalogoProcedimientoUpdate(BaseModel):
    abreviatura: Optional[str] = Field(None, max_length=10)
    nombre: Optional[str] = Field(None, max_length=200)
    descripcion: Optional[str] = None
    anestesia: Optional[int] = Field(None, ge=0)
    especialidad_ref: Optional[int] = None
    activo: Optional[bool] = None


class AreaCuerpoOut(BaseModel):
    id: int
    codigo: str
    nombre: str
    region: Optional[str] = None
    descripcion: Optional[str] = None
    activo: Optional[bool] = True

    model_config = ConfigDict(from_attributes=True)


ProceMedicoOut.model_rebuild()
