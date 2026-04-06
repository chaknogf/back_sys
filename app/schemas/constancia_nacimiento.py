from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import date, datetime
from app.schemas.paciente import PacienteNacimientoConstancia


class ConstanciaNacimientoBase(BaseModel):
    documento: str = Field(..., max_length=20)
    paciente_id: int
    medico_id: int
    registrador_id: int

    nombre_madre: str = Field(..., max_length=200)
    vecindad_madre: Optional[str] = None

    fecha_registro: Optional[date] = None

    menor_edad: Optional[Dict[str, Any]] = None
    hijos: Optional[int] = None
    vivos: Optional[int] = None
    muertos: Optional[int] = None 

    observaciones: Optional[str] = None
    metadatos: Optional[Dict[str, Any]] = None
    paciente: Optional[PacienteNacimientoConstancia] = None


class ConstanciaNacimientoCreate(ConstanciaNacimientoBase):
    pass


class ConstanciaNacimientoUpdate(BaseModel):
    nombre_madre: Optional[str] = None
    vecindad_madre: Optional[str] = None
    menor_edad: Optional[Dict[str, Any]] = None
    hijos: Optional[int] = None
    vivos: Optional[int] = None
    muertos: Optional[int] = None
    observaciones: Optional[str] = None
    metadatos: Optional[Dict[str, Any]] = None
    motivo: str  # obligatorio para historial
    paciente: Optional[PacienteNacimientoConstancia] = None


class ConstanciaNacimientoResponse(ConstanciaNacimientoBase):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    paciente: Optional[PacienteNacimientoConstancia] = None

    class Config:
        from_attributes = True
        
class ConstanciaNacimientoHistorialResponse(BaseModel):
    id: int
    constancia_id: int
    datos_anteriores: Dict[str, Any]
    usuario_id: int
    motivo: str
    fecha: datetime

    class Config:
        from_attributes = True