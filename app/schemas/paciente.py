from typing import List, Optional, Dict
from pydantic import BaseModel, ConfigDict, Field
from datetime import date

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
    identificadores: Optional[List[Identificador]] = None
    nombre: Nombre
    sexo: Optional[str]
    fecha_nacimiento: Optional[date]
    contacto: Optional[List[Contacto]] = None
    referencias: Optional[List[Referencia]] = None
    datos_extra: Optional[List[DatosExtra]] = None
    estado: Optional[str] = "V"
    metadatos: Optional[List[Metadata]] = None
    nombre_completo: Optional[str] = None

class PacienteUpdate(BaseModel):
    id: Optional[int] = None
    unidad: Optional[int]
    identificadores: Optional[List[Identificador]] = None
    nombre: Optional[Nombre] = None
    sexo: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    contacto: Optional[List[Contacto]] = None
    referencias: Optional[List[Referencia]] = None
    datos_extra: Optional[List[DatosExtra]] = None
    estado: Optional[str] = "V"
    metadatos: Optional[List[Metadata]] = None
    

class PacienteCreate(PacienteBase):
    pass

class PacienteOut(PacienteBase):
    id: int
    

    model_config = ConfigDict(from_attributes=True)