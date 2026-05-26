# app/schemas/prestamos.py

from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


# =========================
# BASE
# =========================

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
    # usuario_entrega y usuario_recibe se asignan en el backend,
    # no se exponen en Create ni Update


# =========================
# CREATE — el frontend NO envía usuarios
# =========================

class PrestamoCreate(PrestamoBase):
    pass


# =========================
# UPDATE — el frontend NO envía usuario_recibe
# =========================

class PrestamoUpdate(BaseModel):
    id_consulta: Optional[int] = None
    expediente: Optional[str] = None
    fecha_prestamo: Optional[datetime] = None
    fecha_limite: Optional[datetime] = None
    fecha_devolucion: Optional[datetime] = None   # al enviarla → asigna usuario_recibe
    solicitante: Optional[str] = None
    motivo: Optional[str] = None
    tipo_documento: Optional[str] = None
    activo: Optional[bool] = None
    ubicacion: Optional[str] = None
    nota: Optional[str] = None


# =========================
# RESPONSE — sí devuelve ambos usuarios (solo lectura)
# =========================

class Prestamo(PrestamoBase):
    id: int
    usuario_entrega: Optional[str] = None   # asignado por el backend al crear
    usuario_recibe: Optional[str] = None    # asignado por el backend al devolver
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
    
    
class PrestamoListResponse(BaseModel):
    total: int
    items: List[Prestamo]

    model_config = ConfigDict(from_attributes=True)