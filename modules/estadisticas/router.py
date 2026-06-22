from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import get_current_user
from modules.users.models import UserModel

from .schemas import (
    PacientesAtendidosResponse,
    HospitalizacionInfantilResponse,
    PromedioDiarioResponse,
)
from .service import (
    pacientes_atendidos as svc_pacientes_atendidos,
    hospitalizacion_infantil as svc_hospitalizacion_infantil,
    promedio_diario as svc_promedio_diario,
)

router = APIRouter(prefix="/estadisticas", tags=["Estadísticas y Reportes"])


@router.get("/consultas/pacientesAtendidos", response_model=PacientesAtendidosResponse)
def pacientes_atendidos(
    desde: str = Query(..., description="Fecha inicio (YYYY-MM-DD)"),
    hasta: str = Query(..., description="Fecha fin (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return svc_pacientes_atendidos(db, desde, hasta)


@router.get("/consultas/hospitalizacion-infantil", response_model=HospitalizacionInfantilResponse)
def hospitalizacion_infantil(
    desde: str = Query(..., description="Fecha inicio (YYYY-MM-DD)"),
    hasta: str = Query(..., description="Fecha fin (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return svc_hospitalizacion_infantil(db, desde, hasta)


@router.get("/consultas/promedioDiario", response_model=PromedioDiarioResponse)
def promedio_diario(
    desde: str = Query(..., description="Fecha inicio (YYYY-MM-DD)"),
    hasta: str = Query(..., description="Fecha fin (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return svc_promedio_diario(db, desde, hasta)
