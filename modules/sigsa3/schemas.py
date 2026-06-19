from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date


class Sigsa3Base(BaseModel):
    personal_salud: Optional[str] = Field(None, max_length=100)
    fecha_consulta: Optional[date] = None
    no_historia_clinica: Optional[str] = Field(None, max_length=30)
    nombre_paciente: Optional[str] = Field(None, max_length=150)
    sexo: Optional[str] = Field(None, max_length=1)
    pueblo: Optional[str] = Field(None, max_length=80)
    comunidad_linguistica: Optional[str] = Field(None, max_length=80)
    edad_dias: Optional[int] = None
    edad_meses: Optional[int] = None
    edad_anios: Optional[int] = None
    departamento_residencia: Optional[str] = Field(None, max_length=100)
    municipio_residencia: Optional[str] = Field(None, max_length=100)
    comunidad: Optional[str] = Field(None, max_length=150)
    direccion: Optional[str] = None
    tipo_consulta: Optional[str] = Field(None, max_length=80)
    control: Optional[str] = Field(None, max_length=80)
    semana_gestacional: Optional[int] = None
    descripcion_diagnostico_control: Optional[str] = None
    codigo_cie_10: Optional[str] = Field(None, max_length=30)
    dx: Optional[str] = None
    tipologia: Optional[str] = Field(None, max_length=100)
    especialidad: Optional[str] = Field(None, max_length=100)


class Sigsa3Create(Sigsa3Base):
    pass


class Sigsa3Update(BaseModel):
    personal_salud: Optional[str] = Field(None, max_length=100)
    fecha_consulta: Optional[date] = None
    no_historia_clinica: Optional[str] = Field(None, max_length=30)
    nombre_paciente: Optional[str] = Field(None, max_length=150)
    sexo: Optional[str] = Field(None, max_length=1)
    pueblo: Optional[str] = Field(None, max_length=80)
    comunidad_linguistica: Optional[str] = Field(None, max_length=80)
    edad_dias: Optional[int] = None
    edad_meses: Optional[int] = None
    edad_anios: Optional[int] = None
    departamento_residencia: Optional[str] = Field(None, max_length=100)
    municipio_residencia: Optional[str] = Field(None, max_length=100)
    comunidad: Optional[str] = Field(None, max_length=150)
    direccion: Optional[str] = None
    tipo_consulta: Optional[str] = Field(None, max_length=80)
    control: Optional[str] = Field(None, max_length=80)
    semana_gestacional: Optional[int] = None
    descripcion_diagnostico_control: Optional[str] = None
    codigo_cie_10: Optional[str] = Field(None, max_length=30)
    dx: Optional[str] = None
    tipologia: Optional[str] = Field(None, max_length=100)
    especialidad: Optional[str] = Field(None, max_length=100)


class Sigsa3Out(Sigsa3Base):
    id: int
    model_config = ConfigDict(from_attributes=True)
