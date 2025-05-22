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
    telefono: Optional[str]
    email: Optional[str]
    municipio: Optional[str]
    direccion: Optional[str]

class Referencia(BaseModel):
    nombre: str
    parentesco: str
    telefono: Optional[str]

class DatosExtra(BaseModel):
    nacionalidad: Optional[str]
    ocupacion: Optional[str]
    idiomas: Optional[str]
    fecha_defuncion: Optional[date]
    otros: Optional[str]
    covid: Optional[Union[dict, str]]  # según cómo manejes esa estructura

class Metadata(BaseModel):
    usuario: Optional[str]
    registro: Optional[str]

class PacienteBase(BaseModel):
    identificadores: List[Identificador]
    nombre: Nombre
    sexo: Optional[str]
    fecha_nacimiento: Optional[date]
    contacto: Optional[Contacto]
    referencias: Optional[List[Referencia]]
    datos_extra: Optional[DatosExtra]
    estado: Optional[str] = "A"
    metadatos: Optional[Metadata]

class PacienteCreate(PacienteBase):
    pass

class PacienteOut(PacienteBase):
    id: int
    

    model_config = ConfigDict(from_attributes=True)