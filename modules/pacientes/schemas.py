"""
Schemas para pacientes - Sistema Hospitalario Nacional
Totalmente compatible con Pydantic v2, FastAPI, OpenAPI y frontend.
Validaciones flexibles para datos legacy/inconsistentes.
"""

from typing import Optional, Dict, Any, List, Literal
from datetime import date, datetime, time
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator, field_serializer

from modules.common.schemas import ConsultaBaseOut


# ===================================================================
# Modelos anidados (reutilizables y limpios)
# ===================================================================
class Nombre(BaseModel):
    primer_nombre: str = Field(..., min_length=1, max_length=50)
    segundo_nombre: Optional[str] = Field(None, max_length=50)
    otro_nombre: Optional[str] = Field(None, max_length=50)
    primer_apellido: Optional[str] = Field(None, max_length=50)
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
        ]
        base = " ".join(p.strip() for p in partes if p and p.strip())
        if self.apellido_casada:
            casada = self.apellido_casada.strip()
            if not casada.lower().startswith("de "):
                casada = f"de {casada}"
            base += f" {casada}"
        return base.upper()


class Contacto(BaseModel):
    domicilio: Optional[str] = Field(None, max_length=200)
    vecindad: Optional[str] = None
    municipio: Optional[str] = None
    telefonos: Optional[str] = Field(None, max_length=100)

    @field_validator("telefonos", mode="before")
    @classmethod
    def format_telefonos(cls, v):
        """Valida y formatea teléfonos de manera flexible"""
        if not v:
            return None

        v = str(v).strip()

        if not v or v == "0":
            return None

        numeros = "".join(c for c in v if c.isdigit())

        if len(numeros) < 8:
            return None

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
    telefono: Optional[str] = Field(None, max_length=20)
    expediente: Optional[str] = None
    idpersona: Optional[str] = None
    responsable: Optional[bool] = None
    acompanante: Optional[bool] = None

    @field_validator("telefono", mode="before")
    @classmethod
    def validar_telefono(cls, v):
        """Valida teléfono de manera flexible"""
        if not v:
            return None
        v = str(v).strip()
        return "".join(c for c in v if c.isdigit() or c == "-") or None

class MetadataEvento(BaseModel):
    usuario: Optional[str] = None
    registro: Optional[datetime] = None
    accion: Optional[Literal["CREADO", "ACTUALIZADO", "MERGE_PACIENTE"]] = None
    expediente_duplicado: Optional[bool] = None,
    detalle: Optional[str] = None

class Neonatales(BaseModel):
    peso_nacimiento: Optional[str] = None
    edad_gestacional: Optional[str] = None
    tipo_parto: Optional[str] = None
    clase_parto: Optional[str] = None
    gemelo: Optional[str] = None
    expediente_madre: Optional[str] = None
    id_madre: Optional[str] = None
    id_medico: Optional[int] = None
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
    pasaporte: Optional[str] = Field(None, max_length=50)

    nombre: Nombre
    sexo: Optional[str] = None
    fecha_nacimiento: Optional[date] = None

    contacto: Optional[Contacto] = None
    referencias: Optional[List[Referencia]] = None
    datos_extra: Optional[Dict[str, Any]] = None
    idioma_id: Optional[int] = None
    pueblo_id: Optional[int] = None
    nacionalidad: Optional[str] = None
    lugar_nacimiento: Optional[str] = None
    estado: Optional[str] = Field("V", pattern=r"^(V|F|I|A)$", description="V=Vivo, F=Fallecido, I=Inactivo, A=Activo")

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

class PacienteSchema(PacienteBase):
    id: int
model_config = ConfigDict(from_attributes=True)

# ===================================================================
# Para crear paciente
# ===================================================================
class PacienteCreate(PacienteBase):
    nombre: Nombre
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
    idioma_id: Optional[int] = None
    pueblo_id: Optional[int] = None
    nacionalidad: Optional[str] = None
    lugar_nacimiento: Optional[str] = None
    estado: Optional[str] = None


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
    def socioeconomicos_desde_columnas(cls, data):
        """Inyecta datos socioeconomicos y demograficos desde columnas → datos_extra"""
        extra = None
        if hasattr(data, 'datos_extra'):
            extra = data.datos_extra or {}
        elif isinstance(data, dict):
            extra = data.get('datos_extra') or {}

        if extra is None:
            return data

        socio = {}
        for col, key in [('discapacidad', 'discapacidad'), ('educacion', 'educacion'),
                         ('estado_civil', 'estado_civil'), ('es_estudiante_publico', 'estudiante_publico'),
                         ('ocupacion', 'ocupacion'), ('es_personal_hospital', 'personal_hospital')]:
            if hasattr(data, col):
                val = getattr(data, col)
            elif isinstance(data, dict):
                val = data.get(col)
            else:
                continue
            if val is not None:
                socio[key] = val

        if socio:
            # Preserve fields that only live in JSONB when exposing normalized
            # column values in the API response.
            extra['socioeconomicos'] = {
                **(extra.get('socioeconomicos') or {}),
                **socio,
            }

        demo = {}
        for col, key in [('idioma_id', 'idioma'), ('pueblo_id', 'pueblo'),
                         ('nacionalidad', 'nacionalidad'), ('lugar_nacimiento', 'lugar_nacimiento')]:
            if hasattr(data, col):
                val = getattr(data, col)
            elif isinstance(data, dict):
                val = data.get(col)
            else:
                continue
            if val is not None:
                demo[key] = val

        if demo:
            # ``vecindad`` has no dedicated column. Replacing this object with
            # only normalized columns made it disappear from the response and
            # subsequent edits then persisted it as null.
            extra['demograficos'] = {
                **(extra.get('demograficos') or {}),
                **demo,
            }

        if isinstance(data, dict):
            data['datos_extra'] = extra
        else:
            data.datos_extra = extra
        return data

    @model_validator(mode="before")
    @classmethod
    def generar_nombre_completo(cls, data):
        """Genera nombre completo desde el objeto nombre"""
        if isinstance(data, dict):
            nombre_obj = data.get("nombre")
            if nombre_obj:
                if isinstance(nombre_obj, dict):
                    try:
                        nombre_instance = Nombre(**nombre_obj)
                        data["nombre_completo"] = nombre_instance.completo
                    except:
                        data["nombre_completo"] = ""
                elif hasattr(nombre_obj, "completo"):
                    data["nombre_completo"] = nombre_obj.completo
                else:
                    data["nombre_completo"] = ""
        else:
            nombre_obj = getattr(data, "nombre", None)
            if nombre_obj and hasattr(nombre_obj, "completo"):
                data.nombre_completo = nombre_obj.completo
        return data

    model_config = ConfigDict(from_attributes=True)

class PacienteOut(PacienteOutConsulta):
    metadatos: Optional[List[MetadataEvento]] = None


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


class PacientesResumen(BaseModel):
    id: int
    cui: Optional[int] = None
    expediente: Optional[str] = None
    pasaporte: Optional[str] = None
    nombre: Nombre
    nombre_completo: Optional[str] = None
    sexo: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    estado: Optional[str] = None
    defuncion: Optional[str] = None
    personal_hospital: Optional[str] = None
    ultima_consulta: Optional[date] = None

    @model_validator(mode="before")
    @classmethod
    def extraer_defuncion_nombre(cls, data):
        if not isinstance(data, dict):
            if hasattr(data, "datos_extra"):
                d = {f: getattr(data, f, None) for f in cls.model_fields}
                ph_col = getattr(data, 'es_personal_hospital', None)
                if ph_col in ("S", "N"):
                    d["personal_hospital"] = ph_col
                elif ph_col is None:
                    extras = data.datos_extra
                    if extras:
                        d["defuncion"] = extras.get("defuncion")
                        ph = extras.get("socioeconomicos", {}).get("personal_hospital")
                        if ph is True or ph == "S":
                            d["personal_hospital"] = "S"
                        elif ph is False or ph == "N":
                            d["personal_hospital"] = "N"
                        else:
                            d["personal_hospital"] = None
                nombre_obj = data.nombre
                if not d.get("nombre_completo") and nombre_obj:
                    if isinstance(nombre_obj, dict):
                        try:
                            d["nombre_completo"] = Nombre(**nombre_obj).completo
                        except Exception:
                            pass
                    elif hasattr(nombre_obj, "completo"):
                        d["nombre_completo"] = nombre_obj.completo
                return d
            return data
        if "datos_extra" in data and data["datos_extra"]:
            extras = data["datos_extra"]
            data["defuncion"] = extras.get("defuncion")
            ph_col = data.get("es_personal_hospital")
            if ph_col in ("S", "N"):
                data["personal_hospital"] = ph_col
            else:
                ph = extras.get("socioeconomicos", {}).get("personal_hospital")
                if ph is True or ph == "S":
                    data["personal_hospital"] = "S"
                elif ph is False or ph == "N":
                    data["personal_hospital"] = "N"
                else:
                    data["personal_hospital"] = None
        if not data.get("nombre_completo") and data.get("nombre"):
            nombre_obj = data["nombre"]
            if isinstance(nombre_obj, dict):
                try:
                    nombre_instance = Nombre(**nombre_obj)
                    data["nombre_completo"] = nombre_instance.completo
                except Exception:
                    pass
            elif hasattr(nombre_obj, "completo"):
                data["nombre_completo"] = nombre_obj.completo
        return data

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        extra="ignore"
    )

# ===================================================================
# Lista de pacientes (paginación)
# ===================================================================
class PacienteListResponse(BaseModel):
    total: int
    pacientes: List[PacientesResumen]

    model_config = ConfigDict(from_attributes=True)


class MadreHijoItem(BaseModel):
    sexo: Literal["M", "F"] = Field(..., description="Sexo del recién nacido")
    datos_extra: Neonatales = Field(
        ...,
        description="Datos neonatales del recién nacido"
    )


class PacienteCreateDerivado(BaseModel):
    """
    Schema para crear pacientes derivados (hijos/as) a partir de la madre.
    El frontend SOLO envía información propia del recién nacido.
    Todo lo heredado o estructural lo gestiona el backend.
    """
    fecha_nacimiento: date = Field(..., description="Fecha de nacimiento")
    hijos: list[MadreHijoItem] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="Lista de recién nacidos (1=simple, 2=gemelar, 3=triple, etc.)"
    )
    estado: Optional[Literal["V", "F", "I"]] = "V"

    model_config = {
        "extra": "forbid"
    }


class MadreHijoResponse(BaseModel):
    pacientes: list[PacienteOut]
    total: int

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


class PacienteConsultaBase(BaseModel):
    id: int
    cui: Optional[int] = None
    expediente: Optional[str] = Field(None, max_length=20)
    pasaporte: Optional[str] = Field(None, max_length=50)
    nombre: Nombre
    sexo: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    contacto: Optional[Contacto] = None
    referencias: Optional[List[Referencia]] = None
    estado: Optional[str] = Field("V", pattern=r"^(V|F|I|A)$", description="V=Vivo, F=Fallecido, I=Inactivo, A=Activo")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        extra="ignore"
    )


class PacienteNacimientoConstancia(BaseModel):
    id: int
    cui: Optional[int] = None
    expediente: Optional[str] = Field(None, max_length=20)
    pasaporte: Optional[str] = Field(None, max_length=50)
    nombre: Nombre
    sexo: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    referencias: Optional[List[Referencia]] = None
    datos_extra: Optional[Dict[str, Any]] = None

    @field_validator('referencias')
    @classmethod
    def filtrar_madre(cls, value):
        if not value:
            return value
        return [r for r in value if r.parentesco == 'madre']


    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        extra="ignore"
    )


class PacientesNombre(BaseModel):
    id: int
    nombre: Nombre
    nombre_completo: Optional[str] = None
    expediente: Optional[str] = Field(None, max_length=20)
    sexo: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    contacto: Optional[Contacto] = None
    defuncion: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def extraer_defuncion_nombre(cls, data):
        if isinstance(data, dict):
            if "datos_extra" in data and data["datos_extra"]:
                data["defuncion"] = data["datos_extra"].get("defuncion")
            if not data.get("nombre_completo") and data.get("nombre"):
                nombre_obj = data["nombre"]
                if isinstance(nombre_obj, dict):
                    try:
                        nombre_instance = Nombre(**nombre_obj)
                        data["nombre_completo"] = nombre_instance.completo
                    except Exception:
                        pass
                elif hasattr(nombre_obj, "completo"):
                    data["nombre_completo"] = nombre_obj.completo
            return data
        return data

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        extra="ignore"
    )

class PacienteContacto(BaseModel):
    id: int
    nombre: Optional[Nombre] = None
    nombre_completo: Optional[str] = None
    sexo: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    expediente: Optional[str] = Field(None, max_length=20)
    contacto: Optional[Contacto] = None
    defuncion: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def extraer_defuncion_nombre(cls, data):
        if isinstance(data, dict):
            if "datos_extra" in data and data["datos_extra"]:
                data["defuncion"] = data["datos_extra"].get("defuncion")
            if not data.get("nombre_completo") and data.get("nombre"):
                nombre_obj = data["nombre"]
                if isinstance(nombre_obj, dict):
                    try:
                        nombre_instance = Nombre(**nombre_obj)
                        data["nombre_completo"] = nombre_instance.completo
                    except Exception:
                        pass
                elif hasattr(nombre_obj, "completo"):
                    data["nombre_completo"] = nombre_obj.completo
            return data
        return data

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        extra="ignore"
    )
