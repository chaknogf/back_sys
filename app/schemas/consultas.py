from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import date, time, datetime


class ciclo(BaseModel):
    clave: str
    valor: str

class indicador(BaseModel):
    clave: str
    valor: str
    
class signos_vitales(BaseModel):
    clave: str
    valor: str
    
class ansigmas(BaseModel):
    clave: str
    valor: str
    
class antecedentes(BaseModel):
    clave: str
    valor: str
    
class ordenes(BaseModel):
    clave: str
    valor: str
class estudios(BaseModel):
    clave: str
    valor: str
    
class detalle_clinico(BaseModel):
    clave: str
    valor: str
    
class sistema(BaseModel):
    usuario: str
    accion: str
    fecha: datetime

class ConsultaBase(BaseModel):
    paciente_id: int
    tipo_consulta: Optional[int]
    especialidad: Optional[int]
    servicio: Optional[int]
    documento: Optional[str]
    fecha_consulta: Optional[date]
    hora_consulta: Optional[time]
    ciclo: Optional[ciclo]
    indicadores: Optional[indicador]
    detalle_clinico: Optional[detalle_clinico]
    sistema: Optional[sistema]
    signos_vitales: Optional[signos_vitales]
    ansigmas: Optional[ansigmas]
    antecedentes: Optional[antecedentes]
    ordenes: Optional[ordenes]
    estudios: Optional[estudios]

class ConsultaCreate(ConsultaBase):
    pass

class ConsultaOut(ConsultaBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)