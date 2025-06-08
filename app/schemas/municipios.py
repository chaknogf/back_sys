from pydantic import BaseModel, ConfigDict

class MunicipioSchema(BaseModel):
    codigo: str
    vecindad: str
    municipio: str
    departamento: str
    
    model_config = ConfigDict(from_attributes=True)
    