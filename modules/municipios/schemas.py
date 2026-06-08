from typing import List
from pydantic import BaseModel, ConfigDict, Field


class MunicipioSchema(BaseModel):
    codigo: str = Field(
        ..., 
        max_length=4,
        pattern=r"^\d{4}$",
        description="Código RENAP de 4 dígitos (ej: 0101 para Guatemala)"
    )
    vecindad: str = Field(
        ..., 
        max_length=150,
        description="Nombre de la vecindad o aldea (si aplica)"
    )
    municipio: str = Field(
        ..., 
        max_length=50,
        description="Nombre oficial del municipio"
    )
    departamento: str = Field(
        ..., 
        max_length=50,
        description="Nombre del departamento al que pertenece"
    )

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class MunicipioListResponse(BaseModel):
    total: int = Field(..., ge=0, description="Total de municipios encontrados")
    municipios: List[MunicipioSchema]

    model_config = ConfigDict(from_attributes=True)


class MunicipioSimple(BaseModel):
    codigo: str = Field(..., description="01001")
    label: str = Field(..., description="Guatemala, Guatemala")

    @staticmethod
    def from_orm(municipio) -> "MunicipioSimple":
        return MunicipioSimple(
            codigo=municipio.codigo,
            label=f"{municipio.municipio}, {municipio.departamento}"
        )
        

class DepartamentoOut(BaseModel):
    codigo: str
    departamento: str

    model_config = {
        "from_attributes": True
    }
