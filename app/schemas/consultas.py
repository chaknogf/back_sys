# app/schemas/consultas.py
"""
Schemas para consultas médicas.
Totalmente compatibles con FastAPI + Pydantic v2 + OpenAPI.
"""

from typing import List, Literal, Optional, Dict, Any, Union
from datetime import date, time
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.paciente import PacienteOut


# ===================================================================
# Indicadores clínicos (banderas sí/no)
# ===================================================================
class Indicador(BaseModel):
    """Indicadores sociales y clínicos de la consulta"""
    estudiante_publico: Optional[bool] = None
    empleado_publico: Optional[bool] = None
    accidente_laboral: Optional[bool] = None
    discapacidad: Optional[bool] = None
    accidente_transito: Optional[bool] = None
    arma_fuego: Optional[bool] = None
    arma_blanca: Optional[bool] = None
    ambulancia: Optional[bool] = None
    embarazo: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)


# ===================================================================
# Estados del ciclo clínico
# ===================================================================
EstadoCiclo = Literal[
    "iniciado",       # Estado inicial legacy
    "pendiente",      # Estado inicial
    "admision",       # Paciente admitido
    "signos",         # Toma de signos vitales
    "consulta",       # En consulta con el médico
    "estudios",       # Realizando estudios/laboratorios
    "tratamiento",    # Recibiendo tratamiento
    "observacion",    # En observación
    "evolucion",      # Seguimiento/evolución
    "procedimiento",  # Realizando procedimiento
    "recuperacion",   # En recuperación
    "egreso",         # Alta médica
    "referido",       # Referido a otra institución
    "traslado",       # Trasladado a otro servicio
    "prestamo",       # Expediente prestado
    "archivo",        # Archivado
    "recepcion",      # En recepción
    "actualizado",    # Registro actualizado
    "reprogramado",   # Consulta reprogramada
    "descartado"      # Consulta descartada/cancelada
]


# ===================================================================
# Ciclo clínico completo (estructura flexible pero tipada)
# ===================================================================
class CicloClinico(BaseModel):
    """
    Representa UN registro individual del ciclo clínico.
    Se acumula en una lista, no se sobrescribe.
    """
    # Campos obligatorios de auditoría (siempre se registran)
    estado: EstadoCiclo = Field(
        ..., 
        description="Estado actual del ciclo clínico"
    )
    registro: str = Field(..., description="Timestamp ISO del registro")
    usuario: str = Field(..., description="Usuario que realizó la acción")
    
    # Campos clínicos opcionales (se llenan según el flujo)
    especialidad: Optional[str] = None
    servicio: Optional[str] = None
    detalle_clinicos: Optional[Dict[str, Any]] = None
    signos_vitales: Optional[Dict[str, Any]] = None
    antecedentes: Optional[Dict[str, Any]] = None
    ordenes: Optional[Dict[str, Any]] = None
    estudios: Optional[Dict[str, Any]] = None
    comentario: Optional[Union[str, Dict[str, Any]]] = None  # 👈 Acepta str O dict
    impresion_clinica: Optional[Dict[str, Any]] = None
    tratamiento: Optional[Dict[str, Any]] = None
    examen_fisico: Optional[Dict[str, Any]] = None
    nota_enfermeria: Optional[Dict[str, Any]] = None
    contraindicado: Optional[str] = None
    presa_quirurgica: Optional[Dict[str, Any]] = None
    egreso: Optional[Dict[str, Any]] = None

    @field_validator('estado', mode='before')
    @classmethod
    def normalizar_estado(cls, v):
        """Normaliza estados a minúsculas para compatibilidad con datos legacy"""
        if isinstance(v, str):
            return v.lower()
        return v
    
    @field_validator('comentario', mode='before')
    @classmethod
    def normalizar_comentario(cls, v):
        """Convierte dict vacío a None"""
        if isinstance(v, dict) and not v:
            return None
        return v

    model_config = ConfigDict(extra="allow", from_attributes=True)

class CicloUpdate(BaseModel):
    estado: EstadoCiclo = "actualizado"
    especialidad: Optional[str] = None
    servicio: Optional[str] = None
    detalle_clinicos: Optional[Dict[str, Any]] = None
    signos_vitales: Optional[Dict[str, Any]] = None
    antecedentes: Optional[Dict[str, Any]] = None
    ordenes: Optional[Dict[str, Any]] = None
    estudios: Optional[Dict[str, Any]] = None
    comentario: Optional[Union[str, Dict[str, Any]]] = None  
    impresion_clinica: Optional[Dict[str, Any]] = None
    tratamiento: Optional[Dict[str, Any]] = None
    examen_fisico: Optional[Dict[str, Any]] = None
    nota_enfermeria: Optional[Dict[str, Any]] = None
    contraindicado: Optional[str] = None
    presa_quirurgica: Optional[Dict[str, Any]] = None
    egreso: Optional[Dict[str, Any]] = None
    @field_validator('estado', mode='before')
    @classmethod
    def normalizar_estado(cls, v):
        """Normaliza estados a minúsculas para compatibilidad con datos legacy"""
        if isinstance(v, str):
            return v.lower()
        return v
    @field_validator('comentario', mode='before')
    @classmethod
    def normalizar_comentario(cls, v):
        """Convierte dict vacío a None"""
        if isinstance(v, dict) and not v:
            return None
        return v
    model_config = ConfigDict(extra="allow", from_attributes=True)

# ===================================================================
# Schema base (común)
# ===================================================================
class ConsultaBase(BaseModel):
    expediente: Optional[str] = Field(None, max_length=20)
    paciente_id: int = Field(..., gt=0)
    tipo_consulta: Optional[int] = Field(None, ge=1)
    especialidad: Optional[str] = Field(None, max_length=50)
    servicio: Optional[str] = Field(None, max_length=50)
    documento: Optional[str] = Field(None, max_length=20)
    fecha_consulta: Optional[date] = None
    hora_consulta: Optional[time] = None
    indicadores: Optional[Indicador] = None
    ciclo: Optional[List[CicloClinico]] = None  
    orden: Optional[int] = Field(None, ge=0)

    model_config = ConfigDict(from_attributes=True)


class ConsultaCreate(BaseModel):
    """
    Schema para crear una consulta completa manualmente.
    Usado en POST /consultas/ (endpoint completo, no el simplificado).
    """
    paciente_id: int = Field(..., gt=0, description="ID del paciente")
    tipo_consulta: int = Field(..., ge=1, description="Tipo de consulta")
    especialidad: str = Field(..., max_length=50)
    servicio: str = Field(..., max_length=50)
    documento: Optional[str] = Field(None, max_length=20, description="Se genera automáticamente si no se proporciona")
    fecha_consulta: date = Field(..., description="Fecha de la consulta")
    hora_consulta: time = Field(..., description="Hora de la consulta")
    indicadores: Optional[Indicador] = None
    ciclo: Optional[List[CicloClinico]] = None

    model_config = ConfigDict(from_attributes=True)


class ConsultaUpdate(BaseModel):
    """
    Para actualizar una consulta.
    El campo 'ciclo' aquí es UN SOLO objeto que se agregará al historial.
    """
    expediente: Optional[str] = None
    tipo_consulta: Optional[int] = None
    especialidad: Optional[str] = None
    servicio: Optional[str] = None
    documento: Optional[str] = None
    fecha_consulta: Optional[date] = None
    hora_consulta: Optional[time] = None
    indicadores: Optional[Indicador] = None
    ciclo: Optional[CicloUpdate] = None  
    orden: Optional[int] = None

    model_config = ConfigDict(extra="ignore")


class ConsultaOut(ConsultaBase):
    id: int = Field(..., description="ID único de la consulta")
    paciente: Optional[PacienteOut] = None
    ciclo: Optional[List[CicloClinico]] = None

    @field_validator('ciclo', mode='before')
    @classmethod
    def convertir_ciclo_a_lista(cls, v):
        """
        Convierte ciclo de dict a lista para compatibilidad
        con datos legacy.
        """
        if v is None:
            return None
        
        # Si es un dict vacío, retornar lista vacía
        if isinstance(v, dict) and not v:
            return []
        
        # Si es un dict con datos, convertir a lista con un elemento
        if isinstance(v, dict):
            return [v]
        
        # Si ya es una lista, retornarla tal cual
        if isinstance(v, list):
            return v
        
        # Caso inesperado
        return []

    model_config = ConfigDict(from_attributes=True)


class RegistroConsultaOut(BaseModel):
    id: int
    expediente: str
    paciente_id: int
    tipo_consulta: int
    especialidad: str
    servicio: str
    documento: str
    fecha_consulta: date
    hora_consulta: time
    indicadores: Indicador
    ciclo: List[CicloClinico]  
    orden: int

    model_config = ConfigDict(from_attributes=True)


# ===================================================================
# Para listas con conteo (paginación)
# ===================================================================
class ConsultaListResponse(BaseModel):
    total: int
    consultas: List[ConsultaOut]

    model_config = ConfigDict(from_attributes=True)

    
# ===================================================================
# Schema específico para registro de consultas
# ===================================================================
class RegistroConsultaCreate(BaseModel):
    """
    Schema para registro rápido de consulta.
    El frontend solo envía lo mínimo necesario.
    """
    paciente_id: int = Field(..., gt=0, description="ID del paciente")
    tipo_consulta: int = Field(..., ge=1, le=3, description="1=Primera vez, 2=Subsecuente, 3=Emergencia")
    especialidad: str = Field(..., max_length=50)
    servicio: str = Field(..., max_length=50)
    indicadores: Optional[Indicador] = None

    model_config = ConfigDict(from_attributes=True)