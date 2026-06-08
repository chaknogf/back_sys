from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date

from core.database import get_db
from core.security import get_current_user
from modules.users.models import UserModel

from .schemas import (
    SerieResponse, ResumenResponse, PiramidePoblacional,
    TopProcedimientos, OcupacionResponse, ReporteFechas,
    PersonalSaludReporte,
)
from .service import (
    resumen_dashboard as svc_resumen,
    consultas_por_dia as svc_consultas_por_dia,
    consultas_por_especialidad as svc_consultas_por_especialidad,
    piramide_poblacional as svc_piramide,
    procedimientos_mas_frecuentes as svc_top_procedimientos,
    ocupacion_hospitalaria as svc_ocupacion,
    reporte_personalizado as svc_reporte,
    personal_salud_reporte as svc_personal_salud,
)

router = APIRouter(prefix="/estadisticas", tags=["Estadísticas y Reportes"])


@router.get("/resumen", response_model=ResumenResponse)
def obtener_resumen(
    fecha: Optional[str] = Query(None, description="Fecha objetivo (YYYY-MM-DD). Por defecto: hoy"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return svc_resumen(db, fecha)


@router.get("/consultas/por-dia", response_model=SerieResponse)
def consultas_por_dia(
    desde: str = Query(..., description="Fecha inicio (YYYY-MM-DD)"),
    hasta: str = Query(..., description="Fecha fin (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return svc_consultas_por_dia(db, desde, hasta)


@router.get("/consultas/por-especialidad", response_model=SerieResponse)
def consultas_por_especialidad(
    desde: Optional[str] = Query(None, description="Fecha inicio opcional (YYYY-MM-DD)"),
    hasta: Optional[str] = Query(None, description="Fecha fin opcional (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return svc_consultas_por_especialidad(db, desde, hasta)


@router.get("/pacientes/piramide", response_model=PiramidePoblacional)
def piramide_poblacional(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return svc_piramide(db)


@router.get("/procedimientos/top", response_model=TopProcedimientos)
def procedimientos_mas_frecuentes(
    desde: Optional[str] = Query(None, description="Fecha inicio (YYYY-MM-DD)"),
    hasta: Optional[str] = Query(None, description="Fecha fin (YYYY-MM-DD)"),
    limite: int = Query(10, ge=1, le=50, description="Cantidad de procedimientos a retornar"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return svc_top_procedimientos(db, desde, hasta, limite)


@router.get("/ocupacion", response_model=OcupacionResponse)
def ocupacion_hospitalaria(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return svc_ocupacion(db)


@router.get("/reporte", response_model=ReporteFechas)
def reporte_personalizado(
    tabla: str = Query(..., description="Nombre de la tabla"),
    columnas: str = Query(..., description="Columnas separadas por coma (ej: id,nombre,sexo)"),
    col_fecha: Optional[str] = Query(None, description="Columna de fecha para filtrar por rango"),
    desde: Optional[str] = Query(None, description="Fecha inicio (YYYY-MM-DD)"),
    hasta: Optional[str] = Query(None, description="Fecha fin (YYYY-MM-DD)"),
    filtro_col: Optional[str] = Query(None, description="Columna para filtro exacto"),
    filtro_val: Optional[str] = Query(None, description="Valor del filtro exacto"),
    limite: int = Query(500, ge=1, le=5000),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    cols_list = [c.strip() for c in columnas.split(",") if c.strip()]
    filtros = {filtro_col: filtro_val} if filtro_col and filtro_val else None
    return svc_reporte(db, tabla, cols_list, filtros, desde, hasta, col_fecha, limite)


@router.get("/personal-salud", response_model=PersonalSaludReporte)
def reporte_personal_salud(
    desde: str = Query(..., description="Fecha inicio (YYYY-MM-DD)"),
    hasta: str = Query(..., description="Fecha fin (YYYY-MM-DD)"),
    filtro: str = Query(
        "personal_hospital", description="Indicador a filtrar (por ahora solo personal_hospital)"
    ),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return svc_personal_salud(db, desde, hasta, filtro)
