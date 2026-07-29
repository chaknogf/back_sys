from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class EspecialidadCreate(BaseModel):
    nombre: str = Field(..., max_length=100)
    abreviatura: Optional[str] = Field(None, max_length=10)


class EspecialidadUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=100)
    abreviatura: Optional[str] = Field(None, max_length=10)


class EspecialidadOut(BaseModel):
    id: int
    nombre: str
    abreviatura: Optional[str] = None
    codigo: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
