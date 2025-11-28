# app/routes/renap.py
"""
Integración oficial con RENAP Guatemala
- Búsqueda por CUI (prioritario)
- Búsqueda por nombres + fecha de nacimiento (fallback)
- Validación estricta de CUI
- Rate limiting implícito por servicio externo
- Respuesta estandarizada y segura
"""
from fastapi import APIRouter, HTTPException, Query, Depends, status
from typing import Optional
import re

from app.services.renap_service import fetch_persona
from app.schemas.renap import RespuestaRenap
from app.database.security import get_current_user
from app.models.user import UserModel


router = APIRouter(prefix="/renap", tags=["RENAP Guatemala"])


def validar_cui(cui: str) -> bool:
    """Valida que el CUI tenga 13 dígitos numéricos"""
    return bool(re.fullmatch(r"\d{13}", cui))


@router.get(
    "/persona",
    response_model=RespuestaRenap,
    summary="Consultar persona en RENAP",
    description="""
    **Prioridad de búsqueda:**
    1. Por CUI (13 dígitos) → más rápido y preciso
    2. Por nombres completos + fecha de nacimiento (formato: dd/mm/aaaa)

    Ideal para:
    - Verificación de identidad al ingreso
    - Autocompletado de datos del paciente
    - Prevención de duplicados
    """
)
async def buscar_persona_renap(
    cui: Optional[str] = Query(
        None,
        min_length=13,
        max_length=13,
        regex=r"^\d{13}$",
        description="CUI de 13 dígitos (recomendado)"
    ),
    primer_nombre: Optional[str] = Query(None, min_length=2, max_length=50),
    segundo_nombre: Optional[str] = Query(None, max_length=50),
    primer_apellido: Optional[str] = Query(None, min_length=2, max_length=50),
    segundo_apellido: Optional[str] = Query(None, max_length=50),
    fecha_nacimiento: Optional[str] = Query(
        None,
        regex=r"^\d{2}/\d{2}/\d{4}$",
        description="Fecha en formato dd/mm/aaaa (ej: 15/05/1990)"
    ),
    current_user: UserModel = Depends(get_current_user)
):
    filtros = {}

    # === BÚSQUEDA POR CUI (PRIORITARIA) ===
    if cui:
        if not validar_cui(cui):
            raise HTTPException(
                status_code=400,
                detail="CUI inválido. Debe contener exactamente 13 dígitos numéricos."
            )
        filtros["cui"] = cui

    # === BÚSQUEDA POR NOMBRE + FECHA (FALLBACK) ===
    else:
        if not all([primer_nombre, primer_apellido, fecha_nacimiento]):
            raise HTTPException(
                status_code=400,
                detail="Para buscar sin CUI, debe proporcionar: primer_nombre, primer_apellido y fecha_nacimiento"
            )

        filtros.update({
            "primer_nombre": (primer_nombre or "").strip().upper(),
            "segundo_nombre": (segundo_nombre or "").strip().upper(),
            "primer_apellido": (primer_apellido or "").strip().upper(),
            "segundo_apellido": (segundo_apellido or "").strip().upper(),
            "fecha_nacimiento": fecha_nacimiento
        })

    try:
        resultado = await fetch_persona(filtros)

        # Opcional: auditar consulta
        # background_tasks.add_task(auditar_consulta_renap, current_user.id, filtros)

        return resultado

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Error de conexión con RENAP: {str(e)}"
        )