# app/schema/constancia_nacimiento.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import date, datetime
from app.schemas.paciente import PacienteNacimientoConstancia
from app.schemas.medicos import MedicoBase


class ConstanciaNacimientoBase(BaseModel):
    # ── Vínculos ──────────────────────────────────────────────────────────
    paciente_id: int                                    # neonato — siempre requerido
    madre_id: Optional[int] = None                     # FK a pacientes (madre)
    medico_id: Optional[int] = None
    registrador_id: Optional[int] = None

    # ── Identificación del documento ──────────────────────────────────────
    documento: Optional[str] = Field(None, max_length=20)   # nullable en DB
    fecha_registro: Optional[date] = None                    # default CURRENT_DATE en DB

    # ── Datos de la madre (texto, por si no está en DB) ───────────────────
    nombre_madre: Optional[str] = Field(None, max_length=200)
    vecindad_madre: Optional[str] = None

    # ── Datos clínicos opcionales ─────────────────────────────────────────
    menor_edad: Optional[Dict[str, Any]] = None
    hijos: Optional[int] = None
    vivos: Optional[int] = None
    muertos: Optional[int] = None
    observaciones: Optional[str] = None
    metadatos: Optional[Dict[str, Any]] = None


class ConstanciaNacimientoCreate(ConstanciaNacimientoBase):
    """
    Usado al crear manualmente una constancia.
    paciente_id es el único campo obligatorio;
    el resto se completa después con PUT.
    """
    pass


class ConstanciaNacimientoUpdate(BaseModel):
    """
    Todos los campos editables son opcionales.
    
    """
    medico_id: Optional[int] = None
    documento: Optional[str] = Field(None, max_length=20)
    fecha_registro: Optional[date] = None

    nombre_madre: Optional[str] = Field(None, max_length=200)
    vecindad_madre: Optional[str] = None

    menor_edad: Optional[Dict[str, Any]] = None
    hijos: Optional[int] = None
    vivos: Optional[int] = None
    muertos: Optional[int] = None
    observaciones: Optional[str] = None
    metadatos: Optional[Dict[str, Any]] = None

    

class ConstanciaNacimientoResponse(ConstanciaNacimientoBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Relaciones serializadas
    paciente: Optional[PacienteNacimientoConstancia] = None
    # Si en el futuro serializas la madre también, agrega:
    madre: Optional[PacienteNacimientoConstancia] = None 
    medico: Optional[MedicoBase] = None

    class Config:
        from_attributes = True


class ConstanciaNacimientoHistorialResponse(BaseModel):
    id: int
    constancia_id: int
    datos_anteriores: Dict[str, Any]
    usuario_id: int
    fecha: datetime

    class Config:
        from_attributes = True