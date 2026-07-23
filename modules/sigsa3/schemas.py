from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date


class Sigsa3Base(BaseModel):
    personal_salud: Optional[str] = Field(None, max_length=100)
    fecha_consulta: Optional[date] = None
    no_historia_clinica: Optional[str] = Field(None, max_length=30)
    nombre_paciente: Optional[str] = Field(None, max_length=150)
    sexo: Optional[str] = Field(None, max_length=1)
    edad_dias: Optional[int] = None
    edad_meses: Optional[int] = None
    edad_anios: Optional[int] = None
    tipo_consulta: Optional[str] = Field(None, max_length=80)
    control: Optional[str] = Field(None, max_length=80)
    semana_gestacional: Optional[int] = None
    codigo_cie_10: Optional[str] = Field(None, max_length=30)
    dx: Optional[str] = None
    especialidad: Optional[str] = Field(None, max_length=100)
    paciente_id: Optional[int] = None
    medico_id: Optional[int] = None
    consulta_id: Optional[int] = None


class Sigsa3Create(Sigsa3Base):
    pass


class Sigsa3Update(BaseModel):
    paciente_id: Optional[int] = None
    personal_salud: Optional[str] = Field(None, max_length=100)
    fecha_consulta: Optional[date] = None
    no_historia_clinica: Optional[str] = Field(None, max_length=30)
    nombre_paciente: Optional[str] = Field(None, max_length=150)
    sexo: Optional[str] = Field(None, max_length=1)
    edad_dias: Optional[int] = None
    edad_meses: Optional[int] = None
    edad_anios: Optional[int] = None
    tipo_consulta: Optional[str] = Field(None, max_length=80)
    control: Optional[str] = Field(None, max_length=80)
    semana_gestacional: Optional[int] = None
    codigo_cie_10: Optional[str] = Field(None, max_length=30)
    dx: Optional[str] = None
    especialidad: Optional[str] = Field(None, max_length=100)
    medico_id: Optional[int] = None
    consulta_id: Optional[int] = None


class Sigsa3Out(Sigsa3Base):
    id: int
    paciente_id: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)
