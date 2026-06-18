from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Dict, Any
from datetime import date, time, datetime

from modules.pacientes.schemas import Nombre, Neonatales


class NacimientoBase(BaseModel):
    paciente_id: Optional[int] = None
    madre_id: Optional[int] = None

    expediente: Optional[str] = Field(None, max_length=20)
    nombre_completo: Optional[str] = Field(None, max_length=300)
    sexo: Optional[str] = Field(None, max_length=1)
    fecha_nacimiento: Optional[date] = None

    peso_nacimiento: Optional[str] = None
    edad_gestacional: Optional[str] = None
    tipo_parto: Optional[str] = None
    clase_parto: Optional[str] = None
    gemelo: Optional[str] = None
    hora_nacimiento: Optional[time] = None
    extrahospitalario: Optional[bool] = False

    registrador_id: Optional[int] = None
    datos_extra: Optional[Dict[str, Any]] = None


class NacimientoCreate(NacimientoBase):
    pass


class NacimientoUpdate(BaseModel):
    peso_nacimiento: Optional[str] = None
    edad_gestacional: Optional[str] = None
    tipo_parto: Optional[str] = None
    clase_parto: Optional[str] = None
    gemelo: Optional[str] = None
    hora_nacimiento: Optional[time] = None
    extrahospitalario: Optional[bool] = None


class NacimientoOut(NacimientoBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NacimientoListResponse(BaseModel):
    total: int
    nacimientos: list[NacimientoOut]

    model_config = ConfigDict(from_attributes=True)


class LegacyReferenceOut(BaseModel):
    legacy_id: int
    legacy_doc: Optional[str] = None
    legacy_madre: Optional[str] = None
    legacy_fecha_parto: Optional[date] = None
    legacy_sexo_rn: Optional[str] = None
    legacy_expediente: Optional[int] = None
    legacy_lb: Optional[int] = None
    legacy_onz: Optional[int] = None
    legacy_hora: Optional[time] = None
    legacy_tipo_parto: Optional[int] = None
    legacy_clase_parto: Optional[int] = None
    legacy_medico: Optional[str] = None

    match_tipo: str = "sin_match"
    madre_id: Optional[int] = None
    madre_expediente: Optional[str] = None
    madre_nombre: Optional[str] = None

    paciente_id: Optional[int] = None
    paciente_expediente: Optional[str] = None
    paciente_nombre: Optional[str] = None
    paciente_sexo: Optional[str] = None
    paciente_fecha_nac: Optional[date] = None

    nacimiento_id: Optional[int] = None


class LegacyReferenceResponse(BaseModel):
    total_legacy: int
    coincidencias: int
    sin_coincidencia: int
    con_nacimiento: int
    sin_nacimiento: int
    referencias: list[LegacyReferenceOut]

    model_config = ConfigDict(from_attributes=True)
