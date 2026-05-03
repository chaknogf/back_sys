# app/routes/users.py
"""
CRUD completo de usuarios - Solo admins
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database.db import get_db
from app.models.user import UserModel
from app.schemas.user import UserCreate, UserResponse, UserUpdate, UserBase, UsersList, RecuperarPassword
from app.database.security import get_current_user, hash_password
from app.config.mail_config import conf
from fastapi_mail import FastMail, MessageSchema, MessageType

router = APIRouter(prefix="/users", tags=["Usuarios"])


# === LISTAR USUARIOS ===
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
    query = db.query(UserModel)
    # 🔍 Filtros
    if id is not None:
        query = query.filter(UserModel.id == id)
    if username:
        query = query.filter(UserModel.username.ilike(f"%{username}%"))
    if email:
        query = query.filter(UserModel.email.ilike(f"%{email}%"))
    if rol:
        query = query.filter(UserModel.role == rol)
    # 📊 Total antes de paginar
    total = query.count()
    # 📦 Datos paginados
    usuarios = query.offset(skip).limit(limit).all()
    return {
        "total": total,
        "usuarios": usuarios
    }
    
@router.get("/{user_id}", response_model=UserResponse)
def obtener_usuario(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    usuario = db.query(UserModel).filter(UserModel.id == user_id).first()

    if not usuario:
        raise HTTPException(
            status_code=404,
            detail=f"Usuario con ID {user_id} no encontrado"
        )

    return usuario
   
    


# === CREAR USUARIO + CORREO BIENVENIDA ===
@router.post("/", response_model=UserCreate, status_code=201)
async def crear_usuario(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Solo admins pueden crear usuarios")

    # Validaciones
    if db.query(UserModel).filter(UserModel.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username ya existe")

    if db.query(UserModel).filter(UserModel.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email ya registrado")

    # Crear usuario
    nuevo_usuario = UserModel(
        **user_data.model_dump(),
        password = hash_password("TEMP_DISABLED"),
        estado="I",
        role="regular",
    )

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    # 📩 Enviar correo en segundo plano
    background_tasks.add_task(enviar_bienvenida, nuevo_usuario)

    return nuevo_usuario

# === ACTUALIZAR USUARIO ===
@router.put("/{user_id}", response_model=UserResponse)
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

@router.patch("/recuperar")
def recuperar_contraseña(
    data: RecuperarPassword,
    db: Session = Depends(get_db)
):
    usuario = db.query(UserModel).filter(UserModel.email == data.email).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    usuario.password = hash_password(data.password)

    db.commit()

    return {"message": "Contraseña actualizada correctamente"}


# === ELIMINAR USUARIO ===
@router.delete("/{user_id}", status_code=204)
def eliminar_usuario(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    # 🔐 Solo admin
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Solo admins pueden eliminar")

    # 🚫 Evitar suicidio administrativo
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="No puedes eliminarte a ti mismo")

    usuario = db.query(UserModel).filter(UserModel.id == user_id).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # 💣 Eliminación real
    db.delete(usuario)
    db.commit()

    return None


# === FUNCIÓN DE CORREO (RECIBE LA CONTRASEÑA PLANA) ===
# <p><strong>Contraseña:</strong> <code>{contraseña_plana}</code></p>
async def enviar_bienvenida(usuario: UserModel):
    try:
        fm = FastMail(conf)

        message = MessageSchema(
            subject="¡Bienvenido a MedicalApp!",
            recipients=[usuario.email],
            body=f"""
            <h2>¡Hola {usuario.nombre}!</h2>
            <p>Tu cuenta ha sido creada exitosamente en el Sistema Hospitalario Nacional.</p>
            <hr>
            <p><strong>Usuario:</strong> <code>{usuario.username}</code></p>

            <br>
            <p>
                <a href="https://htecpan.com"
                   style="background:#0066cc; color:white; padding:12px 24px;
                   text-decoration:none; border-radius:8px;">
                   Ingresar al Sistema MedicalApp
                </a>
            </p>

            <p>Selecciona <strong>"¿Olvidaste tu contraseña?"</strong> para definir tu acceso.</p>

            <br>
            <p>¡Gracias por ser parte del equipo que salva vidas!</p>
            """,
            subtype=MessageType.html
        )

        await fm.send_message(message)

    except Exception as e:
        print("❌ Error enviando correo:", str(e))