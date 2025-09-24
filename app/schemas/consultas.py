
from typing import Optional, Dict
from datetime import date, time
from pydantic import BaseModel, ConfigDict, Field

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

class Ciclo(BaseModel):
    estado: Optional[str] = None
    registro: Optional[str] = None
    usuario: Optional[str] = None
    especialidad: Optional[str] = None
    servicio: Optional[str] = None
    detalle_clinicos: Optional[Dict] = None
    sistema: Optional[Dict] = None
    signos_vitales: Optional[Dict] = None
    antecedentes: Optional[Dict] = None
    ordenes: Optional[Dict] = None
    estudios: Optional[Dict] = None
    comentario: Optional[Dict] = None
    impresion_clinica: Optional[Dict] = None
    tratamiento: Optional[Dict] = None
    examen_fisico: Optional[Dict] = None
    nota_enfermeria: Optional[Dict] = None   # <-- aquí un solo objeto
    contraindicado: Optional[str] = None
    presa_quirurgica: Optional[Dict] = None
    egreso: Optional[Dict] = None
    
class ConsultaBase(BaseModel):
    expediente: Optional[str]
    paciente_id: int
    tipo_consulta: Optional[int]
    especialidad: Optional[int]
    servicio: Optional[int]
    documento: Optional[str]
    fecha_consulta: Optional[date]
    hora_consulta: Optional[time]
    indicadores: Optional[ Indicador] = Field(default_factory=dict)
    ciclo: Optional[Dict] = Field(default_factory=dict)
    
    
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
    indicadores: Optional[ Indicador] = Field(default_factory=dict)
    ciclo: Optional[Dict] = Field(default_factory=dict)

class ConsultaCreate(ConsultaBase):
    pass

class ConsultaOut(ConsultaBase):
    id: int
    

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

