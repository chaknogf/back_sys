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
    consulta_id: int | None = Field(None, description="Consulta de hospitalización que origina la intervención")
    expediente: str | None = Field(None, max_length=20)
    personal_atencion_id: int | None = Field(None, description="Cirujano (médico)")
    estado_cirugia_id: int | None = None
    formato_procedimiento_id: int | None = None
    procedencia_procedimiento_id: int | None = None
    rango_especialista_id: int | None = None
    especialidad_id: int | None = Field(None, description="Especialidad de la intervención")
    quirofano_numero_id: int | None = None
    procedimiento_principal: str | None = Field(None, max_length=200)
    procedimiento_2: str | None = Field(None, max_length=200)
    procedimiento_3: str | None = Field(None, max_length=200)
    procedimiento_4: str | None = Field(None, max_length=200)
    procedimiento_5: str | None = Field(None, max_length=200)
    procedimiento_principal_id: int | None = Field(None, description="FK al catálogo maestro")
    procedimiento_2_id: int | None = None
    procedimiento_3_id: int | None = None
    procedimiento_4_id: int | None = None
    procedimiento_5_id: int | None = None
    area_cuerpo_intervenida: str | None = Field(None, max_length=100)
    id_area_cuerpo_intervenida: int | None = Field(None, description="FK al catálogo de áreas del cuerpo")
    fecha: date = Field(default_factory=date.today, description="Fecha de la cirugía (automática)")
    hora_inicio_anestesia: time | None = None
    hora_inicio_intervencion: time | None = None
    hora_finaliza_intervencion: time | None = None
    hora_finaliza_limpieza_prepara_quirofano: time | None = None
    observaciones: str | None = None
    datos_extra: dict | None = Field(
        None,
        description="Datos adicionales (JSONB): equipo quirúrgico (circulante, instrumentista, pediatra, médico de apoyo), etc.",
    )


class IntervencionQuirurgicaUpdate(BaseModel):
    consulta_id: int | None = None
    personal_atencion_id: int | None = None
    estado_cirugia_id: int | None = None
    formato_procedimiento_id: int | None = None
    procedencia_procedimiento_id: int | None = None
    rango_especialista_id: int | None = None
    especialidad_id: int | None = None
    quirofano_numero_id: int | None = None
    procedimiento_principal: str | None = Field(None, max_length=200)
    procedimiento_2: str | None = Field(None, max_length=200)
    procedimiento_3: str | None = Field(None, max_length=200)
    procedimiento_4: str | None = Field(None, max_length=200)
    procedimiento_5: str | None = Field(None, max_length=200)
    procedimiento_principal_id: int | None = None
    procedimiento_2_id: int | None = None
    procedimiento_3_id: int | None = None
    procedimiento_4_id: int | None = None
    procedimiento_5_id: int | None = None
    area_cuerpo_intervenida: str | None = Field(None, max_length=100)
    id_area_cuerpo_intervenida: int | None = None
    fecha: date | None = None
    hora_inicio_anestesia: time | None = None
    hora_inicio_intervencion: time | None = None
    hora_finaliza_intervencion: time | None = None
    hora_finaliza_limpieza_prepara_quirofano: time | None = None
    observaciones: str | None = None
    activo: bool | None = None
    datos_extra: dict | None = None


class IntervencionQuirurgicaOut(BaseModel):
    intervencion_id: int
    paciente_id: int
    consulta_id: int | None = None
    paciente_nombre: str | None = None
    expediente: str | None = None
    personal_atencion_id: int | None = None
    personal_atencion_nombre: str | None = None
    procedimiento_principal: str | None = None
    procedimiento_principal_id: int | None = None
    procedimiento_principal_catalogo_nombre: str | None = None
    procedimiento_2: str | None = None
    procedimiento_2_id: int | None = None
    procedimiento_2_catalogo_nombre: str | None = None
    procedimiento_3: str | None = None
    procedimiento_3_id: int | None = None
    procedimiento_3_catalogo_nombre: str | None = None
    procedimiento_4: str | None = None
    procedimiento_4_id: int | None = None
    procedimiento_4_catalogo_nombre: str | None = None
    procedimiento_5: str | None = None
    procedimiento_5_id: int | None = None
    procedimiento_5_catalogo_nombre: str | None = None
    area_cuerpo_intervenida: str | None = None
    id_area_cuerpo_intervenida: int | None = None
    area_cuerpo_intervenida_nombre: str | None = None
    estado_cirugia_id: int | None = None
    estado_cirugia_nombre: str | None = None
    formato_procedimiento_id: int | None = None
    formato_procedimiento_nombre: str | None = None
    procedencia_procedimiento_id: int | None = None
    procedencia_procedimiento_nombre: str | None = None
    rango_especialista_id: int | None = None
    rango_especialista_nombre: str | None = None
    especialidad_id: int | None = None
    especialidad_nombre: str | None = None
    quirofano_numero_id: int | None = None
    quirofano_numero_nombre: str | None = None
    fecha: date
    hora_inicio_anestesia: time | None = None
    hora_inicio_intervencion: time | None = None
    hora_finaliza_intervencion: time | None = None
    hora_finaliza_limpieza_prepara_quirofano: time | None = None
    observaciones: str | None = None
    activo: bool
    datos_extra: dict | None = None
    created_at: str | None = None
    updated_at: str | None = None

    model_config = ConfigDict(from_attributes=False)


class IntervencionQuirurgicaListResponse(BaseModel):
    total: int
    intervenciones: List[IntervencionQuirurgicaOut]


# ========================
# Configuración de jornada por quirófano
# ========================
class QuirofanoConfigPeriodoOut(BaseModel):
    config_periodo_id: int
    quirofano_numero_id: int
    quirofano_numero_nombre: str | None = None
    hora_apertura: time
    hora_cierre: time
    dias_habiles: int
    activo: bool

    model_config = ConfigDict(from_attributes=False)


class QuirofanoConfigPeriodoUpdate(BaseModel):
    hora_apertura: Optional[time] = None
    hora_cierre: Optional[time] = None
    dias_habiles: Optional[int] = Field(None, ge=0)
    activo: Optional[bool] = None


# ========================
# Reporte / Resumen de quirófanos
# ========================
class IntervencionReporteFila(BaseModel):
    """Fila del detalle tipo hoja Q (columnas A..W + ayudantes)."""

    no: int
    intervencion_id: int
    quirofano_numero_id: int | None = None
    fecha: date
    paciente_nombre: str | None = None
    rango_medico: str | None = None
    especialidad: str | None = None
    medico: str | None = None
    procedencia: str | None = None
    formato: str | None = None
    procedimiento_1: str | None = None
    procedimiento_2: str | None = None
    procedimiento_3: str | None = None
    procedimiento_4: str | None = None
    procedimiento_5: str | None = None
    procedimientos: str | None = None
    area_cuerpo: str | None = None
    observaciones: str | None = None
    hora_inicio_anestesia: str | None = None
    hora_inicio_intervencion: str | None = None
    hora_finaliza_intervencion: str | None = None
    hora_finaliza_limpieza: str | None = None
    tiempo_intervencion_seg: int | None = None
    tiempo_uso_quirofano_seg: int | None = None
    tiempo_limpieza_seg: int | None = None
    estado: str | None = None


class KpiQuirofano(BaseModel):
    quirofano_numero_id: int | None = None
    numero: int | None = None
    nombre: str
    hora_apertura: str | None = None
    hora_cierre: str | None = None
    es_fallback: bool = False
    dias_abiertos: int = 0
    tiempo_disponible_seg: int = 0
    horas_activo_seg: int = 0
    total_intervenciones: int = 0
    finalizadas: int = 0
    canceladas: int = 0
    reprogramadas: int = 0
    procedimientos_total: int = 0
    intervalos_dias_promedio: float | None = None
    tiempo_promedio_intervencion_seg: int | None = None
    tiempo_promedio_uso_quirofano_seg: int | None = None
    tiempo_promedio_limpieza_seg: int | None = None
    porcentaje_uso: float = 0.0
    tasa_cancelacion: float = 0.0
    tasa_cancelacion_con_reprogramadas: float = 0.0


class ProcedimientoResumenFila(BaseModel):
    procedimiento: str
    cantidad: int
    tiempo_promedio_seg: int | None = None
    porcentaje_uso: float = 0.0
    intervalo_dias_promedio: float | None = None


class QuirofanoReporteDetalle(BaseModel):
    kpi: KpiQuirofano
    intervenciones: List[IntervencionReporteFila]


class ResumenReporteResponse(BaseModel):
    fecha_desde: date
    fecha_hasta: date
    generado_en: str
    filtros: dict
    kpi_global: KpiQuirofano
    por_quirofano: List[QuirofanoReporteDetalle]
    procedimientos: List[ProcedimientoResumenFila]
    advertencias: List[str] = []