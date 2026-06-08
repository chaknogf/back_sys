from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional

from core.database import get_db
from core.security import get_current_user
from .models import UserModel
from .schemas import UserCreate, UserResponse, UserUpdate, UsersList, RecuperarPassword
from .service import list_users, get_user_by_id, create_user, update_user, delete_user, recover_password, send_welcome_email

router = APIRouter(prefix="/users", tags=["Usuarios"])


@router.get("/", response_model=UsersList)
def listar_usuarios(
    username: Optional[str] = None,
    id: Optional[int] = None,
    email: Optional[str] = None,
    rol: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")
    filters = {k: v for k, v in {"id": id, "username": username, "email": email, "rol": rol}.items() if v is not None}
    return list_users(db, filters, skip, limit)


@router.get("/{user_id}", response_model=UserResponse)
def obtener_usuario(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return get_user_by_id(db, user_id)


@router.post("/", response_model=UserCreate, status_code=201)
async def crear_usuario(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Solo admins pueden crear usuarios")
    nuevo_usuario = create_user(db, user_data)
    background_tasks.add_task(send_welcome_email, nuevo_usuario)
    return nuevo_usuario


@router.put("/{user_id}", response_model=UserResponse)
def actualizar_usuario(
    user_id: int,
    update_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="No autorizado")
    return update_user(db, user_id, update_data)


@router.patch("/recuperar")
def recuperar_contraseña(
    data: RecuperarPassword,
    db: Session = Depends(get_db)
):
    return recover_password(db, data.email, data.password)


@router.delete("/{user_id}", status_code=204)
def eliminar_usuario(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Solo admins pueden eliminar")
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="No puedes eliminarte a ti mismo")
    delete_user(db, user_id)
    return None
