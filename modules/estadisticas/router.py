from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import get_current_user
from modules.users.models import UserModel
from modules.consultas.schemas import ConsultaListResponse
from modules.consultas.service import (
    consultas_activas_mayores_30_dias as svc_activas_mayores_30_dias,
    reingresos_consulta_tipo3 as svc_reingresos_tipo3,
)

from .schemas import (
    PacientesAtendidosResponse,
    HospitalizacionInfantilResponse,
    PromedioDiarioResponse,
    PersonalHospitalResponse,
    EstudiantePublicoResponse,
    ReingresoResponse,
    NacimientosStatsResponse,
)
from .service import (
    pacientes_atendidos as svc_pacientes_atendidos,
    hospitalizacion_infantil as svc_hospitalizacion_infantil,
    promedio_diario as svc_promedio_diario,
    personal_hospital as svc_personal_hospital,
    estudiante_publico as svc_estudiante_publico,
    reingresos as svc_reingresos,
    estadisticas_nacimientos as svc_estadisticas_nacimientos,
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


@router.get("/consultas/personal-hospital", response_model=PersonalHospitalResponse)
def personal_hospital(
    desde: str = Query(..., description="Fecha inicio (YYYY-MM-DD)"),
    hasta: str = Query(..., description="Fecha fin (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return svc_personal_hospital(db, desde, hasta)


@router.get("/consultas/estudiante-publico", response_model=EstudiantePublicoResponse)
def estudiante_publico(
    desde: str = Query(..., description="Fecha inicio (YYYY-MM-DD)"),
    hasta: str = Query(..., description="Fecha fin (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return svc_estudiante_publico(db, desde, hasta)


@router.get("/consultas/reingresos", response_model=ReingresoResponse)
def reingresos(
    desde: str = Query(..., description="Fecha inicio (YYYY-MM-DD)"),
    hasta: str = Query(..., description="Fecha fin (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return svc_reingresos(db, desde, hasta)


@router.get("/consultas/reingresos-tipo3", response_model=ConsultaListResponse)
def reingresos_tipo3(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return svc_reingresos_tipo3(db, skip=skip, limit=limit)


@router.get("/consultas/activos-mayores-a-30-dias", response_model=ConsultaListResponse)
def activos_mayores_a_30_dias(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return svc_activas_mayores_30_dias(db, skip=skip, limit=limit)


@router.get("/nacimientos", response_model=NacimientosStatsResponse)
def nacimientos(
    desde: str = Query(..., description="Fecha inicio (YYYY-MM-DD)"),
    hasta: str = Query(..., description="Fecha fin (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return svc_estadisticas_nacimientos(db, desde, hasta)
