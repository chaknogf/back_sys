from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date, time


class ConsultaBaseOut(BaseModel):
    expediente: Optional[str] = None
    tipo_consulta: Optional[int] = None
    especialidad: Optional[str] = None
    servicio: Optional[str] = None
    documento: Optional[str] = None
    fecha_consulta: Optional[date] = None
    hora_consulta: Optional[time] = None

    model_config = ConfigDict(from_attributes=True)