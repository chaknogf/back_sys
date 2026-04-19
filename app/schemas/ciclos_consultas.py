# app/schemas/ciclos_consultas.py
from typing import List, Literal, Optional, Dict, Any, Union
from datetime import date, time
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.schemas.consultas import ConsultaHistoriaResumidaOut

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

