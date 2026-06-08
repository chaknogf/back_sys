from .router import router
from .models import Procedimiento, ProceMedico
from .schemas import (
    ProcedimientoBase, ProcedimientoCreate, ProcedimientoUpdate, ProcedimientoOut,
    ProceMedicoBase, ProceMedicoCreate, ProceMedicoUpdate, ProceMedicoOut,
    ProceMedicoInDB, ProceMedicoResponse, ProcedimientosListResponse
)
