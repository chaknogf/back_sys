from pydantic import BaseModel, ConfigDict, field_serializer, field_validator
from typing import Optional, Union
from datetime import date, time, datetime


class NacimientoBase(BaseModel):
    paciente_id: Optional[int] = None
    madre_id: Optional[int] = None


class NacimientoCreate(NacimientoBase):
    mortinato: Optional[bool] = None


class NacimientoUpdate(BaseModel):
    madre_id: Optional[int] = None
    mortinato: Optional[bool] = None


class NeonatalesInfo(BaseModel):
    peso_nacimiento: Optional[str] = None
    edad_gestacional: Optional[str] = None
    tipo_parto: Optional[str] = None
    clase_parto: Optional[str] = None
    gemelo: Optional[str] = None
    hora_nacimiento: Optional[time] = None
    extrahospitalario: Optional[bool] = False

    @field_serializer('hora_nacimiento')
    def serialize_hora(self, hora: Optional[time], _info):
        if hora is None:
            return None
        return hora.strftime('%H:%M:%S')


class PacienteResumen(BaseModel):
    id: int
    expediente: Optional[str] = None
    cui: Optional[Union[str, int]] = None
    nombre_completo: Optional[str] = None
    nombre: Optional[dict] = None
    sexo: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    estado: Optional[str] = None

    @field_validator("cui", mode="before")
    @classmethod
    def coerce_cui(cls, v):
        if isinstance(v, int):
            return str(v)
        return v


class NacimientoOut(NacimientoBase):
    id: int
    registrador_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    mortinato: bool = False
    peso_gramos: Optional[float] = None
    clasificacion_nacimiento: Optional[str] = None
    trabajo_parto: Optional[str] = None
    id_legacy: Optional[int] = None
    neonatales: Optional[NeonatalesInfo] = None
    paciente: Optional[PacienteResumen] = None
    nombre_madre: Optional[str] = None

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
