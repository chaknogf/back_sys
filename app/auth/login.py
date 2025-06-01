from sqlalchemy.exc import SQLAlchemyError
from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session as SQLAlchemySession
from datetime import timedelta
from jose import JWTError, jwt
from app.database.db import SessionLocal
from app.models.user import UserModel
from app.database.config import SECRET_KEY, ALGORITHM
from app.database.security import verify_password, create_access_token

# Dependencia para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Ruta y prefijo para autenticación
router = APIRouter(prefix="/auth", tags=["auth"])

# Sin scopes, solo autenticación básica
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.post("/login")
def login(
    username: str = Form(...),
    password: str = Form(...),
    db: SQLAlchemySession = Depends(get_db)
):
    """
    Autenticación de usuarios, genera un token de acceso si las credenciales son correctas.
    """
    try:
        user = db.query(UserModel).filter(UserModel.username == username).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado"
            )
        
        if not verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Contraseña incorrecta"
            )

        access_token = create_access_token(
            data={"sub": user.username},
            expires_delta=timedelta(minutes=60)
        )

        return {"access_token": access_token, "token_type": "bearer"}

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Error en la base de datos: " + str(e))


@router.get("/me")
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: SQLAlchemySession = Depends(get_db)
):
    """
    Devuelve la información del usuario autenticado usando el token.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")

        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )

        user = db.query(UserModel).filter(UserModel.username == username).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado"
            )

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "unidad": user.unidad
        }

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )