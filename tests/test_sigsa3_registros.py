import time as _time
from datetime import date, timedelta

import pytest

from core.database import SessionLocal
from modules.pacientes.models import PacienteModel
from modules.medicos.models import MedicoModel
from modules.sigsa3.models import Sigsa3RegistroModel


def _sufijo():
    return str(int(_time.time() * 1000000))[-6:]


def _cleanup(paciente_id=None, medico_id=None, registro_id=None):
    db = SessionLocal()
    try:
        if registro_id is not None:
            db.query(Sigsa3RegistroModel).filter(
                Sigsa3RegistroModel.id == registro_id
            ).delete(synchronize_session=False)
        if medico_id is not None:
            db.query(MedicoModel).filter(MedicoModel.id == medico_id).delete(
                synchronize_session=False
            )
        if paciente_id is not None:
            db.query(PacienteModel).filter(PacienteModel.id == paciente_id).delete(
                synchronize_session=False
            )
        db.commit()
    finally:
        db.close()


class TestSigsa3Registros:
    PACIENTE_ID = None
    MEDICO_ID = None
    REGISTRO_ID = None

    def test_create_paciente_helper(self, client, auth_headers):
        s = _sufijo()
        r = client.post(
            "/pacientes/",
            headers=auth_headers,
            json={
                "nombre": {
                    "primer_nombre": "SIG",
                    "segundo_nombre": f"Registro{s}",
                    "primer_apellido": "Test",
                    "segundo_apellido": f"Normalizado{s}",
                },
                "sexo": "F",
                "fecha_nacimiento": "1985-05-20",
            },
        )
        assert r.status_code == 201
        TestSigsa3Registros.PACIENTE_ID = r.json()["id"]

        r = client.post(
            "/medicos/",
            headers=auth_headers,
            json={
                "nombre": f"Medico Test {s}",
                "colegiado": f"{s}",
            },
        )
        assert r.status_code == 201
        TestSigsa3Registros.MEDICO_ID = r.json()["id"]

    def test_create_sigsa3_registro(self, client, auth_headers):
        pid = TestSigsa3Registros.PACIENTE_ID
        mid = TestSigsa3Registros.MEDICO_ID
        if not pid or not mid:
            pytest.skip("No paciente/medico creado")
        r = client.post(
            "/sigsa3-registros/",
            headers=auth_headers,
            json={
                "paciente_id": pid,
                "medico_id": mid,
                "fecha_consulta": date.today().isoformat(),
                "tipo_consulta_id": 1,
                "control": "SIG-TEST",
                "semana_gestacional": 0,
                "especialidad_id": 1,
            },
        )
        assert r.status_code == 201
        data = r.json()
        assert data["id"] > 0
        assert data["paciente_id"] == pid
        assert data["medico_id"] == mid
        assert data["fecha_consulta"] == date.today().isoformat()
        TestSigsa3Registros.REGISTRO_ID = data["id"]

    def test_create_sigsa3_registro_sin_medico(self, client, auth_headers):
        """medico_id es obligatorio: crear sin él debe dar 422."""
        pid = TestSigsa3Registros.PACIENTE_ID
        if not pid:
            pytest.skip("No paciente creado")
        r = client.post(
            "/sigsa3-registros/",
            headers=auth_headers,
            json={
                "paciente_id": pid,
                "fecha_consulta": date.today().isoformat(),
                "tipo_consulta_id": 1,
            },
        )
        assert r.status_code == 422

    def test_create_sigsa3_registro_fk_invalido(self, client, auth_headers):
        """FK de medico inexistente debe dar 404 (coincidencias garantizadas)."""
        pid = TestSigsa3Registros.PACIENTE_ID
        if not pid:
            pytest.skip("No paciente creado")
        r = client.post(
            "/sigsa3-registros/",
            headers=auth_headers,
            json={
                "paciente_id": pid,
                "medico_id": 999999,
                "fecha_consulta": date.today().isoformat(),
                "tipo_consulta_id": 1,
            },
        )
        assert r.status_code == 404

    def test_create_sigsa3_registro_consulta_conflicto(self, client, auth_headers):
        """consulta_id de otro paciente debe dar 409 (coherencia cruzada)."""
        pid = TestSigsa3Registros.PACIENTE_ID
        if not pid:
            pytest.skip("No paciente creado")
        # Crear un paciente B con una consulta
        s = _sufijo()
        r = client.post(
            "/pacientes/",
            headers=auth_headers,
            json={
                "nombre": {
                    "primer_nombre": "OTRO",
                    "primer_apellido": f"Paciente{s}",
                },
                "sexo": "F",
                "fecha_nacimiento": "1990-01-01",
            },
        )
        assert r.status_code == 201
        otro_pid = r.json()["id"]
        r = client.post(
            "/consultas/registro",
            headers=auth_headers,
            json={
                "paciente_id": otro_pid,
                "tipo_consulta": 1,
                "especialidad": "Medicina General",
                "servicio": "COEX",
                "documento": f"DOC-{s}",
                "fecha_consulta": date.today().isoformat(),
                "hora_consulta": "08:00:00",
            },
        )
        assert r.status_code == 201
        con_id = r.json()["id"]
        try:
            r2 = client.post(
                "/sigsa3-registros/",
                headers=auth_headers,
                json={
                    "paciente_id": pid,
                    "medico_id": TestSigsa3Registros.MEDICO_ID,
                    "consulta_id": con_id,
                    "fecha_consulta": date.today().isoformat(),
                    "tipo_consulta_id": 1,
                },
            )
            assert r2.status_code == 409
        finally:
            db = SessionLocal()
            try:
                db.query(Sigsa3RegistroModel).filter(
                    Sigsa3RegistroModel.consulta_id == con_id
                ).delete(synchronize_session=False)
                db.query(PacienteModel).filter(
                    PacienteModel.id == otro_pid
                ).delete(synchronize_session=False)
                db.commit()
            finally:
                db.close()

    def test_list_sigsa3_registros(self, client, auth_headers):
        r = client.get("/sigsa3-registros/", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert "total" in data
        assert "registros" in data
        assert isinstance(data["registros"], list)

    def test_list_sigsa3_registros_filtros(self, client, auth_headers):
        pid = TestSigsa3Registros.PACIENTE_ID
        if not pid:
            pytest.skip("No paciente creado")
        r = client.get(
            f"/sigsa3-registros/?paciente_id={pid}&tipo_consulta_id=1",
            headers=auth_headers,
        )
        assert r.status_code == 200
        assert r.json()["total"] >= 1

    def test_get_sigsa3_registro(self, client, auth_headers):
        rid = TestSigsa3Registros.REGISTRO_ID
        if not rid:
            pytest.skip("No registro creado")
        r = client.get(f"/sigsa3-registros/{rid}", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == rid
        assert data["paciente_nombre"]

    def test_get_sigsa3_registro_not_found(self, client, auth_headers):
        r = client.get("/sigsa3-registros/999999", headers=auth_headers)
        assert r.status_code == 404

    def test_update_sigsa3_registro(self, client, auth_headers):
        rid = TestSigsa3Registros.REGISTRO_ID
        if not rid:
            pytest.skip("No registro creado")
        r = client.patch(
            f"/sigsa3-registros/{rid}",
            headers=auth_headers,
            json={"tipo_consulta_id": 3, "control": "SIG-UPDATED"},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["control"] == "SIG-UPDATED"
        assert data["tipo_consulta_id"] == 3

    def test_delete_sigsa3_registro(self, client, auth_headers):
        rid = TestSigsa3Registros.REGISTRO_ID
        if not rid:
            pytest.skip("No registro creado")
        r = client.delete(f"/sigsa3-registros/{rid}", headers=auth_headers)
        assert r.status_code == 204
        r = client.get(f"/sigsa3-registros/{rid}", headers=auth_headers)
        assert r.status_code == 404
        TestSigsa3Registros.REGISTRO_ID = None

    def test_cleanup_paciente_helper(self, client, auth_headers):
        pid = TestSigsa3Registros.PACIENTE_ID
        if not pid:
            return
        _cleanup(
            paciente_id=pid,
            medico_id=TestSigsa3Registros.MEDICO_ID,
            registro_id=TestSigsa3Registros.REGISTRO_ID,
        )
        TestSigsa3Registros.PACIENTE_ID = None
        TestSigsa3Registros.MEDICO_ID = None
