from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict, Field
from datetime import date, time, datetime


class Datos(BaseModel):
    clave: str
    valor: str
    registro: str

class Signos_vitales(BaseModel):
    pa: str
    fc: str
    fr: str
    sat02: str
    temp: str
    peso: str
    talla: str
    pt: str
    te: str
    pe: str
    gmt: str
    
class Antecedentes(BaseModel):
    familiares: List[Dict[str, Any]]
    medicos: List[Dict[str, Any]]
    quirurgicos: List[Dict[str, Any]]
    alergicos: List[Dict[str, Any]]
    traumaticos: List[Dict[str, Any]]
    ginecoobstetricos: List[Dict[str, Any]]
    habitos: List[Dict[str, Any]]

class Nota(BaseModel):
    usuario: str
    nota: str
    registro: str
    
class Enfermeria(BaseModel):
    usuario: str
    turno: str
    nota: str
    registro: str
    signos: Dict[str, Signos_vitales]  # ✅ Esto es válido
    

  
class Silverman(BaseModel):
    retraso_esternal: int
    aleteo_nasal: int
    quejido_expiratorio: int
    movimiento_toracico: int
    retraccion_supraclavicular: int
    puntuacion_total: int
    
    
class Downe(BaseModel):
    frecuencia_respiratoria: int
    aleteo_nasal: int
    quejido_respiratorio: int
    retraccion_toracoabdominal: int
    cinoasis: int
    puntuacion_total: int

class Cuerpo(BaseModel):
    cabeza: str
    ojos: str
    oidos: str
    nariz: str
    boca: str
    cuello: str
    torax: str
    pulmones: str
    corazon: str
    abdomen: str
    genitales: str
    extremidades: str
    columna: str
    piel: str
    neurologico: str
    
class Glasgow(BaseModel):
    apertura_ocular: int
    respuesta_verbal: int
    respuesta_motora: int
    puntuacion_total: int
    
class Bishop(BaseModel):
    dilatacion: int
    borramiento: int
    posicion: int
    consistencia: int
    altura_presentacion: int
    puntuacion_total: int
    
class Apgar(BaseModel):
    tono_muscular: int
    respuesta_refleja: int
    llanto: int
    respiracion: int
    coloracion: int
    puntuacion_total: int
    interpretacion: str
    
class ExamenFisico(BaseModel):
    silverman: Silverman
    downe: Downe
    cuerpo: Cuerpo
    glasgow: Glasgow
    bishop: Bishop
    apgar: Apgar
    
class Sistema(BaseModel):
    usuario: str
    accion: str
    fecha: str
    
class Dx(BaseModel):
    codigo: str
    descripcion: str
    tipo: str
    
class Egreso(BaseModel):
    registro: str
    usuario: str
    referencia: str
    diagnostico: List[Dx]
    condicion_egreso: str
    
class Presa_quirurgica(BaseModel):
    programada: str
    reprogramada: str
    realizada: str
    detalle: str
    especialidad: str

class Indicador(BaseModel):
    estudiante_publico: bool
    empleado_publico: bool
    accidente_laboral: bool
    discapacidad: bool
    accidente_transito: bool
    arma_fuego: bool
    arma_blanca: bool
    ambulancia: bool
    embarazo: bool
    

class ConsultaBase(BaseModel):
    expediente: Optional[str]
    paciente_id: int
    tipo_consulta: Optional[int]
    especialidad: Optional[int]
    servicio: Optional[int]
    documento: Optional[str]
    fecha_consulta: Optional[date]
    hora_consulta: Optional[time]
    ciclo: Optional[Dict[str, Datos]] = Field(default=None)
    indicadores: Indicador = Field(default_factory=Indicador)
    detalle_clinicos: Optional[Dict[str, Datos]] = Field(default=None)
    sistema: Optional[Dict[str,Sistema]] = Field(default=None)
    signos_vitales: Optional[Dict[str, Signos_vitales]] = Field(default=None)
    antecedentes: Optional[Dict[str, Antecedentes]] = Field(default=None)
    ordenes: Optional[Dict[str, Datos]] = Field(default=None)
    estudios: Optional[Dict[str, Datos]] = Field(default=None)
    comentario: Optional[Dict[str, Nota]] = Field(default=None)
    impresion_clinica: Optional[Dict[str, Nota]] = Field(default=None)
    tratamiento: Optional[Dict[str, Nota]] = Field(default=None)
    examen_fisico: Optional[Dict[str, ExamenFisico]] = None
    nota_enfermeria: Optional[Dict[str, Enfermeria]] = Field(default=None)
    contraindicado: Optional[str] = None
    presa_quirurgica: Optional[Dict[str, Presa_quirurgica]] = Field(default=None)
    egreso: Optional[Dict[str, Egreso]] = Field(default=None)
    
    
    
class ConsultaUpdate(BaseModel):
    id: Optional[int] = None
    expediente: Optional[str]
    paciente_id: int
    tipo_consulta: Optional[int]
    especialidad: Optional[int]
    servicio: Optional[int]
    documento: Optional[str]
    fecha_consulta: Optional[date]
    hora_consulta: Optional[time]
    ciclo: Optional[Dict[str, Datos]] = Field(default=None)
    indicadores: Optional[Dict[str, Datos]] = Field(default=None)
    detalle_clinicos: Optional[Dict[str, Datos]] = Field(default=None)
    sistema: Optional[Dict[str,Sistema]] = Field(default=None)
    signos_vitales: Optional[Dict[str, Signos_vitales]] = Field(default=None)
    antecedentes: Optional[Dict[str, Antecedentes]] = Field(default=None)
    ordenes: Optional[Dict[str, Datos]] = Field(default=None)
    estudios: Optional[Dict[str, Datos]] = Field(default=None)
    comentario: Optional[Dict[str, Nota]] = Field(default=None)
    impresion_clinica: Optional[Dict[str, Nota]] = Field(default=None)
    tratamiento: Optional[Dict[str, Nota]] = Field(default=None)
    examen_fisico: Optional[Dict[str, ExamenFisico]] = None
    nota_enfermeria: Optional[Dict[str, Enfermeria]] = Field(default=None)
    contraindicado: Optional[str] = None
    presa_quirurgica: Optional[Dict[str, Presa_quirurgica]] = Field(default=None)
    egreso: Optional[Dict[str, Egreso]] = Field(default=None)

class ConsultaCreate(ConsultaBase):
    pass

class ConsultaOut(ConsultaBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)