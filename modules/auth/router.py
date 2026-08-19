from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from core.database import get_db
from core.limiter import limiter
from core.security import get_current_user
from .schemas import TokenResponse
from .service import authenticate_user, get_current_user_info
from modules.users.models import UserModel
from modules.audit_log.service import registrar_acceso, detectar_so, obtener_ip

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=TokenResponse, summary="Login con usuario/contraseña")
@limiter.limit("10/minute")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    result = authenticate_user(db, form_data.username, form_data.password)
    ua = request.headers.get("user-agent")
    registrar_acceso(
        db,
        form_data.username,
        "auth",
        "/auth/login",
        metodo="POST",
        ip_address=obtener_ip(request),
        so=detectar_so(ua),
        nombre_equipo=request.headers.get("x-nombre-equipo") or None,
        user_agent=ua,
    )
    return TokenResponse(**result)


@router.get("/me", summary="Obtener datos del usuario autenticado")
def me(current_user: UserModel = Depends(get_current_user)):
    return get_current_user_info(current_user)
