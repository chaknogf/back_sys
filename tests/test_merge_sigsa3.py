"""Integración: el merge de pacientes reasigna registros SIGSA-3 como consultas.

Usa la cuenta admin existente (no crea usuarios). Crea pacientes y registros
sintéticos con un marcador único y los elimina al terminar.
"""

import time

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from core.database import SessionLocal
from main import app


MARCA = f"ZZTESTMERGE{int(time.time() * 1000) % 10**8}"


@pytest.fixture(scope="module")
def admin_headers():
    c = TestClient(app)
    r = c.post("/auth/login", data={"username": "admin", "password": "admin"})
    if r.status_code != 200:
        pytest.skip("admin/admin no disponible")
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def _crear_paciente(client, headers, sufijo):
    r = client.post(
        "/pacientes/",
        headers=headers,
        json={
            "nombre": {"primer_nombre": MARCA, "primer_apellido": sufijo},
            "sexo": "F",
            "fecha_nacimiento": "1990-01-01",
        },
    )
    assert r.status_code == 201, r.text
    return r.json()["id"]


def test_merge_reasigna_sigsa3_y_registros_normalizados(admin_headers):
    client = TestClient(app)
    principal = _crear_paciente(client, admin_headers, "PRINCIPAL")
    duplicado = _crear_paciente(client, admin_headers, "DUPLICADO")

    db = SessionLocal()
    try:
        sig_id = db.execute(text(
            "INSERT INTO sigsa3 (paciente_id, nombre_paciente, fecha_consulta) "
            "VALUES (:p, :n, CURRENT_DATE) RETURNING id"
        ), {"p": duplicado, "n": MARCA}).scalar()
        reg_id = db.execute(text(
            "INSERT INTO sigsa3_registros (paciente_id, fecha_consulta, sin_asociar, nombre_paciente, sigsa3_id) "
            "VALUES (:p, CURRENT_DATE, FALSE, :n, :s) RETURNING id"
        ), {"p": duplicado, "n": MARCA, "s": sig_id}).scalar()
        db.commit()

        r = client.post(
            f"/pacientes/merge?principal_id={principal}&ids={principal}&ids={duplicado}",
            headers=admin_headers,
        )
        assert r.status_code == 200, r.text

        pid_staging = db.execute(text("SELECT paciente_id FROM sigsa3 WHERE id=:i"), {"i": sig_id}).scalar()
        pid_reg = db.execute(text("SELECT paciente_id FROM sigsa3_registros WHERE id=:i"), {"i": reg_id}).scalar()
        assert pid_staging == principal
        assert pid_reg == principal
    finally:
        db.execute(text("DELETE FROM sigsa3_registros WHERE id=:i"), {"i": reg_id})
        db.execute(text("DELETE FROM sigsa3 WHERE id=:i"), {"i": sig_id})
        db.execute(text("DELETE FROM pacientes WHERE id IN (:a, :b) AND nombre_completo LIKE :m"),
                   {"a": principal, "b": duplicado, "m": f"%{MARCA}%"})
        db.commit()
        db.close()
