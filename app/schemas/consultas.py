# app/schemas/consultas.py
"""
Schemas para consultas médicas.
Totalmente compatibles con FastAPI + Pydantic v2 + OpenAPI.
"""

from typing import Optional, Dict, Any
from datetime import date, time
from pydantic import BaseModel, ConfigDict, Field


# ===================================================================
# Indicadores clínicos (banderas sí/no)
# ===================================================================
class Indicador(BaseModel):
    """Indicadores sociales y clínicos de la consulta"""
    estudiante_publico: bool = Field(..., description="¿Es estudiante de institución pública?")
    empleado_publico: bool = Field(..., description="¿Es empleado público?")
    accidente_laboral: bool = Field(..., description="¿Accidente laboral?")
    discapacidad: bool = Field(..., description="¿Tiene discapacidad?")
    accidente_transito: bool = Field(..., description="¿Accidente de tránsito?")
    arma_fuego: bool = Field(..., description="¿Herida por arma de fuego?")
    arma_blanca: bool = Field(..., description="¿Herida por arma blanca?")
    ambulancia: bool = Field(..., description="¿Llegó en ambulancia?")
    embarazo: bool = Field(..., description="¿Paciente embarazada?")

    model_config = ConfigDict(from_attributes=True)


# ===================================================================
# Ciclo clínico completo (estructura flexible pero tipada)
# ===================================================================
class CicloClinico(BaseModel):
    """Estructura completa del ciclo de atención"""
    estado: Optional[str] = None
    registro: Optional[str] = None
    usuario: Optional[str] = None
    especialidad: Optional[str] = None
    servicio: Optional[str] = None
    detalle_clinicos: Optional[Dict[str, Any]] = None
    sistema: Optional[Dict[str, Any]] = None
    signos_vitales: Optional[Dict[str, Any]] = None
    antecedentes: Optional[Dict[str, Any]] = None
    ordenes: Optional[Dict[str, Any]] = None
    estudios: Optional[Dict[str, Any]] = None
    comentario: Optional[Dict[str, Any]] = None
    impresion_clinica: Optional[Dict[str, Any]] = None
    tratamiento: Optional[Dict[str, Any]] = None
    examen_fisico: Optional[Dict[str, Any]] = None
    nota_enfermeria: Optional[Dict[str, Any]] = None
    contraindicado: Optional[str] = None
    presa_quirurgica: Optional[Dict[str, Any]] = None
    egreso: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(extra="allow", from_attributes=True)


# ===================================================================
# Schema base (común)
# ===================================================================
class ConsultaBase(BaseModel):
    expediente: Optional[str] = Field(None, max_length=20, description="Expediente del paciente")
    paciente_id: int = Field(..., gt=0, description="ID del paciente en la tabla pacientes")
    tipo_consulta: Optional[int] = Field(None, ge=1, description="Código del tipo de consulta")
    especialidad: Optional[str] = Field(None, max_length=50)
    servicio: Optional[str] = Field(None, max_length=50)
    documento: Optional[str] = Field(None, max_length=20, description="DPI, pasaporte, etc.")
    fecha_consulta: Optional[date] = None
    hora_consulta: Optional[time] = None
    indicadores: Optional[Indicador] = None
    ciclo: Optional[CicloClinico] = None
    orden: Optional[int] = Field(None, ge=0, description="Orden en la cola de atención")

    model_config = ConfigDict(from_attributes=True)


# ===================================================================
# Para crear una consulta
# ===================================================================
class ConsultaCreate(ConsultaBase):
    """Usado al crear una nueva consulta"""
    # paciente_id, tipo_consulta, fecha_consulta suelen ser obligatorios
    paciente_id: int = Field(..., gt=0)
    tipo_consulta: int = Field(..., ge=1)
    fecha_consulta: date
    hora_consulta: time


# ===================================================================
# Para actualizar (parcial) - PATCH
# ===================================================================
class ConsultaUpdate(BaseModel):
    """Actualización parcial de consulta"""
    expediente: Optional[str] = None
    tipo_consulta: Optional[int] = None
    especialidad: Optional[str] = None
    servicio: Optional[str] = None
    documento: Optional[str] = None
    fecha_consulta: Optional[date] = None
    hora_consulta: Optional[time] = None
    indicadores: Optional[Indicador] = None
    ciclo: Optional[CicloClinico] = None
    orden: Optional[int] = None

    model_config = ConfigDict(extra="ignore")


# ===================================================================
# Respuesta completa al frontend
# ===================================================================
class ConsultaOut(ConsultaBase):
    id: int = Field(..., description="ID único de la consulta")
    creado_en: Optional[date] = None
    actualizado_en: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)


# ===================================================================
# Para listas con conteo (paginación)
# ===================================================================
class ConsultaListResponse(BaseModel):
    total: int
    consultas: list[ConsultaOut]

    model_config = ConfigDict(from_attributes=True)
    
    
    
# class Datos(BaseModel):
#     clave: str
#     valor: str
#     registro: str

# class Signos_vitales(BaseModel):
#     pa: str
#     fc: str
#     fr: str
#     sat02: str
#     temp: str
#     peso: str
#     talla: str
#     pt: str
#     te: str
#     pe: str
#     gmt: str
    
# class Antecedentes(BaseModel):
#     familiares: List[Dict[str, Any]]
#     medicos: List[Dict[str, Any]]
#     quirurgicos: List[Dict[str, Any]]
#     alergicos: List[Dict[str, Any]]
#     traumaticos: List[Dict[str, Any]]
#     ginecoobstetricos: List[Dict[str, Any]]
#     habitos: List[Dict[str, Any]]

# class Nota(BaseModel):
#     usuario: str
#     nota: str
#     registro: str
    
# class Enfermeria(BaseModel):
#     usuario: str
#     turno: str
#     nota: str
#     registro: str
#     signos: Dict[str, Signos_vitales]  
    

  
# class Silverman(BaseModel):
#     retraso_esternal: int
#     aleteo_nasal: int
#     quejido_expiratorio: int
#     movimiento_toracico: int
#     retraccion_supraclavicular: int
#     puntuacion_total: int
    
    
# class Downe(BaseModel):
#     frecuencia_respiratoria: int
#     aleteo_nasal: int
#     quejido_respiratorio: int
#     retraccion_toracoabdominal: int
#     cinoasis: int
#     puntuacion_total: int

# class Cuerpo(BaseModel):
#     cabeza: str
#     ojos: str
#     oidos: str
#     nariz: str
#     boca: str
#     cuello: str
#     torax: str
#     pulmones: str
#     corazon: str
#     abdomen: str
#     genitales: str
#     extremidades: str
#     columna: str
#     piel: str
#     neurologico: str
    
# class Glasgow(BaseModel):
#     apertura_ocular: int
#     respuesta_verbal: int
#     respuesta_motora: int
#     puntuacion_total: int
    
# class Bishop(BaseModel):
#     dilatacion: int
#     borramiento: int
#     posicion: int
#     consistencia: int
#     altura_presentacion: int
#     puntuacion_total: int
    
# class Apgar(BaseModel):
#     tono_muscular: int
#     respuesta_refleja: int
#     llanto: int
#     respiracion: int
#     coloracion: int
#     puntuacion_total: int
#     interpretacion: str
    
# class ExamenFisico(BaseModel):
#     silverman: Silverman
#     downe: Downe
#     cuerpo: Cuerpo
#     glasgow: Glasgow
#     bishop: Bishop
#     apgar: Apgar
    
# class Sistema(BaseModel):
#     usuario: str
#     accion: str
#     fecha: str
    
# class Dx(BaseModel):
#     codigo: str
#     descripcion: str
#     tipo: str
    
# class Egreso(BaseModel):
#     registro: str
#     usuario: str
#     referencia: str
#     diagnostico: List[Dx]
#     condicion_egreso: str
    
# class Presa_quirurgica(BaseModel):
#     programada: str
#     reprogramada: str
#     realizada: str
#     detalle: str
#     especialidad: str

