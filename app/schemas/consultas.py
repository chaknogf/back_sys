from typing import Optional, Dict, Any, List
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
    fecha: str

class ConsultaBase(BaseModel):
    id: Optional[int] = None
    paciente_id: int
    tipo_consulta: Optional[int]
    especialidad: Optional[int]
    servicio: Optional[int]
    documento: Optional[str]
    fecha_consulta: Optional[date]
    hora_consulta: Optional[time]
    ciclo: Optional[List[ciclo]]
    indicadores: Optional[List[indicador]]
    detalle_clinico: Optional[List[detalle_clinico]]
    sistema: Optional[List[sistema]]
    signos_vitales: Optional[List[signos_vitales]]
    ansigmas: Optional[List[ansigmas]]
    antecedentes: Optional[List[antecedentes]]
    ordenes: Optional[List[ordenes]]
    estudios: Optional[List[estudios]]

class ConsultaCreate(ConsultaBase):
    pass

class ConsultaOut(ConsultaBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)