# app/schemas/auth.py
"""
Schemas exclusivos para autenticación y login.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class LoginRequest(BaseModel):
    """Solicitud de login desde el frontend"""
    username: str = Field(..., description="Nombre de usuario o correo electrónico")
    password: str = Field(..., min_length=6, description="Contraseña del usuario")


class TokenResponse(BaseModel):
    """Respuesta estándar con token JWT"""
    access_token: str = Field(..., description="Token de acceso JWT")
    token_type: str = Field("bearer", description="Tipo de token (siempre 'bearer')")
    expires_in: int = Field(86400, description="Segundos hasta expiración (24h por defecto)")
    user: Optional[dict] = None  # Opcional: puedes incluir datos básicos del usuario


class TokenData(BaseModel):
    """Datos extraídos del JWT (para uso interno)"""
    username: str | None = None
    role: str | None = None
    unidad: int | None = None