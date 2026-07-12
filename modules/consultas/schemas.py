# modules/consultas/schemas.py
from typing import List, Literal, Optional, Dict, Any, Union
from datetime import date, time
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from modules.pacientes.schemas import PacienteConsultaBase, PacientesNombre


# ===================================================================
# Indicadores clínicos (banderas sí/no)
# ===================================================================
class Indicador(BaseModel):
    estudiante_publico: Optional[bool] = None
    empleado_publico: Optional[bool] = None
    personal_hospital: Optional[Union[str, bool]] = None
    accidente_laboral: Optional[bool] = None
    discapacidad: Optional[bool] = None
    accidente_transito: Optional[bool] = None
    arma_fuego: Optional[bool] = None 
    arma_blanca: Optional[bool] = None
    ambulancia: Optional[bool] = None
    embarazo: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("personal_hospital", mode="before")
    @classmethod
    def normalize_personal_hospital(cls, v):
        if v is True:
            return "S"
        if v is False:
            return "N"
        return v


# ===================================================================
# Estados del ciclo clínico
# ===================================================================
EstadoCiclo = Literal[
    "iniciado",
    "pendiente",
    "admision",
    "triage",
    "signos",
    "consulta",
    "estudios",
    "tratamiento",
    "observacion",
    "evolucion",
    "seguimiento",
    "procedimiento",
    "recuperacion",
    "egreso",
    "referido",
    "traslado",
    "prestamo",
    "archivo",
    "recepcion",
    "actualizado",
    "reprogramado",
    "descartado",
    "borrado"
]

# ===================================================================
# Egreso clínico
# ===================================================================
class Egreso(BaseModel):
    registro: Optional[str] = Field(None, description="Timestamp ISO del egreso")
    condicion: Optional[str] = Field(None, max_length=100)
    referencia: Optional[str] = Field(None, max_length=200)
    diagnosticos: Optional[str] = None
    medico: Optional[str] = Field(None, max_length=100)
    lactancia_materna: Optional[bool] = None
    model_config = ConfigDict(from_attributes=True)

# ===================================================================
# Ciclo clínico completo (estructura flexible pero tipada)
# ===================================================================
class CicloClinico(BaseModel):
    estado: EstadoCiclo
    registro: str 
    usuario: str 
    especialidad: Optional[str] = None
    servicio: Optional[str] = None
    comentario: Optional[str] = None

    @field_validator('estado', mode='before')
    @classmethod
    def normalizar_estado(cls, v):
        if isinstance(v, str):
            return v.lower()
        return v
    
    @field_validator('comentario', mode='before')
    @classmethod
    def normalizar_comentario(cls, v):
        if isinstance(v, dict) and not v:
            return None
        return v

    model_config = ConfigDict(
        extra="allow", 
        from_attributes=True,
        json_schema_extra={
            "exclude_none": True
        }
    )

class CicloUpdate(BaseModel):
    estado: EstadoCiclo = "actualizado"
    especialidad: Optional[str] = None
    servicio: Optional[str] = None

    @field_validator('estado', mode='before')
    @classmethod
    def normalizar_estado(cls, v):
        return v.lower() if isinstance(v, str) else v

    def model_dump_clean(self, **kwargs) -> dict:
        data = super().model_dump(exclude_none=True, **kwargs)
        return {k: v for k, v in data.items() if v != '' and v != {} and v != []}

    model_config = ConfigDict(
        extra="allow",
        from_attributes=True
    )
       
# ===================================================================
# Schema base (común)
# ===================================================================
class ConsultaBase(BaseModel):
    ultimo_estado: Optional[str] = None
    expediente: Optional[str] = Field(None, max_length=20)
    paciente_id: int = Field(..., gt=0)
    tipo_consulta: Optional[int] = Field(None, ge=1)
    especialidad: Optional[str] = Field(None, max_length=50)
    servicio: Optional[str] = Field(None, max_length=50)
    documento: Optional[str] = Field(None, max_length=20)
    fecha_consulta: Optional[date] = None
    hora_consulta: Optional[time] = None
    indicadores: Optional[Indicador] = None
    ciclo: Optional[List[CicloUpdate]] = None  
    orden: Optional[int] = Field(None, ge=0)
    activo: bool = True
    egreso: Optional[Dict[str, Any]] = None
   
    model_config = ConfigDict(from_attributes=True)


class ConsultaUpdate(BaseModel):
    ultimo_estado: Optional[str] = None
    expediente: Optional[str] = None
    paciente_id: Optional[int] = Field(None, gt=0)
    tipo_consulta: Optional[int] = None
    especialidad: Optional[str] = None
    servicio: Optional[str] = None
    documento: Optional[str] = None
    fecha_consulta: Optional[date] = None
    hora_consulta: Optional[time] = None
    indicadores: Optional[Indicador] = None
    ciclo: Optional[CicloUpdate] = None
    orden: Optional[int] = None
    activo: Optional[bool] = None
    egreso: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(extra="ignore")

    @field_validator("ciclo", mode="before")
    @classmethod
    def no_aceptar_listas(cls, v):
        if isinstance(v, list):
            raise ValueError("El campo 'ciclo' debe ser un objeto, no una lista")
        return v

class ConsultaOut(ConsultaBase):
    id: int 
    ultimo_estado: Optional[str] = None 
    paciente: Optional[PacienteConsultaBase] = None
     
    @field_validator('ciclo', mode='before')
    @classmethod
    def convertir_ciclo_a_lista(cls, v):
        if v is None:
            return None
        if isinstance(v, dict) and not v:
            return []
        if isinstance(v, dict):
            return [v]
        if isinstance(v, list):
            return v
        return []

    model_config = ConfigDict(from_attributes=True)
    
class ConsultasModel(BaseModel):
    id: int
    ultimo_estado: Optional[str] = None 
    expediente: Optional[str] = None
    paciente_id: int
    tipo_consulta: Optional[int] = None
    especialidad: Optional[str] = None
    servicio: Optional[str] = None
    documento: Optional[str] = None
    fecha_consulta: Optional[date] = None
    hora_consulta: Optional[time] = None
    indicadores: Optional[Indicador] = None
    orden: Optional[int] = None
    activo: bool = True
    egreso: Optional[Dict[str, Any]] = None
    paciente: Optional[PacientesNombre] = None
    dias_acumulados: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)

class RegistroConsultaOut(BaseModel):
    id: int
    expediente: Optional[str] = None
    paciente_id: int
    tipo_consulta: int
    especialidad: str
    servicio: str
    documento: Optional[str] = None
    fecha_consulta: date
    hora_consulta: time
    indicadores: Indicador
    ciclo: List[CicloClinico]
    orden: int
    activo: Optional[bool] = None
    egreso: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)

# ===================================================================
# Para listas con conteo (paginación)
# ===================================================================
class ConsultaListResponse(BaseModel):
    total: int
    consultas: List[ConsultasModel]

    model_config = ConfigDict(from_attributes=True)


# ===================================================================
# Schema específico para registro de consultas
# ===================================================================
class RegistroConsultaCreate(BaseModel):
    paciente_id: int = Field(..., gt=0, description="ID del paciente")
    tipo_consulta: int = Field(..., ge=1, le=3, description="1=Primera vez, 2=Subsecuente, 3=Emergencia")
    especialidad: str = Field(..., max_length=50)
    servicio: str = Field(..., max_length=50)
    indicadores: Optional[Indicador] = None

    model_config = ConfigDict(from_attributes=True)
    
class ConsultaBaseOut(BaseModel):
    expediente: Optional[str] = Field(None, max_length=20)
    tipo_consulta: Optional[int] = Field(None, ge=1)
    especialidad: Optional[str] = Field(None, max_length=50)
    servicio: Optional[str] = Field(None, max_length=50)
    documento: Optional[str] = Field(None, max_length=20)
    fecha_consulta: Optional[date] = None
    hora_consulta: Optional[time] = None
    indicadores: Optional[Indicador] = None
    activo: Optional[bool] = None
    egreso: Optional[Egreso] = None
    
    model_config = ConfigDict(from_attributes=True)

class ConsultaHistoriaResumidaOut(ConsultaBaseOut):
    id: int
    paciente: Optional[PacientesNombre] = None
    tipo_consulta: Optional[int] = None
    especialidad: Optional[str] = None
    fecha_consulta: Optional[date] = None
    hora_consulta: Optional[time] = None
    ultimo_estado: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
