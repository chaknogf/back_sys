
from typing import Optional, Dict, Any, List, Literal
from datetime import date, datetime, time
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator, field_serializer

class CNBase (BaseModel):
    fecha_registro: Optional[date] = None
    paciente_id: Optional[int] = None
    madre_id: Optional[int] = None
    medico_id: Optional[int] = None
    usuario_id: Optional[int] = None
    