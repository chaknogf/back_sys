# app/routes/users.py
"""
CRUD completo de usuarios - Solo admins
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from app.database.db import get_db
from app.models.user import UserModel
from app.schemas.user import UserCreate, UserResponse, UserUpdate, UserBase
from app.database.security import get_current_user, hash_password
from app.config.mail_config import conf
from fastapi_mail import FastMail, MessageSchema, MessageType

router = APIRouter(prefix="/users", tags=["Usuarios"])


# === LISTAR USUARIOS ===
@router.get("/", response_model=List[UserResponse])
def listar_usuarios(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    # Opcional: solo admins
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")

    usuarios = db.query(UserModel).offset(skip).limit(limit).all()
    return usuarios


# === CREAR USUARIO + CORREO BIENVENIDA ===
@router.post("/", response_model=UserResponse, status_code=201)
async def crear_usuario(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Solo admins pueden crear usuarios")

    # Verificar duplicados
    if db.query(UserModel).filter(UserModel.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username ya existe")
    if db.query(UserModel).filter(UserModel.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email ya registrado")

    # GUARDAR LA CONTRASEÑA EN TEXTO PLANO TEMPORALMENTE
    contraseña_plana = user_data.password
    hashed = hash_password(user_data.password)

    nuevo_usuario = UserModel(
        **user_data.model_dump(exclude={"password"}), 
        password=hashed
    )
    
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    # ENVIAR CORREO CON LA CONTRASEÑA REAL
    background_tasks.add_task(enviar_bienvenida, nuevo_usuario, contraseña_plana)

    return nuevo_usuario


# === ACTUALIZAR USUARIO ===
@router.patch("/{user_id}", response_model=UserResponse)
def actualizar_usuario(
    user_id: int,
    update_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="No autorizado")

    usuario = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    for key, value in update_data.model_dump(exclude_unset=True).items():
        if key == "password" and value:
            setattr(usuario, key, hash_password(value))
        else:
            setattr(usuario, key, value)

    db.commit()
    db.refresh(usuario)
    return usuario


# === ELIMINAR USUARIO ===
@router.delete("/{user_id}", status_code=204)
def eliminar_usuario(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Solo admins pueden eliminar")

    usuario = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    db.delete(usuario)
    db.commit()
    return None


# === FUNCIÓN DE CORREO (RECIBE LA CONTRASEÑA PLANA) ===
async def enviar_bienvenida(usuario: UserModel, contraseña_plana: str):
    fm = FastMail(conf)
    message = MessageSchema(
        subject="¡Bienvenido a MedicalApp Tecpán!",
        recipients=[usuario.email],
        body=f"""
        <h2>¡Hola {usuario.nombre}!</h2>
        <p>Tu cuenta ha sido creada exitosamente en el Sistema Hospitalario Nacional.</p>
        <hr>
        <p><strong>Usuario:</strong> <code>{usuario.username}</code></p>
        <p><strong>Contraseña:</strong> <code>{contraseña_plana}</code></p>
       
        <br>
        <p><a href="https://hgtecpan.duckdns.org" style="background:#0066cc; color:white; padding:12px 24px; text-decoration:none; border-radius:8px;">
            Ingresar al Sistema
        </a></p>
        <br>
        <p>¡Gracias por ser parte del equipo que salva vidas!</p>
        """,
        subtype=MessageType.html
    )
    await fm.send_message(message)