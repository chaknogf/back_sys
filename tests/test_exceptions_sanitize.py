"""Regresiones para el saneamiento de excepciones (Tarea 3).

Garantiza que ni la validación 422, ni IntegrityError/DataError/Exception
500 exponen cuerpo crudo, SQL, mensajes de psycopg2 ni valores de entrada.

Los errores de BD reales se provocan en una app espejo que usa los mismos
handlers de `core.exceptions` (sin el guard global, para poder montar probes).
"""

import pytest
from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text

from core.database import engine
from core.exceptions import register_exception_handlers
from main import app


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture(scope="module")
def probe_app():
    router = APIRouter(prefix="/__probe__")

    @router.get("/integrity")
    def _integrity_fk():
        # FK real hacia pacientes(id); 999999999 no existe -> IntegrityError.
        with engine.connect() as conn, conn.begin():
            conn.execute(
                text(
                    "INSERT INTO prestamos (id_paciente, solicitante) "
                    "VALUES (999999999, 'probe')"
                )
            )
        return {"ok": True}

    @router.get("/boom")
    def _boom():
        raise RuntimeError("fuga de internals user=admin table=pacientes secret")

    espejo = FastAPI()
    register_exception_handlers(espejo)
    espejo.include_router(router)
    return TestClient(espejo, raise_server_exceptions=False)


def _marcas_fuga(texto: str) -> list[str]:
    marcas = []
    for marca in ("psycopg2", "INSERT", "constraint", "Traceback", "secret", "RuntimeError"):
        if marca.lower() in texto.lower():
            marcas.append(marca)
    return marcas


class TestValidacion422:
    def test_no_devuelve_body_ni_input(self, client, auth_headers):
        r = client.post(
            "/consultas/registro",
            headers=auth_headers,
            json={"paciente_id": "NO-NUMERICO", "documento": "SECRETO-PHI-123"},
        )
        assert r.status_code == 422
        body = r.json()
        assert "body" not in body
        assert "SECRETO-PHI-123" not in r.text
        for err in body.get("errors", []):
            assert "input" not in err
            assert "ctx" not in err

    def test_tiene_detail_y_request_id(self, client, auth_headers):
        r = client.post("/users/", headers=auth_headers, json={})
        assert r.status_code == 422
        body = r.json()
        assert body["detail"] == "Error de validación"
        assert len(body["request_id"]) == 12
        assert "errors" in body


class TestIntegridadYFuga:
    def test_integrity_error_sin_sql(self, probe_app):
        r = probe_app.get("/__probe__/integrity")
        assert r.status_code == 409
        body = r.json()
        assert body["detail"]
        assert "request_id" in body
        assert not _marcas_fuga(r.text), r.text

    def test_500_sin_internals(self, probe_app):
        r = probe_app.get("/__probe__/boom")
        assert r.status_code == 500
        body = r.json()
        assert body["detail"] == "Error interno del servidor"
        assert not _marcas_fuga(r.text), r.text

    def test_data_error_detalle_amable(self, client, auth_headers):
        # colegiado de 300 chars: la app lo rechaza (validación o BD) sin
        # exponer el texto crudo de PostgreSQL.
        r = client.post(
            "/personal-atencion/",
            headers=auth_headers,
            json={"nombre": "X", "colegiado": "C" * 300},
        )
        assert r.status_code in (400, 409, 422)
        assert not _marcas_fuga(r.text), r.text
