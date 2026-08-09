from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class ReglaAgenteBase(BaseModel):
    tipo: str = Field(..., description="sinonimo_entidad|sinonimo_agrupacion|sinonimo_medida")
    clave: str = Field(..., description="Texto o patrón que dispara la regla")
    valor: str = Field(..., description="Entidad/dimensión destino")


class ReglaAgenteCreate(ReglaAgenteBase):
    pass


class ReglaAgenteOut(ReglaAgenteBase):
    id: int
    veces_usado: int = 0
    veces_exito: int = 0
    veces_fracaso: int = 0
    origen: str = "manual"
    usuario: Optional[str] = None
    creado_en: datetime

    model_config = {"from_attributes": True}


class ReglaAgenteList(BaseModel):
    total: int
    items: List[ReglaAgenteOut]


class FeedbackCreate(BaseModel):
    pregunta: str = Field(..., min_length=1)
    respuesta: str = Field(..., min_length=1)
    sql_generado: Optional[str] = None
    correcto: bool
    correccion: Optional[str] = Field(None, description="Corrección sugerida por el usuario")


class FeedbackOut(BaseModel):
    id: int
    pregunta: str
    correcto: bool
    creado_en: datetime

    model_config = {"from_attributes": True}


class RespuestaAgente(BaseModel):
    respuesta: str = Field(..., description="Respuesta en lenguaje natural")
    datos: List[dict] = Field(default_factory=list)
    columnas: List[str] = Field(default_factory=list)
    total_filas: int = 0
    ejecucion_ms: int = 0
    modelo: str = "agente-rule"
    error: Optional[str] = None
    generado_en: datetime = Field(default_factory=datetime.now)