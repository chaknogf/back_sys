import pytest
import time as _time

from core.database import SessionLocal
from modules.especialidades.models import EspecialidadModel
from modules.quirofano.models import ProcedimientoQuirofanoModel


created_ids = {
    "especialidades": [],
    "procedimientos_quirofano": [],
}


def _sufijo() -> str:
    return str(int(_time.time() * 1000000))[-6:]


def cleanup():
    db = SessionLocal()
    try:
        for tid in created_ids["procedimientos_quirofano"]:
            db.query(ProcedimientoQuirofanoModel).filter(
                ProcedimientoQuirofanoModel.procedimiento_quirofano_id == tid
            ).delete()
        for eid in created_ids["especialidades"]:
            db.query(EspecialidadModel).filter(
                EspecialidadModel.id == eid
            ).delete()
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()
    created_ids["especialidades"].clear()
    created_ids["procedimientos_quirofano"].clear()


class TestEspecialidades:
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        yield
        cleanup()

    def _crear(self, client, auth_headers, **overrides):
        s = _sufijo()
        payload = {
            "nombre": f"TEST-ESP-{s}",
            "abreviatura": f"E{s[-4:]}",
            "codigo": f"C{s[-4:]}",
        }
        payload.update(overrides)
        r = client.post("/especialidades/", headers=auth_headers, json=payload)
        assert r.status_code == 201, r.text
        data = r.json()
        created_ids["especialidades"].append(data["id"])
        return data

    def test_crear_defaults_estado_y_sop(self, client, auth_headers):
        data = self._crear(client, auth_headers)
        assert data["estado"] is True
        assert data["sop"] is True

    def test_crear_con_flags_false(self, client, auth_headers):
        data = self._crear(client, auth_headers, estado=False, sop=False)
        assert data["estado"] is False
        assert data["sop"] is False

    def test_filtro_estado_true_sop_true(self, client, auth_headers):
        activa = self._crear(client, auth_headers, estado=True, sop=True)
        inactiva = self._crear(client, auth_headers, estado=False, sop=True)
        sin_sop = self._crear(client, auth_headers, estado=True, sop=False)

        r = client.get(
            "/especialidades/",
            headers=auth_headers,
            params={"estado": "true", "sop": "true"},
        )
        assert r.status_code == 200
        ids = {e["id"] for e in r.json()}
        assert activa["id"] in ids
        assert inactiva["id"] not in ids
        assert sin_sop["id"] not in ids

    def test_filtro_estado_false(self, client, auth_headers):
        activa = self._crear(client, auth_headers, estado=True)
        inactiva = self._crear(client, auth_headers, estado=False)

        r = client.get(
            "/especialidades/",
            headers=auth_headers,
            params={"estado": "false"},
        )
        assert r.status_code == 200
        ids = {e["id"] for e in r.json()}
        assert inactiva["id"] in ids
        assert activa["id"] not in ids

    def test_actualizar_flags(self, client, auth_headers):
        data = self._crear(client, auth_headers, estado=True, sop=True)
        r = client.put(
            f"/especialidades/{data['id']}",
            headers=auth_headers,
            json={"estado": False, "sop": False},
        )
        assert r.status_code == 200
        body = r.json()
        assert body["estado"] is False
        assert body["sop"] is False

    def test_nombre_duplicado(self, client, auth_headers):
        data = self._crear(client, auth_headers)
        r = client.post(
            "/especialidades/",
            headers=auth_headers,
            json={"nombre": data["nombre"]},
        )
        assert r.status_code == 409

    def test_eliminar(self, client, auth_headers):
        data = self._crear(client, auth_headers)
        r = client.delete(f"/especialidades/{data['id']}", headers=auth_headers)
        assert r.status_code == 200
        created_ids["especialidades"].remove(data["id"])

        r = client.get(f"/especialidades/{data['id']}", headers=auth_headers)
        assert r.status_code == 404

    def test_eliminar_referenciada_da_409(self, client, auth_headers):
        data = self._crear(client, auth_headers)
        s = _sufijo()
        r = client.post(
            "/quirofano/procedimientos-quirofano/",
            headers=auth_headers,
            json={"nombre": f"Proc Test {s}", "especialidad_id": data["id"]},
        )
        assert r.status_code == 201, r.text
        created_ids["procedimientos_quirofano"].append(r.json()["procedimiento_quirofano_id"])

        r = client.delete(f"/especialidades/{data['id']}", headers=auth_headers)
        assert r.status_code == 409
