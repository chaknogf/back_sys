import pytest
import time as _time
from datetime import datetime, timedelta
from core.database import SessionLocal
from modules.pacientes.models import PacienteModel
from modules.medicos.models import MedicoModel
from modules.defunciones.models import DefuncionModel


created_ids = {
    "medicos": [],
    "pacientes": [],
    "defunciones": [],
}


def cleanup():
    db = SessionLocal()
    try:
        for did in created_ids["defunciones"]:
            db.query(DefuncionModel).filter(DefuncionModel.id == did).delete()
        for pid in created_ids["pacientes"]:
            db.query(PacienteModel).filter(PacienteModel.id == pid).delete()
        for mid in created_ids["medicos"]:
            db.query(MedicoModel).filter(MedicoModel.id == mid).delete()
        db.commit()
    finally:
        db.close()


def _sufijo():
    return str(int(_time.time() * 1000000))[-6:]


class TestDefunciones:
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        yield
        cleanup()

    def _crear_medico(self, client):
        s = _sufijo()
        r = client.post(
            "/medicos/",
            json={
                "nombre": f"Dr. Forense {s}",
                "colegiado": int(s),
                "dpi": 1234567890123,
                "sexo": "M",
                "especialidad": "MEDICINA_FORENSE",
            },
        )
        assert r.status_code in (200, 201)
        data = r.json()
        created_ids["medicos"].append(data["id"])
        return data

    def _crear_paciente(self, client, auth_headers, sexo="M", fecha_nac="1980-05-15"):
        s = _sufijo()
        r = client.post(
            "/pacientes/",
            headers=auth_headers,
            json={
                "nombre": {
                    "primer_nombre": f"Difunto{s}",
                    "primer_apellido": f"Prueba{s}",
                },
                "sexo": sexo,
                "fecha_nacimiento": fecha_nac,
            },
        )
        assert r.status_code == 201
        data = r.json()
        created_ids["pacientes"].append(data["id"])
        return data

    def test_create_defuncion(self, client, auth_headers):
        medico = self._crear_medico(client)
        paciente = self._crear_paciente(client, auth_headers)
        now = datetime.now().isoformat()

        r = client.post(
            "/defunciones/",
            headers=auth_headers,
            json={
                "medico_id": medico["id"],
                "paciente_id": paciente["id"],
                "fecha_defuncion": now,
                "causa_a": "Infarto agudo de miocardio",
                "causa_b": "Hipertensión arterial",
                "fue_presunto": "ACCIDENTE",
            },
        )
        assert r.status_code == 201
        data = r.json()
        assert data["paciente_id"] == paciente["id"]
        assert data["medico_id"] == medico["id"]
        assert data["causa_a"] == "Infarto agudo de miocardio"
        assert data["fallecido_edad_anios"] is not None
        created_ids["defunciones"].append(data["id"])

    def test_create_defuncion_fetal(self, client, auth_headers):
        medico = self._crear_medico(client)
        madre = self._crear_paciente(client, auth_headers, sexo="F", fecha_nac="1995-03-20")

        r = client.post(
            "/defunciones/",
            headers=auth_headers,
            json={
                "medico_id": medico["id"],
                "paciente_id": madre["id"],
                "fecha_defuncion": datetime.now().isoformat(),
                "es_fetal": True,
                "fetal_sexo": "M",
                "fetal_semanas_gestacion": 38,
                "fetal_via_parto": "CESAREA",
                "embarazos_previvos_vivos": 2,
                "fetal_causas_fetales": "Asfixia perinatal",
            },
        )
        assert r.status_code == 201
        data = r.json()
        assert data["es_fetal"] is True
        assert data["fetal_sexo"] == "M"
        assert data["fetal_semanas_gestacion"] == 38
        created_ids["defunciones"].append(data["id"])

    def test_list_defunciones(self, client, auth_headers):
        r = client.get("/defunciones/", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert "total" in data
        assert "defunciones" in data
        assert isinstance(data["defunciones"], list)

    def test_get_defuncion(self, client, auth_headers):
        medico = self._crear_medico(client)
        paciente = self._crear_paciente(client, auth_headers)

        cr = client.post(
            "/defunciones/",
            headers=auth_headers,
            json={
                "medico_id": medico["id"],
                "paciente_id": paciente["id"],
                "fecha_defuncion": datetime.now().isoformat(),
                "causa_a": "Paro cardíaco",
            },
        )
        def_id = cr.json()["id"]
        created_ids["defunciones"].append(def_id)

        r = client.get(f"/defunciones/{def_id}", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == def_id
        assert data["paciente"] is not None
        assert data["paciente"]["nombre_completo"] is not None

    def test_get_defuncion_not_found(self, client, auth_headers):
        r = client.get("/defunciones/999999", headers=auth_headers)
        assert r.status_code == 404

    def test_update_defuncion(self, client, auth_headers):
        medico = self._crear_medico(client)
        paciente = self._crear_paciente(client, auth_headers)

        cr = client.post(
            "/defunciones/",
            headers=auth_headers,
            json={
                "medico_id": medico["id"],
                "paciente_id": paciente["id"],
                "fecha_defuncion": datetime.now().isoformat(),
                "causa_a": "Causa original",
            },
        )
        def_id = cr.json()["id"]
        created_ids["defunciones"].append(def_id)

        r = client.patch(
            f"/defunciones/{def_id}",
            headers=auth_headers,
            json={
                "causa_a": "Causa actualizada",
                "causa_b": "Nueva causa secundaria",
            },
        )
        assert r.status_code == 200
        data = r.json()
        assert data["causa_a"] == "Causa actualizada"
        assert data["causa_b"] == "Nueva causa secundaria"

    def test_delete_defuncion(self, client, auth_headers):
        medico = self._crear_medico(client)
        paciente = self._crear_paciente(client, auth_headers)

        cr = client.post(
            "/defunciones/",
            headers=auth_headers,
            json={
                "medico_id": medico["id"],
                "paciente_id": paciente["id"],
                "fecha_defuncion": datetime.now().isoformat(),
            },
        )
        def_id = cr.json()["id"]
        created_ids["defunciones"].append(def_id)

        r = client.delete(f"/defunciones/{def_id}", headers=auth_headers)
        assert r.status_code == 204
        created_ids["defunciones"].remove(def_id)

        r = client.get(f"/defunciones/{def_id}", headers=auth_headers)
        assert r.status_code == 404

    def test_registrar_defuncion_endpoint(self, client, auth_headers):
        medico = self._crear_medico(client)
        paciente = self._crear_paciente(client, auth_headers)

        r = client.post(
            f"/defunciones/registrar/{paciente['id']}",
            headers=auth_headers,
            json={
                "medico_id": medico["id"],
                "fecha_defuncion": datetime.now().isoformat(),
                "causa_a": "Hemorragia interna",
            },
        )
        assert r.status_code == 201
        data = r.json()
        assert data["paciente_id"] == paciente["id"]
        created_ids["defunciones"].append(data["id"])

        rp = client.get(f"/pacientes/{paciente['id']}", headers=auth_headers)
        assert rp.status_code == 200
        assert rp.json()["estado"] == "F"

    def test_registrar_defuncion_ya_fallecido(self, client, auth_headers):
        medico = self._crear_medico(client)
        paciente = self._crear_paciente(client, auth_headers)

        r = client.post(
            f"/defunciones/registrar/{paciente['id']}",
            headers=auth_headers,
            json={"medico_id": medico["id"]},
        )
        def_id = r.json()["id"]
        created_ids["defunciones"].append(def_id)

        r2 = client.post(
            f"/defunciones/registrar/{paciente['id']}",
            headers=auth_headers,
            json={"medico_id": medico["id"]},
        )
        assert r2.status_code == 400

    def test_patch_paciente_v_to_f_auto_defuncion(self, client, auth_headers):
        paciente = self._crear_paciente(client, auth_headers)
        pid = paciente["id"]

        r = client.patch(
            f"/pacientes/{pid}",
            headers=auth_headers,
            json={"estado": "F"},
            params={"accion": "mantener"},
        )
        assert r.status_code == 200

        r2 = client.get("/defunciones/", headers=auth_headers)
        defs = [d for d in r2.json()["defunciones"] if d["paciente_id"] == pid]
        assert len(defs) == 1
        created_ids["defunciones"].append(defs[0]["id"])

    def test_buscar_pacientes_fallecidos(self, client, auth_headers):
        paciente = self._crear_paciente(client, auth_headers)
        pid = paciente["id"]

        r = client.patch(
            f"/pacientes/{pid}",
            headers=auth_headers,
            json={"estado": "F"},
            params={"accion": "mantener"},
        )
        assert r.status_code == 200

        r2 = client.get(
            "/defunciones/pacientes",
            headers=auth_headers,
        )
        assert r2.status_code == 200
        data = r2.json()
        assert "total" in data
        assert "pacientes" in data
        found = [p for p in data["pacientes"] if p["id"] == pid]
        assert len(found) == 1
        assert found[0]["estado"] == "F"
        if found[0].get("defuncion"):
            created_ids["defunciones"].append(found[0]["defuncion"]["id"])

    def test_buscar_pacientes_fallecidos_por_nombre(self, client, auth_headers):
        s = _sufijo()
        r = client.post(
            "/pacientes/",
            headers=auth_headers,
            json={
                "nombre": {
                    "primer_nombre": f"FallecidoBusqueda{s}",
                    "primer_apellido": "Test",
                },
                "sexo": "M",
                "fecha_nacimiento": "1970-01-01",
            },
        )
        pid = r.json()["id"]
        created_ids["pacientes"].append(pid)

        client.patch(
            f"/pacientes/{pid}",
            headers=auth_headers,
            json={"estado": "F"},
            params={"accion": "mantener"},
        )

        r2 = client.get(
            f"/defunciones/pacientes?q=FallecidoBusqueda",
            headers=auth_headers,
        )
        assert r2.status_code == 200
        data = r2.json()
        assert data["total"] >= 1

    def test_paciente_f_to_v_desactiva_defuncion(self, client, auth_headers):
        """Cambiar paciente de F a V debe poner defuncion.estado = I"""
        paciente = self._crear_paciente(client, auth_headers)
        pid = paciente["id"]

        # Marcar como fallecido → se crea defunción automática
        r = client.patch(
            f"/pacientes/{pid}",
            headers=auth_headers,
            json={"estado": "F"},
            params={"accion": "mantener"},
        )
        assert r.status_code == 200

        r2 = client.get(f"/defunciones/?paciente_id={pid}&estado=", headers=auth_headers)
        assert r2.status_code == 200
        assert r2.json()["total"] == 1
        def_id = r2.json()["defunciones"][0]["id"]
        assert r2.json()["defunciones"][0]["estado"] == "A"
        created_ids["defunciones"].append(def_id)

        # Cambiar de F a A (desfallecer) → defunción debe quedar I
        r = client.patch(
            f"/pacientes/{pid}",
            headers=auth_headers,
            json={"estado": "A"},
            params={"accion": "mantener"},
        )
        assert r.status_code == 200

        r3 = client.get(f"/defunciones/{def_id}", headers=auth_headers)
        assert r3.status_code == 200
        assert r3.json()["estado"] == "I"

        # Ya no aparece en listado default (solo A)
        r4 = client.get(f"/defunciones/?paciente_id={pid}", headers=auth_headers)
        assert r4.json()["total"] == 0

    def test_paciente_vuelve_a_f_reactiva_defuncion(self, client, auth_headers):
        """Paciente con defunción inactiva que vuelve a F debe reactivarla (estado=A)"""
        paciente = self._crear_paciente(client, auth_headers)
        pid = paciente["id"]

        # F → se crea defunción activa
        client.patch(
            f"/pacientes/{pid}",
            headers=auth_headers,
            json={"estado": "F"},
            params={"accion": "mantener"},
        )
        r = client.get(f"/defunciones/?paciente_id={pid}&estado=", headers=auth_headers)
        def_id = r.json()["defunciones"][0]["id"]
        created_ids["defunciones"].append(def_id)

        # F → A → defunción se desactiva
        client.patch(
            f"/pacientes/{pid}",
            headers=auth_headers,
            json={"estado": "A"},
            params={"accion": "mantener"},
        )

        # A → F → defunción debe reactivarse
        client.patch(
            f"/pacientes/{pid}",
            headers=auth_headers,
            json={"estado": "F"},
            params={"accion": "mantener"},
        )

        r2 = client.get(f"/defunciones/{def_id}", headers=auth_headers)
        assert r2.status_code == 200
        assert r2.json()["estado"] == "A"

        # Aparece en listado default
        r3 = client.get(f"/defunciones/?paciente_id={pid}", headers=auth_headers)
        assert r3.json()["total"] == 1
        assert r3.json()["defunciones"][0]["estado"] == "A"

    def test_paciente_f_sin_defuncion_previa_crea_nueva(self, client, auth_headers):
        """Paciente sin defunción previa que pasa a F debe crear un registro nuevo"""
        paciente = self._crear_paciente(client, auth_headers)
        pid = paciente["id"]

        # Verificar que no tiene defunción
        r0 = client.get(f"/defunciones/?paciente_id={pid}&estado=", headers=auth_headers)
        assert r0.json()["total"] == 0

        # Pasar a F
        r = client.patch(
            f"/pacientes/{pid}",
            headers=auth_headers,
            json={"estado": "F"},
            params={"accion": "mantener"},
        )
        assert r.status_code == 200

        # Debe tener defunción activa
        r1 = client.get(f"/defunciones/?paciente_id={pid}&estado=", headers=auth_headers)
        assert r1.json()["total"] == 1
        d = r1.json()["defunciones"][0]
        assert d["estado"] == "A"
        assert d["paciente_id"] == pid
        assert d["fecha_defuncion"] is not None, "La defunción autogenerada debe tener fecha"
        assert d["paciente"] is not None, "Debe incluir datos del paciente vía JOIN"
        assert d["paciente"]["nombre_completo"] is not None, "Debe mostrar nombre del paciente"
        assert d["paciente"]["fecha_nacimiento"] is not None, "Debe mostrar fecha_nacimiento del paciente"
        created_ids["defunciones"].append(d["id"])
