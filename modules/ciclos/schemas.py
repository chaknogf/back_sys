# modules/ciclos/schemas.py
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
    consulta_id: int
    numero: int = 0
    activo: bool = True
    registro: Optional[datetime] = None
    usuario: str = ""
    especialidad: Optional[str] = None
    servicio: Optional[str] = None
    contenido: Optional[str] = None
    datos_medicos: Optional[Dict[str, Any]] = None
    model_config = ConfigDict(from_attributes=True)

class CicloConsulta (CicloConsultaBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)
    
class CicloOut(CicloConsultaBase):
    id: int
    consulta: ConsultaHistoriaResumidaOut
    
    model_config = ConfigDict(from_attributes=True)

    
class CicloOutList(CicloConsultaBase):
    total: int
    consulta: ConsultaHistoriaResumidaOut   
    model_config = ConfigDict(from_attributes=True)
