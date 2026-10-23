"""Hash de contraseñas, emisión de JWT y dependencias de autorización."""

import re
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Annotated
from uuid import uuid4

from joserfc import jwt
from joserfc.jwk import OctKey
from joserfc.errors import JoseError
from joserfc.jwt import JWTClaimsRegistry
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from core.database import get_db
from core.config import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

_jwt_key = OctKey.import_key(SECRET_KEY.encode("utf-8"))

JWT_ISSUER = "fah-backend"
JWT_AUD_API = "fah-api"                 # tokens de sesión
JWT_AUD_PASSWORD_RESET = "fah-password-reset"  # tokens de recuperación


def _claims_registry(audience: str) -> JWTClaimsRegistry:
    return JWTClaimsRegistry(
        iss={"essential": True, "value": JWT_ISSUER},
        aud={"essential": True, "value": audience},
        exp={"essential": True},
        iat={"essential": True},
    )


def _decode_token(token: str, audience: str) -> dict:
    """Verifica firma HS256 fija, emisor, audiencia y expiración. Lanza JoseError."""
    token_obj = jwt.decode(token, _jwt_key, algorithms=[ALGORITHM])
    _claims_registry(audience).validate(token_obj.claims)
    return token_obj.claims

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__memory_cost=65536,
    argon2__time_cost=3,
    argon2__parallelism=4,
)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/fah/auth/login"
)


class Role(str, Enum):
    """Roles de la aplicación. `regular` es el rol histórico de edición y
    equivale a `EDITOR` (compatibilidad con cuentas ya creadas); `read_only`
    es el rol de solo lectura pensado para integraciones externas (p. ej. un
    CRM que consulta pacientes sin modificarlos)."""

    ADMIN = "admin"
    EDITOR = "editor"
    REGULAR = "regular"  # histórico: mismo nivel de escritura que EDITOR
    READ_ONLY = "read_only"


# Roles de dominio ya existentes en producción (registro, UISAU, etc.). Todos
# conservan capacidad de escritura nivel EDITOR: el read-only real es `Role.READ_ONLY`.
ROLES_ESCRITURA_LEGADOS: tuple[str, ...] = (
    "registro",
    "std",
    "uisau",
    "ts",
    "medic",
    "paramedic",
    "lab",
    "rx",
    "epi",
    "nutric",
    "odonto",
)

# jerarquía numérica: mayor = más permisos; rol desconocido = 0 (sin escritura)
ROLE_LEVELS: dict[str, int] = {
    Role.ADMIN.value: 3,
    Role.EDITOR.value: 2,
    Role.REGULAR.value: 2,
    Role.READ_ONLY.value: 1,
    **{r: 2 for r in ROLES_ESCRITURA_LEGADOS},
}


def all_role_values() -> tuple[str, ...]:
    """Roles válidos para asignar (enum nuevo + legados de dominio)."""
    return tuple(r.value for r in Role) + ROLES_ESCRITURA_LEGADOS

WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

# Rutas que aceptan escritura anónima o con cualquier rol (histórico del
# proyecto). Endpoints sensibles como /pacientes/merge o borrados físicos ya
# exigen admin en su router, así que el nivel EDITOR no los debilita.
WRITE_PUBLIC_ROUTES: frozenset[str] = frozenset({
    "/auth/login",
    "/users/recuperar/solicitar",
    "/users/recuperar/confirmar",
    "/encamamiento",
    "/municipios",
})

_ANON_RE = re.compile(r"^/fah/auth/login/?$")


def role_level(role: str | None) -> int:
    """Nivel jerárquico de un rol; desconocido o ausente vale 0."""
    return ROLE_LEVELS.get(role or "", 0)


def es_ruta_exenta_de_escritura(ruta: str) -> bool:
    """True si la ruta está exenta del guard de escritura (lista documentada)."""
    return any(ruta == p or ruta.startswith(p + "/") for p in WRITE_PUBLIC_ROUTES)


def write_guard(
    request: Request,
    db: Session = Depends(get_db),
):
    """Guardia global: los métodos de escritura exigen rol >= EDITOR.

    - GET/HEAD/OPTIONS nunca se bloquean: el rol `read_only` puede leer todo.
    - Rutas listas para escritura anónima (login, recuperación, catálogos
      legacy) quedan exentas para no romper contratos existentes.
    - Cualquier otro método de escritura requiere un token válido cuyo usuario,
      según la BD (fuente de verdad, no el claim del JWT), tenga nivel
      >= EDITOR. `read_only` recibe 403.
    """
    if request.method.upper() not in WRITE_METHODS:
        return

    path = request.url.path
    ruta = re.sub(r"^/fah(?=/|$)", "", path)
    if _ANON_RE.match(path) or es_ruta_exenta_de_escritura(ruta):
        return

    auth = request.headers.get("authorization") or ""
    if not auth.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autorizado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    from modules.users.models import UserModel

    try:
        payload = _decode_token(auth.split(" ", 1)[1], JWT_AUD_API)
        username = payload.get("sub")
    except JoseError:
        username = None
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(UserModel).filter(UserModel.username == username).first()
    if not user or user.estado != "A":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if role_level(user.role) < role_level(Role.EDITOR):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: su rol es de solo lectura",
        )


def hash_password(password: str) -> str:
    """Guarda contraseñas con Argon2; nunca se conserva el texto original."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compara una contraseña en texto claro con su hash Argon2 almacenado."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None,
    audience: str = JWT_AUD_API,
) -> str:
    """Firma un JWT con expiración y un identificador único de emisión."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({
        "iss": JWT_ISSUER,
        "aud": audience,
        "exp": expire,
        "iat": now,
        "jti": uuid4().hex,
    })
    return jwt.encode({"alg": ALGORITHM}, to_encode, _jwt_key)


PASSWORD_RESET_EXPIRE_MINUTES = 30


def create_password_reset_token(email: str) -> str:
    """JWT de un solo uso para restablecer contraseña (30 min)."""
    return create_access_token(
        {"sub": email, "purpose": "password_reset"},
        expires_delta=timedelta(minutes=PASSWORD_RESET_EXPIRE_MINUTES),
        audience=JWT_AUD_PASSWORD_RESET,
    )


def verify_password_reset_token(token: str) -> str | None:
    """Devuelve el email si el token de reseteo es válido; si no, None."""
    try:
        payload = _decode_token(token, JWT_AUD_PASSWORD_RESET)
    except JoseError:
        return None
    if payload.get("purpose") != "password_reset":
        return None
    return payload.get("sub")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
):
    """Valida firma y sujeto del JWT y exige que la cuenta permanezca activa."""
    from modules.users.models import UserModel

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = _decode_token(token, JWT_AUD_API)
        username: str | None = payload.get("sub")
        if not username:
            raise credentials_exception
    except JoseError:
        raise credentials_exception
    user = (
        db.query(UserModel)
        .filter(UserModel.username == username)
        .first()
    )
    if not user:
        raise credentials_exception
    if user.estado != "A":
        if user.estado == "I":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cuenta no activada"
            )
        elif user.estado == "B":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cuenta bloqueada"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario no autorizado"
            )
    return user


def get_current_admin_user(
    current_user=Depends(get_current_user),
):
    """Restringe la dependencia al rol administrador."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: se requieren permisos de administrador",
        )
    return current_user


def require_role(*roles: Role | str):
    """Dependency factory: exige que el usuario tenga uno de los roles dados.

    Uso: `dependencies=[Depends(require_role(Role.ADMIN))]` o por parámetro.
    """
    permitido = {r.value if isinstance(r, Role) else r for r in roles}

    def _guard(current_user=Depends(get_current_user)):
        if current_user.role not in permitido:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acceso denegado: rol insuficiente",
            )
        return current_user

    return _guard


def require_min_level(min_level: int):
    """Dependency factory: exige un nivel jerárquico mínimo (ver ROLE_LEVELS)."""

    def _guard(current_user=Depends(get_current_user)):
        if role_level(current_user.role) < min_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acceso denegado: rol insuficiente",
            )
        return current_user

    return _guard
