# models/renap.py
from pydantic import BaseModel
from typing import List, Optional

class Persona(BaseModel):
    CUI: Optional[str] = None
    PRIMER_NOMBRE: Optional[str] = None
    SEGUNDO_NOMBRE: Optional[str] = None
    TERCER_NOMBRE: Optional[str] = None
    PRIMER_APELLIDO: Optional[str] = None
    SEGUNDO_APELLIDO: Optional[str] = None
    APELLIDO_CASADA: Optional[str] = None
    SEXO: Optional[str] = None
    ESTADO_CIVIL: Optional[str] = None
    FECHA_NACIMIENTO: Optional[str] = None

class RespuestaRenap(BaseModel):
    error: bool
    mensaje: str
    resultado: Optional[List[Persona]] = []            # opcional, para casos de error
    solicitudes_restantes: Optional[int] = 0          # opcional, para casos de error