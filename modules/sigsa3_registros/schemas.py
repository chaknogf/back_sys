from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import date, datetime


class Sigsa3RegistroBase(BaseModel):
    paciente_id: int = Field(..., description="ID del paciente (obligatorio)")
    medico_id: Optional[int] = None
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
    medico_id: Optional[int] = None
    personal_salud_id: Optional[int] = None
    consulta_id: Optional[int] = None
    fecha_consulta: Optional[date] = None
    tipo_consulta_id: Optional[int] = None
    control: Optional[str] = Field(None, max_length=80)
    semana_gestacional: Optional[int] = None
    codigo_cie_10_id: Optional[int] = None
    especialidad_id: Optional[int] = None


class Sigsa3RegistroOut(Sigsa3RegistroBase):
    id: int
    normalized_at: Optional[datetime] = None
    paciente_nombre: Optional[str] = None
    paciente_expediente: Optional[str] = None
    sexo: Optional[str] = None
    medico_nombre: Optional[str] = None
    personal_salud_nombre: Optional[str] = None
    tipo_consulta_nombre: Optional[str] = None
    codigo_cie_10: Optional[str] = None
    codigo_cie_10_descripcion: Optional[str] = None
    especialidad_nombre: Optional[str] = None
    sigsa3_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class Sigsa3RegistroListResponse(BaseModel):
    total: int
    registros: list[Sigsa3RegistroOut]
