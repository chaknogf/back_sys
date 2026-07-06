from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import date, datetime


class CensoCamasCreate(BaseModel):
    fecha: date
    servicio_id: int
    sexo: int = Field(..., ge=0, le=1, description="0=M, 1=F")
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


class CensoCamasUpdate(BaseModel):
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


class CensoCamasOut(BaseModel):
    id: int
    fecha: date
    servicio_id: int
    sexo: int
    ocupados: int
    camas_ocupadas: int = Field(description="Calculado: (emergencia + huespedes + ingresos + otro_ingresos + ocupados) - egresos_totales")
    egresos_totales: int = Field(description="Calculado: egresos + fallecidos + referido + traslado + contraindicados")
    egresos: int
    fallecidos: int
    referido: int
    traslado: int
    contraindicados: int
    otro_ingresos: int
    ingresos: int
    huespedes: int
    emergencia: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ServicioResumen(BaseModel):
    servicio_id: int
    servicio_nombre: str
    camas_censables: int
    masculino: Optional[CensoCamasOut] = None
    femenino: Optional[CensoCamasOut] = None

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
