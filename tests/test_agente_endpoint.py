"""Tests E2E del agente: /agente/consulta, feedback y reglas."""
import pytest


def test_consulta_reconocida(client, auth_headers):
    r = client.post("/agente/consulta", params={"pregunta": "¿cuántos pacientes hay?"},
                    headers=auth_headers)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["modelo"] == "agente-rule"
    assert isinstance(body["datos"], list)
    assert "total" in body["columnas"]
    assert body["error"] is None
    assert "sql_generado" not in body


def test_consulta_no_reconocida(client, auth_headers):
    r = client.post("/agente/consulta",
                    params={"pregunta": "¿qué hora es en Marte?"}, headers=auth_headers)
    assert r.status_code == 200
    assert "sql_generado" not in r.json()
    assert "reconozco" in r.json()["respuesta"].lower()


def test_feedback_aprende_sinonimo(client, auth_headers):
    r = client.post("/agente/consulta",
                    params={"pregunta": "cuántos afiliados hay"}, headers=auth_headers)
    assert r.status_code == 200
    r = client.post("/agente/feedback", json={
        "pregunta": "cuántos afiliados hay",
        "respuesta": "No reconozco sobre qué datos preguntas.",
        "correcto": False,
        "correccion": "medicos",
    }, headers=auth_headers)
    assert r.status_code == 200, r.text
    # ahora debe resolver como médicos
    r = client.post("/agente/consulta",
                    params={"pregunta": "cuántos afiliados hay"}, headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["error"] is None


def test_reglas_crud(client, auth_headers):
    r = client.get("/agente/reglas", headers=auth_headers)
    assert r.status_code == 200
    body = r.json()
    assert "items" in body or isinstance(body, list)
    r = client.post("/agente/reglas", json={
        "tipo": "sinonimo_entidad", "clave": "bichos", "valor": "pacientes",
    }, headers=auth_headers)
    assert r.status_code in (200, 201, 409), r.text
    regla = r.json()
    if r.status_code in (200, 201) and regla.get("id"):
        r = client.delete(f"/agente/reglas/{regla['id']}", headers=auth_headers)
        assert r.status_code in (200, 204)