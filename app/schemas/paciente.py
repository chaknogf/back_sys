from typing import List, Optional, Union, Dict
from pydantic import BaseModel, ConfigDict, Field, root_validator
from datetime import date

class Nombre(BaseModel):
    primer: str
    segundo: Optional[str] = None
    otro: Optional[str] = None
    apellido_primero: str
    apellido_segundo: Optional[str] = None
    casada: Optional[str] = None

class Contacto(BaseModel):
    direccion: Optional[str] = None
    localidad: Optional[str] = None
    departamento: Optional[str] = None
    municipio: Optional[str] = None
    telefono: Optional[str] = None
    telefono2: Optional[str] = None
    telefono3: Optional[str] = None

class Referencia(BaseModel):
    nombre: str
    parentesco: Optional[str] = None
    telefono: Optional[str] = None

class DatosExtra(BaseModel):
    tipo: str
    valor: str

class Metadata(BaseModel):
    usuario: Optional[str] = None
    registro: Optional[str] = None

class PacienteBase(BaseModel):
    unidad: Optional[int]
    cui: Optional[int] = None
    expediente: Optional[str] = None
    pasaporte: Optional[str] = None
    otro_id: Optional[str] = None
    #identificadores: Optional[Dict[str, Union[str, int]]] = None  # sigue disponible pero opcional
    nombre: Nombre
    sexo: Optional[str]
    fecha_nacimiento: Optional[date]
    contacto: Optional[Contacto] = None
    referencias: Optional[Dict[str, Referencia]] = None
    datos_extra: Optional[Dict[str, DatosExtra]] = None
    estado: Optional[str] = "V"
    metadatos: Optional[Dict[str, Metadata]] = None

class PacienteUpdate(PacienteBase):
    id: Optional[int] = None
    nombre_completo: str = ""

    @root_validator(pre=True)
    def generar_nombre_completo(cls, values):
        nombre = values.get("nombre", {})
        partes = [
            str(nombre.get("primer", "")).strip(),
            str(nombre.get("segundo", "")).strip(),
            str(nombre.get("otro", "")).strip(),
            str(nombre.get("apellido_primero", "")).strip(),
            str(nombre.get("apellido_segundo", "")).strip(),
            str(nombre.get("casada", "")).strip()
        ]
        values["nombre_completo"] = " ".join(p for p in partes if p)
        return values

class PacienteCreate(PacienteBase):
    pass

class PacienteOut(PacienteBase):
    id: int
    
model_config = ConfigDict(from_attributes=True)
    
def dict(self, **kwargs) -> dict:
        original = super().dict(**kwargs)
        # Eliminar claves vacías en el nivel superior
        limpio = {
            k: v for k, v in original.items()
            if v not in (None, "", {}, [])
        }
        return limpio
    
    