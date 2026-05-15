from pydantic import BaseModel, ConfigDict
from typing import Optional
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
    usuario_entrega: Optional[str] = None
    usuario_recibe: Optional[str] = None
    solicitante: str
    motivo: Optional[str] = None
    tipo_documento: Optional[str] = "EXPEDIENTE"
    activo: Optional[bool] = True
    ubicacion: Optional[str] = None
    nota: Optional[str] = None


# =========================
# CREATE
# =========================

class PrestamoCreate(PrestamoBase):
    pass


# =========================
# UPDATE
# =========================

class PrestamoUpdate(BaseModel):
    id_consulta: Optional[int] = None
    expediente: Optional[str] = None
    fecha_prestamo: Optional[datetime] = None
    fecha_limite: Optional[datetime] = None
    fecha_devolucion: Optional[datetime] = None
    usuario_entrega: Optional[str] = None
    usuario_recibe: Optional[str] = None
    solicitante: Optional[str] = None
    motivo: Optional[str] = None
    tipo_documento: Optional[str] = None
    activo: Optional[bool] = None
    ubicacion: Optional[str] = None
    nota: Optional[str] = None


# =========================
# LISTAR / RESPONSE
# =========================

class Prestamo(PrestamoBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)