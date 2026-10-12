from .router import router
from .models import CatalogoProcedimiento, AreaCuerpoIntervenida, ProceMedico
from .schemas import (
    CatalogoProcedimientoBase, CatalogoProcedimientoCreate,
    CatalogoProcedimientoUpdate, CatalogoProcedimientoOut,
    AreaCuerpoOut,
    ProceMedicoBase, ProceMedicoCreate, ProceMedicoUpdate, ProceMedicoOut,
    ProceMedicoInDB, ProceMedicoResponse, ProcedimientosListResponse
)