# app/routes/totales.py
"""
Dashboard de indicadores clave (KPIs) en tiempo real
Usa vista materializada `vista_totales` para máxima velocidad
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.database.db import get_db
from app.schemas.totales import TotalesResponse, TotalesItem
from app.database.security import get_current_user
from app.models.user import UserModel
from datetime import datetime


router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/totales",
    response_model=TotalesResponse,
    summary="Indicadores clave del hospital",
    description="""
    KPIs en tiempo real:
    - Pacientes activos
    - Consultas del día
    - Emergencias atendidas
    - Usuarios conectados
    - Camas ocupadas, etc.
    
    Usa vista materializada → respuesta en < 30ms
    """
)
def obtener_totales(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Devuelve todos los totales desde la vista materializada `vista_totales`
    """
    from sqlalchemy import text

    try:
        query = text("""
            SELECT 
                entidad,
                total,
                icono,
                color
            FROM vista_totales 
            ORDER BY orden;
        """)
        
        resultado = db.execute(query).fetchall()

        totales = [
            TotalesItem(
                entidad=row.entidad,
                total=row.total,
                icono=row.icono or "bar-chart",
                color=row.color or "blue"
            )
            for row in resultado
        ]

        return TotalesResponse(
            totales=totales,
            generado_en=datetime.now().isoformat()
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener indicadores del dashboard"
        )