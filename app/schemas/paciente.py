"""
Schemas para pacientes - Sistema Hospitalario Nacional
Totalmente compatible con Pydantic v2, FastAPI, OpenAPI y frontend.
Validaciones flexibles para datos legacy/inconsistentes.
"""

from typing import Optional, Dict, Any, List, Literal
from datetime import date, datetime, time
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator, field_serializer

from app.schemas.common import ConsultaBaseOut


# ===================================================================
# Modelos anidados (reutilizables y limpios)
# ===================================================================
class Nombre(BaseModel):
    primer_nombre: str = Field(..., min_length=1, max_length=50)
    segundo_nombre: Optional[str] = Field(None, max_length=50)
    otro_nombre: Optional[str] = Field(None, max_length=50)
    primer_apellido: str = Field(..., min_length=1, max_length=50)  # Cambiado de 2 a 1
    segundo_apellido: Optional[str] = Field(None, max_length=50)
    apellido_casada: Optional[str] = Field(None, max_length=50)

    @field_validator("primer_nombre", "primer_apellido", mode="before")
    @classmethod
    def limpiar_nombres(cls, v):
        """Limpia espacios en blanco y valida que no esté vacío"""
        if v is None:
            return v
        v = str(v).strip()
        return v if v else None

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
    telefonos: Optional[str] = Field(None, max_length=100)  # Removido el pattern restrictivo

    @field_validator("telefonos", mode="before")
    @classmethod
    def format_telefonos(cls, v):
        """Valida y formatea teléfonos de manera flexible"""
        if not v:
            return None
        
        v = str(v).strip()
        
        # Si está vacío o es solo "0", retornar None
        if not v or v == "0":
            return None
        
        # Remover caracteres no numéricos
        numeros = "".join(c for c in v if c.isdigit())
        
        # Si no hay suficientes dígitos, retornar None
        if len(numeros) < 8:
            return None
        
        # Formatear en bloques de 8
        return "-".join(numeros[i:i + 8] for i in range(0, len(numeros), 8))

    @field_validator("municipio", mode="before")
    @classmethod
    def municipio_a_string(cls, v):
        if v is None:
            return None
        return str(v)


class Referencia(BaseModel):
    nombre: str = Field(..., max_length=100)
    parentesco: Optional[str] = None
    telefono: Optional[str] = Field(None, max_length=20)  # Más flexible
    expediente: Optional[str] = None
    idpersona: Optional[str] = None
    responsable: Optional[bool] = None

    @field_validator("telefono", mode="before")
    @classmethod
    def validar_telefono(cls, v):
        """Valida teléfono de manera flexible"""
        if not v:
            return None
        v = str(v).strip()
        # Solo números y guiones
        return "".join(c for c in v if c.isdigit() or c == "-") or None
    
class MetadataEvento(BaseModel):
    usuario: Optional[str] = None
    registro: Optional[datetime] = None
    accion: Optional[Literal["CREADO", "ACTUALIZADO", "MERGE_PACIENTE", "MERGE_CAMPO_DUPLICADO"]] = None
    expediente_duplicado: Optional[bool] = None,
    detalle: Optional[str] = None
    
    
class Neonatales(BaseModel):
    peso_nacimiento: Optional[str] = None
    edad_gestacional: Optional[str] = None
    parto: Optional[str] = None
    gemelo: Optional[str] = None
    expediente_madre: Optional[str] = None
    extrahositalario: Optional[bool] = False
    hora_nacimiento: Optional[time] = None
    
    @field_serializer('hora_nacimiento')
    def serialize_hora(self, hora: Optional[time], _info):
        """Convierte time a string formato HH:MM:SS"""
        if hora is None:
            return None
        return hora.strftime('%H:%M:%S')


# ===================================================================
# Schema base del paciente
# ===================================================================
class PacienteBase(BaseModel):
    cui: Optional[int] = None
    expediente: Optional[str] = Field(None, max_length=20)
    pasaporte: Optional[str] = Field(None, max_length=20)

    nombre: Nombre 
    sexo: Optional[str] = None
    fecha_nacimiento: Optional[date] = None

    contacto: Optional[Contacto] = None
    referencias: Optional[List[Referencia]] = None
    datos_extra: Optional[Dict[str, Any]] = None
    estado: Optional[str] = Field("V", pattern=r"^(V|F|I|A)$", description="V=Vivo, F=Fallecido, I=Inactivo, A=Activo")
    # metadatos: Optional[List[MetadataEvento]] = None
    
    @field_validator("cui", mode="before")
    @classmethod
    def normalizar_cui(cls, v):
        if v is None or v == "":
            return None
        return int(v) if str(v).isdigit() else None

    @field_validator("expediente", "pasaporte", mode="before")
    @classmethod
    def limpiar_strings(cls, v):
        """Limpia strings opcionales"""
        if not v:
            return None
        v = str(v).strip()
        return v if v else None

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
    cui: Optional[int] = None
    expediente: Optional[str] = None
    pasaporte: Optional[str] = None
    nombre: Optional[Nombre] = None
    sexo: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    contacto: Optional[Contacto] = None
    referencias: Optional[List[Referencia]] = None
    datos_extra: Optional[Dict[str, Any]] = None
    estado: Optional[str] = None
    # metadatos: Optional[List[MetadataEvento]] = None


# ===================================================================
# Respuesta completa al frontend
# ===================================================================
class PacienteOutConsulta(PacienteBase):
    id: int = Field(..., description="ID único en la base de datos")
    nombre_completo: str = Field(..., description="Nombre completo generado automáticamente")
    creado_en: Optional[date] = None
    actualizado_en: Optional[date] = None
   
   
    @model_validator(mode="before")
    @classmethod
    def generar_nombre_completo(cls, data):
        """Genera nombre completo desde el objeto nombre"""
        if isinstance(data, dict):
            nombre_obj = data.get("nombre")
            if nombre_obj:
                # Si es un dict, crear el objeto Nombre
                if isinstance(nombre_obj, dict):
                    try:
                        nombre_instance = Nombre(**nombre_obj)
                        data["nombre_completo"] = nombre_instance.completo
                    except:
                        data["nombre_completo"] = ""
                # Si ya es un objeto Nombre
                elif hasattr(nombre_obj, "completo"):
                    data["nombre_completo"] = nombre_obj.completo
                else:
                    data["nombre_completo"] = ""
        return data

    model_config = ConfigDict(from_attributes=True)

class PacienteOut(PacienteOutConsulta):
    metadatos: Optional[List[MetadataEvento]] = None
   

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
        
        

        
class PacienteCreateDerivado(BaseModel):
    """
    Schema para crear un paciente derivado (hijo/a) a partir de la madre.
    El frontend SOLO envía información propia del recién nacido.
    Todo lo heredado o estructural lo gestiona el backend.
    """
    # =========================
    # Datos obligatorios
    # =========================
    sexo: Literal["M", "F"] = Field(..., description="Sexo del recién nacido")
    fecha_nacimiento: date = Field(..., description="Fecha de nacimiento")
    # =========================
    # Datos clínicos neonatales
    # =========================
    datos_extra: Neonatales = Field(
        ...,
        description="Datos neonatales del recién nacido"
    )
    # =========================
    # Estado inicial
    # =========================
    estado: Optional[Literal["V", "F", "I"]] = "V"

    model_config = {
        "extra": "forbid"
    }
    
class PacientesConConsultas(BaseModel):
    cui: Optional[int] = None
    expediente: Optional[str] = None
    pasaporte: Optional[str] = None
    nombre: Nombre
    sexo: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    datos_extra: Optional[Dict[str, Any]] = None
    consultas: List[ConsultaBaseOut]

    model_config = ConfigDict(from_attributes=True)