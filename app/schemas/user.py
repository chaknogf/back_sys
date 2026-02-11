# app/schemas/user.py
"""
Schemas para usuarios del sistema (administradores, médicos, etc.)
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=100, description="Nombre completo del usuario")
    username: str = Field(..., min_length=4, max_length=20, description="Nombre de usuario único")
    email: EmailStr = Field(..., description="Correo electrónico válido")
    role: str = Field(
        ..., 
        pattern=r"^(admin|medico|enfermeria|recepcion|laboratorio|farmacia|usuario|registros)$",
        description="Rol del usuario en el sistema"
    )
    unidad: Optional[int] = Field(None, ge=1, description="ID de la unidad de salud")
    estado: str = Field("A", pattern=r"^(A|I)$", description="A=Activo, I=Inactivo")
    datos_extra: Optional[dict] = None


class UserCreate(UserBase):
    """Para crear un nuevo usuario (admin o registro)"""
    password: str = Field(..., min_length=4, description="Contraseña plana (se hashea con Argon2)")


class UserUpdate(BaseModel):
    """Para actualizar usuario (PATCH)"""
    nombre: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    unidad: Optional[int] = None
    estado: Optional[str] = None
    password: Optional[str] = Field(None, min_length=4, description="Nueva contraseña (opcional)")
    datos_extra: Optional[dict] = None
    


class UserResponse(UserBase):
    """Respuesta al frontend - NUNCA incluye password"""
    id: int = Field(..., description="ID único del usuario")
    # creado_en: Optional[datetime] = None
    # actualizado_en: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        exclude={"password"}  # ¡NUNCA devolver la contraseña!
    )


class UserInDB(UserResponse):
    """Solo para uso interno (CRUD) - incluye hash"""
    password: str  # Hash Argon2

    model_config = ConfigDict(from_attributes=True)