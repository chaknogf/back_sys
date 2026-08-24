from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List


# ========================
# Formato Procedimiento
# ========================
class FormatoProcedimientoCreate(BaseModel):
    codigo: str = Field(..., max_length=5)
    nombre: str = Field(..., max_length=100)
    activo: bool = True


class FormatoProcedimientoUpdate(BaseModel):
    codigo: Optional[str] = Field(None, max_length=5)
    nombre: Optional[str] = Field(None, max_length=100)
    activo: Optional[bool] = None


class FormatoProcedimientoOut(BaseModel):
    formato_procedimiento_id: int
    codigo: str
    nombre: str
    activo: bool

    model_config = ConfigDict(from_attributes=True)


# ========================
# Estado Cirugía
# ========================
class EstadoCirugiaCreate(BaseModel):
    codigo: str = Field(..., max_length=5)
    nombre: str = Field(..., max_length=50)
    activo: bool = True


class EstadoCirugiaUpdate(BaseModel):
    codigo: Optional[str] = Field(None, max_length=5)
    nombre: Optional[str] = Field(None, max_length=50)
    activo: Optional[bool] = None


class EstadoCirugiaOut(BaseModel):
    estado_cirugia_id: int
    codigo: str
    nombre: str
    activo: bool

    model_config = ConfigDict(from_attributes=True)


# ========================
# Rango Especialista
# ========================
class RangoEspecialistaCreate(BaseModel):
    codigo: str = Field(..., max_length=5)
    nombre: str = Field(..., max_length=50)
    activo: bool = True


class RangoEspecialistaUpdate(BaseModel):
    codigo: Optional[str] = Field(None, max_length=5)
    nombre: Optional[str] = Field(None, max_length=50)
    activo: Optional[bool] = None


class RangoEspecialistaOut(BaseModel):
    rango_especialista_id: int
    codigo: str
    nombre: str
    activo: bool

    model_config = ConfigDict(from_attributes=True)


# ========================
# Procedencia Procedimiento
# ========================
class ProcedenciaProcedimientoCreate(BaseModel):
    codigo: str = Field(..., max_length=5)
    nombre: str = Field(..., max_length=50)
    activo: bool = True


class ProcedenciaProcedimientoUpdate(BaseModel):
    codigo: Optional[str] = Field(None, max_length=5)
    nombre: Optional[str] = Field(None, max_length=50)
    activo: Optional[bool] = None


class ProcedenciaProcedimientoOut(BaseModel):
    procedencia_procedimiento_id: int
    codigo: str
    nombre: str
    activo: bool

    model_config = ConfigDict(from_attributes=True)


# ========================
# Categoría Procedimiento
# ========================
class CategoriaProcedimientoCreate(BaseModel):
    codigo: str = Field(..., max_length=10)
    nombre: str = Field(..., max_length=150)
    activo: bool = True


class CategoriaProcedimientoUpdate(BaseModel):
    codigo: Optional[str] = Field(None, max_length=10)
    nombre: Optional[str] = Field(None, max_length=150)
    activo: Optional[bool] = None


class CategoriaProcedimientoOut(BaseModel):
    categoria_procedimiento_id: int
    codigo: str
    nombre: str
    activo: bool

    model_config = ConfigDict(from_attributes=True)


class CategoriaProcedimientoConTiposOut(CategoriaProcedimientoOut):
    tipos: List["TipoProcedimientoOut"] = []

    model_config = ConfigDict(from_attributes=True)


# ========================
# Tipo Procedimiento
# ========================
class TipoProcedimientoCreate(BaseModel):
    codigo: str = Field(..., max_length=10)
    nombre: str = Field(..., max_length=200)
    categoria_procedimiento_id: int
    activo: bool = True


class TipoProcedimientoUpdate(BaseModel):
    codigo: Optional[str] = Field(None, max_length=10)
    nombre: Optional[str] = Field(None, max_length=200)
    categoria_procedimiento_id: Optional[int] = None
    activo: Optional[bool] = None


class TipoProcedimientoOut(BaseModel):
    tipo_procedimiento_id: int
    codigo: str
    nombre: str
    categoria_procedimiento_id: int
    activo: bool

    model_config = ConfigDict(from_attributes=True)


class TipoProcedimientoConCategoriaOut(TipoProcedimientoOut):
    categoria: Optional[CategoriaProcedimientoOut] = None

    model_config = ConfigDict(from_attributes=True)


# Resolver forward reference
CategoriaProcedimientoConTiposOut.model_rebuild()