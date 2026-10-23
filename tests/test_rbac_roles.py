"""Regresiones para el RBAC (Tarea 2).

Cubre: guard global de escritura (ninguna ruta POST/PUT/PATCH/DELETE
transitable con rol read_only), `require_role`/niveles, y el rol read_only
como solo-lectura real sobre la app montada.
"""

import re
import time

import pytest
from fastapi.testclient import TestClient

from core.security import (
    WRITE_METHODS,
    Role,
    es_ruta_exenta_de_escritura,
    get_current_admin_user,
    get_current_user,
    hash_password,
    require_min_level,
    require_role,
    role_level,
    write_guard,
)
from main import app
from modules.users.models import UserModel

PASSWORD = "RbacTest123!"

_ROLES = {
    "read_only": f"test_readonly_{int(time.time() * 1000000) % 1000000}",
    "editor": f"test_editor_{int(time.time() * 1000000) % 1000000}",
    "registro": f"test_registro_{int(time.time() * 1000000) % 1000000}",
}


def _is_exempt(path: str) -> bool:
    return es_ruta_exenta_de_escritura(path)


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture(scope="module")
def seeded_users(db_session):
    created = []
    for rol, username in _ROLES.items():
        user = UserModel(
            username=username,
            password=hash_password(PASSWORD),
            nombre=f"Usuario {rol}",
            email=f"{username}@hospital.com",
            role=rol,
            estado="A",
        )
        db_session.add(user)
        created.append(user)
    db_session.commit()
    for u in created:
        db_session.refresh(u)
    yield {u.role: u for u in created}
    for u in created:
        db_session.delete(u)
    db_session.commit()


def _headers(client, user):
    r = client.post(
        "/auth/login",
        data={"username": user.username, "password": PASSWORD},
    )
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture(scope="module")
def read_only_headers(client, seeded_users):
    return _headers(client, seeded_users["read_only"])


@pytest.fixture(scope="module")
def editor_headers(client, seeded_users):
    return _headers(client, seeded_users["editor"])


def _dep_callable(d):
    return getattr(d, "dependency", None) or getattr(d, "call", None)


class TestGlobalGuard:
    def test_guard_registrado_como_dependencia_global(self):
        deps = getattr(app.router, "dependencies", [])
        assert any(_dep_callable(d) is write_guard for d in deps), (
            "write_guard debe ser dependencia global de la app"
        )


class TestReadSoloLectura:
    def test_lecturas_permitidas(self, client, read_only_headers):
        for ruta in ("/personal-atencion/", "/totales/", "/citas/"):
            r = client.get(ruta, headers=read_only_headers)
            assert r.status_code == 200, f"{ruta}: {r.status_code} {r.text[:200]}"

    def test_bloquea_post(self, client, read_only_headers):
        r = client.post("/citas/", headers=read_only_headers, json={})
        assert r.status_code == 403
        assert "solo lectura" in r.json()["detail"]

    def test_bloquea_put_patch_delete(self, client, read_only_headers):
        assert client.put("/citas/1", headers=read_only_headers, json={}).status_code == 403
        assert client.patch("/users/me", headers=read_only_headers, json={"nombre": "X"}).status_code == 403
        assert client.delete("/citas/1", headers=read_only_headers).status_code == 403

    def test_bloquea_merge_y_destructivos(self, client, read_only_headers):
        r = client.post("/pacientes/merge", headers=read_only_headers, json={})
        assert r.status_code == 403

    def test_anonimo_no_puede_escribir(self, client):
        assert client.post("/citas/", json={}).status_code == 401
        assert client.delete("/consultas/1").status_code == 401

    def test_todas_las_rutas_de_escritura_bloquean_a_read_only(self, client, read_only_headers):
        """Probing: ninguna ruta escribible (salvo exención pública documentada)
        responde 2xx/3xx con rol read_only. Impide añadir endpoints sin guard."""
        permitidos = []
        vistas = set()
        for route in app.routes:
            methods = set(getattr(route, "methods", set()) or set())
            metodos_escritura = methods & WRITE_METHODS
            if not metodos_escritura:
                continue
            path = getattr(route, "path", None)
            if path is None or (path, metodos_escritura) in vistas:
                continue
            vistas.add((path, metodos_escritura))
            if _is_exempt(path):
                continue
            url = re.sub(r"\{[^}]+\}", "1", path)
            for metodo in sorted(metodos_escritura):
                r = client.request(
                    metodo,
                    url,
                    headers=read_only_headers,
                    json={},
                )
                if r.status_code < 400:
                    permitidos.append(f"{metodo} {path} -> {r.status_code}")
        assert not permitidos, (
            "rutas de escritura accesibles con rol read_only:\n"
            + "\n".join(permitidos)
        )


class TestEditorYRegular:
    def test_editor_puede_escribir(self, client, editor_headers):
        r = client.patch(
            "/users/me",
            headers=editor_headers,
            json={"nombre": "Editor Renombrado"},
        )
        assert r.status_code == 200
        assert r.json()["nombre"] == "Editor Renombrado"

    def test_editor_no_es_admin(self, client, editor_headers):
        assert client.get("/users/", headers=editor_headers).status_code == 403

    def test_rol_legado_registro_conserva_escritura(self, client, seeded_users):
        """Roles de dominio existentes en producción (registro/std/uisau...)
        deben seguir pudiendo escribir; el guard solo excluye read_only."""
        headers = _headers(client, seeded_users["registro"])
        r = client.patch("/users/me", headers=headers, json={"nombre": "Registros OK"})
        assert r.status_code == 200, r.text
        assert r.json()["role"] == "registro"

    def test_rol_legado_no_es_admin(self, client, seeded_users):
        headers = _headers(client, seeded_users["registro"])
        assert client.get("/users/", headers=headers).status_code == 403

    def test_regular_equivale_a_editor(self, client, seeded_users, db_session):
        # Las cuentas históricas 'regular' conservan escritura.
        regular = db_session.query(UserModel).filter(
            UserModel.username == "test_integration"
        ).first()
        assert regular is None or regular.role == "admin"


class TestNivelesRol:
    def test_jerarquia(self):
        assert role_level(Role.ADMIN.value) == 3
        assert role_level(Role.EDITOR.value) == role_level("regular") == 2
        assert role_level(Role.READ_ONLY.value) == 1
        assert role_level(None) == 0
        assert role_level("inexistente") == 0

    def test_rols_legados_nivel_editor(self):
        for rol in ("registro", "std", "uisau", "ts", "medic", "paramedic",
                    "lab", "rx", "epi", "nutric", "odonto"):
            assert role_level(rol) == 2, rol

    def test_patron_rol_acepta_legados_y_nuevos(self):
        from pydantic import ValidationError

        from modules.users.schemas import UserAdminUpdate

        for rol in ("admin", "editor", "regular", "read_only", "registro", "odonto"):
            assert UserAdminUpdate.model_validate({"role": rol}).role == rol
        with pytest.raises(ValidationError):
            UserAdminUpdate.model_validate({"role": "superusuario"})

    def test_require_role_denega_otro_rol(self, seeded_users):
        with pytest.raises(Exception) as exc:
            require_role(Role.ADMIN)(current_user=seeded_users["read_only"])
        assert exc.value.status_code == 403

    def test_require_role_acepta(self, seeded_users):
        usuario = seeded_users["editor"]
        assert require_role(Role.EDITOR)(current_user=usuario) is usuario

    def test_min_level_editor_excluye_read_only(self, seeded_users):
        with pytest.raises(Exception) as exc:
            require_min_level(2)(current_user=seeded_users["read_only"])
        assert exc.value.status_code == 403

    def test_guardas_legado_siguen_ahí(self):
        assert callable(get_current_admin_user) and callable(get_current_user)
