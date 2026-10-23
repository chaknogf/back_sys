"""Regresiones para la auto-escalada de privilegios en /users (Tarea 1).

Garantiza que un usuario `regular` no puede ascenderse a sí mismo a `admin`
ni desactivar usuarios, y que solo un admin puede cambiar `role`/`estado`.
"""

import time

import pytest
from fastapi.testclient import TestClient

from core.security import hash_password
from main import app
from modules.users.models import UserModel

PASSWORD = "EscaladaTest123!"


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture(scope="module")
def regular_user(db_session):
    username = f"test_regular_{int(time.time() * 1000000) % 1000000}"
    user = UserModel(
        username=username,
        password=hash_password(PASSWORD),
        nombre="Usuario Regular",
        email=f"{username}@hospital.com",
        role="regular",
        estado="A",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    yield user
    db_session.delete(user)
    db_session.commit()


@pytest.fixture(scope="module")
def regular_headers(client, regular_user):
    r = client.post(
        "/auth/login",
        data={"username": regular_user.username, "password": PASSWORD},
    )
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


class TestEscaladaPrivilegios:
    def test_no_puede_escalarse_a_admin(self, client, regular_headers, regular_user, db_session):
        r = client.put(
            f"/users/{regular_user.id}",
            headers=regular_headers,
            json={"nombre": "Usuario Editado", "role": "admin", "estado": "A"},
        )
        assert r.status_code == 200
        body = r.json()
        assert body["nombre"] == "Usuario Editado"
        assert body["role"] == "regular"

        db_session.expire_all()
        db_user = db_session.get(UserModel, regular_user.id)
        assert db_user.role == "regular"

    def test_no_puede_desactivarse(self, client, regular_headers, regular_user, db_session):
        r = client.put(
            f"/users/{regular_user.id}",
            headers=regular_headers,
            json={"estado": "I"},
        )
        assert r.status_code == 200
        assert r.json()["estado"] == "A"

    def test_no_puede_editar_otro_usuario(self, client, regular_headers, auth_headers, db_session):
        admin = db_session.query(UserModel).filter(
            UserModel.username == "test_integration"
        ).first()
        r = client.put(
            f"/users/{admin.id}",
            headers=regular_headers,
            json={"nombre": "Inyeccion"},
        )
        assert r.status_code == 403

    def test_admin_si_puede_cambiar_role(self, client, auth_headers, regular_user, db_session):
        r = client.put(
            f"/users/{regular_user.id}",
            headers=auth_headers,
            json={"role": "admin"},
        )
        assert r.status_code == 200
        assert r.json()["role"] == "admin"
        # devolver a regular para el resto de la clase
        r2 = client.put(
            f"/users/{regular_user.id}",
            headers=auth_headers,
            json={"role": "regular"},
        )
        assert r2.status_code == 200 and r2.json()["role"] == "regular"

    def test_patch_me_ignora_role(self, client, regular_headers, regular_user):
        r = client.patch(
            "/users/me",
            headers=regular_headers,
            json={"nombre": "Renombrado Yo", "role": "admin", "estado": "I"},
        )
        assert r.status_code == 200
        body = r.json()
        assert body["nombre"] == "Renombrado Yo"
        assert body["role"] == "regular"
        assert body["estado"] == "A"
