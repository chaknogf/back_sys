from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import date, datetime


class CensoCamasSexCreate(BaseModel):
    ocupados: int = Field(0, ge=0)
    egresos: int = Field(0, ge=0)
    fallecidos: int = Field(0, ge=0)
    referido: int = Field(0, ge=0)
    traslado: int = Field(0, ge=0)
    contraindicados: int = Field(0, ge=0)
    otro_ingresos: int = Field(0, ge=0)
    ingresos: int = Field(0, ge=0)
    huespedes: int = Field(0, ge=0)
    emergencia: int = Field(0, ge=0)


class CensoCamasSexUpdate(BaseModel):
    ocupados: Optional[int] = Field(None, ge=0)
    egresos: Optional[int] = Field(None, ge=0)
    fallecidos: Optional[int] = Field(None, ge=0)
    referido: Optional[int] = Field(None, ge=0)
    traslado: Optional[int] = Field(None, ge=0)
    contraindicados: Optional[int] = Field(None, ge=0)
    otro_ingresos: Optional[int] = Field(None, ge=0)
    ingresos: Optional[int] = Field(None, ge=0)
    huespedes: Optional[int] = Field(None, ge=0)
    emergencia: Optional[int] = Field(None, ge=0)


class CensoCamasCreate(BaseModel):
    fecha: date
    servicio_id: int
    masculino: CensoCamasSexCreate
    femenino: CensoCamasSexCreate


class CensoCamasUpdate(BaseModel):
    masculino: Optional[CensoCamasSexUpdate] = None
    femenino: Optional[CensoCamasSexUpdate] = None


class CensoCamasSexOut(CensoCamasSexCreate):
    camas_ocupadas: int = Field(description="Calculado a partir de ingresos y egresos")
    egresos_totales: int = Field(description="Suma de todos los movimientos de egreso")


class CensoCamasTotales(BaseModel):
    ocupados: int
    egresos: int
    fallecidos: int
    referido: int
    traslado: int
    contraindicados: int
    otro_ingresos: int
    ingresos: int
    huespedes: int
    emergencia: int
    camas_ocupadas: int
    egresos_totales: int


class CensoCamasOut(CensoCamasTotales):
    id: int
    fecha: date
    servicio_id: int
    masculino: CensoCamasSexOut
    femenino: CensoCamasSexOut
    totales: CensoCamasTotales
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ServicioResumen(BaseModel):
    servicio_id: int
    servicio_nombre: str
    camas_censables: int
    masculino: Optional[CensoCamasSexOut] = None
    femenino: Optional[CensoCamasSexOut] = None

    model_config = ConfigDict(from_attributes=True)


class CensoDiarioResumen(BaseModel):
    fecha: date
    servicios: list[ServicioResumen]
    total_ocupados: int
    promedio: float

    model_config = ConfigDict(from_attributes=True)


class CensoCamasListResponse(BaseModel):
    total: int
    registros: list[CensoCamasOut]

    model_config = ConfigDict(from_attributes=True)


class HospitalizacionEspecialidadItem(BaseModel):
    especialidad: str
    masculinos: int
    femeninos: int
    total: int
    dias_promedio_estancia: float = Field(default=0.0, description="Promedio de días de estancia de pacientes activos")
    servicio_encamamiento: Optional[str] = Field(None, description="Servicio de encamamiento asociado (match por nombre)")


class HospitalizacionEspecialidadResponse(BaseModel):
    desde: date
    hasta: date
    total_hospitalizados: int
    especialidades: list[HospitalizacionEspecialidadItem]

    model_config = ConfigDict(from_attributes=True)


class CopiarDiaRequest(BaseModel):
    origen: date = Field(..., description="Fecha origen de la que se copian los registros")
    destino: date = Field(..., description="Fecha destino a la que se copian")
    servicio_id: Optional[int] = Field(None, description="Filtrar solo este servicio; omitir para todos")


class CopiarDiaResponse(BaseModel):
    origen: date
    destino: date
    copiados: int
    actualizados: int
    sin_datos: int

    model_config = ConfigDict(from_attributes=True)


class EstadisticaServicio(BaseModel):
    servicio_id: int
    servicio_nombre: str
    camas_censables: int
    dias_en_rango: int
    dco: int = Field(description="Días Cama Ocupada: suma de camas_ocupadas en el rango")
    egresos_totales: int = Field(description="Total de egresos en el rango")
    porcentaje_ocupacion: float = Field(description="camas_ocupadas / (camas_censables * días) * 100")
    dcd: int = Field(description="Días Cama Desocupado: (camas_censables * días) - camas_ocupadas, min 0")
    dias_estancia: float = Field(description="camas_ocupadas / egresos_totales")
    rotacion: float = Field(description="egresos_totales / dcd, 1 decimal")


class EstadisticaGlobal(BaseModel):
    camas_censables_total: int
    dias_en_rango: int
    dco: int
    egresos_totales: int
    porcentaje_ocupacion: float
    dcd: int
    dias_estancia: float
    rotacion: float


class CensoEstadisticasResponse(BaseModel):
    desde: date
    hasta: date
    servicios: list[EstadisticaServicio]
    global_: EstadisticaGlobal = Field(alias="global")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
