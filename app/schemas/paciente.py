from typing import List, Optional, Union
from pydantic import BaseModel, ConfigDict
from datetime import date, datetime

class Identificador(BaseModel):
    tipo: str
    valor: str

class Nombre(BaseModel):
    primer: str
    segundo: Optional[str]
    otro: Optional[str]
    apellido_primero: str
    apellido_segundo: Optional[str]
    casada: Optional[str]

class Contacto(BaseModel):
    clave: str
    valor: str

class Referencia(BaseModel):
    nombre: str
    parentesco: Optional[str]
    telefono: Optional[str]

class DatosExtra(BaseModel):
    tipo: str
    valor: str

class Metadata(BaseModel):
    usuario: Optional[str]
    registro: Optional[str]

class PacienteBase(BaseModel):
    unidad: Optional[int]
    identificadores: Optional[List[Identificador]]
    nombre: Nombre
    sexo: Optional[str]
    fecha_nacimiento: Optional[date]
    contacto: Optional[List[Contacto]]
    referencias: Optional[List[Referencia]]
    datos_extra: Optional[List[DatosExtra]]
    estado: Optional[str] = "A"
    metadatos: Optional[List[Metadata]] 
    
    
class PacienteUpdate(BaseModel):
    id: Optional[int] = None
    unidad: Optional[int]
    identificadores: Optional[List[Identificador]]
    nombre: Nombre
    sexo: Optional[str]
    fecha_nacimiento: Optional[date]
    contacto: Optional[List[Contacto]]
    referencias: Optional[List[Referencia]]
    datos_extra: Optional[List[DatosExtra]]
    estado: Optional[str] = "A"
    metadatos: Optional[List[Metadata]] 
    nombre_completo: Optional[str]


class PacienteCreate(PacienteBase):
    pass

class PacienteOut(PacienteBase):
    id: int
    

    model_config = ConfigDict(from_attributes=True)