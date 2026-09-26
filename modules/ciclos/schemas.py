# modules/ciclos/schemas.py
"""Esquemas de ciclos clínicos y de la historia agrupada por consulta."""

from typing import List, Literal, Optional, Dict, Any, Union
from datetime import date, time, datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from modules.consultas.schemas import ConsultaHistoriaResumidaOut

# ===================================================================
# Egreso clínico
# ===================================================================
class Egreso(BaseModel):
    registro: Optional[str] = Field(None, description="Timestamp ISO del egreso")
    condicion: Optional[str] = Field(None, max_length=100, description="Condición al egreso: alta, fallecido, referido, etc.")
    referencia: Optional[str] = Field(None, max_length=200, description="Institución o servicio de referencia si aplica")
    diagnosticos: Optional[List[Dict[str, Any]]] = Field(None, description="Lista de diagnósticos al egreso")
    medico: Optional[str] = Field(None, max_length=100, description="Médico responsable del egreso")
    model_config = ConfigDict(from_attributes=True)


# ===================================================================
# Schema base (común)
# ===================================================================
class CicloConsultaBase(BaseModel):
    """Datos de escritura de un ciclo; el servidor determina usuario y número."""
    consulta_id: int
    numero: int = 0
    activo: bool = True
    registro: Optional[datetime] = None
    usuario: str = ""
    especialidad: Optional[str] = None
    especialidad_id: Optional[int] = None
    servicio: Optional[str] = None
    contenido: Optional[str] = None
    datos_medicos: Optional[Dict[str, Any]] = None
    model_config = ConfigDict(from_attributes=True)

class CicloConsulta (CicloConsultaBase):
    """Representación persistida que incorpora el identificador del ciclo."""
    id: int
    
    model_config = ConfigDict(from_attributes=True)
    
class CicloOut(CicloConsultaBase):
    id: int
    consulta: ConsultaHistoriaResumidaOut
    usuario_nombre: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

    
class CicloOutList(CicloConsultaBase):
    total: int
    consulta: ConsultaHistoriaResumidaOut   
    model_config = ConfigDict(from_attributes=True)


# ===================================================================
# Historia clínica agrupada por consulta
# ===================================================================
class CicloResumen(BaseModel):
    """Resumen ligero de un ciclo para la vista de historia clínica."""
    id: int
    numero: int
    registro: Optional[datetime] = None
    usuario: str = ""
    usuario_nombre: Optional[str] = None
    especialidad: Optional[str] = None
    servicio: Optional[str] = None
    resumen: Optional[str] = None
    signos_vitales: Optional[Dict[str, Any]] = None
    impresion_clinica: Optional[str] = None
    egreso: Optional[Dict[str, Any]] = None
    odontologia: Optional[Dict[str, Any]] = None
    model_config = ConfigDict(from_attributes=True)


class ConsultaHistoria(BaseModel):
    """Una consulta con todos sus ciclos agrupados."""
    consulta: ConsultaHistoriaResumidaOut
    ciclos: List[CicloResumen]
    total_ciclos: int


class HistoriaClinicaResponse(BaseModel):
    """Historia clínica completa de un paciente, agrupada por consulta."""
    paciente_id: int
    paciente_nombre: Optional[str] = None
    paciente_expediente: Optional[str] = None
    consultas: List[ConsultaHistoria]
    total_consultas: int
    total_ciclos: int
