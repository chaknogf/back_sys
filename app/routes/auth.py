# app/routes/auth.py
"""
Router de autenticación - Login, token, magic link (opcional)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.models.user import UserModel
from app.database.security import verify_password, create_access_token
from app.schemas.auth import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=TokenResponse, summary="Login con usuario/contraseña")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(UserModel).filter(UserModel.username == form_data.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
    if not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
    if user.estado != "A":
        if user.estado == "I":
            raise HTTPException(403, "Cuenta no activada. Revise su correo.")
        elif user.estado == "B":
            raise HTTPException(403, "Cuenta bloqueada.")
        else:
            raise HTTPException(403, "Usuario no autorizado.")
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role, "estado": user.estado}
    )
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=86400,
        user={
            "id": user.id,
            "nombre": user.nombre,
            "role": user.role,
            "unidad": user.unidad
        }

    )