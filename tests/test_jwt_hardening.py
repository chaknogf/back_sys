"""Endurecimiento de JWT (paso 3).

Un token solo es válido si: firma HS256 con la clave del servidor, emisor
`fah-backend`, audiencia correcta y no expirado. Los de recuperación de
contraseña no sirven como sesión y viceversa. `alg: none` se rechaza.
"""

import base64
import json
import time
from datetime import datetime, timezone

from fastapi.testclient import TestClient
from joserfc import jwt

from core.config import ACCESS_TOKEN_EXPIRE_MINUTES
from core.security import (
    JWT_AUD_API,
    JWT_AUD_PASSWORD_RESET,
    JWT_ISSUER,
    _jwt_key,
    verify_password_reset_token,
    create_access_token,
)
from main import app

client = TestClient(app)


def _firmar(claims: dict, alg: str = "HS256") -> str:
    now = int(time.time())
    base = {"sub": "test_integration", "iss": JWT_ISSUER, "aud": JWT_AUD_API,
            "iat": now, "exp": now + 600}
    base.update(claims)
    return jwt.encode({"alg": alg}, base, _jwt_key)


def _me(token: str):
    return client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})


def test_token_valido_acepta(auth_headers):
    assert _me(_firmar({})).status_code == 200


def test_sin_audiencia_rechazado():
    claims = {"sub": "test_integration", "iss": JWT_ISSUER, "iat": int(time.time()),
              "exp": int(time.time()) + 600}
    assert _me(jwt.encode({"alg": "HS256"}, claims, _jwt_key)).status_code == 401


def test_audiencia_reset_no_sirve_como_sesion():
    assert _me(_firmar({"aud": JWT_AUD_PASSWORD_RESET})).status_code == 401


def test_emisor_incorrecto_rechazado():
    assert _me(_firmar({"iss": "otro-servicio"})).status_code == 401


def test_expirado_rechazado():
    assert _me(_firmar({"exp": int(time.time()) - 5})).status_code == 401


def test_alg_none_rechazado():
    def b64(d):
        return base64.urlsafe_b64encode(json.dumps(d).encode()).rstrip(b"=").decode()
    token = f"{b64({'alg': 'none'})}.{b64({'sub': 'test_integration', 'iss': JWT_ISSUER, 'aud': JWT_AUD_API, 'exp': int(time.time()) + 600})}."
    assert _me(token).status_code == 401


def test_token_de_acceso_no_es_token_de_reset():
    token = create_access_token({"sub": "x@hospital.com", "purpose": "password_reset"})
    assert verify_password_reset_token(token) is None


def test_login_expires_in_coincide_con_configuracion(auth_headers):
    r = client.post("/auth/login", data={"username": "test_integration", "password": "TestPass123!"})
    assert r.status_code == 200, r.text
    assert r.json()["expires_in"] == ACCESS_TOKEN_EXPIRE_MINUTES * 60
