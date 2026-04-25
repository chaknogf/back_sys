# app/schemas/ciclos_consultas.py
from typing import List, Literal, Optional, Dict, Any, Union
from datetime import date, time
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.schemas.consultas import ConsultaHistoriaResumidaOut

# ===================================================================
# Egreso clínico
# ===================================================================
class Egreso(BaseModel):
    """Datos del egreso médico de la consulta"""
    registro: Optional[str] = Field(None, description="Timestamp ISO del egreso")
    condicion: Optional[str] = Field(None, max_length=100, description="Condición al egreso: alta, fallecido, referido, etc.")
    referencia: Optional[str] = Field(None, max_length=200, description="Institución o servicio de referencia si aplica")
    diagnosticos: Optional[List[Dict[str, Any]]] = Field(None, description="Lista de diagnósticos al egreso")
    medico: Optional[str] = Field(None, max_length=100, description="Médico responsable del egreso")
    model_config = ConfigDict(from_attributes=True)


# ===================================================================
# Schema base (común)
# ===================================================================
class CicloConsultaBase(BaseModel): #para crear y actualizar
    consulta_id: int
    numero: int
    activo: bool
    registro: str
    usuario: str
    especialidad: Optional[str] = None
    servicio: Optional[str] = None
    contenido: Optional[str] = None
    datos_medicos: Optional[Dict[str, Any]] = None
    egreso: Optional[Egreso] = None
    model_config = ConfigDict(from_attributes=True)

class CicloConsulta (CicloConsultaBase): #para mostrar un ciclo consulta específico
    id: int
    
    model_config = ConfigDict(from_attributes=True)
    
class CicloOut(CicloConsultaBase): #para mostrar un ciclo consulta específico con la consulta resumida
    id: int
    consulta: ConsultaHistoriaResumidaOut
    
    model_config = ConfigDict(from_attributes=True)

    
class CicloOutList(CicloConsultaBase): #para mostrar ciclos consultas en una lista con la consulta resumida
    total: int
    consulta: ConsultaHistoriaResumidaOut   
    model_config = ConfigDict(from_attributes=True)

