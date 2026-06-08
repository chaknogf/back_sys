from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Any, Literal
from datetime import date, datetime


class SerieItem(BaseModel):
    label: str = Field(..., description="Etiqueta del punto (fecha, especialidad, rango etario, etc)")
    valor: int | float = Field(..., ge=0, description="Valor numérico")
    porcentaje: Optional[float] = Field(None, ge=0, le=100, description="Porcentaje del total")


class SerieResponse(BaseModel):
    titulo: str = Field(..., description="Título de la serie")
    datos: List[SerieItem] = Field(..., description="Puntos de la serie")
    total: int = Field(..., ge=0, description="Suma total de la serie")
    generado_en: str = Field(..., description="Timestamp ISO de generación")


class ResumenItem(BaseModel):
    etiqueta: str = Field(..., description="Nombre del indicador")
    valor: int = Field(..., ge=0, description="Valor numérico")
    variacion: Optional[float] = Field(None, description="Variación porcentual respecto al periodo anterior")
    tendencia: Optional[str] = Field(None, pattern="^(up|down|stable)$", description="Dirección de la tendencia")


class ResumenResponse(BaseModel):
    indicadores: List[ResumenItem] = Field(..., description="Lista de indicadores clave")
    periodo: str = Field(..., description="Descripción del periodo (ej: 'Hoy', 'Últimos 30 días')")
    generado_en: str = Field(..., description="Timestamp ISO de generación")


class HistogramaEtario(BaseModel):
    rango: str = Field(..., description="Rango de edad (ej: '0-4', '5-9', ...)")
    hombres: int = Field(0, ge=0, description="Cantidad de pacientes masculinos")
    mujeres: int = Field(0, ge=0, description="Cantidad de pacientes femeninos")
    total: int = Field(0, ge=0, description="Total del rango")


class PiramidePoblacional(BaseModel):
    titulo: str = "Pirámide Poblacional"
    rangos: List[HistogramaEtario] = Field(..., description="Distribución por rango etario y sexo")
    total_hombres: int = Field(..., ge=0)
    total_mujeres: int = Field(..., ge=0)
    total_pacientes: int = Field(..., ge=0)
    generado_en: str


class ProcedimientoFrecuente(BaseModel):
    nombre: str = Field(..., description="Nombre del procedimiento")
    total: int = Field(..., ge=0, description="Cantidad de veces realizado")
    porcentaje: float = Field(..., ge=0, le=100, description="Porcentaje del total")


class TopProcedimientos(BaseModel):
    titulo: str = "Procedimientos Más Frecuentes"
    procedimientos: List[ProcedimientoFrecuente] = Field(..., description="Lista ordenada por frecuencia descendente")
    total_general: int = Field(..., ge=0)
    periodo: str
    generado_en: str


class OcupacionItem(BaseModel):
    servicio: str = Field(..., description="Servicio hospitalario")
    camas_disponibles: int = Field(..., ge=0)
    camas_ocupadas: int = Field(..., ge=0)
    porcentaje_ocupacion: float = Field(..., ge=0, le=100)
    tendencia: Optional[str] = None


class OcupacionResponse(BaseModel):
    titulo: str = "Ocupación Hospitalaria"
    servicios: List[OcupacionItem]
    total_camas: int
    total_ocupadas: int
    porcentaje_global: float
    generado_en: str


class ReporteFechas(BaseModel):
    desde: Optional[date] = Field(None, description="Fecha de inicio (opcional)")
    hasta: Optional[date] = Field(None, description="Fecha de fin (opcional)")
    generado_en: str = Field(..., description="Timestamp de generación")
    data: List[dict] = Field(..., description="Datos del reporte en formato tabular")
    columnas: List[str] = Field(..., description="Nombres de las columnas")
    total_filas: int = Field(..., ge=0)


class PersonalSaludFila(BaseModel):
    sexo: str = Field(..., description="Sexo del paciente (M/F)")
    diagnostico: Optional[str] = Field(None, description="Diagnóstico principal del egreso")
    especialidad: str = Field(..., description="Especialidad de la consulta")
    tipo_consulta: int = Field(..., description="1=COEX, 2=Hospitalización, 3=Emergencia")
    tipo_consulta_nombre: str = Field(..., description="Nombre del tipo de consulta")
    total: int = Field(..., ge=0, description="Cantidad de consultas")


class PersonalSaludDetalle(BaseModel):
    expediente: Optional[str] = None
    nombre: str = Field(..., description="Nombre completo del paciente")
    sexo: Optional[str] = Field(None, description="Sexo del paciente (M/F)")
    fecha_nacimiento: Optional[date] = None
    diagnostico: Optional[str] = None
    fecha_consulta: date = Field(..., description="Fecha de la consulta")
    especialidad: str = Field(..., description="Especialidad de la consulta")
    tipo_consulta: int = Field(..., description="1=COEX, 2=Hospitalización, 3=Emergencia")


class PersonalSaludReporte(BaseModel):
    titulo: str = "Consulta de Personal de Salud"
    desde: date
    hasta: date
    filtro_aplicado: str = Field(..., description="Indicador usado para filtrar (personal_hospital)")
    resumen: List[PersonalSaludFila] = Field(..., description="Filas agrupadas")
    detalle: List[PersonalSaludDetalle] = Field(default_factory=list, description="Listado detallado de pacientes")
    total_consultas: int = Field(..., ge=0)
    total_sexo_m: int = Field(..., ge=0)
    total_sexo_f: int = Field(..., ge=0)
    generado_en: str
