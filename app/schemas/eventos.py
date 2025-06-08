from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class datosExtra(BaseModel):
    clave: str
    valor: str
    
class responsable(BaseModel):
    nombre: str
    registro: str
    nota: Optional[str]
    
class EventoConsultaBase(BaseModel):
    consulta_id: int
    tipo_evento: int
    datos: Optional[datosExtra]
    responsable: Optional[responsable]
    estado: Optional[str] = "A"

class EventoConsultaCreate(EventoConsultaBase):
    pass

class EventoConsultaOut(EventoConsultaBase):
    id: int
    creado_en: datetime
    actualizado_en: datetime

    model_config = ConfigDict(from_attributes=True)