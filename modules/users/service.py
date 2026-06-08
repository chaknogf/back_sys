from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from core.security import hash_password
from modules.users.models import UserModel
from modules.users.schemas import UserCreate, UserUpdate
from core.mail import mail_config
from fastapi_mail import FastMail, MessageSchema, MessageType


def list_users(db: Session, filters: dict, skip: int = 0, limit: int = 50):
    query = db.query(UserModel)
    if filters.get("id") is not None:
        query = query.filter(UserModel.id == filters["id"])
    if filters.get("username"):
        query = query.filter(UserModel.username.ilike(f"%{filters['username']}%"))
    if filters.get("email"):
        query = query.filter(UserModel.email.ilike(f"%{filters['email']}%"))
    if filters.get("rol"):
        query = query.filter(UserModel.role == filters["rol"])
    total = query.count()
    usuarios = query.offset(skip).limit(limit).all()
    return {"total": total, "usuarios": usuarios}


def get_user_by_id(db: Session, user_id: int):
    usuario = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail=f"Usuario con ID {user_id} no encontrado")
    return usuario


def create_user(db: Session, user_data: UserCreate):
    if db.query(UserModel).filter(UserModel.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username ya existe")
    if db.query(UserModel).filter(UserModel.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email ya registrado")
    nuevo_usuario = UserModel(
        **user_data.model_dump(),
        password=hash_password("TEMP_DISABLED"),
        estado="I",
        role="regular",
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario


def update_user(db: Session, user_id: int, update_data: UserUpdate):
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


def delete_user(db: Session, user_id: int):
    usuario = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.delete(usuario)
    db.commit()


def recover_password(db: Session, email: str, password: str):
    usuario = db.query(UserModel).filter(UserModel.email == email).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    usuario.password = hash_password(password)
    db.commit()
    return {"message": "Contraseña actualizada correctamente"}


async def send_welcome_email(usuario: UserModel):
    try:
        fm = FastMail(mail_config)
        message = MessageSchema(
            subject="¡Bienvenido a MedicalApp!",
            recipients=[usuario.email],
            body=f"""
            <h2>¡Hola {usuario.nombre}!</h2>
            <p>Tu cuenta ha sido creada exitosamente en el Sistema Hospitalario Nacional.</p>
            <hr>
            <p><strong>Usuario:</strong> <code>{usuario.username}</code></p>
            <br>
            <p><a href="https://htecpan.com" style="background:#0066cc; color:white; padding:12px 24px; text-decoration:none; border-radius:8px;">Ingresar al Sistema MedicalApp</a></p>
            <p>Selecciona <strong>"¿Olvidaste tu contraseña?"</strong> para definir tu acceso.</p>
            <br>
            <p>¡Gracias por ser parte del equipo que salva vidas!</p>
            """,
            subtype=MessageType.html
        )
        await fm.send_message(message)
    except Exception as e:
        print("❌ Error enviando correo:", str(e))
