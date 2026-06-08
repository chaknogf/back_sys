from datetime import date, datetime, time
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
from modules.laboratorios.models import Laboratorios
from modules.rayos_x.models import RayosX
from modules.users.models import UserModel
from core.security import hash_password

created_ids = {
    "pacientes": [],
    "medicos": [],
    "consultas": [],
    "citas": [],
    "ciclos": [],
    "prestamos": [],
    "procedimientos": [],
    "eventos": [],
    "constancias": [],
    "laboratorios": [],
    "rayos_x": [],
    "users": [],
}


def cleanup():
    db = SessionLocal()
    try:
        for table, ids in created_ids.items():
            if not ids:
                continue
            model_map = {
                "pacientes": PacienteModel,
                "medicos": MedicoModel,
                "consultas": ConsultaModel,
                "citas": CitaModel,
                "ciclos": CiclosConsulta,
                "prestamos": Prestamo,
                "procedimientos": Procedimiento,
                "eventos": EventoConsultaModel,
                "constancias": ConstanciaNacimientoModel,
                "laboratorios": Laboratorios,
                "rayos_x": RayosX,
                "users": UserModel,
            }
            model = model_map.get(table)
            if model:
                db.query(model).filter(model.id.in_(ids)).delete(
                    synchronize_session=False
                )
        db.commit()
    finally:
        db.close()


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

    def test_recover_password(self, client, auth_headers, db_session):
        r = client.patch(
            "/users/recuperar",
            json={
                "email": "test_integration@hospital.com",
                "password": "NewPass123!",
            },
        )
        assert r.status_code == 200

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


# =====================================================================
# MEDICOS
# =====================================================================
class TestMedicos:
    def test_create_medico(self, client, auth_headers):
        r = client.post(
            "/medicos/",
            headers=auth_headers,
            json={
                "nombre": "Dr. Test",
                "colegiado": 99999,
                "dpi": 1234567890123,
                "sexo": "M",
                "especialidad": "TEST",
            },
        )
        assert r.status_code in (200, 201)
        data = r.json()
        created_ids["medicos"].append(data["id"])

    def test_list_medicos(self, client, auth_headers):
        r = client.get("/medicos/", headers=auth_headers)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_get_medico(self, client, auth_headers):
        if not created_ids["medicos"]:
            pytest.skip("No medico created")
        r = client.get(f"/medicos/{created_ids['medicos'][0]}", headers=auth_headers)
        assert r.status_code == 200


# =====================================================================
# PACIENTES
# =====================================================================
class TestPacientes:
    def test_create_paciente(self, client, auth_headers):
        r = client.post(
            "/pacientes/",
            headers=auth_headers,
            json={
                "nombre": {
                    "primer_nombre": "Juan",
                    "segundo_nombre": "Carlos",
                    "primer_apellido": "Perez",
                    "segundo_apellido": "Test",
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
        r = client.get(
            "/pacientes/?nombre=Juan Carlos", headers=auth_headers
        )
        assert r.status_code == 200
        data = r.json()
        assert data["total"] > 0

    def test_get_paciente(self, client, auth_headers):
        if not created_ids["pacientes"]:
            pytest.skip("No paciente created")
        r = client.get(
            f"/pacientes/{created_ids['pacientes'][0]}", headers=auth_headers
        )
        assert r.status_code == 200
        assert r.json()["nombre"]["primer_nombre"] == "Juan"

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
                "indicadores": {},
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

    def test_get_consulta(self, client, auth_headers):
        if not created_ids["consultas"]:
            pytest.skip("No consulta created")
        r = client.get(
            f"/consultas/{created_ids['consultas'][0]}", headers=auth_headers
        )
        assert r.status_code == 200

    def test_list_consultas_by_paciente(self, client, auth_headers):
        if not created_ids["pacientes"]:
            pytest.skip("No paciente created")
        r = client.get(
            f"/consultas/pacienteId/{created_ids['pacientes'][0]}",
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
                "expediente": "TEST-CITA",
                "especialidad": "MED",
                "fecha_cita": "2026-06-15",
            },
        )
        assert r.status_code in (200, 201)
        data = r.json()
        created_ids["citas"].append(data["id"])

    def test_list_citas(self, client, auth_headers):
        r = client.get("/citas/", headers=auth_headers)
        assert r.status_code == 200


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

    def test_list_ciclos(self, client, auth_headers):
        if not created_ids.get("ciclos"):
            pytest.skip("No ciclo created")
        r = client.get(f"/ciclos/{created_ids['ciclos'][0]}", headers=auth_headers)
        assert r.status_code == 200

    def test_get_ciclos_by_consulta(self, client, auth_headers):
        if not created_ids["consultas"]:
            pytest.skip("No consulta created")
        r = client.get(
            f"/ciclos/consulta/{created_ids['consultas'][0]}",
            headers=auth_headers,
        )
        assert r.status_code == 200


# =====================================================================
# EXPEDIENTE (CORRELATIVOS)
# =====================================================================
class TestExpediente:
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

    def test_generar_constancia_nac(self, client, auth_headers):
        r = client.post("/correlativos/constancia_nacimiento", headers=auth_headers)
        assert r.status_code == 201
        data = r.json()
        assert "constancia_nacimiento" in data


# =====================================================================
# MUNICIPIOS
# =====================================================================
class TestMunicipios:
    def test_list_municipios(self, client, auth_headers):
        r = client.get("/municipios/", headers=auth_headers)
        assert r.status_code == 200

    def test_list_departamentos(self, client, auth_headers):
        r = client.get("/municipios/departamentos", headers=auth_headers)
        assert r.status_code == 200


# =====================================================================
# PAISES ISO
# =====================================================================
class TestPaises:
    def test_list_paises(self, client, auth_headers):
        r = client.get("/paises/", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)

    def test_list_paises_select(self, client, auth_headers):
        r = client.get("/paises/select", headers=auth_headers)
        assert r.status_code == 200


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


# =====================================================================
# PRESTAMOS
# =====================================================================
class TestPrestamos:
    def test_create_prestamo(self, client, auth_headers):
        if not created_ids["pacientes"] or not created_ids["consultas"]:
            pytest.skip("Need paciente and consulta")
        r = client.post(
            "/prestamos/",
            headers=auth_headers,
            json={
                "id_paciente": created_ids["pacientes"][0],
                "id_consulta": created_ids["consultas"][0],
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


# =====================================================================
# PROCEDIMIENTOS
# =====================================================================
class TestProcedimientos:
    def test_create_procedimiento_catalogo(self, client, auth_headers):
        import time
        suffix = str(int(time.time() * 1000))[-6:]
        r = client.post(
            "/procedimientos/catalogo",
            headers=auth_headers,
            json={
                "nombre": f"TEST-PROC-{suffix}",
                "abreviatura": f"TP{suffix}",
                "descripcion": "Procedimiento de prueba",
            },
        )
        assert r.status_code in (200, 201)
        data = r.json()
        created_ids["procedimientos"].append(data["id"])

    def test_list_catalogo(self, client, auth_headers):
        r = client.get("/procedimientos/catalogo", headers=auth_headers)
        assert r.status_code == 200


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


# =====================================================================
# LABORATORIOS
# =====================================================================
class TestLaboratorios:
    def test_create_laboratorio(self, client, auth_headers):
        if not created_ids["consultas"]:
            pytest.skip("No consulta created")
        r = client.post(
            "/laboratorios/",
            headers=auth_headers,
            json={
                "consulta_id": created_ids["consultas"][0],
                "cod_lab": "TEST-LAB",
                "resultados": {"prueba": "hemograma", "valor": "normal"},
            },
        )
        if r.status_code in (200, 201):
            created_ids["laboratorios"].append(r.json()["id"])

    def test_laboratorio_import(self, client, auth_headers):
        """Just verify the module loads"""
        import modules.laboratorios
        assert modules.laboratorios is not None


# =====================================================================
# RAYOS X
# =====================================================================
class TestRayosX:
    def test_create_rayo_x(self, client, auth_headers):
        if not created_ids["consultas"]:
            pytest.skip("No consulta created")
        r = client.post(
            "/rayos_x/",
            headers=auth_headers,
            json={
                "consulta_id": created_ids["consultas"][0],
                "cod_rx": "TEST-RX",
                "resultados": {"estudio": "RX torax", "hallazgo": "normal"},
            },
        )
        if r.status_code in (200, 201):
            created_ids["rayos_x"].append(r.json()["id"])

    def test_rayos_x_import(self):
        import modules.rayos_x
        assert modules.rayos_x is not None


# =====================================================================
# CONSTANCIAS NACIMIENTO
# =====================================================================
class TestConstanciasNacimiento:
    def test_create_constancia(self, client, auth_headers, db_session):
        if not created_ids["pacientes"]:
            pytest.skip("No paciente created")
        if not created_ids["medicos"]:
            pytest.skip("No medico created")
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

    def test_list_constancias(self, client, auth_headers):
        r = client.get("/constancias-nacimiento/", headers=auth_headers)
        assert r.status_code == 200


# =====================================================================
# NACIMIENTOS LEGACY
# =====================================================================
class TestNacimientosLegacy:
    def test_list_nacimientos(self, client, auth_headers):
        r = client.get("/nacimientos-legacy/", headers=auth_headers)
        assert r.status_code == 200


import pytest  # noqa: E402 (needed for skip in class methods)
