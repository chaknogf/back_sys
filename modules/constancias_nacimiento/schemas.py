from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Dict, Any
from datetime import date, datetime
from modules.pacientes.schemas import PacienteNacimientoConstancia
from modules.medicos.schemas import MedicoOut


class ConstanciaNacimientoBase(BaseModel):
    paciente_id: int
    madre_id: Optional[int] = None
    medico_id: Optional[int] = None
    registrador_id: Optional[int] = None

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


class ConstanciaNacimientoCreate(ConstanciaNacimientoBase):
    pass


class ConstanciaNacimientoUpdate(BaseModel):
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

    paciente: Optional[PacienteNacimientoConstancia] = None
    madre: Optional[PacienteNacimientoConstancia] = None 
    medico: Optional[MedicoOut] = None

    class Config:
        from_attributes = True

class ConstanciaNacimientoListResponse(BaseModel):
    total: int
    constancias: list[ConstanciaNacimientoResponse]
    model_config = ConfigDict(from_attributes=True)
    

class ConstanciaNacimientoHistorialResponse(BaseModel):
    id: int
    constancia_id: int
    datos_anteriores: Dict[str, Any]
    usuario_id: int
    fecha: datetime

    class Config:
        from_attributes = True
