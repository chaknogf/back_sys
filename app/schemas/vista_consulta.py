# app/schemas/vista_consultas.py
"""
Schema para la vista materializada `vista_consultas`.
Ideal para reportes, búsquedas rápidas y exportación.
"""

from typing import Optional, Dict, Any
from datetime import date, time
from pydantic import BaseModel, ConfigDict, Field


class VistaConsultas(BaseModel):
    """
    Representación completa de la vista materializada `vista_consultas`.
    Solo lectura - optimizada para rendimiento.
    """
    # === PACIENTE ===
    id_paciente: int = Field(..., description="ID del paciente")
    expediente: Optional[str] = Field(None, max_length=20)
    cui: Optional[int] = Field(None, ge=100000000, le=9999999999)
    otro_id: Optional[str] = None

    # === NOMBRE COMPLETO (desglosado y compuesto) ===
    nombre: Optional[Dict[str, Any]] = None  # JSON original
    primer_nombre: Optional[str] = None
    segundo_nombre: Optional[str] = None
    otro_nombre: Optional[str] = None
    primer_apellido: Optional[str] = None
    segundo_apellido: Optional[str] = None
    apellido_casada: Optional[str] = None

    # === DATOS DEMOGRÁFICOS ===
    sexo: Optional[str] = Field(None, pattern=r"^(M|F|O)$")
    fecha_nacimiento: Optional[date] = None
    edad: Optional[int] = Field(None, ge=0, le=130, description="Edad calculada automáticamente")

    # === ESTADO ===
    estado: Optional[str] = Field(None, description="Estado del paciente")

    # === CONSULTA ===
    id_consulta: int = Field(..., description="ID de la consulta")
    tipo_consulta: Optional[int] = None
    especialidad: Optional[str] = None
    servicio: Optional[str] = None
    documento: Optional[str] = None
    fecha_consulta: date = Field(..., description="Fecha de la consulta")
    hora_consulta: Optional[time] = None
    ciclo: Optional[Dict[str, Any]] = None
    orden: Optional[int] = None

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        extra="ignore"
    )

    @property
    def nombre_completo(self) -> str:
        partes = [
            self.primer_nombre,
            self.segundo_nombre,
            self.otro_nombre,
            self.primer_apellido,
            self.segundo_apellido,
            self.apellido_casada
        ]
        return " ".join(p.strip() for p in partes if p and p.strip()).upper()


# === Para listas y reportes ===
class VistaConsultasListResponse(BaseModel):
    total: int
    consultas: List[VistaConsultas]
    fecha_generacion: str