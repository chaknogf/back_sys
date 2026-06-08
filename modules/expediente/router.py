from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import get_current_user
from .service import (
    generar_expediente as generar_exp,
    generar_emergencia as generar_emerg,
    generar_constancia_nacimiento as generar_cn,
    generar_defuncion as generar_def,
    generar_constancia_medica as generar_cm
)
from modules.users.models import UserModel

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
    try:
        expediente = generar_exp(db)
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
    try:
        hoja = generar_emerg(db)
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


@router.post(
    "/constancia_nacimiento",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Generar constancia de nacimiento",
    description="Devuelve un número único para constancia de nacimiento: CN-######"
)
def generar_constancia_nacimiento(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        correlativo = generar_cn(db)
        return {
            "constancia_nacimiento": correlativo,
            "tipo": "constancia_nacimiento",
            "generado_por": current_user.nombre,
            "fecha": __import__("datetime").datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al generar constancia de nacimiento: {str(e)}"
        )


@router.post(
    "/constancia_defuncion",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Generar constancia de defunción",
    description="Devuelve un número único para constancia de defunción: DF-######"
)
def generar_constancia_defuncion(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        correlativo = generar_def(db)
        return {
            "constancia_defuncion": correlativo,
            "tipo": "constancia_defuncion",
            "generado_por": current_user.nombre,
            "fecha": __import__("datetime").datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al generar constancia de defunción: {str(e)}"
        )


@router.post(
    "/constancia_medica",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Generar constancia médica",
    description="Devuelve un número único para constancia médica: CM-######"
)
def generar_constancia_medica(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        correlativo = generar_cm(db)
        return {
            "constancia_medica": correlativo,
            "tipo": "constancia_medica",
            "generado_por": current_user.nombre,
            "fecha": __import__("datetime").datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al generar constancia médica: {str(e)}"
        )
