# app/database/security.py
"""
Módulo central de autenticación y autorización.
Aquí vive TODO lo relacionado con:
- Hash de contraseñas (Argon2)
- JWT
- OAuth2
- Usuario actual
"""

from datetime import datetime, timedelta, timezone
from typing import Annotated
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.models.user import UserModel
from app.database.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# ======================
# CRYPT CONTEXT – ARGON2 (MÁS SEGURO 2025)
# ======================
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__memory_cost=65536,   # 64 MB
    argon2__time_cost=3,
    argon2__parallelism=4,
)

# ======================
# OAUTH2 SCHEME
# ======================
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ======================
# HASH Y VERIFICACIÓN
# ======================
def hash_password(password: str) -> str:
    """Encripta una contraseña con Argon2"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica contraseña plana contra hash"""
    return pwd_context.verify(plain_password, hashed_password)

# ======================
# JWT
# ======================
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ======================
# USUARIO ACTUAL
# ======================
def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db)
) -> UserModel:
    """
    Dependencia que decodifica el JWT y devuelve el usuario autenticado.
    Úsala en cualquier endpoint protegido.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(UserModel).filter(UserModel.username == username).first()
    if user is None:
        raise credentials_exception

    return user

# ======================
# USUARIO ADMIN
# ======================
def get_current_admin_user(current_user: UserModel = Depends(get_current_user)) -> UserModel:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Acceso denegado: se requieren permisos de administrador")
    return current_user

# Exporta todo lo útil
__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "oauth2_scheme",
    "get_current_user",
    "get_current_admin_user",
    "pwd_context"
]