# app/schemas/pacientes.py
"""
Schemas para pacientes - Sistema Hospitalario Nacional
Totalmente compatible con Pydantic v2, FastAPI, OpenAPI y frontend.
"""

from typing import Optional, Dict, Any, List
from datetime import date
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


# ===================================================================
# Modelos anidados (reutilizables y limpios)
# ===================================================================
class Nombre(BaseModel):
    primer_nombre: str = Field(..., min_length=2, max_length=50)
    segundo_nombre: Optional[str] = Field(None, max_length=50)
    otro_nombre: Optional[str] = Field(None, max_length=50)
    primer_apellido: str = Field(..., min_length=2, max_length=50)
    segundo_apellido: Optional[str] = Field(None, max_length=50)
    apellido_casada: Optional[str] = Field(None, max_length=50)

    @property
    def completo(self) -> str:
        partes = [
            self.primer_nombre,
            self.segundo_nombre,
            self.otro_nombre,
            self.primer_apellido,
            self.segundo_apellido,
            self.apellido_casada
        ]
        return " ".join(p.strip() for p in partes if p and p.strip()).upper()


class Contacto(BaseModel):
    domicilio: Optional[str] = Field(None, max_length=200)
    vecindad: Optional[str] = None
    municipio: Optional[str] = None
    telefonos: Optional[str] = Field(None, pattern=r"^\d{8,30}$")
    
    @field_validator("telefonos", mode="before")
    @classmethod
    def format_telefonos(cls, v: str) -> str:
        if not v:
            return v
        # Remove any existing dashes
        v = v.replace("-", "")
        # Add dash every 8 digits
        return "-".join(v[i:i+8] for i in range(0, len(v), 8))


class Referencia(BaseModel):
    nombre: str = Field(..., max_length=100)
    parentesco: Optional[str] = None
    telefono: Optional[str] = Field(None, pattern=r"^\d{8,15}$")


# ===================================================================
# Schema base del paciente
# ===================================================================
class PacienteBase(BaseModel):
    # unidad: Optional[int] = Field(None, ge=1, description="ID de la unidad de salud")
    cui: Optional[int] = Field(None, ge=100000000, le=999999999, description="CUI del paciente")
    expediente: Optional[str] = Field(None, max_length=20)
    pasaporte: Optional[str] = Field(None, max_length=20)
    # otro_id: Optional[str] = Field(None, max_length=30)

    nombre: Nombre
    sexo: Optional[str] = None
    fecha_nacimiento: Optional[date] = None

    contacto: Optional[Contacto] = None
    referencias: Optional[List[Referencia]] = None
    datos_extra: Optional[Dict[str, Any]] = None
    estado: Optional[str] = Field("A", pattern=r"^(A|I|V)$", description="A=Activo, I=Inactivo, V=Fallecido")
    metadatos: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        extra="ignore"
    )


# ===================================================================
# Para crear paciente
# ===================================================================
class PacienteCreate(PacienteBase):
    nombre: Nombre  # Obligatorio
    cui: Optional[int] = None
    expediente: Optional[str] = None


# ===================================================================
# Para actualizar (parcial)
# ===================================================================
class PacienteUpdate(BaseModel):
    # unidad: Optional[int] = None
    cui: Optional[int] = None
    expediente: Optional[str] = None
    pasaporte: Optional[str] = None
    # otro_id: Optional[str] = None
    nombre: Optional[Nombre] = None
    sexo: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    contacto: Optional[Contacto] = None
    referencias: Optional[List[Referencia]] = None
    datos_extra: Optional[Dict[str, Any]] = None
    estado: Optional[str] = None
    metadatos: Optional[Dict[str, Any]] = None


# ===================================================================
# Respuesta completa al frontend
# ===================================================================
class PacienteOut(PacienteBase):
    id: int = Field(..., description="ID único en la base de datos")
    nombre_completo: str = Field(..., description="Nombre completo generado automáticamente")
    creado_en: Optional[date] = None
    actualizado_en: Optional[date] = None

    @field_validator("nombre_completo", mode="before")
    @classmethod
    def generar_nombre_completo(cls, v: Any, values: Any) -> str:
        nombre = values.data.get("nombre")
        if not nombre:
            return ""
        return nombre.completo

    model_config = ConfigDict(from_attributes=True)


# ===================================================================
# Lista de pacientes (paginación)
# ===================================================================
class PacienteListResponse(BaseModel):
    total: int
    pacientes: List[PacienteOut]

    model_config = ConfigDict(from_attributes=True)


# ===================================================================
# Búsqueda rápida para autocomplete
# ===================================================================
class PacienteSimple(BaseModel):
    id: int
    cui: Optional[int] = None
    expediente: Optional[str] = None
    nombre_completo: str
    fecha_nacimiento: Optional[date] = None

    @staticmethod
    def from_orm(paciente) -> "PacienteSimple":
        return PacienteSimple(
            id=paciente.id,
            cui=paciente.cui,
            expediente=paciente.expediente,
            nombre_completo=paciente.nombre_completo or "",
            fecha_nacimiento=paciente.fecha_nacimiento
        )