from typing import List, Optional, Union, Dict
from pydantic import BaseModel, ConfigDict, Field
from datetime import date, datetime

class Identificador(BaseModel):
    cui: Optional[int]
    expediente: Optional[str]
    pasaporte: Optional[str]
    otro: Optional[str]

class Nombre(BaseModel):
    primer: str
    segundo: Optional[str]
    otro: Optional[str]
    apellido_primero: str
    apellido_segundo: Optional[str]
    casada: Optional[str]

class Contacto(BaseModel):
    direccion: Optional[str]
    municipio: Optional[str]
    telefono: Optional[str]
    telefono2: Optional[str]
    telefono3: Optional[str]

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
    identificadores: Optional[Identificador]
    nombre: Nombre
    sexo: Optional[str]
    fecha_nacimiento: Optional[date]
    contacto: Optional[Contacto]
    referencias: Optional[Dict[str,Referencia]] = Field(default=None)
    datos_extra: Optional[Dict[str,DatosExtra]] = Field(default=None)
    estado: Optional[str] = "V"
    metadatos: Optional[Dict[str, Metadata]] = Field(default=None)
    
    
class PacienteUpdate(BaseModel):
    id: Optional[int] = None
    unidad: Optional[int]
    identificadores: Optional[Identificador]
    nombre: Nombre
    sexo: Optional[str]
    fecha_nacimiento: Optional[date]
    contacto: Optional[Contacto]
    referencias: Optional[Dict[str,Referencia]] = Field(default=None)
    datos_extra: Optional[Dict[str,DatosExtra]] = Field(default=None)
    estado: Optional[str] = "V"
    metadatos: Optional[Dict[str, Metadata]] = Field(default=None)
    nombre_completo: Optional[str]


class PacienteCreate(PacienteBase):
    pass

class PacienteOut(PacienteBase):
    id: int
    

    model_config = ConfigDict(from_attributes=True)