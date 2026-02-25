from pydantic import BaseModel
from typing import Optional
from datetime import date, time, datetime

class NacimientoLegacyBase(BaseModel):
    fecha: Optional[date]
    cor: Optional[int]
    ao: Optional[int]
    doc: Optional[str]
    fecha_parto: Optional[date]
    madre: Optional[str]
    dpi: Optional[int]
    passport: Optional[str]
    libro: Optional[int]
    folio: Optional[int]
    partida: Optional[str]
    muni: Optional[int]
    edad: Optional[int]
    vecindad: Optional[int]
    sexo_rn: Optional[str]
    lb: Optional[int]
    onz: Optional[int]
    hora: Optional[time]
    medico: Optional[str]
    colegiado: Optional[int]
    dpi_medico: Optional[int]
    hijos: Optional[int]
    vivos: Optional[int]
    muertos: Optional[int]
    tipo_parto: Optional[int]
    clase_parto: Optional[int]
    certifica: Optional[str]
    create_by: Optional[str]
    depto: Optional[int]
    expediente: Optional[int]
    pais: Optional[str]
    nacionalidad: Optional[str]

class NacimientoLegacyResponse(NacimientoLegacyBase):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True