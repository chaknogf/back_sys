from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from core.security import verify_password, create_access_token
from modules.users.models import UserModel


def authenticate_user(db: Session, username: str, password: str) -> dict:
    user = db.query(UserModel).filter(UserModel.username == username).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.estado != "A":
        estado_map = {"I": "Cuenta no activada. Revise su correo.",
                      "B": "Cuenta bloqueada."}
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=estado_map.get(user.estado, "Usuario no autorizado.")
        )
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role, "estado": user.estado}
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 86400,
        "user": {
            "id": user.id,
            "nombre": user.nombre,
            "role": user.role,
            "unidad": user.unidad
        }
    }


def get_current_user_info(user) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "nombre": user.nombre,
        "role": user.role,
        "estado": user.estado
    }
