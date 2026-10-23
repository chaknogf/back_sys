"""Endpoints destructivos y de auditoría restringidos a administrador (paso 2).

Un usuario con rol de escritura (editor) pasa el guard global de escritura,
pero debe recibir 403 aquí porque la dependencia exige rol admin.
"""

import time

import pytest
from fastapi.testclient import TestClient

from core.security import hash_password
from main import app
from modules.users.models import UserModel

PASSWORD = "AdminOnlyTest123!"
USERNAME = f"test_editor_admin_{int(time.time() * 1000000) % 1000000}"

# (método, ruta) — todas deben exigir admin
RUTAS_SOLO_ADMIN = [
    ("POST", "/pacientes/merge"),
    ("DELETE", "/consultas/1"),
    ("DELETE", "/consultas/1/eliminar"),
    ("DELETE", "/constancias-nacimiento/1"),
    ("DELETE", "/procedimientos/1"),
    ("DELETE", "/sigsa3/1"),
    ("DELETE", "/sigsa3-registros/1"),
    ("DELETE", "/quirofano/intervenciones/1"),
    ("POST", "/agente/reglas"),
    ("DELETE", "/agente/reglas/1"),
    ("GET", "/audit-log/"),
]


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture(scope="module")
def editor_headers(client, db_session):
    user = UserModel(
        username=USERNAME,
        password=hash_password(PASSWORD),
        nombre="Editor Admin Test",
        email=f"{USERNAME}@hospital.com",
        role="editor",
        estado="A",
    )
    db_session.add(user)
    db_session.commit()
    try:
        r = client.post("/auth/login", data={"username": USERNAME, "password": PASSWORD})
        assert r.status_code == 200, r.text
        yield {"Authorization": f"Bearer {r.json()['access_token']}"}
    finally:
        db_session.delete(db_session.get(UserModel, user.id))
        db_session.commit()


@pytest.mark.parametrize("metodo,ruta", RUTAS_SOLO_ADMIN)
def test_editor_recibe_403(client, editor_headers, metodo, ruta):
    r = client.request(metodo, ruta, headers=editor_headers, json={})
    assert r.status_code == 403, f"{metodo} {ruta} -> {r.status_code}"

