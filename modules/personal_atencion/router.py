# modules/personal_atencion/router.py
"""Rutas del catálogo de personal de atención médica."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional

from core.database import get_db
from core.security import get_current_user, get_current_admin_user
from .models import PersonalAtencionModel
from .schemas import (
    PersonalAtencionCreate,
    PersonalAtencionUpdate,
    PersonalAtencionOut,
    PersonalAtencionListResponse,
)
from .service import (
    crear_personal_atencion as service_crear_personal_atencion,
    listar_personal_atencion as service_listar_personal_atencion,
    obtener_personal_atencion as service_obtener_personal_atencion,
    actualizar_personal_atencion as service_actualizar_personal_atencion,
    eliminar_personal_atencion as service_eliminar_personal_atencion,
)

router = APIRouter(
    prefix="/personal-atencion",
    tags=["Personal de Atencion"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/", response_model=PersonalAtencionOut, status_code=status.HTTP_201_CREATED)
def crear_personal_atencion(
    data: PersonalAtencionCreate,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin_user),
):
    return service_crear_personal_atencion(data, db)


@router.get("/", response_model=PersonalAtencionListResponse)
def listar_personal_atencion(
    id: Optional[int] = None,
    activo: Optional[bool] = None,
    nombre: Optional[str] = None,
    colegiado: Optional[str] = None,
    pasaporte: Optional[str] = None,
    especialidad_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Busca y pagina personal de atención por identificadores y datos de catálogo."""
    return service_listar_personal_atencion(
        db=db,
        id=id,
        activo=activo,
        nombre=nombre,
        colegiado=colegiado,
        pasaporte=pasaporte,
        especialidad_id=especialidad_id,
        skip=skip,
        limit=limit,
    )


@router.get("/{personal_atencion_id}", response_model=PersonalAtencionOut)
def obtener_personal_atencion(personal_atencion_id: int, db: Session = Depends(get_db)):
    return service_obtener_personal_atencion(personal_atencion_id, db)


@router.put("/{personal_atencion_id}", response_model=PersonalAtencionOut)
def actualizar_personal_atencion(
    personal_atencion_id: int,
    data: PersonalAtencionUpdate,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin_user),
):
    return service_actualizar_personal_atencion(personal_atencion_id, data, db)


@router.delete("/{personal_atencion_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_personal_atencion(
    personal_atencion_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin_user),
):
    return service_eliminar_personal_atencion(personal_atencion_id, db)
