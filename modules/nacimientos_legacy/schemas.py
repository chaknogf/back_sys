from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date, time, datetime


class NacimientoLegacyBase(BaseModel):
    fecha: Optional[date] = None
    cor: Optional[int] = None
    ao: Optional[int] = None
    doc: Optional[str] = None
    fecha_parto: Optional[date] = None
    madre: Optional[str] = None
    dpi: Optional[int] = None
    passport: Optional[str] = None
    libro: Optional[int] = None
    folio: Optional[int] = None
    partida: Optional[str] = None
    muni: Optional[int] = None
    edad: Optional[int] = None
    vecindad: Optional[int] = None
    sexo_rn: Optional[str] = None
    lb: Optional[int] = None
    onz: Optional[int] = None
    hora: Optional[time] = None
    medico: Optional[str] = None
    colegiado: Optional[int] = None
    dpi_medico: Optional[int] = None
    hijos: Optional[int] = None
    vivos: Optional[int] = None
    muertos: Optional[int] = None
    tipo_parto: Optional[int] = None
    clase_parto: Optional[int] = None
    certifica: Optional[str] = None
    create_by: Optional[str] = None
    depto: Optional[int] = None
    expediente: Optional[int] = None
    pais: Optional[str] = None
    nacionalidad: Optional[str] = None

class NacimientoLegacyResponse(NacimientoLegacyBase):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)
