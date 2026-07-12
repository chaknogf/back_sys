from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class Cie10Out(BaseModel):
    codigo: str = Field(..., description="Código CIE-10 (ej: A00.0)")
    descripcion: str = Field(..., description="Descripción del diagnóstico")
    nivel: int = Field(..., description="Nivel jerárquico (0=capítulo, 1=grupo, etc.)")
    codigo_padre: Optional[str] = Field(None, description="Código del nivel superior")

    model_config = ConfigDict(from_attributes=True)


class Cie10SearchResponse(BaseModel):
    total: int
    resultados: List[Cie10Out]
    consulta: str = Field(..., description="Término buscado")


class MensajeChat(BaseModel):
    role: str = Field(..., pattern="^(user|assistant|system)$",
                      description="Rol del mensaje: user, assistant o system")
    content: str = Field(..., min_length=1, max_length=2000,
                         description="Contenido del mensaje")


class Cie10ChatRequest(BaseModel):
    mensajes: List[MensajeChat] = Field(..., min_length=1,
                                        description="Historial de la conversación")
    codigos_contexto: Optional[List[str]] = Field(
        None, description="Códigos CIE-10 relevantes para contextualizar"
    )


class Cie10ChatResponse(BaseModel):
    respuesta: str = Field(..., description="Respuesta del asistente")
    codigos_relacionados: List[Cie10Out] = Field(
        default_factory=list, description="Códigos CIE-10 mencionados en la respuesta"
    )
    modelo: str = Field(..., description="Modelo LLM usado")
    generado_en: datetime
