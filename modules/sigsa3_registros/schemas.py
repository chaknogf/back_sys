"""Esquemas de entrada/salida para filas SIGSA-3 normalizadas y enriquecidas."""

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import date, datetime


class Sigsa3RegistroBase(BaseModel):
    """Datos normalizados; la fecha es obligatoria y el paciente puede faltar
    (registros normalizados sin asociar conservan los datos crudos)."""
    paciente_id: Optional[int] = Field(None, description="ID del paciente (opcional; NULL si no se pudo asociar)")
    personal_atencion_id: Optional[int] = Field(None, description="ID del médico (opcional)")
    personal_salud_id: Optional[int] = None
    consulta_id: Optional[int] = None
    fecha_consulta: date = Field(..., description="Fecha de la consulta (obligatorio)")
    tipo_consulta_id: Optional[int] = None
    control: Optional[str] = Field(None, max_length=80)
    semana_gestacional: Optional[int] = None
    codigo_cie_10_id: Optional[int] = None
    especialidad_id: Optional[int] = None


class Sigsa3RegistroCreate(Sigsa3RegistroBase):
    pass


class Sigsa3RegistroUpdate(BaseModel):
    paciente_id: Optional[int] = None
    personal_atencion_id: Optional[int] = None
    personal_salud_id: Optional[int] = None
    consulta_id: Optional[int] = None
    fecha_consulta: Optional[date] = None
    tipo_consulta_id: Optional[int] = None
    control: Optional[str] = Field(None, max_length=80)
    semana_gestacional: Optional[int] = None
    codigo_cie_10_id: Optional[int] = None
    especialidad_id: Optional[int] = None


class Sigsa3RegistroOut(Sigsa3RegistroBase):
    """Respuesta enriquecida con nombres legibles de paciente y catálogos."""
    id: int
    normalized_at: Optional[datetime] = None
    paciente_nombre: Optional[str] = None
    paciente_expediente: Optional[str] = None
    sexo: Optional[str] = None
    personal_atencion_nombre: Optional[str] = None
    personal_salud_nombre: Optional[str] = None
    tipo_consulta_nombre: Optional[str] = None
    codigo_cie_10: Optional[str] = None
    codigo_cie_10_descripcion: Optional[str] = None
    codigo_cie_10_completo: Optional[str] = None
    especialidad_nombre: Optional[str] = None
    sigsa3_id: Optional[int] = None
    # Fallback crudo cuando el registro quedó sin paciente asociado.
    sin_asociar: bool = False
    nombre_paciente_raw: Optional[str] = None
    no_historia_clinica: Optional[str] = None
    edad_anios: Optional[int] = None
    edad_meses: Optional[int] = None
    edad_dias: Optional[int] = None
    tipo_consulta_raw: Optional[str] = None
    codigo_cie_10_raw: Optional[str] = None
    personal_salud_raw: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class Sigsa3RegistroListResponse(BaseModel):
    total: int
    registros: list[Sigsa3RegistroOut]
