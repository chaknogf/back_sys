from pydantic import BaseModel

class TotalesResponse(BaseModel):
    entidad: str
    total: int