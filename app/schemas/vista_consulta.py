from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict, Field
from datetime import date, time, datetime

class VistaConsultas(BaseModel):
    id_paciente: int
    identificadores: Optional[Dict[str, Any]]
    expediente: Optional[str]
    cui: Optional[int]
    nombre: Optional[Dict[str, Any]]
    primer_nombre: Optional[str]
    segundo_nombre: Optional[str]
    otro_nombre: Optional[str]
    primer_apellido: Optional[str]
    segundo_apellido: Optional[str]
    apellido_casada: Optional[str]
    sexo: Optional[str]
    fecha_nacimiento: Optional[date]
    estado: Optional[str]
    id_consulta: Optional[int]
    tipo_consulta: Optional[int]
    especialidad: Optional[str]
    servicio: Optional[str]
    documento: Optional[str]
    fecha_consulta: Optional[date]
    hora_consulta: Optional[time]
    ciclo: Optional[Dict[str, Any]]

    model_config = ConfigDict(from_attributes=True)