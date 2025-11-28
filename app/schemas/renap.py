# app/schemas/renap.py
"""
Schemas para integración con RENAP Guatemala.
Usado en búsqueda por CUI y validación de identidad.
"""

from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field, validator
from datetime import date


class PersonaRenap(BaseModel):
    """
    Datos devueltos por el servicio RENAP.
    Los campos vienen en MAYÚSCULAS según el estándar oficial.
    """
    CUI: str = Field(
        ..., 
        pattern=r"^\d{13}$",
        description="CUI de 13 dígitos (sin guiones ni espacios)"
    )
    PRIMER_NOMBRE: str = Field(..., max_length=50)
    SEGUNDO_NOMBRE: Optional[str] = Field(None, max_length=50)
    TERCER_NOMBRE: Optional[str] = Field(None, max_length=50)
    PRIMER_APELLIDO: str = Field(..., max_length=50)
    SEGUNDO_APELLIDO: Optional[str] = Field(None, max_length=50)
    APELLIDO_CASADA: Optional[str] = Field(None, max_length=50)
    SEXO: str = Field(..., pattern=r"^(M|F)$", description="M=Masculino, F=Femenino")
    ESTADO_CIVIL: Optional[str] = Field(None, description="Ej: SOLTERO, CASADO, VIUDO")
    FECHA_NACIMIENTO: str = Field(
        ..., 
        description="Formato YYYY-MM-DD o DD/MM/YYYY según el servicio"
    )

    @validator("FECHA_NACIMIENTO", pre=True)
    def parsear_fecha(cls, v):
        if isinstance(v, date):
            return v.isoformat()
        if isinstance(v, str):
            # Acepta ambos formatos comunes
            for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
                try:
                    return date.strptime(v, fmt).isoformat()
                except ValueError:
                    continue
        return v  # si no se puede parsear, devolver tal cual

    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore"
    )


class RespuestaRenap(BaseModel):
    """
    Respuesta estandarizada del servicio RENAP.
    """
    error: bool = Field(False, description="True si hubo error en la consulta")
    mensaje: str = Field(..., description="Mensaje descriptivo del resultado")
    resultado: Optional[List[PersonaRenap]] = Field(
        None, 
        description="Lista de personas encontradas (normalmente 1)"
    )
    solicitudes_restantes: Optional[int] = Field(
        None, 
        ge=0,
        description="Cuántas consultas te quedan en el día (límite RENAP)"
    )

    model_config = ConfigDict(from_attributes=True)


# ===================================================================
# Schema para respuesta normalizada al frontend (opcional pero ÉPICO)
# ===================================================================
class PersonaNormalizada(BaseModel):
    """Versión limpia y amigable para tu frontend"""
    cui: str
    nombre_completo: str
    fecha_nacimiento: date
    sexo: str

    @classmethod
    def from_renap(cls, persona: PersonaRenap) -> "PersonaNormalizada":
        nombre_parts = [
            persona.PRIMER_NOMBRE,
            persona.SEGUNDO_NOMBRE,
            persona.TERCER_NOMBRE,
            persona.PRIMER_APELLIDO,
            persona.SEGUNDO_APELLIDO,
            persona.APELLIDO_CASADA,
        ]
        nombre_completo = " ".join(p for p in nombre_parts if p).strip()
        
        return cls(
            cui=persona.CUI,
            nombre_completo=nombre_completo,
            fecha_nacimiento=date.fromisoformat(persona.FECHA_NACIMIENTO.split("T")[0]),
            sexo="Masculino" if persona.SEXO == "M" else "Femenino"
        )