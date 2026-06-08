from .router import router
from .duplicados_router import router as duplicados_router
from .merge_router import router as merge_router
from .recien_nacido_router import router as recien_nacido_router
from .models import PacienteModel
from .schemas import (
    PacienteCreate, PacienteOut, PacienteUpdate,
    PacienteListResponse, PacienteSimple, PacienteContacto
)
