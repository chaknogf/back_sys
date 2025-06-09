from pydantic import BaseModel, ConfigDict

class PaisOut(BaseModel):
    id: int
    nombre: str
    codigo_iso3: str

     
    model_config = ConfigDict(from_attributes=True)
    