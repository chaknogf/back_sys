from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import date, datetime


class Sigsa3Base(BaseModel):
    personal_salud: Optional[str] = Field(None, max_length=100)
    personal_salud_id: Optional[int] = None
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
    codigo_cie_10_id: Optional[int] = None
    dx: Optional[str] = None
    especialidad_id: Optional[int] = None
    paciente_id: Optional[int] = None
    medico_id: Optional[int] = None
    consulta_id: Optional[int] = None


class Sigsa3Create(Sigsa3Base):
    pass


class Sigsa3Update(BaseModel):
    paciente_id: Optional[int] = None
    personal_salud: Optional[str] = Field(None, max_length=100)
    personal_salud_id: Optional[int] = None
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
    codigo_cie_10_id: Optional[int] = None
    dx: Optional[str] = None
    especialidad_id: Optional[int] = None
    medico_id: Optional[int] = None
    consulta_id: Optional[int] = None


class Sigsa3Out(Sigsa3Base):
    id: int
    paciente_id: Optional[int] = None
    especialidad_nombre: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class Sigsa3RegistroOut(BaseModel):
    id: int
    paciente_id: int
    medico_id: Optional[int] = None
    personal_salud_id: Optional[int] = None
    consulta_id: Optional[int] = None
    fecha_consulta: date
    tipo_consulta_id: Optional[int] = None
    control: Optional[str] = None
    semana_gestacional: Optional[int] = None
    codigo_cie_10_id: Optional[int] = None
    especialidad_id: Optional[int] = None
    sigsa3_id: Optional[int] = None
    normalized_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ── Schemas para revisión de pendientes ──

class CandidatoHomonimo(BaseModel):
    pac_id: int
    nombre: str
    sexo: Optional[str] = None
    expediente: Optional[str] = None
    estado: Optional[str] = None


class PendienteDetalle(BaseModel):
    sigsa3_id: int
    nombre_sigsa: str
    tipo: str  # "homonimo" | "submatch_bajo_score" | "sexo_discrepante" | "typo_sin_corroborar" | "typo_probable_ambiguo"
    sexo_sigsa: Optional[str] = None
    expediente_sigsa: Optional[str] = None
    fecha_consulta: Optional[date] = None
    tipo_consulta: Optional[str] = None
    # Para submatch
    nombre_paciente_sugerido: Optional[str] = None
    pac_id_sugerido: Optional[int] = None
    score: Optional[float] = None
    zona: Optional[str] = None
    evolucion: Optional[dict] = None
    # Para homónimo
    pacientes: Optional[List[str]] = None
    candidatos: Optional[List[CandidatoHomonimo]] = None


class ResolverPendienteRequest(BaseModel):
    sigsa3_id: int = Field(..., description="ID del registro SIGSA-3 a resolver")
    paciente_id: int = Field(..., description="ID del paciente a asociar")


class ResolverPendienteResponse(BaseModel):
    sigsa3_id: int
    paciente_id: int
    nombre_paciente: str
    message: str


# ── Schemas para duplicados y merge ──

class PacienteDuplicado(BaseModel):
    pac_id: int
    nombre: str
    expediente: Optional[str] = None
    sexo: Optional[str] = None
    estado: Optional[str] = None
    sigsa3_count: int = 0


class ClusterDuplicado(BaseModel):
    nombre: str
    firma: List[str]
    total_pacientes: int
    total_sigsa3_pendientes: int
    con_sexo_diferente: bool
    con_expediente_diferente: bool
    candidato_principal: PacienteDuplicado
    duplicados: List[PacienteDuplicado]
    pueden_desambiguarse: bool


class MergeDuplicadosRequest(BaseModel):
    principal_id: int = Field(..., description="ID del paciente principal (sobrevive)")
    duplicado_ids: List[int] = Field(..., min_length=1, description="IDs de pacientes a fusionar en el principal")
    reasignar_sigsa3: bool = Field(True, description="Reasignar registros SIGSA-3 al principal")


class FusiacionDetalle(BaseModel):
    duplicado_id: int
    nombre: Optional[str] = None
    consultas_movidas: int = 0
    sigsa3_staging_movidos: int = 0
    sigsa3_registros_movidos: int = 0
    citas_movidas: int = 0
    defunciones_movidas: int = 0
    nacimientos_movidos: int = 0
    campos_completados: List[str] = []


class MergeDuplicadosResponse(BaseModel):
    principal_id: int
    nombre_principal: str
    fusiones: List[FusiacionDetalle]
    total_duplicados_fusionados: int
