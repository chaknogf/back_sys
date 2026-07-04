import logging
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from core.database import get_db
from core.security import get_current_user
from modules.users.models import UserModel
from modules.totales.service import get_totales

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/totales", tags=["totales"])


@router.get(
    "/",
    summary="Indicadores clave del hospital",
    description="KPIs en tiempo real o de una fecha específica.",
)
def obtener_totales(
    fecha: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return get_totales(db, fecha)
