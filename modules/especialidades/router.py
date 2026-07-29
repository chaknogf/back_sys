from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from core.dependencies import get_db, get_current_admin_user
from modules.users.models import UserModel
from .schemas import EspecialidadCreate, EspecialidadUpdate, EspecialidadOut
from . import service as svc

router = APIRouter(
    prefix="/especialidades",
    tags=["Especialidades"],
)


@router.get("", response_model=List[EspecialidadOut])
@router.get("/", response_model=List[EspecialidadOut])
def listar(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user),
):
    return svc.listar(db)


@router.get("/{esp_id}", response_model=EspecialidadOut)
def obtener(
    esp_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user),
):
    return svc.obtener(esp_id, db)


@router.post("", response_model=EspecialidadOut, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=EspecialidadOut, status_code=status.HTTP_201_CREATED)
def crear(
    data: EspecialidadCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user),
):
    return svc.crear(data, db)


@router.put("/{esp_id}", response_model=EspecialidadOut)
def actualizar(
    esp_id: int,
    data: EspecialidadUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user),
):
    return svc.actualizar(esp_id, data, db)


@router.delete("/{esp_id}")
def eliminar(
    esp_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user),
):
    return svc.eliminar(esp_id, db)
