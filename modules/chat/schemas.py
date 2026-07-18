from typing import List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime


class MensajeChat(BaseModel):
    role: str = Field(
        ...,
        pattern="^(user|assistant)$",
        description="Rol del mensaje: user o assistant",
    )
    content: str = Field(
        ..., min_length=1, max_length=5000,
        description="Contenido del mensaje",
    )


class ChatRequest(BaseModel):
    mensajes: List[MensajeChat] = Field(
        ..., min_length=1,
        description="Historial de la conversación",
    )
    max_filas: int = Field(
        100, ge=1, le=1000,
        description="Máximo de filas a retornar",
    )
    tablas: Optional[List[str]] = Field(
        None,
        description="Limitar a tablas específicas (opcional)",
    )


class ColumnaInfo(BaseModel):
    nombre: str
    tipo: str
    nullable: bool
    descripcion: str = ""


class TablaInfo(BaseModel):
    nombre: str
    columnas: List[ColumnaInfo] = Field(
        default_factory=list,
        description="Columnas de la tabla",
    )
    filas_aprox: int = 0
    descripcion: str = ""


class ChatResponse(BaseModel):
    respuesta: str = Field(
        ..., description="Respuesta en lenguaje natural",
    )
    datos: List[dict] = Field(
        default_factory=list,
        description="Filas resultado de la consulta",
    )
    columnas: List[str] = Field(
        default_factory=list,
        description="Nombres de columnas del resultado",
    )
    sql_generado: Optional[str] = Field(
        None, description="SQL ejecutado",
    )
    total_filas: int = Field(0, description="Número de filas")
    ejecucion_ms: int = Field(0, description="Tiempo de ejecución en ms")
    modelo: str = Field("", description="Modelo LLM usado")
    error: Optional[str] = Field(None, description="Error si ocurrió")
    generado_en: datetime = Field(default_factory=lambda: datetime.now())
