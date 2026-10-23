"""Endpoints autenticados que generan correlativos clínicos y registran su emisor.

Cada endpoint es el límite transaccional: el servicio solo incrementa el
contador con flush(); aquí se confirma (commit) o se revierte (rollback).
"""

import logging
from datetime import datetime
from typing import Callable

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.config import APP_TIMEZONE
from core.database import get_db
from core.security import get_current_user
from modules.users.models import UserModel
from .service import (
    generar_expediente as generar_exp,
    generar_emergencia as generar_emerg,
    generar_constancia_nacimiento as generar_cn,
    generar_defuncion as generar_def,
    generar_constancia_medica as generar_cm,
)

logger = logging.getLogger("expediente.router")

router = APIRouter(prefix="/correlativos", tags=["Correlativos Clínicos"])


def _emitir(db: Session, generador: Callable[[Session], str], etiqueta: str) -> str:
    """Genera y confirma un correlativo; ante fallo revierte y no expone detalles."""
    try:
        valor = generador(db)
        db.commit()
        return valor
    except Exception:
        db.rollback()
        logger.exception("Error generando correlativo: %s", etiqueta)
        raise HTTPException(
            status_code=500,
            detail=f"Error al generar {etiqueta}",
        )


def _respuesta(clave: str, valor: str, tipo: str, usuario: UserModel) -> dict:
    return {
        clave: valor,
        "tipo": tipo,
        "generado_por": usuario.nombre,
        "fecha": datetime.now(APP_TIMEZONE).isoformat(),
    }


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
    expediente = _emitir(db, generar_exp, "expediente")
    return _respuesta("expediente", expediente, "general", current_user)


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
    hoja = _emitir(db, generar_emerg, "hoja de emergencia")
    return _respuesta("hoja_emergencia", hoja, "emergencia", current_user)


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
    correlativo = _emitir(db, generar_cn, "constancia de nacimiento")
    return _respuesta("constancia_nacimiento", correlativo, "constancia_nacimiento", current_user)


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
    correlativo = _emitir(db, generar_def, "constancia de defunción")
    return _respuesta("constancia_defuncion", correlativo, "constancia_defuncion", current_user)


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
    correlativo = _emitir(db, generar_cm, "constancia médica")
    return _respuesta("constancia_medica", correlativo, "constancia_medica", current_user)
