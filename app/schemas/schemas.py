from pydantic import BaseModel

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    
    

# schemas.py o models.py

from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    nombre: str
    username: str
    email: EmailStr
    password: str
    role: str
    estado: str = "A"

class UserCreate(UserBase):
    pass  # No incluir 'id'

class UserResponse(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)