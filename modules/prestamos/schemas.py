from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


class PrestamoBase(BaseModel):
    id_paciente: int
    id_consulta: Optional[int] = None
    expediente: Optional[str] = None
    fecha_prestamo: Optional[datetime] = None
    fecha_limite: Optional[datetime] = None
    fecha_devolucion: Optional[datetime] = None
    solicitante: str
    motivo: Optional[str] = None
    tipo_documento: Optional[str] = "EXPEDIENTE"
    activo: Optional[bool] = True
    ubicacion: Optional[str] = None
    nota: Optional[str] = None


class PrestamoCreate(PrestamoBase):
    pass


class PrestamoUpdate(BaseModel):
    id_consulta: Optional[int] = None
    expediente: Optional[str] = None
    fecha_prestamo: Optional[datetime] = None
    fecha_limite: Optional[datetime] = None
    fecha_devolucion: Optional[datetime] = None
    solicitante: Optional[str] = None
    motivo: Optional[str] = None
    tipo_documento: Optional[str] = None
    activo: Optional[bool] = None
    ubicacion: Optional[str] = None
    nota: Optional[str] = None


class Prestamo(PrestamoBase):
    id: int
    usuario_entrega: Optional[str] = None
    usuario_recibe: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
    
    
class PrestamoListResponse(BaseModel):
    total: int
    items: List[Prestamo]

    model_config = ConfigDict(from_attributes=True)
