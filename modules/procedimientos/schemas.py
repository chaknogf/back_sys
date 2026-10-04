"""Validación de entradas y respuestas del catálogo y registro de procedimientos."""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import date, datetime
from typing import Optional


# Grupos of age (IMCI/OMS) accepted in procedure records
GRUPOS_EDAD = {
    "NEO": "Neonatos (0 a 28 días)",
    "LAC": "Lactantes (más de 28 días a 12 meses)",
    "PRI": "Primera infancia (1 a menos de 5 años)",
    "SEG": "Segunda infancia (más de 5 años a 11 años)",
    "ADO": "Adolescentes (12 a menos de 18 años)",
    "ADU": "Adulto (18 a 59 años)",
    "ADM": "Adulto mayor (60 años en adelante)",
}


class ProcedimientoBase(BaseModel):
    abreviatura: Optional[str] = Field(None, max_length=10)
    nombre: str = Field(..., max_length=200)
    descripcion: Optional[str] = None
    anestesia: Optional[int] = Field(0, ge=0)

class ProcedimientoCreate(ProcedimientoBase):
    pass

class ProcedimientoUpdate(BaseModel):
    abreviatura: Optional[str] = Field(None, max_length=10)
    nombre: Optional[str] = Field(None, max_length=200)
    descripcion: Optional[str] = None
    anestesia: Optional[int] = Field(None, ge=0)

class ProcedimientoOut(ProcedimientoBase):
    id: int

    model_config = ConfigDict(
        from_attributes=True
    )

class ProcedimientoResponse(ProcedimientoOut):
    pass


class GrupoEdadCantidades(BaseModel):
    """Cantidades de un grupo de edad separadas por sexo."""
    m: int = Field(0, ge=0)
    f: int = Field(0, ge=0)


def validar_detalle_grupos(valor):
    """Normaliza el desglose: solo los 7 grupos válidos, cantidades enteras >= 0 y al menos un grupo con cantidad."""
    if valor is None:
        return None

    if not isinstance(valor, dict):
        raise ValueError("grupo_edad_detalle debe ser un objeto con los grupos de edad")

    detalle = {}
    for codigo, cantidades in valor.items():
        codigo = str(codigo).upper()
        if codigo not in GRUPOS_EDAD:
            raise ValueError(
                f"grupo de edad inválido: {codigo}. Valores permitidos: {', '.join(GRUPOS_EDAD)}"
            )

        if not isinstance(cantidades, dict):
            raise ValueError(f"el grupo {codigo} debe tener las cantidades m y f")

        m = int(cantidades.get("m") or 0)
        f = int(cantidades.get("f") or 0)
        if m < 0 or f < 0:
            raise ValueError(f"las cantidades del grupo {codigo} no pueden ser negativas")

        # Solo se guardan los grupos que realmente tienen cantidad
        if m or f:
            detalle[codigo] = {"m": m, "f": f}

    if not detalle:
        raise ValueError("debe registrar al menos un grupo de edad con cantidad")

    return detalle


def total_detalle_grupos(detalle) -> int:
    """Suma de todas las cantidades del desglose (acepta dicts u objetos)."""
    if not detalle:
        return 0

    total = 0
    for cantidades in detalle.values():
        if isinstance(cantidades, dict):
            total += int(cantidades.get("m", 0) or 0) + int(cantidades.get("f", 0) or 0)
        else:
            total += int(cantidades.m) + int(cantidades.f)
    return total


class ProceMedicoBase(BaseModel):
    """Datos clínicos del procedimiento con el desglose de cantidades por grupo de edad y sexo."""
    fecha: Optional[date] = None
    lugar_servicio: Optional[str] = None
    id_procedimiento: Optional[int] = None
    id_catalogo_procedimiento: Optional[int] = None
    id_area_cuerpo_intervenida: Optional[int] = None
    especialidad: Optional[str] = None
    especialidad_id: Optional[int] = None
    responsable: Optional[str] = Field(None, max_length=20)
    anestesia: Optional[int] = Field(0, ge=0)
    grupo_edad_detalle: Optional[dict[str, GrupoEdadCantidades]] = None
    created_by: Optional[str] = Field(None, max_length=10)

    @field_validator('grupo_edad_detalle', mode='before')
    @classmethod
    def validate_detalle(cls, v):
        return validar_detalle_grupos(v)

    @property
    def total_cantidad(self) -> int:
        return total_detalle_grupos(self.grupo_edad_detalle)

class ProceMedicoCreate(ProceMedicoBase):
    grupo_edad_detalle: dict[str, GrupoEdadCantidades]

    @field_validator('grupo_edad_detalle', mode='before')
    @classmethod
    def validate_detalle_requerido(cls, v):
        detalle = validar_detalle_grupos(v)
        if not detalle:
            raise ValueError("debe registrar al menos un grupo de edad con cantidad")
        return detalle

class ProceMedicoUpdate(BaseModel):
    fecha: Optional[date] = None
    lugar_servicio: Optional[str] = None
    id_procedimiento: Optional[int] = None
    id_catalogo_procedimiento: Optional[int] = None
    id_area_cuerpo_intervenida: Optional[int] = None
    especialidad: Optional[str] = None
    especialidad_id: Optional[int] = None
    responsable: Optional[str] = Field(None, max_length=20)
    anestesia: Optional[int] = Field(None, ge=0)
    grupo_edad_detalle: Optional[dict[str, GrupoEdadCantidades]] = None
    created_by: Optional[str] = Field(None, max_length=10)

    @field_validator('grupo_edad_detalle', mode='before')
    @classmethod
    def validate_detalle(cls, v):
        return validar_detalle_grupos(v)

    @property
    def total_cantidad(self) -> int:
        return total_detalle_grupos(self.grupo_edad_detalle)

class ProceMedicoOut(ProceMedicoBase):
    id: int
    cantidad: int = 0
    sexo: Optional[str] = None
    procedimiento: Optional[ProcedimientoOut] = None
    catalogo: Optional["CatalogoProcedimientoOut"] = None
    area_cuerpo: Optional["AreaCuerpoOut"] = None

    model_config = ConfigDict(
        from_attributes=True
    )

class ProceMedicoInDB(ProceMedicoBase):
    id: int
    cantidad: int = 0
    sexo: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True
    )

class ProceMedicoResponse(ProceMedicoInDB):
    procedimiento_info: Optional[ProcedimientoResponse] = None
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
