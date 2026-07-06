from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import get_current_user
from modules.users.models import UserModel
from modules.consultas.schemas import ConsultaListResponse
from modules.consultas.service import (
    consultas_activas_admision_mayores_7_dias as svc_activas_admision_mayores_7_dias,
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
    Sigsa3EspecialidadResponse,
    Sigsa3DxFrecuentesResponse,
)
from .service import (
    pacientes_atendidos as svc_pacientes_atendidos,
    hospitalizacion_infantil as svc_hospitalizacion_infantil,
    promedio_diario as svc_promedio_diario,
    personal_hospital as svc_personal_hospital,
    estudiante_publico as svc_estudiante_publico,
    reingresos as svc_reingresos,
    estadisticas_nacimientos as svc_estadisticas_nacimientos,
    sigsa3_por_especialidad as svc_sigsa3_especialidad,
    sigsa3_dx_frecuentes as svc_sigsa3_dx,
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
    skip: int = Query(0, ge=0, description="Registros a saltar"),
    limit: int = Query(100, ge=1, le=500, description="Máximo de registros"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return svc_personal_hospital(db, desde, hasta, skip, limit)


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


@router.get("/consultas/mayores-a-7-dias", response_model=ConsultaListResponse)
def consultas_mayores_7_dias(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return svc_activas_admision_mayores_7_dias(db, skip=skip, limit=limit)


@router.get("/nacimientos", response_model=NacimientosStatsResponse)
def nacimientos(
    desde: str = Query(..., description="Fecha inicio (YYYY-MM-DD)"),
    hasta: str = Query(..., description="Fecha fin (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return svc_estadisticas_nacimientos(db, desde, hasta)


@router.get("/sigsa3/por-especialidad", response_model=Sigsa3EspecialidadResponse)
def sigsa3_especialidad(
    desde: str = Query(..., description="Fecha inicio (YYYY-MM-DD)"),
    hasta: str = Query(..., description="Fecha fin (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Consulta SIGSA-3 agrupada por especialidad, tipo_consulta y sexo."""
    return svc_sigsa3_especialidad(db, desde, hasta)


@router.get("/sigsa3/dx-frecuentes", response_model=Sigsa3DxFrecuentesResponse)
def sigsa3_dx(
    desde: str = Query(..., description="Fecha inicio (YYYY-MM-DD)"),
    hasta: str = Query(..., description="Fecha fin (YYYY-MM-DD)"),
    top: int = Query(10, ge=1, le=50, description="Cantidad de diagnósticos top por grupo"),
    tipo_consulta: int = Query(None, description="Filtrar por tipo: 1=Primeras, 2=Reconsultas, 3=Emergencias, 4=Interconsultas"),
    especialidad: str = Query(None, description="Filtrar por especialidad médica"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Top diagnósticos más frecuentes por especialidad, tipo_consulta y sexo."""
    return svc_sigsa3_dx(db, desde, hasta, top, tipo_consulta, especialidad)
