from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict, Field
from datetime import date, time, datetime


class Ciclo(BaseModel):
    clave: str
    valor: str

class Indicador(BaseModel):
    clave: str
    valor: str
    
class Signos_vitales(BaseModel):
    clave: str
    valor: str
    
class Ansigmas(BaseModel):
    clave: str
    valor: str
    
class Antecedentes(BaseModel):
    clave: str
    valor: str
    
class Ordenes(BaseModel):
    clave: str
    valor: str
class Estudios(BaseModel):
    clave: str
    valor: str
    
class Detalle_clinico(BaseModel):
    clave: str
    valor: str
    
class Sistema(BaseModel):
    usuario: str
    accion: str
    fecha: str

class ConsultaBase(BaseModel):
    paciente_id: int
    tipo_consulta: Optional[int]
    especialidad: Optional[int]
    servicio: Optional[int]
    documento: Optional[str]
    fecha_consulta: Optional[date]
    hora_consulta: Optional[time]
    ciclo: Optional[Dict[str, Ciclo]] = Field(default=None)
    indicadores: Optional[Dict[str, Indicador]] = Field(default=None)
    detalle_clinico: Optional[Dict[str, Detalle_clinico]] = Field(default=None)
    sistema: Optional[Dict[str,Sistema]] = Field(default=None)
    signos_vitales: Optional[Dict[str, Signos_vitales]] = Field(default=None)
    ansigmas: Optional[Dict[str, Ansigmas]] = Field(default=None)
    antecedentes: Optional[Dict[str, Antecedentes]] = Field(default=None)
    ordenes: Optional[Dict[str, Ordenes]] = Field(default=None)
    estudios: Optional[Dict[str, Estudios]] = Field(default=None)
    
class ConsultaUpdate(BaseModel):
    id: Optional[int] = None
    paciente_id: int
    tipo_consulta: Optional[int]
    especialidad: Optional[int]
    servicio: Optional[int]
    documento: Optional[str]
    fecha_consulta: Optional[date]
    hora_consulta: Optional[time]
    ciclo: Optional[Dict[str, Ciclo]] = Field(default=None)
    indicadores: Optional[Dict[str, Indicador]] = Field(default=None)
    detalle_clinico: Optional[Dict[str, Detalle_clinico]] = Field(default=None)
    sistema: Optional[Dict[str,Sistema]] = Field(default=None)
    signos_vitales: Optional[Dict[str, Signos_vitales]] = Field(default=None)
    ansigmas: Optional[Dict[str, Ansigmas]] = Field(default=None)
    antecedentes: Optional[Dict[str, Antecedentes]] = Field(default=None)
    ordenes: Optional[Dict[str, Ordenes]] = Field(default=None)
    estudios: Optional[Dict[str, Estudios]] = Field(default=None)

class ConsultaCreate(ConsultaBase):
    pass

class ConsultaOut(ConsultaBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)