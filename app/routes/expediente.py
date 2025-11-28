# app/routes/correlativos.py
"""
Router para generación segura de correlativos clínicos
- Expediente general (por año + secuencial)
- Hoja de emergencia (correlativo independiente)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.utils.expediente import generar_expediente, generar_emergencia
from app.database.security import get_current_user
from app.models.user import UserModel

router = APIRouter(prefix="/correlativos", tags=["Correlativos Clínicos"])


@router.post(
    "/expediente",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Generar nuevo expediente anual",
    description="Devuelve un expediente único en formato: EXP-YYYY-######"
)
def generar_nuevo_expediente(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Genera un expediente único para pacientes nuevos.
    Formato: EXP-2025-000001
    """
    try:
        expediente = generar_expediente(db)
        return {
            "expediente": expediente,
            "tipo": "general",
            "generado_por": current_user.nombre,
            "fecha": __import__("datetime").datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al generar expediente: {str(e)}"
        )


@router.post(
    "/emergencia",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Generar hoja de emergencia",
    description="Devuelve un número único para hoja de emergencia: EMERG-######"
)
def generar_hoja_emergencia(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Genera un correlativo único para emergencias.
    Formato: EMERG-000001
    """
    try:
        hoja = generar_emergencia(db)
        return {
            "hoja_emergencia": hoja,
            "tipo": "emergencia",
            "generado_por": current_user.nombre,
            "fecha": __import__("datetime").datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al generar hoja de emergencia: {str(e)}"
        )