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


class NacimientoMortinatoItem(BaseModel):
    sexo: str = Field(..., description="Sexo del neonato (M/F)")
    estado: str = Field(..., description="Estado por mortinato (Vivo/Mortinato)")
    total: int = Field(..., ge=0, description="Cantidad de nacimientos")


class NacimientoSexoEstadoFallecidoItem(BaseModel):
    sexo: str = Field(..., description="Sexo del neonato (M/F)")
    estado: str = Field(..., description="Estado del paciente en el sistema (V/F)")
    total: int = Field(..., ge=0, description="Cantidad de nacimientos")


class NacimientoClasePartoItem(BaseModel):
    clase_parto: Optional[str] = Field(None, description="Clase de parto (UNICO/GEMELAR/TRIPLE/MULTIPLE)")
    estado: str = Field(..., description="Estado: Vivo, Mortinato o Fallecido")
    sexo: str = Field(..., description="Sexo del neonato (M/F)")
    total: int = Field(..., ge=0)


class NacimientoClasificacionPartoItem(BaseModel):
    clasificacion_parto: Optional[str] = Field(None, description="Clasificación del nacimiento (EBP/MBP/BP/PN)")
    estado: str = Field(..., description="Estado: Vivo, Mortinato o Fallecido")
    sexo: str = Field(..., description="Sexo del neonato (M/F)")
    total: int = Field(..., ge=0)


class NacimientoTrabajoPartoItem(BaseModel):
    trabajo_parto: Optional[str] = Field(None, description="Trabajo de parto (Prematuro/a Termino/Prolongado)")
    estado: str = Field(..., description="Estado: Vivo, Mortinato o Fallecido")
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
    skip: int = Field(..., ge=0)
    limit: int = Field(..., ge=1)
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


class ReingresoEspecialidadItem(BaseModel):
    especialidad: str = Field(..., description="Especialidad médica")
    menores_a_8_dias: int = Field(0, ge=0, description="Reingresos <8 días")
    por_complicaciones: int = Field(0, ge=0, description="Reingresos por complicaciones")
    total: int = Field(..., ge=0, description="Total de reingresos en la especialidad")


class ReingresoResponse(BaseModel):
    titulo: str = "Reingresos Hospitalarios"
    desde: date
    hasta: date
    datos: List[ReingresoItem]
    resumen: dict = Field(..., description="Conteo por clasificación: menores a 8 dias, por complicaciones")
    por_especialidad: List[ReingresoEspecialidadItem] = Field(..., description="Reingresos agrupados por especialidad y clasificación")
    total_general: int = Field(..., ge=0)
    generado_en: str


class NacimientosStatsResponse(BaseModel):
    titulo: str = "Estadísticas de Nacimientos"
    desde: date
    hasta: date
    total: int = Field(..., ge=0, description="Total de nacimientos en el período")
    por_mortinato: List[NacimientoMortinatoItem] = Field(..., description="Agrupación por sexo y mortinato (Vivo/Mortinato)")
    por_fallecidos_posteriores: List[NacimientoSexoEstadoFallecidoItem] = Field(..., description="Agrupación por sexo y estado del paciente (post-natal)")
    por_clase_parto: List[NacimientoClasePartoItem]
    por_clasificacion_parto: List[NacimientoClasificacionPartoItem]
    por_trabajo_parto: List[NacimientoTrabajoPartoItem]
    generado_en: str


# =====================================================================
# SIGSA-3 ESTADÍSTICAS
# =====================================================================
class Sigsa3EspecialidadItem(BaseModel):
    especialidad: Optional[str] = None
    tipo_consulta: Optional[str] = None
    sexo: Optional[str] = None
    total: int = Field(..., ge=0)


class Sigsa3EspecialidadResponse(BaseModel):
    titulo: str = "Consultas SIGSA-3 por Especialidad, Tipo y Sexo"
    desde: date
    hasta: date
    datos: List[Sigsa3EspecialidadItem]
    total_general: int = Field(..., ge=0)
    generado_en: str


class Sigsa3DxItem(BaseModel):
    especialidad: Optional[str] = None
    tipo_consulta: Optional[str] = None
    dx: Optional[str] = None
    total_m: int = Field(0, ge=0)
    total_f: int = Field(0, ge=0)
    total: int = Field(..., ge=0)


class Sigsa3DxTotalGrupoItem(BaseModel):
    especialidad: Optional[str] = None
    tipo_consulta: Optional[str] = None
    total_top: int = Field(..., ge=0)
    total_resto: int = Field(..., ge=0)
    total: int = Field(..., ge=0)


class Sigsa3DxFrecuentesResponse(BaseModel):
    titulo: str = "Diagnósticos Más Frecuentes por Especialidad"
    desde: date
    hasta: date
    top: int = Field(..., ge=1, description="Cantidad de diagnósticos top por grupo")
    datos: List[Sigsa3DxItem]
    totales_por_grupo: List[Sigsa3DxTotalGrupoItem]
    total_general: int = Field(..., ge=0)
    generado_en: str


# =====================================================================
# INDICADORES DE CONSULTA (jsonb consultas.indicadores)
# =====================================================================
class IndicadorTipoConsultaItem(BaseModel):
    tipo_consulta: int = Field(..., description="1=COEX, 2=Hospitalización, 3=Emergencia")
    tipo_consulta_nombre: str
    total: int = Field(..., ge=0)


class IndicadorConsultaItem(BaseModel):
    indicador: str = Field(..., description="Clave dentro del jsonb indicadores")
    etiqueta: str = Field(..., description="Nombre legible del indicador")
    tipo_dato: str = Field(..., description="booleano o texto")
    clave_ausente: int = Field(0, ge=0, description="Consultas cuyo jsonb no incluye la clave")
    sin_valor: int = Field(0, ge=0, description="Consultas con la clave presente pero nula o vacía")
    verdadero: int = Field(0, ge=0, description="Consultas con el indicador marcado (solo booleanos)")
    falso: int = Field(0, ge=0, description="Consultas con el indicador en negativo (solo booleanos)")
    con_texto: int = Field(0, ge=0, description="Consultas con texto no vacío (solo indicadores de texto)")
    valores_distintos: int = Field(0, ge=0, description="Valores de texto diferentes (solo indicadores de texto)")
    pacientes: int = Field(0, ge=0, description="Pacientes distintos con el indicador marcado")
    porcentaje_consultas: float = Field(0, ge=0, description="Porcentaje sobre las consultas del período")
    porcentaje_pacientes: float = Field(0, ge=0, description="Porcentaje sobre los pacientes del período")
    por_tipo_consulta: List[IndicadorTipoConsultaItem] = Field(default_factory=list)


class IndicadorReferenciaItem(BaseModel):
    indicador: str = Field(..., description="viene_referido o fue_referido")
    valor: str
    total: int = Field(..., ge=0)


class IndicadoresCobertura(BaseModel):
    consultas_sin_columna: int = Field(0, ge=0, description="Consultas con indicadores IS NULL")
    consultas_sin_claves: int = Field(0, ge=0, description="Consultas con el jsonb vacío")
    claves_distintas: int = Field(0, ge=0, description="Claves diferentes halladas en el período")
    promedio_claves_por_consulta: float = Field(0, ge=0)


class IndicadoresConsultasResponse(BaseModel):
    titulo: str = "Resumen de Indicadores de Consultas"
    desde: date
    hasta: date
    total_consultas: int = Field(..., ge=0)
    pacientes_distintos: int = Field(..., ge=0)
    dias_con_registros: int = Field(..., ge=0)
    cobertura: IndicadoresCobertura
    datos: List[IndicadorConsultaItem]
    referencias: List[IndicadorReferenciaItem] = Field(
        default_factory=list, description="Orígenes y destinos más frecuentes de las referencias"
    )
    total_general: int = Field(..., ge=0)
    generado_en: str


# =====================================================================
# REFERENCIAS (consultas.indicadores: viene_referido_de, va_referido_a)
# =====================================================================
class ReferenciaItemLista(BaseModel):
    id: int = Field(..., description="ID de la consulta")
    paciente_id: Optional[int] = None
    expediente: Optional[str] = None
    tipo_consulta: Optional[int] = None
    tipo_consulta_nombre: Optional[str] = None
    especialidad: Optional[str] = None
    fecha_consulta: Optional[date] = None
    viene_referido_de: Optional[str] = None
    va_referido_a: Optional[str] = None
    viene_referido: Optional[str] = None
    fue_referido: Optional[str] = None


class ReferenciaVarianteItem(BaseModel):
    valor: str = Field(..., description="Texto tal como se capturó en la consulta")
    total: int = Field(..., ge=0)


class ReferenciaResumenItem(BaseModel):
    direccion: str = Field(..., description="viene = viene_referido_de, va = va_referido_a")
    direccion_nombre: str = Field(..., description="Viene referido de / Va referido a")
    referencia: str = Field(..., description="Nombre normalizado (upper, sin acentos)")
    referencia_normalizada: str = Field(..., description="Alias de referencia, mismo valor")
    total_consultas: int = Field(0, ge=0)
    consultas_distintas: int = Field(0, ge=0)
    pacientes_distintos: int = Field(0, ge=0)
    variantes: List[ReferenciaVarianteItem] = Field(
        default_factory=list, description="Textos crudos que colapsan en esta referencia"
    )


class ReferenciasCobertura(BaseModel):
    consultas_con_jsonb: int = Field(0, ge=0)
    consultas_sin_jsonb: int = Field(0, ge=0)
    consultas_con_referencia: int = Field(0, ge=0)
    consultas_sin_referencia: int = Field(0, ge=0)
    con_origen: int = Field(0, ge=0, description="Consultas con viene_referido_de")
    con_destino: int = Field(0, ge=0, description="Consultas con va_referido_a")
    ambos_sentidos: int = Field(0, ge=0)
    porcentaje_con_referencia: float = Field(0, ge=0)


class ReferenciasResponse(BaseModel):
    titulo: str = "Referencias de Consultas (viene_referido_de / va_referido_a)"
    desde: date
    hasta: date
    total_consultas: int = Field(..., ge=0)
    pacientes_distintos: int = Field(..., ge=0)
    dias_con_registros: int = Field(..., ge=0)
    cobertura: ReferenciasCobertura
    lista: List[ReferenciaItemLista] = Field(default_factory=list)
    resumen: List[ReferenciaResumenItem] = Field(default_factory=list)
    total_general: int = Field(..., ge=0)
    skip: int = Field(..., ge=0)
    limit: int = Field(..., ge=1)
    generado_en: str
