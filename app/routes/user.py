from sqlalchemy.exc import SQLAlchemyError
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy import func, desc
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import date, datetime, time
from app.database.db import SessionLocal
from app.models.user import UserModel
from sqlalchemy.orm import Session as SQLAlchemySession
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from app.schemas.schemas import UserCreate, UserBase, UserResponse






class Userschema(BaseModel):
   
    nombre: str | None = None
    username: str | None = None
    email: EmailStr | None = None
    role: str | None = None
    password: str | None = None
    estado: str | None = None
    


    class Config:
        from_attributes = True



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
router = APIRouter() 
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
        
@router.get("/user/", response_model=List[UserResponse], tags=["users"])
async def get_users(
    id: Optional[int] = Query(None, description="ID del usuario"),
    nombre: Optional[str] = Query(None, description="Nombre del usuario"),
    username: Optional[str] = Query(None, description="Username del usuario"),
    email: Optional[str] = Query(None, description="Email del usuario"),
    role: Optional[str] = Query(None, description="Role del usuario"),
    current_user: dict = Depends(oauth2_scheme),  # Esto ya valida el token
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=0),
    db: SQLAlchemySession = Depends(get_db)
):
    try:
       query = db.query(UserModel).order_by(desc(UserModel.id))

       if id:
           query = query.filter(UserModel.id == id)
       if nombre:
           query = query.filter(UserModel.nombre.ilike(f"%{nombre}%"))
       if username:
           query = query.filter(UserModel.username.ilike(f"%{username}%"))
       if email:
           query = query.filter(UserModel.email.ilike(f"%{email}%"))
       if role:
           query = query.filter(UserModel.role == role)
       
       result = query.offset(skip).limit(limit).all()
       return JSONResponse(status_code=200, content=jsonable_encoder(result))

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
        
        
# Ruta para crear un nuevo usuario
@router.post("/user/crear", tags=["users"])
async def create_user(
    user: UserCreate, 
    token: str = Depends(oauth2_scheme),
    db: SQLAlchemySession = Depends(get_db)):
    try:
        # Asegúrate de que la contraseña esté cifrada
        if user.password:
            hashed_password = pwd_context.hash(user.password)
            user.password = hashed_password

        # Crear el nuevo usuario con los datos proporcionados
        new_user = UserModel(**user.model_dump())
        
        # Añadir y confirmar el nuevo usuario en la base de datos
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Retornar el nuevo usuario en formato JSON
        return JSONResponse(status_code=200, content={"message": "User created successfully"})
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.put("/user/actualizar/{user_id}", tags=["users"])
async def update_user(
    user_id: int, 
    user: UserBase, 
    token: str = Depends(oauth2_scheme),
    db: SQLAlchemySession = Depends(get_db)):
    try:
        db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        for key, value in user.model_dump().items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
        return JSONResponse(status_code=200, content=jsonable_encoder(db_user))
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@router.delete("/user/eliminar/{user_id}", tags=["users"])
async def delete_user(
    user_id: int, 
    current_user: dict = Depends(oauth2_scheme),
    db: SQLAlchemySession = Depends(get_db)):
    try:
        db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        db.delete(db_user)
        db.commit()
        return JSONResponse(status_code=200, content={"message": "User deleted successfully"})
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
