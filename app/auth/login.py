# app/auth/login.py
"""
Router de autenticación.
Todo limpio, sin duplicados, usando los módulos centrales.
"""

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.database.security import verify_password, create_access_token, get_current_user
from app.models.user import UserModel

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", summary="Login con usuario y contraseña")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Endpoint estándar de FastAPI para login.
    Cliente envía: username y password en form-data.
    Devuelve: access_token + token_type
    """
    user = db.query(UserModel).filter(UserModel.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username})
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", summary="Obtener datos del usuario autenticado")
def me(current_user: UserModel = Depends(get_current_user)):
    """
    Usa la dependencia mágica get_current_user() → 0 líneas de JWT manual!
    """
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "nombre": current_user.nombre,
        "role": current_user.role,
        # "servicio_id": current_user.servicio_id,
        "estado": current_user.estado
    }