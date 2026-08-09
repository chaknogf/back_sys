"""End-to-end del endpoint /prestamos (crear, listar por nombre, devolver,
reactivar, desactivar), creando sus propios pacientes de prueba para ser
independiente del orden de otros Test*.
"""
import pytest
import time
from datetime import datetime, timezone, timedelta

created_ids = {"pacientes": [], "prestamos": []}


@pytest.fixture(scope="module")
def _datos(client):
    from core.database import SessionLocal
    from sqlalchemy import text

    db = SessionLocal()
    if created_ids["pacientes"]:
        db.execute(text("DELETE FROM pacientes WHERE id = ANY(:ids)"),
                   {"ids": created_ids["pacientes"]})
        db.commit()
    if created_ids["prestamos"]:
        db.execute(text("DELETE FROM prestamos WHERE id = ANY(:ids)"),
                   {"ids": created_ids["prestamos"]})
        db.commit()
    created_ids["pacientes"] = []
    created_ids["prestamos"] = []
    db.close()


class TestEndpointPrestamos:
    def test_crear(self, client, auth_headers, _datos):
        marca = int(time.time() * 1000)
        r = client.post(
            "/pacientes/",
            headers=auth_headers,
            json={
                "nombre": {
                    "primer_nombre": f"E2E{marca}",
                    "primer_apellido": "Prestamos",
                },
                "sexo": "F",
            },
        )
        assert r.status_code in (200, 201), r.text
        pid = r.json().get("id")
        created_ids["pacientes"].append(pid)
        r = client.post(
            "/prestamos/",
            headers=auth_headers,
            json={
                "id_paciente": pid,
                "expediente": "E2E-PRESTAMO",
                "solicitante": "Dr. E2E",
                "motivo": "Integracion",
            },
        )
        assert r.status_code in (200, 201), r.text
        created_ids["prestamos"].append(r.json()["id"])

    def test_listar_filtro_nombre(self, client, auth_headers, _datos):
        r = client.get(
            "/prestamos/",
            headers=auth_headers,
            params={"nombre_paciente": "E2E", "activo": "true", "limit": "50"},
        )
        assert r.status_code == 200, r.text
        assert "items" in r.json()

    def test_listar_filtro_rango_fechas(self, client, auth_headers, _datos):
        """El préstamo creado hoy debe aparecer en un rango que abarque hoy,
        y quedar fuera de un rango completamente en el pasado."""
        if not created_ids["prestamos"]:
            pytest.skip("No prestamo creado")
        pid = created_ids["prestamos"][-1]

        desde = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        hasta = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

        # Rango amplio que abarca hoy → debe incluir el préstamo creado en el test
        r = client.get(
            "/prestamos/",
            headers=auth_headers,
            params={
                "activo": "true",
                "limit": "100",
                "fecha_desde": desde,
                "fecha_hasta": hasta,
            },
        )
        assert r.status_code == 200, r.text
        ids_amplio = {item["id"] for item in r.json()["items"]}
        assert pid in ids_amplio, "El rango amplio debería incluir el préstamo de hoy"

        # Rango solo en el pasado → no debe incluir el préstamo de hoy
        r = client.get(
            "/prestamos/",
            headers=auth_headers,
            params={
                "activo": "true",
                "limit": "100",
                "fecha_desde": "2000-01-01",
                "fecha_hasta": "2000-01-31",
            },
        )
        assert r.status_code == 200, r.text
        ids_pasado = {item["id"] for item in r.json()["items"]}
        assert pid not in ids_pasado, "Un rango en el pasado no debería incluirlo"

    def test_devolver(self, client, auth_headers, _datos):
        if not created_ids["prestamos"]:
            pytest.skip("No prestamo creado")
        pid = created_ids["prestamos"][0]
        r = client.put(
            f"/prestamos/{pid}",
            headers=auth_headers,
            json={"fecha_devolucion": datetime.now(timezone.utc).isoformat()},
        )
        assert r.status_code == 200, r.text
        assert r.json()["activo"] is False
        assert r.json().get("usuario_recibe")

    def test_quitar_devolucion_reactiva(self, client, auth_headers, _datos):
        if not created_ids["prestamos"]:
            pytest.skip("No prestamo creado")
        pid = created_ids["prestamos"][0]
        r = client.put(
            f"/prestamos/{pid}",
            headers=auth_headers,
            json={"fecha_devolucion": None},
        )
        assert r.status_code == 200, r.text
        assert r.json()["activo"] is True
        assert r.json().get("usuario_recibe") is None

    def test_eliminar(self, client, auth_headers, _datos):
        if not created_ids["prestamos"]:
            pytest.skip("No prestamo creado")
        pid = created_ids["prestamos"][-1]
        r = client.delete(f"/prestamos/{pid}", headers=auth_headers)
        assert r.status_code == 200, r.text