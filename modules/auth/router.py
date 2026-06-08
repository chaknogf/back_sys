from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import get_current_user
from .schemas import TokenResponse
from .service import authenticate_user, get_current_user_info
from modules.users.models import UserModel

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=TokenResponse, summary="Login con usuario/contraseña")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    result = authenticate_user(db, form_data.username, form_data.password)
    return TokenResponse(**result)


@router.get("/me", summary="Obtener datos del usuario autenticado")
def me(current_user: UserModel = Depends(get_current_user)):
    return get_current_user_info(current_user)
