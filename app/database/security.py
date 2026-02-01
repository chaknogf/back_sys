"""
Módulo central de autenticación y autorización.

Responsabilidades:
- Hash y verificación de contraseñas (Argon2)
- Creación y validación de JWT
- OAuth2 Bearer
- Obtención del usuario autenticado
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
from app.database.config import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

# ======================================================
# CONTEXTO CRIPTOGRÁFICO – ARGON2 (SEGURIDAD MODERNA)
# ======================================================
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__memory_cost=65536,   # 64 MB
    argon2__time_cost=3,
    argon2__parallelism=4,
)

# ======================================================
# OAUTH2
# ======================================================
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ======================================================
# HASH DE CONTRASEÑAS
# ======================================================
def hash_password(password: str) -> str:
    """Genera un hash seguro usando Argon2."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña contra su hash."""
    return pwd_context.verify(plain_password, hashed_password)

# ======================================================
# JWT
# ======================================================
def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None
) -> str:
    """
    Crea un JWT firmado.
    `data` debe incluir al menos el campo 'sub'.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ======================================================
# USUARIO AUTENTICADO
# ======================================================
def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
) -> UserModel:
    """
    Decodifica el JWT y devuelve el usuario autenticado
    como una instancia de UserModel.
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")

        if not username:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = (
        db.query(UserModel)
        .filter(UserModel.username == username)
        .first()
    )

    if not user:
        raise credentials_exception

    return user

# ======================================================
# USUARIO ADMINISTRADOR
# ======================================================
def get_current_admin_user(
    current_user: UserModel = Depends(get_current_user),
) -> UserModel:
    """
    Verifica que el usuario autenticado tenga rol admin.
    """

    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: se requieren permisos de administrador",
        )

    return current_user

# ======================================================
# EXPORTS
# ======================================================
__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "oauth2_scheme",
    "get_current_user",
    "get_current_admin_user",
    "pwd_context",
]