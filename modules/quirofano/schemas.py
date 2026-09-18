from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import date, time


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
# Procedimiento Quirófano
# ========================
class ProcedimientoQuirofanoCreate(BaseModel):
    codigo: Optional[str] = Field(None, max_length=10)
    nombre: str = Field(..., max_length=200)
    especialidad_id: Optional[int] = Field(
        None, description="Especialidad; NULL = aplica a todas (mixta)"
    )
    activo: bool = True


class ProcedimientoQuirofanoUpdate(BaseModel):
    codigo: Optional[str] = Field(None, max_length=10)
    nombre: Optional[str] = Field(None, max_length=200)
    especialidad_id: Optional[int] = None
    activo: Optional[bool] = None


class ProcedimientoQuirofanoOut(BaseModel):
    procedimiento_quirofano_id: int
    codigo: str
    nombre: str
    especialidad_id: Optional[int] = None
    especialidad_nombre: Optional[str] = None
    activo: bool

    model_config = ConfigDict(from_attributes=True)


# ========================
# Número de Quirófano
# ========================
class QuirofanoNumeroCreate(BaseModel):
    numero: int = Field(..., gt=0, description="Número de quirófano")
    nombre: str = Field(..., max_length=50)
    activo: bool = True


class QuirofanoNumeroUpdate(BaseModel):
    numero: Optional[int] = Field(None, gt=0)
    nombre: Optional[str] = Field(None, max_length=50)
    activo: Optional[bool] = None


class QuirofanoNumeroOut(BaseModel):
    quirofano_numero_id: int
    numero: int
    nombre: str
    activo: bool

    model_config = ConfigDict(from_attributes=True)


# ========================
# Intervención Quirúrgica
# ========================
class IntervencionQuirurgicaCreate(BaseModel):
    paciente_id: int = Field(..., description="ID del paciente")
    expediente: str | None = Field(None, max_length=20)
    medico_id: int | None = Field(None, description="Cirujano (médico)")
    estado_cirugia_id: int | None = None
    formato_procedimiento_id: int | None = None
    procedencia_procedimiento_id: int | None = None
    rango_especialista_id: int | None = None
    quirofano_numero_id: int | None = None
    procedimiento_principal: str | None = Field(None, max_length=200)
    procedimiento_2: str | None = Field(None, max_length=200)
    procedimiento_3: str | None = Field(None, max_length=200)
    procedimiento_4: str | None = Field(None, max_length=200)
    procedimiento_5: str | None = Field(None, max_length=200)
    area_cuerpo_intervenida: str | None = Field(None, max_length=100)
    fecha: date = Field(default_factory=date.today, description="Fecha de la cirugía (automática)")
    hora_inicio_anestesia: time | None = None
    hora_inicio_intervencion: time | None = None
    hora_finaliza_intervencion: time | None = None
    hora_finaliza_limpieza_prepara_quirofano: time | None = None
    observaciones: str | None = None


class IntervencionQuirurgicaUpdate(BaseModel):
    medico_id: int | None = None
    estado_cirugia_id: int | None = None
    formato_procedimiento_id: int | None = None
    procedencia_procedimiento_id: int | None = None
    rango_especialista_id: int | None = None
    quirofano_numero_id: int | None = None
    procedimiento_principal: str | None = Field(None, max_length=200)
    procedimiento_2: str | None = Field(None, max_length=200)
    procedimiento_3: str | None = Field(None, max_length=200)
    procedimiento_4: str | None = Field(None, max_length=200)
    procedimiento_5: str | None = Field(None, max_length=200)
    area_cuerpo_intervenida: str | None = Field(None, max_length=100)
    fecha: date | None = None
    hora_inicio_anestesia: time | None = None
    hora_inicio_intervencion: time | None = None
    hora_finaliza_intervencion: time | None = None
    hora_finaliza_limpieza_prepara_quirofano: time | None = None
    observaciones: str | None = None
    activo: bool | None = None


class IntervencionQuirurgicaOut(BaseModel):
    intervencion_id: int
    paciente_id: int
    paciente_nombre: str | None = None
    expediente: str | None = None
    medico_id: int | None = None
    medico_nombre: str | None = None
    procedimiento_principal: str | None = None
    procedimiento_2: str | None = None
    procedimiento_3: str | None = None
    procedimiento_4: str | None = None
    procedimiento_5: str | None = None
    area_cuerpo_intervenida: str | None = None
    estado_cirugia_id: int | None = None
    estado_cirugia_nombre: str | None = None
    formato_procedimiento_id: int | None = None
    formato_procedimiento_nombre: str | None = None
    procedencia_procedimiento_id: int | None = None
    procedencia_procedimiento_nombre: str | None = None
    rango_especialista_id: int | None = None
    rango_especialista_nombre: str | None = None
    quirofano_numero_id: int | None = None
    quirofano_numero_nombre: str | None = None
    fecha: date
    hora_inicio_anestesia: time | None = None
    hora_inicio_intervencion: time | None = None
    hora_finaliza_intervencion: time | None = None
    hora_finaliza_limpieza_prepara_quirofano: time | None = None
    observaciones: str | None = None
    activo: bool
    created_at: str | None = None
    updated_at: str | None = None

    model_config = ConfigDict(from_attributes=False)


class IntervencionQuirurgicaListResponse(BaseModel):
    total: int
    intervenciones: List[IntervencionQuirurgicaOut]