from fastapi import APIRouter, Depends, HTTPException, Request, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional

from core.database import get_db
from core.limiter import limiter
from core.security import get_current_user, create_password_reset_token
from core.config import APP_BASE_URL
from .models import UserModel
from .schemas import UserCreate, UserResponse, UserUpdate, UsersList, SolicitarRecuperacion, ConfirmarRecuperacion
from .service import (
    list_users,
    get_user_by_id,
    create_user,
    update_user,
    delete_user,
    confirmar_recuperacion,
    send_welcome_email,
    send_reset_password_email,
)

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


@router.post("/", response_model=UserResponse, status_code=201)
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


@router.post("/recuperar/solicitar")
@limiter.limit("5/minute")
def solicitar_restablecer(
    request: Request,
    data: SolicitarRecuperacion,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Envía un enlace de restablecimiento al correo registrado (si existe).

    Devuelve siempre el mismo mensaje para no revelar qué correos están
    registrados (evita enumeración de usuarios).
    """
    usuario = (
        db.query(UserModel)
        .filter(UserModel.email.ilike(data.email))
        .first()
    )
    if usuario:
        token = create_password_reset_token(usuario.email)
        link = f"{APP_BASE_URL}/resetpass?token={token}&email={usuario.email}"
        background_tasks.add_task(
            send_reset_password_email, usuario.email, usuario.nombre, link
        )
    return {
        "message": (
            "Si el correo está registrado, recibirás un enlace para "
            "restablecer tu contraseña. Revisa tu bandeja de entrada."
        )
    }


@router.post("/recuperar/confirmar")
def confirmar_restablecer(
    data: ConfirmarRecuperacion,
    db: Session = Depends(get_db),
):
    return confirmar_recuperacion(db, data.email, data.token, data.password)


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
