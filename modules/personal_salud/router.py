from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from core.dependencies import get_db, get_current_user
from modules.users.models import UserModel
from .schemas import PersonalSaludCreate, PersonalSaludUpdate, PersonalSaludOut
from .service import (
    listar_personal_salud as service_listar,
    obtener_personal_salud as service_obtener,
    crear_personal_salud as service_crear,
    actualizar_personal_salud as service_actualizar,
    eliminar_personal_salud as service_eliminar,
)

router = APIRouter(
    prefix="/sigsa3/personal-salud",
    tags=["Personal Salud"],
)


@router.get("", response_model=List[PersonalSaludOut])
@router.get("/", response_model=List[PersonalSaludOut])
def listar(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return service_listar(db)


@router.get("/{ps_id}", response_model=PersonalSaludOut)
def obtener(
    ps_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return service_obtener(ps_id, db)


@router.post("", response_model=PersonalSaludOut, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=PersonalSaludOut, status_code=status.HTTP_201_CREATED)
def crear(
    data: PersonalSaludCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return service_crear(data.nombre, data.especialidad_id, data.medico_id, db)


@router.put("/{ps_id}", response_model=PersonalSaludOut)
def actualizar(
    ps_id: int,
    data: PersonalSaludUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return service_actualizar(ps_id, data.nombre, data.especialidad_id, data.medico_id, db)


@router.delete("/{ps_id}")
def eliminar(
    ps_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return service_eliminar(ps_id, db)
