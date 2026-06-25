from pydantic import BaseModel, Field
from typing import List, Optional
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


class NacimientoSexoEstadoItem(BaseModel):
    sexo: str = Field(..., description="Sexo del neonato (M/F)")
    estado: str = Field(..., description="Estado (V=Vivo, F=Fallecido)")
    total: int = Field(..., ge=0, description="Cantidad de nacimientos")


class NacimientoClasePartoItem(BaseModel):
    clase_parto: Optional[str] = Field(None, description="Clase de parto (UNICO/GEMELAR/TRIPLE/MULTIPLE)")
    estado: str = Field(..., description="Estado (V/F)")
    sexo: str = Field(..., description="Sexo del neonato (M/F)")
    total: int = Field(..., ge=0)


class NacimientoClasificacionPartoItem(BaseModel):
    clasificacion_parto: Optional[str] = Field(None, description="Clasificación del nacimiento (EBP/MBP/BP/PN)")
    estado: str = Field(..., description="Estado (V/F)")
    sexo: str = Field(..., description="Sexo del neonato (M/F)")
    total: int = Field(..., ge=0)


class NacimientoTrabajoPartoItem(BaseModel):
    trabajo_parto: Optional[str] = Field(None, description="Trabajo de parto (Prematuro/a Termino/Prolongado)")
    estado: str = Field(..., description="Estado (V/F)")
    sexo: str = Field(..., description="Sexo del neonato (M/F)")
    total: int = Field(..., ge=0)


class PersonalHospitalItem(BaseModel):
    nombre: Optional[dict] = Field(None, description="Nombre del paciente (JSONB)")
    nombre_completo: Optional[str] = None
    expediente: Optional[str] = Field(None, description="Expediente del paciente")
    tipo_consulta: int = Field(..., description="1=COEX, 2=Hospitalización, 3=Emergencia")
    tipo_consulta_nombre: str = Field(..., description="Nombre del tipo de consulta")
    sexo: Optional[str] = Field(None, description="Sexo del paciente (M/F)")
    edad: Optional[int] = Field(None, description="Edad del paciente en años al momento de la consulta")
    especialidad: str = Field(..., description="Especialidad médica")
    documento: Optional[str] = Field(None, description="Documento de la consulta")
    diagnostico: Optional[str] = Field(None, description="Diagnóstico de egreso")
    fecha_consulta: Optional[date] = None
    paciente_id: Optional[int] = None


class PersonalHospitalResponse(BaseModel):
    titulo: str = "Consultas de Personal del Hospital"
    desde: date
    hasta: date
    datos: List[PersonalHospitalItem]
    total_general: int = Field(..., ge=0)
    generado_en: str


class EstudiantePublicoItem(BaseModel):
    nombre: Optional[dict] = Field(None, description="Nombre del paciente (JSONB)")
    nombre_completo: Optional[str] = None
    expediente: Optional[str] = Field(None, description="Expediente del paciente")
    tipo_consulta: int = Field(..., description="1=COEX, 2=Hospitalización, 3=Emergencia")
    tipo_consulta_nombre: str = Field(..., description="Nombre del tipo de consulta")
    sexo: Optional[str] = Field(None, description="Sexo del paciente (M/F)")
    edad: Optional[int] = Field(None, description="Edad del paciente en años al momento de la consulta")
    especialidad: str = Field(..., description="Especialidad médica")
    documento: Optional[str] = Field(None, description="Documento de la consulta")
    diagnostico: Optional[str] = Field(None, description="Diagnóstico de egreso")
    fecha_consulta: Optional[date] = None
    paciente_id: Optional[int] = None


class EstudiantePublicoResponse(BaseModel):
    titulo: str = "Consultas de Estudiantes Públicos"
    desde: date
    hasta: date
    datos: List[EstudiantePublicoItem]
    total_general: int = Field(..., ge=0)
    generado_en: str


class ReingresoItem(BaseModel):
    nombre: Optional[dict] = Field(None, description="Nombre del paciente (JSONB)")
    sexo: Optional[str] = Field(None, description="Sexo del paciente (M/F)")
    estado: Optional[str] = Field(None, description="Estado del paciente (V/F)")
    edad: Optional[int] = Field(None, description="Edad del paciente en años al momento de la consulta")
    fecha_consulta: date = Field(..., description="Fecha de la consulta (reingreso)")
    especialidad: str = Field(..., description="Especialidad médica")
    prev_fecha_consulta: Optional[date] = Field(None, description="Fecha de la consulta anterior")
    prev_especialidad: Optional[str] = Field(None, description="Especialidad de la consulta anterior")
    egreso_actual_registro: Optional[str] = Field(None, description="Fecha y hora de egreso del reingreso actual")
    egreso_registro: Optional[str] = Field(None, description="Fecha y hora de egreso del ingreso anterior")
    diagnostico: Optional[str] = Field(None, description="Diagnóstico del egreso anterior")
    dias_entre_consultas: Optional[int] = Field(None, description="Días entre consultas (egreso anterior si existe, o diferencia entre fechas)")
    clasificacion: Optional[str] = Field(None, description="Clasificación: menores a 8 dias / por complicaciones")


class ReingresoResponse(BaseModel):
    titulo: str = "Reingresos Hospitalarios"
    desde: date
    hasta: date
    datos: List[ReingresoItem]
    resumen: dict = Field(..., description="Conteo por clasificación: menores a 8 dias, por complicaciones")
    total_general: int = Field(..., ge=0)
    generado_en: str


class NacimientosStatsResponse(BaseModel):
    titulo: str = "Estadísticas de Nacimientos"
    desde: date
    hasta: date
    total: int = Field(..., ge=0, description="Total de nacimientos en el período")
    por_sexo_estado: List[NacimientoSexoEstadoItem]
    por_clase_parto: List[NacimientoClasePartoItem]
    por_clasificacion_parto: List[NacimientoClasificacionPartoItem]
    por_trabajo_parto: List[NacimientoTrabajoPartoItem]
    generado_en: str
