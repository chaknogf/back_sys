from pydantic import BaseModel, Field
from typing import List
from datetime import date, datetime


class PacientesAtendidosItem(BaseModel):
    tipo_consulta: int = Field(..., description="1=COEX, 2=Hospitalización, 3=Emergencia")
    tipo_consulta_nombre: str = Field(..., description="Nombre del tipo de consulta")
    especialidad: str = Field(..., description="Especialidad médica")
    sexo: str = Field(..., description="Sexo del paciente (M/F)")
    total: int = Field(..., ge=0, description="Cantidad de consultas")


class PacientesAtendidosResponse(BaseModel):
    titulo: str = "Pacientes Atendidos por Tipo, Especialidad y Sexo"
    desde: date
    hasta: date
    datos: List[PacientesAtendidosItem]
    total_general: int = Field(..., ge=0)
    generado_en: str


class HospitalizacionInfantilItem(BaseModel):
    especialidad: str = Field(..., description="Especialidad médica")
    sexo: str = Field(..., description="Sexo del paciente (M/F)")
    total: int = Field(..., ge=0, description="Cantidad de hospitalizaciones")


class HospitalizacionInfantilResponse(BaseModel):
    titulo: str = "Hospitalizaciones Infantiles (>28 días y <5 años)"
    desde: date
    hasta: date
    datos: List[HospitalizacionInfantilItem]
    total_general: int = Field(..., ge=0)
    generado_en: str


class PromedioTipoConsulta(BaseModel):
    tipo_consulta: int = Field(..., description="1=COEX, 2=Hospitalización, 3=Emergencia")
    tipo_consulta_nombre: str = Field(..., description="Nombre del tipo de consulta")
    total: int = Field(..., ge=0, description="Total de consultas")
    dias_con_registros: int = Field(..., ge=0, description="Días con al menos un registro")
    promedio_diario: float = Field(..., ge=0, description="Promedio de consultas por día")


class PromedioDiarioItem(BaseModel):
    especialidad: str = Field(..., description="Especialidad médica")
    total_consultas: int = Field(..., ge=0, description="Total de consultas")
    dias_con_registros: int = Field(..., ge=0, description="Días con al menos un registro")
    promedio_diario: float = Field(..., ge=0, description="Promedio de consultas por día")
    por_tipo: List[PromedioTipoConsulta] = Field(..., description="Desglose por tipo de consulta")


class PromedioDiarioResponse(BaseModel):
    titulo: str = "Promedio Diario de Consultas"
    desde: date
    hasta: date
    datos: List[PromedioDiarioItem]
    total_general: int = Field(..., ge=0)
    generado_en: str
