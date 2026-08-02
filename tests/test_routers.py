import pytest
import time as _time
from datetime import date, datetime, timedelta
from core.database import SessionLocal
from modules.pacientes.models import PacienteModel
from modules.medicos.models import MedicoModel
from modules.consultas.models import ConsultaModel
from modules.citas.models import CitaModel
from modules.ciclos.models import CiclosConsulta
from modules.prestamos.models import Prestamo
from modules.procedimientos.models import Procedimiento, ProceMedico
from modules.eventos.models import EventoConsultaModel
from modules.constancias_nacimiento.models import ConstanciaNacimientoModel
from modules.nacimientos.models import NacimientoModel
from modules.encamamiento.models import EncamamientoModel
from modules.sigsa3.models import Sigsa3Model
from modules.users.models import UserModel
from core.security import hash_password

created_ids = {
    "pacientes": [],
    "medicos": [],
    "consultas": [],
    "citas": [],
    "ciclos": [],
    "prestamos": [],
    "procedimientos_catalogo": [],
    "procedimientos_realizados": [],
    "eventos": [],
    "constancias": [],
    "nacimientos": [],
    "encamamiento": [],
    "sigsa3": [],
    "users": [],
}


def cleanup():
    db = SessionLocal()
    try:
        model_map = {
            "pacientes": PacienteModel,
            "medicos": MedicoModel,
            "consultas": ConsultaModel,
            "citas": CitaModel,
            "ciclos": CiclosConsulta,
            "prestamos": Prestamo,
            "procedimientos_catalogo": Procedimiento,
            "procedimientos_realizados": ProceMedico,
            "eventos": EventoConsultaModel,
            "constancias": ConstanciaNacimientoModel,
            "nacimientos": NacimientoModel,
            "encamamiento": EncamamientoModel,
            "sigsa3": Sigsa3Model,
            "users": UserModel,
        }
        for table, ids in created_ids.items():
            if not ids:
                continue
            model = model_map.get(table)
            if model:
                db.query(model).filter(model.id.in_(ids)).delete(
                    synchronize_session=False
                )
        db.commit()
    finally:
        db.close()


def _sufijo():
    return str(int(_time.time() * 1000000))[-6:]


# =====================================================================
# HEALTH
# =====================================================================
class TestHealth:
    def test_health_check(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert data["database"] == "connected"


# =====================================================================
# AUTH
# =====================================================================
class TestAuth:
    def test_login_success(self, client, auth_headers):
        assert "Authorization" in auth_headers
        assert auth_headers["Authorization"].startswith("Bearer ")

    def test_login_fail(self, client):
        r = client.post("/auth/login", data={"username": "no_existe", "password": "x"})
        assert r.status_code == 401

    def test_me(self, client, auth_headers):
        r = client.get("/auth/me", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert data["username"] == "test_integration"
        assert data["role"] == "admin"

    def test_me_no_auth(self, client):
        r = client.get("/auth/me")
        assert r.status_code in (401, 403)


# =====================================================================
# USERS
# =====================================================================
class TestUsers:
    def test_list_users(self, client, auth_headers):
        r = client.get("/users/", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert "total" in data
        assert "usuarios" in data

    def test_get_user(self, client, auth_headers, db_session):
        user = db_session.query(UserModel).filter(
            UserModel.username == "test_integration"
        ).first()
        r = client.get(f"/users/{user.id}", headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["username"] == "test_integration"

    def test_get_user_not_found(self, client, auth_headers):
        r = client.get("/users/999999", headers=auth_headers)
        assert r.status_code == 404

    def test_create_user(self, client, auth_headers, monkeypatch):
        s = _sufijo()
        monkeypatch.setattr(
            "modules.users.service.send_welcome_email",
            lambda *a, **kw: None,
        )
        r = client.post(
            "/users/",
            headers=auth_headers,
            json={
                "username": f"test_user_{s}",
                "password": "TestPass123!",
                "nombre": f"Test User {s}",
                "email": f"test_{s}@hospital.com",
                "role": "regular",
            },
        )
        assert r.status_code in (200, 201)
        data = r.json()
        created_ids["users"].append(data["id"])

    def test_update_user(self, client, auth_headers, db_session):
        user = db_session.query(UserModel).filter(
            UserModel.username == "test_integration"
        ).first()
        r = client.put(
            f"/users/{user.id}",
            headers=auth_headers,
            json={"nombre": "Test Updated"},
        )
        assert r.status_code == 200
        assert r.json()["nombre"] == "Test Updated"

    def test_recover_password(self, client, auth_headers):
        r = client.patch(
            "/users/recuperar",
            headers=auth_headers,
            json={
                "email": "test_integration@hospital.com",
                "password": "NewPass123!",
            },
        )
        assert r.status_code == 200

    def test_delete_user(self, client, auth_headers):
        if not created_ids["users"]:
            pytest.skip("No user created")
        uid = created_ids["users"][-1]
        r = client.delete(f"/users/{uid}", headers=auth_headers)
        assert r.status_code == 204


# =====================================================================
# MEDICOS
# =====================================================================
class TestMedicos:
    def test_create_medico(self, client, auth_headers):
        s = _sufijo()
        r = client.post(
            "/medicos/",
            json={
                "nombre": f"Dr. Test {s}",
                "colegiado": str(int(s)),
                "dpi": 1234567890123,
                "sexo": "M",
                "especialidad_id": 1,
            },
        )
        assert r.status_code in (200, 201)
        data = r.json()
        created_ids["medicos"].append(data["id"])

    def test_list_medicos(self, client, auth_headers):
        r = client.get("/medicos/")
        assert r.status_code == 200
        data = r.json()
        assert "total" in data
        assert "medicos" in data

    def test_list_medicos_with_filter(self, client, auth_headers):
        r = client.get("/medicos/?especialidad_id=1")
        assert r.status_code == 200

    def test_get_medico(self, client, auth_headers):
        if not created_ids["medicos"]:
            pytest.skip("No medico created")
        r = client.get(f"/medicos/{created_ids['medicos'][0]}")
        assert r.status_code == 200

    def test_get_medico_not_found(self, client, auth_headers):
        r = client.get("/medicos/999999")
        assert r.status_code == 404

    def test_update_medico(self, client, auth_headers):
        if not created_ids["medicos"]:
            pytest.skip("No medico created")
        mid = created_ids["medicos"][0]
        # Usar un colegiado único (columna UNIQUE) para no colisionar
        # con registros persistentes de la BD (ej. 99999).
        s = _sufijo()
        r = client.put(
            f"/medicos/{mid}",
            json={
                "nombre": "Dr. Test Updated",
                "colegiado": f"CU{s}",
                "dpi": 1234567890123,
                "sexo": "M",
            },
        )
        assert r.status_code == 200
        assert r.json()["nombre"] == "Dr. Test Updated"

    def test_delete_medico(self, client, auth_headers):
        if not created_ids["medicos"]:
            pytest.skip("No medico created")
        mid = created_ids["medicos"][-1]
        r = client.delete(f"/medicos/{mid}")
        assert r.status_code == 204
        created_ids["medicos"].remove(mid)


# =====================================================================
# PACIENTES
# =====================================================================
class TestPacientes:
    def test_create_paciente(self, client, auth_headers):
        s = _sufijo()
        r = client.post(
            "/pacientes/",
            headers=auth_headers,
            json={
                "nombre": {
                    "primer_nombre": "Juan",
                    "segundo_nombre": f"Paciente{s}",
                    "primer_apellido": "Perez",
                    "segundo_apellido": f"Test{s}",
                },
                "sexo": "M",
                "fecha_nacimiento": "1990-01-15",
            },
        )
        assert r.status_code == 201
        data = r.json()
        created_ids["pacientes"].append(data["id"])

    def test_list_pacientes(self, client, auth_headers):
        r = client.get("/pacientes/", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert "total" in data
        assert "pacientes" in data

    def test_search_paciente_by_name(self, client, auth_headers):
        r = client.get("/pacientes/?nombre=Juan", headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["total"] > 0

    def test_search_paciente_by_sexo(self, client, auth_headers):
        r = client.get("/pacientes/?sexo=M", headers=auth_headers)
        assert r.status_code == 200

    def test_search_paciente_by_estado(self, client, auth_headers):
        r = client.get("/pacientes/?estado=ACTIVO", headers=auth_headers)
        assert r.status_code == 200

    def test_get_paciente(self, client, auth_headers):
        if not created_ids["pacientes"]:
            pytest.skip("No paciente created")
        r = client.get(
            f"/pacientes/{created_ids['pacientes'][0]}", headers=auth_headers
        )
        assert r.status_code == 200
        assert r.json()["nombre"]["primer_nombre"] == "Juan"

    def test_get_paciente_not_found(self, client, auth_headers):
        r = client.get("/pacientes/999999", headers=auth_headers)
        assert r.status_code == 404

    def test_update_paciente(self, client, auth_headers):
        if not created_ids["pacientes"]:
            pytest.skip("No paciente created")
        r = client.patch(
            f"/pacientes/{created_ids['pacientes'][0]}",
            headers=auth_headers,
            json={"sexo": "M"},
            params={"accion": "mantener"},
        )
        assert r.status_code == 200

    def test_get_paciente_by_expediente(self, client, auth_headers, db_session):
        if not created_ids["pacientes"]:
            pytest.skip("No paciente created")
        pac = db_session.get(PacienteModel, created_ids["pacientes"][0])
        if not pac or not pac.expediente:
            pytest.skip("Paciente has no expediente")
        r = client.get(
            f"/pacientes/expediente/{pac.expediente}", headers=auth_headers
        )
        assert r.status_code == 200

    def test_paciente_debug_count(self, client, auth_headers):
        r = client.get("/pacientes/debug/count", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert "total" in data

    def test_paciente_duplicados_nombres_similares(self, client, auth_headers):
        r = client.get("/pacientes/duplicados/nombres-similares", headers=auth_headers)
        assert r.status_code == 200

    def test_paciente_neonatales(self, client, auth_headers):
        r = client.get("/pacientes/neonatales", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert "total" in data
        assert "pacientes" in data


# =====================================================================
# MADRE-HIJO
# =====================================================================
class TestMadreHijo:
    MADRE_ID = None
    _fecha_nac = None

    @classmethod
    def _fecha(cls) -> str:
        if cls._fecha_nac is None:
            cls._fecha_nac = date.today().isoformat()
        return cls._fecha_nac

    def test_create_mother(self, client, auth_headers):
        s = _sufijo()
        r = client.post(
            "/pacientes/",
            headers=auth_headers,
            json={
                "nombre": {
                    "primer_nombre": "Maria",
                    "segundo_nombre": f"Madre{s}",
                    "primer_apellido": "Test",
                    "segundo_apellido": s,
                },
                "sexo": "F",
                "fecha_nacimiento": "1990-05-20",
                "contacto": {"telefonos": "12345678"},
            },
        )
        assert r.status_code == 201
        TestMadreHijo.MADRE_ID = r.json()["id"]
        created_ids["pacientes"].append(r.json()["id"])

    def test_create_hijo_success(self, client, auth_headers):
        if not TestMadreHijo.MADRE_ID:
            pytest.skip("No mother created")
        r = client.post(
            f"/pacientes/madre-hijo/{TestMadreHijo.MADRE_ID}",
            headers=auth_headers,
            json={
                "fecha_nacimiento": TestMadreHijo._fecha(),
                "hijos": [
                    {
                        "sexo": "M",
                        "datos_extra": {
                            "peso_nacimiento": "3.5",
                            "edad_gestacional": "39",
                            "tipo_parto": "EUTOCICO",
                        },
                    }
                ],
                "estado": "V",
            },
        )
        assert r.status_code == 201
        data = r.json()
        assert len(data["pacientes"]) == 1
        assert data["pacientes"][0]["sexo"] == "M"
        assert data["total"] == 1
        created_ids["pacientes"].append(data["pacientes"][0]["id"])

    def test_create_duplicate_hijo_returns_409(self, client, auth_headers):
        if not TestMadreHijo.MADRE_ID:
            pytest.skip("No mother created")
        r = client.post(
            f"/pacientes/madre-hijo/{TestMadreHijo.MADRE_ID}",
            headers=auth_headers,
            json={
                "fecha_nacimiento": TestMadreHijo._fecha(),
                "hijos": [
                    {
                        "sexo": "M",
                        "datos_extra": {
                            "peso_nacimiento": "3.5",
                            "edad_gestacional": "39",
                            "tipo_parto": "EUTOCICO",
                        },
                    }
                ],
                "estado": "V",
            },
        )
        assert r.status_code == 409

    def test_create_twins_bypass_duplicate(self, client, auth_headers):
        if not TestMadreHijo.MADRE_ID:
            pytest.skip("No mother created")
        r = client.post(
            f"/pacientes/madre-hijo/{TestMadreHijo.MADRE_ID}",
            headers=auth_headers,
            json={
                "fecha_nacimiento": TestMadreHijo._fecha(),
                "hijos": [
                    {
                        "sexo": "F",
                        "datos_extra": {
                            "peso_nacimiento": "2.8",
                            "edad_gestacional": "39",
                            "tipo_parto": "EUTOCICO",
                        },
                    },
                    {
                        "sexo": "M",
                        "datos_extra": {
                            "peso_nacimiento": "3.0",
                            "edad_gestacional": "39",
                            "tipo_parto": "EUTOCICO",
                        },
                    },
                ],
                "estado": "V",
            },
        )
        assert r.status_code == 201
        data = r.json()
        assert len(data["pacientes"]) == 2
        assert data["total"] == 2
        assert "#1" in data["pacientes"][0]["nombre"]["otro_nombre"]
        assert "#2" in data["pacientes"][1]["nombre"]["otro_nombre"]
        for p in data["pacientes"]:
            created_ids["pacientes"].append(p["id"])

    def test_create_triplets_and_verify_constancias(self, client, auth_headers, db_session):
        if not TestMadreHijo.MADRE_ID:
            pytest.skip("No mother created")
        fecha = date.today().isoformat()
        r = client.post(
            f"/pacientes/madre-hijo/{TestMadreHijo.MADRE_ID}",
            headers=auth_headers,
            json={
                "fecha_nacimiento": fecha,
                "hijos": [
                    {
                        "sexo": "M",
                        "datos_extra": {
                            "peso_nacimiento": "5 lb 8 onz",
                            "edad_gestacional": "36",
                            "tipo_parto": "CESAREA",
                            "hora_nacimiento": "08:15:00",
                        },
                    },
                    {
                        "sexo": "F",
                        "datos_extra": {
                            "peso_nacimiento": "5 lb 2 onz",
                            "edad_gestacional": "36",
                            "tipo_parto": "CESAREA",
                            "hora_nacimiento": "08:16:00",
                        },
                    },
                    {
                        "sexo": "M",
                        "datos_extra": {
                            "peso_nacimiento": "6 lb",
                            "edad_gestacional": "36",
                            "tipo_parto": "CESAREA",
                            "hora_nacimiento": "08:17:00",
                        },
                    },
                ],
                "estado": "V",
            },
        )
        assert r.status_code == 201
        data = r.json()
        assert len(data["pacientes"]) == 3
        assert data["total"] == 3

        for p in data["pacientes"]:
            pid = p["id"]
            created_ids["pacientes"].append(pid)

            constancia = db_session.query(ConstanciaNacimientoModel).filter(
                ConstanciaNacimientoModel.paciente_id == pid
            ).first()
            assert constancia is not None, f"Constancia no encontrada para paciente {pid}"
            assert constancia.madre_id == TestMadreHijo.MADRE_ID
            assert constancia.documento is not None

            nacimiento = db_session.query(NacimientoModel).filter(
                NacimientoModel.paciente_id == pid
            ).first()
            assert nacimiento is not None, f"Nacimiento no encontrado para paciente {pid}"
            assert nacimiento.madre_id == TestMadreHijo.MADRE_ID
            assert nacimiento.clasificacion_nacimiento is not None


# =====================================================================
# CONSULTAS
# =====================================================================
class TestConsultas:
    def test_registrar_consulta(self, client, auth_headers):
        if not created_ids["pacientes"]:
            pytest.skip("No paciente created")
        r = client.post(
            "/consultas/registro",
            headers=auth_headers,
            json={
                "paciente_id": created_ids["pacientes"][0],
                "tipo_consulta": 1,
                "especialidad": "MEDICINA GENERAL",
                "servicio": "COEX",
            },
        )
        assert r.status_code == 201
        data = r.json()
        created_ids["consultas"].append(data["id"])

    def test_list_consultas(self, client, auth_headers):
        r = client.get("/consultas/", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert "total" in data
        assert "consultas" in data

    def test_list_consultas_with_filters(self, client, auth_headers):
        r = client.get("/consultas/?especialidad=MEDICINA GENERAL", headers=auth_headers)
        assert r.status_code == 200

    def test_get_consulta(self, client, auth_headers):
        if not created_ids["consultas"]:
            pytest.skip("No consulta created")
        r = client.get(
            f"/consultas/{created_ids['consultas'][0]}", headers=auth_headers
        )
        assert r.status_code == 200

    def test_get_consulta_not_found(self, client, auth_headers):
        r = client.get("/consultas/999999", headers=auth_headers)
        assert r.status_code == 404

    def test_list_consultas_by_paciente(self, client, auth_headers):
        if not created_ids["pacientes"]:
            pytest.skip("No paciente created")
        r = client.get(
            f"/consultas/pacienteId/{created_ids['pacientes'][0]}",
            headers=auth_headers,
        )
        assert r.status_code == 200

    def test_update_consulta(self, client, auth_headers):
        if not created_ids["consultas"]:
            pytest.skip("No consulta created")
        cid = created_ids["consultas"][0]
        r = client.patch(
            f"/consultas/{cid}",
            headers=auth_headers,
            json={"especialidad": "MEDICINA GENERAL"},
        )
        assert r.status_code == 200

    def test_desactivar_consulta(self, client, auth_headers):
        if not created_ids["consultas"]:
            pytest.skip("No consulta created")
        cid = created_ids["consultas"][-1]
        r = client.delete(f"/consultas/{cid}", headers=auth_headers)
        assert r.status_code == 200
        created_ids["consultas"].remove(cid)

    def test_buscar_paciente_via_consultas(self, client, auth_headers):
        r = client.get("/consultas/buscarpaciente", headers=auth_headers)
        assert r.status_code == 200

    def test_sincronizar_indicadores(self, client, auth_headers):
        desde = (date.today() - timedelta(days=30)).isoformat()
        hasta = date.today().isoformat()
        r = client.patch(
            f"/consultas/sincronizar-indicadores?desde={desde}&hasta={hasta}",
            headers=auth_headers,
        )
        assert r.status_code == 200


# =====================================================================
# CITAS
# =====================================================================
class TestCitas:
    def test_create_cita(self, client, auth_headers):
        if not created_ids["pacientes"]:
            pytest.skip("No paciente created")
        r = client.post(
            "/citas/",
            headers=auth_headers,
            json={
                "paciente_id": created_ids["pacientes"][0],
                "expediente": "TST-CITA",
                "especialidad": "MED",
                "fecha_cita": (date.today() + timedelta(days=30)).isoformat(),
            },
        )
        assert r.status_code in (200, 201)
        data = r.json()
        created_ids["citas"].append(data["id"])

    def test_list_citas(self, client, auth_headers):
        r = client.get("/citas/", headers=auth_headers)
        assert r.status_code == 200

    def test_list_citas_with_filters(self, client, auth_headers):
        r = client.get("/citas/?especialidad=MED", headers=auth_headers)
        assert r.status_code == 200

    def test_get_cita(self, client, auth_headers):
        if not created_ids["citas"]:
            pytest.skip("No cita created")
        r = client.get(f"/citas/{created_ids['citas'][0]}", headers=auth_headers)
        assert r.status_code == 200

    def test_get_cita_not_found(self, client, auth_headers):
        r = client.get("/citas/999999", headers=auth_headers)
        assert r.status_code == 404

    def test_get_citas_by_paciente(self, client, auth_headers):
        if not created_ids["pacientes"]:
            pytest.skip("No paciente created")
        r = client.get(
            f"/citas/paciente/{created_ids['pacientes'][0]}", headers=auth_headers
        )
        assert r.status_code == 200

    def test_citas_disponibles(self, client, auth_headers):
        r = client.get("/citas/disponibles?especialidad=MED", headers=auth_headers)
        assert r.status_code == 200

    def test_update_cita(self, client, auth_headers):
        if not created_ids["citas"]:
            pytest.skip("No cita created")
        cid = created_ids["citas"][0]
        r = client.put(
            f"/citas/{cid}",
            headers=auth_headers,
            json={
                "paciente_id": created_ids["pacientes"][0] if created_ids["pacientes"] else 1,
                "expediente": "UPD",
                "especialidad": "MED",
                "fecha_cita": (date.today() + timedelta(days=31)).isoformat(),
            },
        )
        assert r.status_code == 200

    def test_delete_cita(self, client, auth_headers):
        if not created_ids["citas"]:
            pytest.skip("No cita created")
        cid = created_ids["citas"][-1]
        r = client.delete(f"/citas/{cid}", headers=auth_headers)
        assert r.status_code == 200
        created_ids["citas"].remove(cid)


# =====================================================================
# CICLOS
# =====================================================================
class TestCiclos:
    def test_create_ciclo(self, client, auth_headers):
        if not created_ids["consultas"]:
            pytest.skip("No consulta created")
        r = client.post(
            "/ciclos/",
            headers=auth_headers,
            json={
                "consulta_id": created_ids["consultas"][0],
                "numero": 1,
                "usuario": "test",
                "especialidad": "MEDICINA GENERAL",
                "servicio": "COEX",
            },
        )
        assert r.status_code in (200, 201)
        data = r.json()
        created_ids["ciclos"].append(data["id"])

    def test_list_ciclos_by_consulta(self, client, auth_headers):
        if not created_ids["consultas"]:
            pytest.skip("No consulta created")
        r = client.get(
            f"/ciclos/consulta/{created_ids['consultas'][0]}",
            headers=auth_headers,
        )
        assert r.status_code == 200

    def test_get_ciclo(self, client, auth_headers):
        if not created_ids["ciclos"]:
            pytest.skip("No ciclo created")
        r = client.get(f"/ciclos/{created_ids['ciclos'][0]}", headers=auth_headers)
        assert r.status_code == 200

    def test_get_ciclo_not_found(self, client, auth_headers):
        r = client.get("/ciclos/999999", headers=auth_headers)
        assert r.status_code == 404


# =====================================================================
# EVENTOS
# =====================================================================
class TestEventos:
    def test_create_evento(self, client, auth_headers):
        if not created_ids["consultas"]:
            pytest.skip("No consulta created")
        r = client.post(
            "/eventos/",
            headers=auth_headers,
            json={
                "consulta_id": created_ids["consultas"][0],
                "tipo_evento": 1,
                "datos": {"accion": "test"},
                "responsable": {"nombre": "Dr. Test", "registro": "MED-001"},
            },
        )
        assert r.status_code in (200, 201)
        data = r.json()
        created_ids["eventos"].append(data["id"])

    def test_list_eventos(self, client, auth_headers):
        r = client.get("/eventos/", headers=auth_headers)
        assert r.status_code == 200

    def test_get_evento(self, client, auth_headers):
        if not created_ids["eventos"]:
            pytest.skip("No evento created")
        r = client.get(f"/eventos/{created_ids['eventos'][0]}", headers=auth_headers)
        assert r.status_code == 200

    def test_get_evento_not_found(self, client, auth_headers):
        r = client.get("/eventos/999999", headers=auth_headers)
        assert r.status_code == 404

    def test_update_evento(self, client, auth_headers):
        if not created_ids["eventos"]:
            pytest.skip("No evento created")
        eid = created_ids["eventos"][0]
        r = client.patch(
            f"/eventos/{eid}",
            headers=auth_headers,
            json={"datos": {"accion": "updated"}},
        )
        assert r.status_code == 200

    def test_delete_evento(self, client, auth_headers):
        if not created_ids["eventos"]:
            pytest.skip("No evento created")
        eid = created_ids["eventos"][-1]
        r = client.delete(f"/eventos/{eid}", headers=auth_headers)
        assert r.status_code == 204
        created_ids["eventos"].remove(eid)


# =====================================================================
# ENCAMAMIENTO
# =====================================================================
class TestEncamamiento:
    def test_create_encamamiento(self, client, auth_headers):
        s = _sufijo()
        r = client.post(
            "/encamamiento/",
            json={
                "nombre_servicio": f"Servicio Test {s}",
                "descripcion": "Servicio de prueba",
                "camas_censables": 10,
            },
        )
        assert r.status_code in (200, 201)
        data = r.json()
        created_ids["encamamiento"].append(data["id"])

    def test_list_encamamiento(self, client, auth_headers):
        r = client.get("/encamamiento/")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_list_encamamiento_activo(self, client, auth_headers):
        r = client.get("/encamamiento/?activo=true")
        assert r.status_code == 200

    def test_get_encamamiento(self, client, auth_headers):
        if not created_ids["encamamiento"]:
            pytest.skip("No encamamiento created")
        eid = created_ids["encamamiento"][0]
        r = client.get(f"/encamamiento/{eid}")
        assert r.status_code == 200

    def test_get_encamamiento_not_found(self, client, auth_headers):
        r = client.get("/encamamiento/999999")
        assert r.status_code == 404

    def test_update_encamamiento(self, client, auth_headers):
        if not created_ids["encamamiento"]:
            pytest.skip("No encamamiento created")
        eid = created_ids["encamamiento"][0]
        r = client.patch(
            f"/encamamiento/{eid}",
            json={"camas_censables": 15},
        )
        assert r.status_code == 200
        assert r.json()["camas_censables"] == 15

    def test_delete_encamamiento(self, client, auth_headers):
        if not created_ids["encamamiento"]:
            pytest.skip("No encamamiento created")
        eid = created_ids["encamamiento"][-1]
        r = client.delete(f"/encamamiento/{eid}")
        assert r.status_code == 204
        created_ids["encamamiento"].remove(eid)


# =====================================================================
# NACIMIENTOS
# =====================================================================
class TestNacimientos:
    def test_list_nacimientos(self, client, auth_headers):
        r = client.get("/nacimientos/", headers=auth_headers)
        assert r.status_code == 200

    def test_create_nacimiento(self, client, auth_headers):
        if not created_ids["pacientes"]:
            pytest.skip("No paciente created")
        r = client.post(
            "/nacimientos/",
            headers=auth_headers,
            json={"paciente_id": created_ids["pacientes"][0]},
        )
        assert r.status_code in (200, 201)
        data = r.json()
        created_ids["nacimientos"].append(data["id"])

    def test_get_nacimiento(self, client, auth_headers):
        if not created_ids["nacimientos"]:
            pytest.skip("No nacimiento created")
        nid = created_ids["nacimientos"][0]
        r = client.get(f"/nacimientos/{nid}", headers=auth_headers)
        assert r.status_code == 200

    def test_get_nacimiento_not_found(self, client, auth_headers):
        r = client.get("/nacimientos/999999", headers=auth_headers)
        assert r.status_code == 404

    def test_update_nacimiento_mortinato(self, client, auth_headers):
        if not created_ids["nacimientos"]:
            pytest.skip("No nacimiento created")
        nid = created_ids["nacimientos"][0]
        r = client.patch(
            f"/nacimientos/{nid}",
            headers=auth_headers,
            json={"mortinato": True},
        )
        assert r.status_code == 200
        assert r.json()["mortinato"] is True

    def test_nacimiento_mortinato_persist(self, client, auth_headers):
        if not created_ids["nacimientos"]:
            pytest.skip("No nacimiento created")
        nid = created_ids["nacimientos"][0]
        r = client.get(f"/nacimientos/{nid}", headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["mortinato"] is True

    def test_delete_nacimiento(self, client, auth_headers):
        if not created_ids["nacimientos"]:
            pytest.skip("No nacimiento created")
        nid = created_ids["nacimientos"][-1]
        r = client.delete(f"/nacimientos/{nid}", headers=auth_headers)
        assert r.status_code == 204
        created_ids["nacimientos"].remove(nid)

    def test_nacimiento_desde_paciente(self, client, auth_headers):
        if not created_ids["pacientes"]:
            pytest.skip("No paciente created")
        pid = created_ids["pacientes"][0]
        r = client.post(
            f"/nacimientos/desde-paciente/{pid}",
            headers=auth_headers,
        )
        if r.status_code == 201:
            created_ids["nacimientos"].append(r.json()["id"])
        else:
            assert r.status_code in (400, 409)

    def test_nacimiento_sincronizar(self, client, auth_headers):
        r = client.post("/nacimientos/sincronizar", headers=auth_headers)
        assert r.status_code == 200

    def test_nacimiento_referenciar_legacy(self, client, auth_headers):
        r = client.get("/nacimientos/referenciar-legacy", headers=auth_headers)
        assert r.status_code == 200


# =====================================================================
# PROCEDIMIENTOS
# =====================================================================
class TestProcedimientos:
    PROC_ID = None

    def test_create_catalogo(self, client, auth_headers):
        s = _sufijo()
        r = client.post(
            "/procedimientos/catalogo",
            headers=auth_headers,
            json={
                "nombre": f"TEST-PROC-{s}",
                "abreviatura": f"TP{s}",
                "descripcion": "Procedimiento de prueba",
            },
        )
        assert r.status_code in (200, 201)
        data = r.json()
        created_ids["procedimientos_catalogo"].append(data["id"])
        TestProcedimientos.PROC_ID = data["id"]

    def test_list_catalogo(self, client, auth_headers):
        r = client.get("/procedimientos/catalogo", headers=auth_headers)
        assert r.status_code == 200

    def test_list_catalogo_with_filter(self, client, auth_headers):
        r = client.get("/procedimientos/catalogo?nombre=TEST", headers=auth_headers)
        assert r.status_code == 200

    def test_get_catalogo_by_id(self, client, auth_headers):
        if not TestProcedimientos.PROC_ID:
            pytest.skip("No procedimiento created")
        r = client.get(
            f"/procedimientos/catalogo/{TestProcedimientos.PROC_ID}",
            headers=auth_headers,
        )
        assert r.status_code == 200

    def test_update_catalogo(self, client, auth_headers):
        if not TestProcedimientos.PROC_ID:
            pytest.skip("No procedimiento created")
        r = client.put(
            f"/procedimientos/catalogo/{TestProcedimientos.PROC_ID}",
            headers=auth_headers,
            json={"nombre": "TEST-PROC-UPDATED"},
        )
        assert r.status_code == 200

    def test_create_procedimiento_realizado(self, client, auth_headers):
        if not created_ids["pacientes"] or not TestProcedimientos.PROC_ID:
            pytest.skip("Need paciente and procedimiento")
        r = client.post(
            "/procedimientos/",
            headers=auth_headers,
            json={
                "fecha": date.today().isoformat(),
                "lugar_servicio": "COEX",
                "sexo": "M",
                "id_procedimiento": TestProcedimientos.PROC_ID,
                "especialidad": "TEST",
                "cantidad": 1,
                "responsable": "Dr. Test",
            },
        )
        assert r.status_code in (200, 201)
        data = r.json()
        created_ids["procedimientos_realizados"].append(data["id"])

    def test_list_procedimientos_realizados(self, client, auth_headers):
        r = client.get("/procedimientos/", headers=auth_headers)
        assert r.status_code == 200

    def test_get_procedimiento_realizado(self, client, auth_headers):
        if not created_ids["procedimientos_realizados"]:
            pytest.skip("No procedimiento realizado")
        pid = created_ids["procedimientos_realizados"][0]
        r = client.get(f"/procedimientos/{pid}", headers=auth_headers)
        assert r.status_code == 200

    def test_update_procedimiento_realizado(self, client, auth_headers):
        if not created_ids["procedimientos_realizados"]:
            pytest.skip("No procedimiento realizado")
        pid = created_ids["procedimientos_realizados"][0]
        r = client.put(
            f"/procedimientos/{pid}",
            headers=auth_headers,
            json={"cantidad": 2},
        )
        assert r.status_code == 200

    def test_delete_procedimiento_realizado(self, client, auth_headers):
        if not created_ids["procedimientos_realizados"]:
            pytest.skip("No procedimiento realizado")
        pid = created_ids["procedimientos_realizados"][-1]
        r = client.delete(f"/procedimientos/{pid}", headers=auth_headers)
        assert r.status_code == 200
        created_ids["procedimientos_realizados"].remove(pid)

    def test_delete_catalogo(self, client, auth_headers):
        if not TestProcedimientos.PROC_ID:
            pytest.skip("No procedimiento created")
        r = client.delete(
            f"/procedimientos/catalogo/{TestProcedimientos.PROC_ID}",
            headers=auth_headers,
        )
        assert r.status_code == 200
        created_ids["procedimientos_catalogo"].remove(TestProcedimientos.PROC_ID)

    def test_reporte_procedimientos(self, client, auth_headers):
        r = client.get("/procedimientos/reporte", headers=auth_headers)
        assert r.status_code == 200

    def test_estadisticas_procedimientos(self, client, auth_headers):
        anio = date.today().year
        r = client.get(
            f"/procedimientos/estadisticas/resumen?anio={anio}",
            headers=auth_headers,
        )
        assert r.status_code == 200


# =====================================================================
# PRESTAMOS
# =====================================================================
class TestPrestamos:
    def test_create_prestamo(self, client, auth_headers):
        if not created_ids["pacientes"]:
            pytest.skip("Need paciente")
        r = client.post(
            "/prestamos/",
            headers=auth_headers,
            json={
                "id_paciente": created_ids["pacientes"][0],
                "expediente": "TEST-PRESTAMO",
                "solicitante": "Dr. Test",
                "motivo": "Prueba integracion",
                "tipo_documento": "Expediente",
            },
        )
        assert r.status_code in (200, 201)
        data = r.json()
        created_ids["prestamos"].append(data["id"])

    def test_list_prestamos(self, client, auth_headers):
        r = client.get("/prestamos/", headers=auth_headers)
        assert r.status_code == 200

    def test_get_prestamo(self, client, auth_headers):
        if not created_ids["prestamos"]:
            pytest.skip("No prestamo created")
        pid = created_ids["prestamos"][0]
        r = client.get(f"/prestamos/{pid}", headers=auth_headers)
        assert r.status_code == 200

    def test_get_prestamo_not_found(self, client, auth_headers):
        r = client.get("/prestamos/999999", headers=auth_headers)
        assert r.status_code == 404

    def test_update_prestamo(self, client, auth_headers):
        if not created_ids["prestamos"]:
            pytest.skip("No prestamo created")
        pid = created_ids["prestamos"][0]
        r = client.put(
            f"/prestamos/{pid}",
            headers=auth_headers,
            json={"motivo": "Actualizado"},
        )
        assert r.status_code == 200

    def test_delete_prestamo(self, client, auth_headers):
        if not created_ids["prestamos"]:
            pytest.skip("No prestamo created")
        pid = created_ids["prestamos"][-1]
        r = client.delete(f"/prestamos/{pid}", headers=auth_headers)
        assert r.status_code == 200
        created_ids["prestamos"].remove(pid)


# =====================================================================
# CORRELATIVOS
# =====================================================================
class TestCorrelativos:
    def test_generar_expediente(self, client, auth_headers):
        r = client.post("/correlativos/expediente", headers=auth_headers)
        assert r.status_code == 201
        data = r.json()
        assert "expediente" in data

    def test_generar_emergencia(self, client, auth_headers):
        r = client.post("/correlativos/emergencia", headers=auth_headers)
        assert r.status_code == 201
        data = r.json()
        assert "hoja_emergencia" in data

    def test_generar_constancia_nacimiento(self, client, auth_headers):
        r = client.post("/correlativos/constancia_nacimiento", headers=auth_headers)
        assert r.status_code == 201
        data = r.json()
        assert "constancia_nacimiento" in data

    def test_generar_constancia_defuncion(self, client, auth_headers):
        r = client.post("/correlativos/constancia_defuncion", headers=auth_headers)
        assert r.status_code == 201
        data = r.json()
        assert "constancia_defuncion" in data

    def test_generar_constancia_medica(self, client, auth_headers):
        r = client.post("/correlativos/constancia_medica", headers=auth_headers)
        assert r.status_code == 201
        data = r.json()
        assert "constancia_medica" in data


# =====================================================================
# MUNICIPIOS
# =====================================================================
class TestMunicipios:
    def test_list_municipios(self, client, auth_headers):
        r = client.get("/municipios/")
        assert r.status_code == 200

    def test_list_municipios_with_filter(self, client, auth_headers):
        r = client.get("/municipios/?departamento=CHIMALTENANGO")
        assert r.status_code == 200

    def test_list_departamentos(self, client, auth_headers):
        r = client.get("/municipios/departamentos")
        assert r.status_code == 200
        assert isinstance(r.json(), list)


# =====================================================================
# PAISES ISO
# =====================================================================
class TestPaises:
    def test_list_paises(self, client, auth_headers):
        r = client.get("/paises/")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_list_paises_select(self, client, auth_headers):
        r = client.get("/paises/select")
        assert r.status_code == 200

    def test_get_pais_by_codigo(self, client, auth_headers):
        r = client.get("/paises/GTM")
        assert r.status_code == 200
        data = r.json()
        assert data["codigo_iso3"] == "GTM"

    def test_get_pais_not_found(self, client, auth_headers):
        r = client.get("/paises/ZZZ")
        assert r.status_code == 404


# =====================================================================
# CONSTANCIAS NACIMIENTO
# =====================================================================
class TestConstanciasNacimiento:
    CONSTANCIA_ID = None

    def test_create_constancia(self, client, auth_headers, db_session):
        if not created_ids["pacientes"] or not created_ids["medicos"]:
            pytest.skip("Need paciente and medico")
        user = db_session.query(UserModel).filter(
            UserModel.username == "test_integration"
        ).first()
        r = client.post(
            "/constancias-nacimiento/",
            headers=auth_headers,
            json={
                "paciente_id": created_ids["pacientes"][0],
                "medico_id": created_ids["medicos"][0],
                "registrador_id": user.id,
                "nombre_madre": "MARIA TEST",
                "vecindad_madre": "TECPAN",
            },
        )
        assert r.status_code in (200, 201)
        data = r.json()
        created_ids["constancias"].append(data["id"])
        TestConstanciasNacimiento.CONSTANCIA_ID = data["id"]

    def test_list_constancias(self, client, auth_headers):
        r = client.get("/constancias-nacimiento/", headers=auth_headers)
        assert r.status_code == 200

    def test_get_constancia(self, client, auth_headers):
        if not TestConstanciasNacimiento.CONSTANCIA_ID:
            pytest.skip("No constancia created")
        cid = TestConstanciasNacimiento.CONSTANCIA_ID
        r = client.get(f"/constancias-nacimiento/{cid}", headers=auth_headers)
        assert r.status_code == 200

    def test_get_constancia_not_found(self, client, auth_headers):
        r = client.get("/constancias-nacimiento/999999", headers=auth_headers)
        assert r.status_code == 404

    def test_update_constancia(self, client, auth_headers):
        if not TestConstanciasNacimiento.CONSTANCIA_ID:
            pytest.skip("No constancia created")
        cid = TestConstanciasNacimiento.CONSTANCIA_ID
        r = client.put(
            f"/constancias-nacimiento/{cid}",
            headers=auth_headers,
            json={"nombre_madre": "MARIA TEST UPDATED"},
        )
        assert r.status_code == 200

    def test_historial_constancia(self, client, auth_headers):
        if not TestConstanciasNacimiento.CONSTANCIA_ID:
            pytest.skip("No constancia created")
        cid = TestConstanciasNacimiento.CONSTANCIA_ID
        r = client.get(
            f"/constancias-nacimiento/historial/{cid}", headers=auth_headers
        )
        assert r.status_code == 200

    def test_delete_constancia(self, client, auth_headers):
        if not created_ids["constancias"]:
            pytest.skip("No constancia created")
        cid = created_ids["constancias"][-1]
        r = client.delete(f"/constancias-nacimiento/{cid}", headers=auth_headers)
        assert r.status_code == 200
        created_ids["constancias"].remove(cid)

    def test_estado_informe(self, client, auth_headers):
        if not created_ids["constancias"]:
            pytest.skip("No constancia created")
        cid = created_ids["constancias"][0]
        # PATCH a entregado
        r = client.patch(
            f"/constancias-nacimiento/{cid}/estado-informe",
            headers=auth_headers,
            json={"estado_informe": "entregado"},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["metadatos"]["estado_informe"] == "entregado"
        assert "historial" in data["metadatos"]
        assert len(data["metadatos"]["historial"]) >= 1

        # PATCH a reimpreso (verifica que historial crece)
        r2 = client.patch(
            f"/constancias-nacimiento/{cid}/estado-informe",
            headers=auth_headers,
            json={"estado_informe": "reimpreso"},
        )
        assert r2.status_code == 200
        assert r2.json()["metadatos"]["estado_informe"] == "reimpreso"
        assert len(r2.json()["metadatos"]["historial"]) >= 2

        # estado inválido debe fallar
        r3 = client.patch(
            f"/constancias-nacimiento/{cid}/estado-informe",
            headers=auth_headers,
            json={"estado_informe": "invalido"},
        )
        assert r3.status_code == 422

    def test_constancia_actualiza_partos_madre(self, client, auth_headers):
        """Crear constancias con madre_id debe actualizar datos_extra.partos de la madre."""
        s = _sufijo()

        # Crear madre
        r = client.post(
            "/pacientes/",
            headers=auth_headers,
            json={
                "nombre": {
                    "primer_nombre": f"Madre{s}",
                    "primer_apellido": f"Partos{s}",
                },
                "sexo": "F",
                "fecha_nacimiento": "1990-05-15",
            },
        )
        assert r.status_code == 201
        madre_id = r.json()["id"]
        created_ids["pacientes"].append(madre_id)

        # Crear hijo 1
        r = client.post(
            "/pacientes/",
            headers=auth_headers,
            json={
                "nombre": {
                    "primer_nombre": f"Hijo1{s}",
                    "primer_apellido": f"Partos{s}",
                },
                "sexo": "M",
                "fecha_nacimiento": "2026-07-15",
            },
        )
        assert r.status_code == 201
        hijo1_id = r.json()["id"]
        created_ids["pacientes"].append(hijo1_id)

        # Crear constancia para hijo1 con vivos=1, muertos=0
        r = client.post(
            "/constancias-nacimiento/",
            headers=auth_headers,
            json={
                "paciente_id": hijo1_id,
                "madre_id": madre_id,
                "nombre_madre": f"MADRE PARTOS {s}",
                "vivos": 1,
                "muertos": 0,
            },
        )
        assert r.status_code in (200, 201)
        const1_id = r.json()["id"]
        created_ids["constancias"].append(const1_id)

        # Verificar madre: partos.nacidos_vivos=1, nacidos_muertos=0
        r = client.get(f"/pacientes/{madre_id}", headers=auth_headers)
        assert r.status_code == 200
        madre = r.json()
        partos = madre.get("datos_extra", {}).get("partos", {})
        assert partos.get("nacidos_vivos") == 1, f"Esperado 1, obtenido {partos}"
        assert partos.get("nacidos_muertos") == 0, f"Esperado 0, obtenido {partos}"

        # Crear hijo 2
        r = client.post(
            "/pacientes/",
            headers=auth_headers,
            json={
                "nombre": {
                    "primer_nombre": f"Hijo2{s}",
                    "primer_apellido": f"Partos{s}",
                },
                "sexo": "F",
                "fecha_nacimiento": "2026-07-15",
            },
        )
        assert r.status_code == 201
        hijo2_id = r.json()["id"]
        created_ids["pacientes"].append(hijo2_id)

        # Crear constancia para hijo2 con vivos=0, muertos=1
        r = client.post(
            "/constancias-nacimiento/",
            headers=auth_headers,
            json={
                "paciente_id": hijo2_id,
                "madre_id": madre_id,
                "nombre_madre": f"MADRE PARTOS {s}",
                "vivos": 0,
                "muertos": 1,
            },
        )
        assert r.status_code in (200, 201)
        const2_id = r.json()["id"]
        created_ids["constancias"].append(const2_id)

        # Verificar madre: nacidos_vivos=1, nacidos_muertos=1 (suma de ambas constancias)
        r = client.get(f"/pacientes/{madre_id}", headers=auth_headers)
        assert r.status_code == 200
        madre = r.json()
        partos = madre.get("datos_extra", {}).get("partos", {})
        assert partos.get("nacidos_vivos") == 1, f"Esperado 1, obtenido {partos}"
        assert partos.get("nacidos_muertos") == 1, f"Esperado 1, obtenido {partos}"

        # Actualizar const1: cambiar vivos a 3
        r = client.put(
            f"/constancias-nacimiento/{const1_id}",
            headers=auth_headers,
            json={"vivos": 3, "muertos": 0},
        )
        assert r.status_code == 200

        # Verificar madre: nacidos_vivos=3, nacidos_muertos=1 (3+0)
        r = client.get(f"/pacientes/{madre_id}", headers=auth_headers)
        assert r.status_code == 200
        madre = r.json()
        partos = madre.get("datos_extra", {}).get("partos", {})
        assert partos.get("nacidos_vivos") == 3, f"Esperado 3, obtenido {partos}"
        assert partos.get("nacidos_muertos") == 1, f"Esperado 1, obtenido {partos}"


# =====================================================================
# NACIMIENTOS LEGACY
# =====================================================================
class TestNacimientosLegacy:
    def test_list_nacimientos_legacy(self, client, auth_headers):
        r = client.get("/nacimientos-legacy/", headers=auth_headers)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_list_with_filters(self, client, auth_headers):
        r = client.get("/nacimientos-legacy/?madre=test", headers=auth_headers)
        assert r.status_code == 200


# =====================================================================
# ESTADISTICAS
# =====================================================================
class TestEstadisticas:
    DESDE = (date.today() - timedelta(days=365)).isoformat()
    HASTA = date.today().isoformat()

    def test_pacientes_atendidos(self, client, auth_headers):
        r = client.get(
            f"/estadisticas/consultas/pacientesAtendidos?desde={self.DESDE}&hasta={self.HASTA}",
            headers=auth_headers,
        )
        assert r.status_code == 200
        data = r.json()
        assert "datos" in data
        assert "total_general" in data

    def test_hospitalizacion_infantil(self, client, auth_headers):
        r = client.get(
            f"/estadisticas/consultas/hospitalizacion-infantil?desde={self.DESDE}&hasta={self.HASTA}",
            headers=auth_headers,
        )
        assert r.status_code == 200
        data = r.json()
        assert "datos" in data

    def test_promedio_diario(self, client, auth_headers):
        r = client.get(
            f"/estadisticas/consultas/promedioDiario?desde={self.DESDE}&hasta={self.HASTA}",
            headers=auth_headers,
        )
        assert r.status_code == 200
        data = r.json()
        assert "datos" in data

    def test_personal_hospital(self, client, auth_headers):
        r = client.get(
            f"/estadisticas/consultas/personal-hospital?desde={self.DESDE}&hasta={self.HASTA}",
            headers=auth_headers,
        )
        assert r.status_code == 200
        data = r.json()
        assert "datos" in data

    def test_estudiante_publico(self, client, auth_headers):
        r = client.get(
            f"/estadisticas/consultas/estudiante-publico?desde={self.DESDE}&hasta={self.HASTA}",
            headers=auth_headers,
        )
        assert r.status_code == 200
        data = r.json()
        assert "datos" in data

    def test_reingresos(self, client, auth_headers):
        r = client.get(
            f"/estadisticas/consultas/reingresos?desde={self.DESDE}&hasta={self.HASTA}",
            headers=auth_headers,
        )
        assert r.status_code == 200
        data = r.json()
        assert "datos" in data

    def test_reingresos_tipo3(self, client, auth_headers):
        r = client.get(
            "/estadisticas/consultas/reingresos-tipo3?skip=0&limit=10",
            headers=auth_headers,
        )
        assert r.status_code == 200

    def test_mayores_a_7_dias(self, client, auth_headers):
        r = client.get(
            "/estadisticas/consultas/mayores-a-7-dias?skip=0&limit=10",
            headers=auth_headers,
        )
        assert r.status_code == 200

    def test_nacimientos_stats(self, client, auth_headers):
        r = client.get(
            f"/estadisticas/nacimientos?desde={self.DESDE}&hasta={self.HASTA}",
            headers=auth_headers,
        )
        assert r.status_code == 200
        data = r.json()
        assert "total" in data

    def test_estadisticas_fecha_invalida(self, client, auth_headers):
        r = client.get(
            "/estadisticas/consultas/pacientesAtendidos?desde=invalid&hasta=2025-01-01",
            headers=auth_headers,
        )
        assert r.status_code == 400


# =====================================================================
# TOTALES (DASHBOARD)
# =====================================================================
class TestTotales:
    def test_get_totales(self, client, auth_headers):
        r = client.get("/totales/", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert "totales" in data
        assert "generado_en" in data
        assert len(data["totales"]) == 7

    def test_get_totales_with_fecha(self, client, auth_headers):
        r = client.get("/totales/?fecha=2025-01-01", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert "totales" in data

    def test_get_totales_fecha_invalida(self, client, auth_headers):
        r = client.get("/totales/?fecha=invalid", headers=auth_headers)
        assert r.status_code == 400


# =====================================================================
# SIGSA-3
# =====================================================================
class TestSigsa3:
    SIGSA_ID = None

    def test_create_sigsa3(self, client, auth_headers):
        r = client.post(
            "/sigsa3/",
            headers=auth_headers,
            json={
                "personal_salud": "Dr. Test SIGSA",
                "fecha_consulta": date.today().isoformat(),
                "no_historia_clinica": "HC-TEST-001",
                "nombre_paciente": "Paciente SIGSA Test",
                "sexo": "M",
                "tipo_consulta": "Primera vez",
                "especialidad": "MEDICINA GENERAL",
            },
        )
        assert r.status_code == 201
        data = r.json()
        created_ids["sigsa3"].append(data["id"])
        TestSigsa3.SIGSA_ID = data["id"]

    def test_list_sigsa3(self, client, auth_headers):
        r = client.get("/sigsa3/", headers=auth_headers)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_list_sigsa3_with_filters(self, client, auth_headers):
        r = client.get("/sigsa3/?especialidad=MEDICINA GENERAL", headers=auth_headers)
        assert r.status_code == 200

    def test_list_sigsa3_with_q(self, client, auth_headers):
        r = client.get("/sigsa3/?q=Paciente", headers=auth_headers)
        assert r.status_code == 200

    def test_get_sigsa3(self, client, auth_headers):
        if not TestSigsa3.SIGSA_ID:
            pytest.skip("No sigsa3 created")
        r = client.get(f"/sigsa3/{TestSigsa3.SIGSA_ID}", headers=auth_headers)
        assert r.status_code == 200

    def test_get_sigsa3_not_found(self, client, auth_headers):
        r = client.get("/sigsa3/999999", headers=auth_headers)
        assert r.status_code == 404

    def test_update_sigsa3(self, client, auth_headers):
        if not TestSigsa3.SIGSA_ID:
            pytest.skip("No sigsa3 created")
        sid = TestSigsa3.SIGSA_ID
        r = client.put(
            f"/sigsa3/{sid}",
            headers=auth_headers,
            json={"especialidad": "PEDIATRIA"},
        )
        assert r.status_code == 200

    def test_delete_sigsa3(self, client, auth_headers):
        if not created_ids["sigsa3"]:
            pytest.skip("No sigsa3 created")
        sid = created_ids["sigsa3"][-1]
        r = client.delete(f"/sigsa3/{sid}", headers=auth_headers)
        assert r.status_code == 204
        created_ids["sigsa3"].remove(sid)

    def test_no_asociados(self, client, auth_headers):
        r = client.get("/sigsa3/no-asociados/", headers=auth_headers)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_dx_z34(self, client, auth_headers):
        desde = (date.today() - timedelta(days=365)).isoformat()
        hasta = date.today().isoformat()
        r = client.get(
            f"/sigsa3/dx/z34?desde={desde}&hasta={hasta}",
            headers=auth_headers,
        )
        assert r.status_code == 200
        data = r.json()
        assert "datos" in data
        assert "total_general" in data
        assert "total_pacientes" in data
        assert "codigos_filtrados" in data
        assert data["codigos_filtrados"] == ["Z:34"]

    def test_dx_z10(self, client, auth_headers):
        desde = (date.today() - timedelta(days=365)).isoformat()
        hasta = date.today().isoformat()
        r = client.get(
            f"/sigsa3/dx/z10?desde={desde}&hasta={hasta}",
            headers=auth_headers,
        )
        assert r.status_code == 200
        data = r.json()
        assert "datos" in data
        assert "total_general" in data
        assert "total_pacientes" in data
        assert data["codigos_filtrados"] == ["Z:10:4", "Z:10:5", "Z:10:6"]

    def test_dx_z34_fecha_invalida(self, client, auth_headers):
        r = client.get(
            "/sigsa3/dx/z34?desde=invalid&hasta=2025-01-01",
            headers=auth_headers,
        )
        assert r.status_code == 422

    def test_dx_z10_fecha_invalida(self, client, auth_headers):
        r = client.get(
            "/sigsa3/dx/z10?desde=invalid&hasta=2025-01-01",
            headers=auth_headers,
        )
        assert r.status_code == 422

    def test_dx_z34_sin_auth(self, client):
        desde = (date.today() - timedelta(days=365)).isoformat()
        hasta = date.today().isoformat()
        r = client.get(f"/sigsa3/dx/z34?desde={desde}&hasta={hasta}")
        assert r.status_code in (401, 403)

    def test_dx_z10_sin_auth(self, client):
        desde = (date.today() - timedelta(days=365)).isoformat()
        hasta = date.today().isoformat()
        r = client.get(f"/sigsa3/dx/z10?desde={desde}&hasta={hasta}")
        assert r.status_code in (401, 403)


# =====================================================================
# AUDIT LOG
# =====================================================================
class TestAuditLog:
    def test_list_audit_logs(self, client, auth_headers):
        r = client.get("/audit-log/", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert "total" in data
        assert "logs" in data

    def test_list_audit_logs_with_filters(self, client, auth_headers):
        r = client.get("/audit-log/?tabla=consultas", headers=auth_headers)
        assert r.status_code == 200

    def test_list_audit_logs_with_username(self, client, auth_headers):
        r = client.get("/audit-log/?username=test", headers=auth_headers)
        assert r.status_code == 200

    def test_list_audit_logs_with_dates(self, client, auth_headers):
        desde = (date.today() - timedelta(days=7)).isoformat()
        hasta = date.today().isoformat()
        r = client.get(
            f"/audit-log/?desde={desde}&hasta={hasta}", headers=auth_headers
        )
        assert r.status_code == 200


# =====================================================================
# REDIRECT ROOT
# =====================================================================
class TestRoot:
    def test_root_redirects_to_docs(self, client):
        r = client.get("/", follow_redirects=False)
        assert r.status_code == 307
        assert "/docs" in r.headers["location"]
