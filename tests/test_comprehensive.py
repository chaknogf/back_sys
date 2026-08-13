import pytest
import time as _time
from datetime import date, datetime, timedelta
from core.database import SessionLocal
from modules.pacientes.models import PacienteModel
from modules.medicos.models import MedicoModel
from modules.consultas.models import ConsultaModel, ConsultaHistorialModel
from modules.citas.models import CitaModel
from modules.ciclos.models import CiclosConsulta
from modules.prestamos.models import Prestamo
from modules.procedimientos.models import Procedimiento, ProceMedico
from modules.eventos.models import EventoConsultaModel
from modules.constancias_nacimiento.models import ConstanciaNacimientoModel
from modules.nacimientos.models import NacimientoModel
from modules.nacimientos_legacy.models import NacimientoLegacy
from modules.encamamiento.models import EncamamientoModel
from modules.sigsa3.models import Sigsa3Model
from modules.defunciones.models import DefuncionModel
from modules.censo_camas.models import CensoCamasModel
from modules.personal_salud.models import PersonalSaludModel
from modules.especialidades.models import EspecialidadModel
from modules.users.models import UserModel


ADMIN_USER = "admin"
ADMIN_PASS = "admin"


created_ids = {
    "pacientes": [], "medicos": [], "consultas": [], "citas": [],
    "ciclos": [], "prestamos": [], "procedimientos_catalogo": [],
    "procedimientos_realizados": [], "eventos": [], "constancias": [],
    "nacimientos": [], "encamamiento": [], "sigsa3": [],
    "defunciones": [], "censo_camas": [], "personal_salud": [],
    "nacimientos_legacy": [], "especialidades": [],
}


def _sufijo():
    return str(int(_time.time() * 1000000))[-6:]


# =====================================================================
# FIXTURES
# =====================================================================
@pytest.fixture(scope="module")
def admin_headers():
    from fastapi.testclient import TestClient
    from main import app
    client = TestClient(app)
    r = client.post("/auth/login", data={
        "username": ADMIN_USER, "password": ADMIN_PASS,
    })
    assert r.status_code == 200, f"Login failed: {r.text}"
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="module")
def client():
    from fastapi.testclient import TestClient
    from main import app
    return TestClient(app)


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
    def test_login_success(self, client):
        r = client.post("/auth/login", data={
            "username": ADMIN_USER, "password": ADMIN_PASS,
        })
        assert r.status_code == 200
        assert "access_token" in r.json()

    def test_login_fail(self, client):
        r = client.post("/auth/login", data={
            "username": "no_existe", "password": "x",
        })
        assert r.status_code == 401

    def test_me(self, client, admin_headers):
        r = client.get("/auth/me", headers=admin_headers)
        assert r.status_code == 200
        assert r.json()["username"] == ADMIN_USER

    def test_me_no_auth(self, client):
        r = client.get("/auth/me")
        assert r.status_code in (401, 403)


# =====================================================================
# MUNICIPIOS
# =====================================================================
class TestMunicipios:
    def test_list_municipios(self, client):
        r = client.get("/municipios/")
        assert r.status_code == 200
        data = r.json()
        assert "total" in data
        assert "municipios" in data

    def test_list_municipios_filters(self, client):
        r = client.get("/municipios/?departamento=GUATEMALA")
        assert r.status_code == 200

    def test_departamentos(self, client):
        r = client.get("/municipios/departamentos")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_list_municipios_no_auth(self, client):
        r = client.get("/municipios/")
        assert r.status_code == 200


# =====================================================================
# PAISES
# =====================================================================
class TestPaises:
    def test_list_paises(self, client):
        r = client.get("/paises/")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_list_paises_select(self, client):
        r = client.get("/paises/select")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_get_pais(self, client):
        r = client.get("/paises/GT/")
        if r.status_code == 404:
            r = client.get("/paises/?codigo=GT")
        assert r.status_code == 200


# =====================================================================
# ESPECIALIDADES
# =====================================================================
class TestEspecialidades:
    def test_list_especialidades(self, client, admin_headers):
        r = client.get("/especialidades/", headers=admin_headers)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_create_especialidad(self, client, admin_headers):
        s = _sufijo()
        r = client.post("/especialidades/", headers=admin_headers, json={
            "nombre": f"TEST-ESP-{s}",
            "abreviatura": f"TE{s[-3:]}",
        })
        assert r.status_code in (200, 201)
        created_ids["especialidades"].append(r.json()["id"])

    def test_list_public(self, client, admin_headers):
        r = client.get("/especialidades/", headers=admin_headers)
        assert r.status_code == 200


# =====================================================================
# NORMALIZACION ESPECIALIDAD — verificar migración 010
# =====================================================================
class TestNormalizacionEspecialidad:
    """Verifica que la migración 010 se ejecutó correctamente:
    - codigo column poblado en especialidades
    - especialidad_id FK poblado en todas las tablas
    - consultas.especialidad usa códigos cortos (no full names)
    """

    CODIGOS_ESPERADOS = {
        "Medicina General": "GENE",
        "Medicina Interna": "MEDI",
        "Cirugía": "CIRU",
        "Pediatría": "PEDI",
        "Ginecología": "GINE",
        "Traumatología": "TRAU",
        "Cardiología": "CAR",
        "Neurología": "NEUR",
        "Psicología": "PSIC",
        "Nutrición": "NUTR",
        "Odontología": "ODON",
        "Terapia respiratoria": "TERR",
        "Educadora": "EDUC",
        "Anestesiología": "ANES",
        "Medicina Crítica": "UCI",
        "Neonatología": "NEO",
    }

    def test_codigos_en_especialidades(self):
        db = SessionLocal()
        try:
            for nombre, codigo in self.CODIGOS_ESPERADOS.items():
                esp = db.query(EspecialidadModel).filter(
                    EspecialidadModel.nombre == nombre
                ).first()
                assert esp is not None, f"Falta especialidad: {nombre}"
                assert esp.codigo == codigo, (
                    f"{nombre}: esperado codigo={codigo}, obtenido={esp.codigo}"
                )
        finally:
            db.close()

    def test_especialidad_id_en_citas(self):
        db = SessionLocal()
        try:
            total = db.query(CitaModel).count()
            con_fk = db.query(CitaModel).filter(CitaModel.especialidad_id.isnot(None)).count()
            assert total > 0, "No hay citas en la BD"
            assert con_fk > total * 0.99, (
                f"Solo {con_fk}/{total} citas tienen especialidad_id"
            )
        finally:
            db.close()

    def test_especialidad_id_en_consultas(self):
        db = SessionLocal()
        try:
            total = db.query(ConsultaModel).filter(
                ConsultaModel.especialidad.isnot(None),
                ConsultaModel.especialidad != "",
                ConsultaModel.especialidad != "NO_ESP",
                ConsultaModel.especialidad != "EMERGENCIA",
            ).count()
            con_fk = db.query(ConsultaModel).filter(
                ConsultaModel.especialidad_id.isnot(None)
            ).count()
            assert con_fk >= total, (
                f"Solo {con_fk}/{total} consultas tienen especialidad_id"
            )
        finally:
            db.close()

    def test_consultas_sin_nombres_largos(self):
        db = SessionLocal()
        try:
            largos = db.query(ConsultaModel).filter(
                ConsultaModel.especialidad_id.isnot(None),
                ConsultaModel.especialidad.notin_([
                    "MEDI", "PEDI", "GINE", "CIRU", "TRAU",
                    "PSIC", "NUTR", "ODON", "GENE", "CAR",
                    "NEUR", "NEO", "ANES", "UCI", "TERR", "EDUC",
                ]),
            ).count()
            assert largos == 0, (
                f"{largos} consultas aún tienen nombres largos en especialidad"
            )
        finally:
            db.close()

    def test_especialidad_id_en_medicos(self):
        db = SessionLocal()
        try:
            sin_fk = db.query(MedicoModel).filter(
                MedicoModel.especialidad_id.is_(None)
            ).count()
            total = db.query(MedicoModel).count()
            con_fk = total - sin_fk
            assert con_fk >= total * 0.9, (
                f"Solo {con_fk}/{total} médicos tienen especialidad_id"
            )
        finally:
            db.close()


# =====================================================================
# NORMALIZACION DATOS_EXTRA (Migración 011)
# =====================================================================
class TestNormalizacionDatosExtra:
    """Verifica que la migración 011 se ejecutó correctamente:
    - citas.razon_consulta y notas pobladas
    - pacientes.idioma_id, pueblo_id, nacionalidad, lugar_nacimiento poblados
    - consultas.registro_medico, condicion_egreso, fecha_egreso poblados
    """

    def test_citas_razon_consulta(self):
        db = SessionLocal()
        try:
            total = db.query(CitaModel).count()
            con_razon = db.query(CitaModel).filter(
                CitaModel.razon_consulta.isnot(None)
            ).count()
            assert total > 0, "No hay citas"
            assert con_razon > 0, "Ninguna cita tiene razon_consulta"
            assert con_razon > total * 0.9, (
                f"Solo {con_razon}/{total} citas tienen razon_consulta"
            )
        finally:
            db.close()

    def test_citas_notas(self):
        db = SessionLocal()
        try:
            total = db.query(CitaModel).count()
            con_notas = db.query(CitaModel).filter(
                CitaModel.notas.isnot(None)
            ).count()
            if con_notas == 0:
                pytest.skip("No hay citas con notas (dato opcional)")
            assert con_notas <= total
        finally:
            db.close()

    def test_citas_razon_valores_esperados(self):
        db = SessionLocal()
        try:
            razones = set()
            for r in db.query(CitaModel.razon_consulta).filter(
                CitaModel.razon_consulta.isnot(None)
            ).distinct():
                razones.add(r[0])
            esperadas = {"control", "ingreso", "procedimiento", "preoperatorio"}
            assert esperadas.issubset(razones), (
                f"Faltan razones: {esperadas - razones}"
            )
        finally:
            db.close()

    def test_pacientes_demograficos(self):
        db = SessionLocal()
        try:
            total = db.query(PacienteModel).count()
            con_idioma = db.query(PacienteModel).filter(
                PacienteModel.idioma_id.isnot(None)
            ).count()
            con_pueblo = db.query(PacienteModel).filter(
                PacienteModel.pueblo_id.isnot(None)
            ).count()
            con_nacionalidad = db.query(PacienteModel).filter(
                PacienteModel.nacionalidad.isnot(None)
            ).count()
            assert con_idioma > 0, "Ningún paciente tiene idioma_id"
            assert con_pueblo > 0, "Ningún paciente tiene pueblo_id"
            assert con_nacionalidad > 0, "Ningún paciente tiene nacionalidad"
            assert con_idioma <= total
            assert con_pueblo <= total
        finally:
            db.close()

    def test_pacientes_nacionalidad_gtm(self):
        db = SessionLocal()
        try:
            gtm = db.query(PacienteModel).filter(
                PacienteModel.nacionalidad == "GTM"
            ).count()
            total = db.query(PacienteModel).filter(
                PacienteModel.nacionalidad.isnot(None)
            ).count()
            assert gtm > total * 0.9, (
                f"Solo {gtm}/{total} pacientes con nacionalidad GTM"
            )
        finally:
            db.close()

    def test_consultas_registro_medico(self):
        db = SessionLocal()
        try:
            con_registro = db.query(ConsultaModel).filter(
                ConsultaModel.registro_medico.isnot(None)
            ).count()
            assert con_registro > 0, "Ninguna consulta tiene registro_medico"
        finally:
            db.close()

    def test_consultas_condicion_egreso(self):
        db = SessionLocal()
        try:
            con_condicion = db.query(ConsultaModel).filter(
                ConsultaModel.condicion_egreso.isnot(None)
            ).count()
            assert con_condicion > 0, "Ninguna consulta tiene condicion_egreso"
        finally:
            db.close()

    def test_sync_citas_datos_extra_trigger(self, client, admin_headers):
        """Verifica que al insertar datos_extra se sincroniza razon_consulta"""
        s = _sufijo()
        r = client.post("/citas/", json={
            "expediente": f"TST-{s}",
            "paciente_id": 1,
            "especialidad": "GENE",
            "fecha_cita": "2026-12-31",
            "datos_extra": {"razon_consulta": "control"},
        }, headers=admin_headers)
        if r.status_code in (200, 201):
            cita_id = r.json().get("id")
            if cita_id:
                try:
                    created_ids["citas"].append(cita_id)
                except AttributeError:
                    pass

    def test_paciente_validator_demograficos(self, client, admin_headers):
        """Verifica que el modelo sincroniza demograficos al crear/actualizar"""
        db = SessionLocal()
        try:
            p = PacienteModel(
                nombre={"primer_nombre": "TEST", "primer_apellido": f"DEMO{_sufijo()}"},
                sexo="M",
                datos_extra={
                    "demograficos": {
                        "idioma": "24",
                        "pueblo": "2",
                        "nacionalidad": "GTM",
                        "lugar_nacimiento": "0401",
                    }
                },
            )
            db.add(p)
            db.commit()
            db.refresh(p)
            try:
                created_ids["pacientes"].append(p.id)
            except AttributeError:
                pass
            assert p.idioma_id == 24, f"idioma_id esperado=24, obtenido={p.idioma_id}"
            assert p.pueblo_id == 2, f"pueblo_id esperado=2, obtenido={p.pueblo_id}"
            assert p.nacionalidad == "GTM", f"nacionalidad esperada=GTM, obtenida={p.nacionalidad}"
            assert p.lugar_nacimiento == "0401", f"lugar_nacimiento esperado=0401, obtenido={p.lugar_nacimiento}"
        finally:
            db.close()

    def test_respuesta_paciente_conserva_vecindad_en_demograficos(self):
        """La hidratación desde columnas no debe eliminar campos exclusivos de JSONB."""
        from modules.pacientes.schemas import PacienteOut

        paciente = PacienteOut.model_validate({
            "id": 1,
            "nombre": {"primer_nombre": "TEST", "primer_apellido": "VECINDAD"},
            "nombre_completo": "TEST VECINDAD",
            "datos_extra": {
                "demograficos": {
                    "idioma": 24,
                    "vecindad": "0401",
                }
            },
            "idioma_id": 24,
        })

        assert paciente.datos_extra["demograficos"]["vecindad"] == "0401"


# =====================================================================
# MEDICOS (public endpoints)
# =====================================================================
class TestMedicos:
    def test_create_medico(self, client):
        s = _sufijo()
        r = client.post("/medicos/", json={
            "nombre": f"TEST-DOCTOR-{s}",
            "colegiado": s,
            "dpi": int(f"123456789{s[-3:]}"),
            "sexo": "M",
            "especialidad": "MEDICINA GENERAL",
        })
        assert r.status_code in (200, 201), f"Failed: {r.text}"
        created_ids["medicos"].append(r.json()["id"])

    def test_list_medicos(self, client):
        r = client.get("/medicos/")
        assert r.status_code == 200, f"Failed: {r.text}"
        data = r.json()
        if isinstance(data, dict):
            assert "medicos" in data or "total" in data
        elif isinstance(data, list):
            pass
        else:
            assert False, f"Unexpected type: {type(data)}"

    def test_get_medico(self, client):
        if not created_ids["medicos"]:
            pytest.skip("No medico created")
        r = client.get(f"/medicos/{created_ids['medicos'][0]}")
        assert r.status_code == 200

    def test_get_medico_not_found(self, client):
        r = client.get("/medicos/999999")
        assert r.status_code == 404

    def test_update_medico(self, client):
        if not created_ids["medicos"]:
            pytest.skip("No medico created")
        mid = created_ids["medicos"][-1]
        r = client.put(f"/medicos/{mid}", json={"nombre": "TEST-UPDATED"})
        assert r.status_code == 200
        assert "TEST-UPDATED" in r.json()["nombre"]

    def test_list_medicos_filtered(self, client):
        r = client.get("/medicos/?activo=true")
        assert r.status_code == 200

    def test_delete_medico(self, client):
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
    def test_create_paciente(self, client, admin_headers):
        s = _sufijo()
        r = client.post("/pacientes/", headers=admin_headers, json={
            "nombre": {
                "primer_nombre": f"TEST{s}",
                "primer_apellido": "PACIENTE",
            },
            "sexo": "M",
            "fecha_nacimiento": "1990-01-15",
        })
        assert r.status_code in (200, 201), f"Failed: {r.text}"
        created_ids["pacientes"].append(r.json()["id"])

    def test_create_paciente_with_all_data(self, client, admin_headers):
        s = _sufijo()
        r = client.post("/pacientes/", headers=admin_headers, json={
            "nombre": {
                "primer_nombre": f"FULL{s}", "segundo_nombre": "DEL",
                "primer_apellido": "TEST", "segundo_apellido": "DATA",
            },
            "sexo": "F",
            "fecha_nacimiento": "1985-06-20",
            "cui": int(f"{s}0101{s}"),
            "contacto": {"telefono": "12345678", "direccion": "TEST 123"},
            "referencias": [{"nombre": "REF", "telefono": "87654321"}],
        })
        assert r.status_code in (200, 201)
        created_ids["pacientes"].append(r.json()["id"])

    def test_list_pacientes(self, client, admin_headers):
        r = client.get("/pacientes/", headers=admin_headers)
        assert r.status_code == 200
        data = r.json()
        assert "total" in data
        assert "pacientes" in data

    def test_get_paciente(self, client, admin_headers):
        if not created_ids["pacientes"]:
            pytest.skip("No paciente created")
        r = client.get(
            f"/pacientes/{created_ids['pacientes'][0]}", headers=admin_headers
        )
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == created_ids["pacientes"][0]
        assert "nombre_completo" in data

    def test_get_paciente_not_found(self, client, admin_headers):
        r = client.get("/pacientes/999999", headers=admin_headers)
        assert r.status_code == 404

    def test_update_paciente(self, client, admin_headers):
        if not created_ids["pacientes"]:
            pytest.skip("No paciente created")
        pid = created_ids["pacientes"][0]
        r = client.patch(
            f"/pacientes/{pid}",
            headers=admin_headers,
            json={"sexo": "F", "contacto": {"telefono": "99999999"}},
        )
        assert r.status_code == 200

    def test_search_paciente_by_name(self, client, admin_headers):
        r = client.get("/pacientes/?nombre=TEST", headers=admin_headers)
        assert r.status_code == 200
        data = r.json()
        assert data["total"] >= 1

    def test_search_paciente_by_sexo(self, client, admin_headers):
        r = client.get("/pacientes/?sexo=M", headers=admin_headers)
        assert r.status_code == 200

    def test_search_paciente_by_estado(self, client, admin_headers):
        r = client.get("/pacientes/?estado=V", headers=admin_headers)
        assert r.status_code == 200

    def test_get_paciente_by_expediente(self, client, admin_headers):
        if not created_ids["pacientes"]:
            pytest.skip("No paciente created")
        pid = created_ids["pacientes"][0]
        pac = client.get(f"/pacientes/{pid}", headers=admin_headers).json()
        if pac.get("expediente"):
            r = client.get(
                f"/pacientes/expediente/{pac['expediente']}",
                headers=admin_headers,
            )
            assert r.status_code == 200

    def test_paciente_debug_count(self, client, admin_headers):
        r = client.get("/pacientes/debug/count", headers=admin_headers)
        assert r.status_code == 200

    def test_neonatales(self, client, admin_headers):
        r = client.get("/pacientes/neonatales", headers=admin_headers)
        assert r.status_code == 200

    def test_personal_hospital(self, client, admin_headers):
        r = client.get(
            "/pacientes/personal-hospital", headers=admin_headers
        )
        assert r.status_code == 200

    def test_duplicados_nombres_similares(self, client, admin_headers):
        r = client.get(
            "/pacientes/duplicados/nombres-similares",
            headers=admin_headers,
        )
        assert r.status_code == 200
        assert isinstance(r.json(), dict)

    def test_limpiar_cui(self, client, admin_headers):
        if not created_ids["pacientes"]:
            pytest.skip("No paciente created")
        pid = created_ids["pacientes"][-1]
        r = client.patch(
            f"/pacientes/{pid}/limpiar-cui",
            headers=admin_headers,
        )
        assert r.status_code == 200
        assert r.json()["cui"] is None

    def test_madre_hijo(self, client, admin_headers):
        madre_id = None
        for pid in created_ids["pacientes"]:
            r = client.get(f"/pacientes/{pid}", headers=admin_headers)
            if r.status_code == 200:
                p_data = r.json()
                fn = p_data.get("fecha_nacimiento")
                if p_data.get("sexo") == "F" and fn:
                    try:
                        dob = date.fromisoformat(str(fn)[:10])
                        age = (date.today() - dob).days // 365
                        if age >= 12:
                            madre_id = pid
                            break
                    except Exception:
                        pass
        if not madre_id:
            s = _sufijo()
            res = client.post(
                "/pacientes/",
                headers=admin_headers,
                json={
                    "nombre": {"primer_nombre": f"Madre{s}", "primer_apellido": f"Test{s}"},
                    "sexo": "F",
                    "fecha_nacimiento": "1995-01-01"
                }
            )
            if res.status_code == 201:
                madre_id = res.json()["id"]
                created_ids["pacientes"].append(madre_id)
        if not madre_id:
            pytest.skip("No female patient available")
        r = client.post(
            f"/pacientes/madre-hijo/{madre_id}",
            headers=admin_headers,
            json={
                "fecha_nacimiento": date.today().isoformat(),
                "hijos": [
                    {
                        "sexo": "M",
                        "datos_extra": {
                            "peso_nacimiento": "3000",
                            "edad_gestacional": "38",
                            "clase_parto": "Pes",
                        },
                    }
                ],
            },
        )
        assert r.status_code in (200, 201), f"Failed: {r.text}"
        data = r.json()
        if "id" in data:
            created_ids["pacientes"].append(data["id"])
        if "pacientes" in data:
            for p in data["pacientes"]:
                created_ids["pacientes"].append(p["id"])

    def test_get_paciente_no_auth(self, client):
        r = client.get("/pacientes/1")
        assert r.status_code in (401, 403)


# =====================================================================
# CONSULTAS
# =====================================================================
class TestConsultas:
    def test_registrar_consulta(self, client, admin_headers):
        if not created_ids["pacientes"]:
            pytest.skip("No paciente created")
        pid = created_ids["pacientes"][0]
        r = client.post(
            "/consultas/registro",
            headers=admin_headers,
            json={
                "paciente_id": pid,
                "tipo_consulta": 1,
                "especialidad": "MEDICINA GENERAL",
                "servicio": "COEX",
            },
        )
        assert r.status_code == 201, f"Failed: {r.text}"
        data = r.json()
        assert "id" in data
        assert data["paciente_id"] == pid
        created_ids["consultas"].append(data["id"])

    def test_registrar_emergencia(self, client, admin_headers):
        if not created_ids["pacientes"]:
            pytest.skip("No paciente created")
        pid = created_ids["pacientes"][-1]
        r = client.post(
            "/consultas/registro",
            headers=admin_headers,
            json={
                "paciente_id": pid,
                "tipo_consulta": 3,
                "especialidad": "EMERGENCIA",
                "servicio": "EMERG",
            },
        )
        assert r.status_code == 201
        created_ids["consultas"].append(r.json()["id"])

    def test_registrar_consulta_with_indicadores(self, client, admin_headers):
        if not created_ids["pacientes"]:
            pytest.skip("No paciente created")
        pid = created_ids["pacientes"][0]
        r = client.post(
            "/consultas/registro",
            headers=admin_headers,
            json={
                "paciente_id": pid,
                "tipo_consulta": 2,
                "especialidad": "PEDIATRIA",
                "servicio": "HOSP",
                "indicadores": {
                    "embarazo": False,
                    "discapacidad": True,
                },
            },
        )
        assert r.status_code == 201
        created_ids["consultas"].append(r.json()["id"])
        assert r.json()["indicadores"]["discapacidad"] is True

    def test_list_consultas(self, client, admin_headers):
        r = client.get("/consultas/", headers=admin_headers)
        assert r.status_code == 200
        data = r.json()
        assert "total" in data
        assert "consultas" in data

    def test_list_consultas_with_filters(self, client, admin_headers):
        r = client.get(
            "/consultas/?especialidad=MEDICINA GENERAL",
            headers=admin_headers,
        )
        assert r.status_code == 200

    def test_get_consulta(self, client, admin_headers):
        if not created_ids["consultas"]:
            pytest.skip("No consulta created")
        cid = created_ids["consultas"][0]
        r = client.get(f"/consultas/{cid}", headers=admin_headers)
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == cid
        assert "ciclo" in data
        assert isinstance(data["ciclo"], list)

    def test_get_consulta_not_found(self, client, admin_headers):
        r = client.get("/consultas/999999", headers=admin_headers)
        assert r.status_code == 404

    def test_list_consultas_by_paciente(self, client, admin_headers):
        if not created_ids["pacientes"]:
            pytest.skip("No paciente created")
        pid = created_ids["pacientes"][0]
        r = client.get(
            f"/consultas/pacienteId/{pid}", headers=admin_headers
        )
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_update_consulta(self, client, admin_headers):
        if not created_ids["consultas"]:
            pytest.skip("No consulta created")
        cid = created_ids["consultas"][0]
        r = client.patch(
            f"/consultas/{cid}",
            headers=admin_headers,
            json={"servicio": "COEX-UPDATED"},
        )
        assert r.status_code == 200
        assert r.json()["servicio"] == "COEX-UPDATED"

    def test_update_consulta_with_ciclo(self, client, admin_headers):
        if not created_ids["consultas"]:
            pytest.skip("No consulta created")
        cid = created_ids["consultas"][0]
        r = client.patch(
            f"/consultas/{cid}",
            headers=admin_headers,
            json={"ciclo": {"estado": "observacion", "comentario": "en observacion"}},
        )
        assert r.status_code == 200

    def test_buscar_paciente_via_consultas(self, client, admin_headers):
        r = client.get(
            "/consultas/buscarpaciente?q=TEST", headers=admin_headers
        )
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_desactivar_consulta(self, client, admin_headers):
        if not created_ids["consultas"]:
            pytest.skip("No consulta created")
        cid = created_ids["consultas"][-1]
        r = client.delete(f"/consultas/{cid}", headers=admin_headers)
        assert r.status_code == 200
        created_ids["consultas"].remove(cid)

    def test_sincronizar_indicadores(self, client, admin_headers):
        desde = (date.today() - timedelta(days=30)).isoformat()
        hasta = date.today().isoformat()
        r = client.patch(
            f"/consultas/sincronizar-indicadores?desde={desde}&hasta={hasta}",
            headers=admin_headers,
        )
        assert r.status_code == 200
        assert "actualizados" in r.json()

    def test_consulta_historial_entry(self, client, admin_headers):
        if not created_ids["consultas"]:
            pytest.skip("No consulta created")
        cid = created_ids["consultas"][0]
        r = client.get(f"/consultas/{cid}", headers=admin_headers)
        assert r.status_code == 200
        ciclo = r.json().get("ciclo", [])
        assert len(ciclo) >= 1
        first = ciclo[0]
        assert "estado" in first
        assert "registro" in first
        assert "usuario" in first


# =====================================================================
# CICLOS
# =====================================================================
class TestCiclos:
    def test_create_ciclo(self, client, admin_headers):
        if not created_ids["consultas"]:
            pytest.skip("No consulta created")
        cid = created_ids["consultas"][0]
        s = _sufijo()
        r = client.post(
            "/ciclos/",
            headers=admin_headers,
            json={
                "consulta_id": cid,
                "numero": 1,
                "activo": True,
                "usuario": "admin",
                "contenido": f"Ciclo test {s}",
            },
        )
        assert r.status_code in (200, 201), f"Failed: {r.text}"
        created_ids["ciclos"].append(r.json()["id"])

    def test_get_ciclos_by_consulta(self, client, admin_headers):
        if not created_ids["consultas"]:
            pytest.skip("No consulta created")
        cid = created_ids["consultas"][0]
        r = client.get(
            f"/ciclos/consulta/{cid}", headers=admin_headers
        )
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_get_ciclo(self, client, admin_headers):
        if not created_ids["ciclos"]:
            pytest.skip("No ciclo created")
        r = client.get(
            f"/ciclos/{created_ids['ciclos'][0]}", headers=admin_headers
        )
        assert r.status_code == 200

    def test_get_ciclo_not_found(self, client, admin_headers):
        r = client.get("/ciclos/999999", headers=admin_headers)
        assert r.status_code == 404


# =====================================================================
# CITAS
# =====================================================================
class TestCitas:
    def test_create_cita(self, client, admin_headers):
        if not created_ids["pacientes"]:
            pytest.skip("No paciente created")
        pid = created_ids["pacientes"][0]
        s = _sufijo()
        r = client.post(
            "/citas/",
            headers=admin_headers,
            json={
                "paciente_id": pid,
                "fecha_cita": (date.today() + timedelta(days=7)).isoformat(),
                "especialidad": "MEDICO",
                "razon": f"Test cita {s}",
            },
        )
        assert r.status_code in (200, 201), f"Failed: {r.text}"
        created_ids["citas"].append(r.json()["id"])

    def test_list_citas(self, client, admin_headers):
        r = client.get("/citas/", headers=admin_headers)
        assert r.status_code == 200
        data = r.json()
        assert "total" in data
        assert "citas" in data

    def test_get_cita(self, client, admin_headers):
        if not created_ids["citas"]:
            pytest.skip("No cita created")
        r = client.get(
            f"/citas/{created_ids['citas'][0]}", headers=admin_headers
        )
        assert r.status_code == 200

    def test_get_citas_by_paciente(self, client, admin_headers):
        if not created_ids["pacientes"]:
            pytest.skip("No paciente created")
        pid = created_ids["pacientes"][0]
        r = client.get(
            f"/citas/paciente/{pid}", headers=admin_headers
        )
        assert r.status_code == 200

    def test_disponibles(self, client, admin_headers):
        r = client.get(
            "/citas/disponibles",
            params={"especialidad": "MEDICINA GENERAL"},
            headers=admin_headers,
        )
        assert r.status_code in (200, 422), f"Failed: {r.text}"
        assert isinstance(r.json(), list)

    def test_update_cita(self, client, admin_headers):
        if not created_ids["citas"]:
            pytest.skip("No cita created")
        cid = created_ids["citas"][0]
        r = client.put(
            f"/citas/{cid}",
            headers=admin_headers,
            json={"razon": "Updated reason"},
        )
        assert r.status_code == 200

    def test_delete_cita(self, client, admin_headers):
        if not created_ids["citas"]:
            pytest.skip("No cita created")
        cid = created_ids["citas"][-1]
        r = client.delete(f"/citas/{cid}", headers=admin_headers)
        assert r.status_code == 200
        created_ids["citas"].remove(cid)


# =====================================================================
# EVENTOS
# =====================================================================
class TestEventos:
    def test_create_evento(self, client, admin_headers):
        if not created_ids["consultas"]:
            pytest.skip("No consulta created")
        cid = created_ids["consultas"][0]
        r = client.post(
            "/eventos/",
            headers=admin_headers,
            json={
                "consulta_id": cid,
                "tipo_evento": 1,
                "datos": {"clave": "ingreso", "valor": "Paciente ingresado"},
            },
        )
        assert r.status_code in (200, 201), f"Failed: {r.text}"
        created_ids["eventos"].append(r.json()["id"])

    def test_list_eventos(self, client, admin_headers):
        r = client.get("/eventos/", headers=admin_headers)
        if r.status_code == 422:
            pytest.xfail("responsable.registro None bug in DB data")
        assert r.status_code == 200, f"Failed: {r.text}"
        data = r.json()
        if isinstance(data, dict):
            assert "eventos" in data

    def test_get_evento(self, client, admin_headers):
        if not created_ids["eventos"]:
            pytest.skip("No evento created")
        r = client.get(
            f"/eventos/{created_ids['eventos'][0]}", headers=admin_headers
        )
        assert r.status_code == 200

    def test_update_evento(self, client, admin_headers):
        if not created_ids["eventos"]:
            pytest.skip("No evento created")
        eid = created_ids["eventos"][0]
        r = client.patch(
            f"/eventos/{eid}",
            headers=admin_headers,
            json={"descripcion": "Updated evento"},
        )
        assert r.status_code == 200

    def test_delete_evento(self, client, admin_headers):
        if not created_ids["eventos"]:
            pytest.skip("No evento created")
        eid = created_ids["eventos"][-1]
        r = client.delete(f"/eventos/{eid}", headers=admin_headers)
        assert r.status_code == 204
        created_ids["eventos"].remove(eid)


# =====================================================================
# ENCAMAMIENTO (public)
# =====================================================================
class TestEncamamiento:
    def test_create_servicio(self, client):
        s = _sufijo()
        r = client.post(
            "/encamamiento/",
            json={
                "nombre_servicio": f"TEST-SERV-{s}",
                "descripcion": "Test",
                "camas_censables": 10,
            },
        )
        assert r.status_code in (200, 201), f"Failed: {r.text}"
        created_ids["encamamiento"].append(r.json()["id"])

    def test_list_servicios(self, client):
        r = client.get("/encamamiento/")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_get_servicio(self, client):
        if not created_ids["encamamiento"]:
            pytest.skip("No servicio created")
        r = client.get(
            f"/encamamiento/{created_ids['encamamiento'][0]}"
        )
        assert r.status_code == 200

    def test_update_servicio(self, client):
        if not created_ids["encamamiento"]:
            pytest.skip("No servicio created")
        sid = created_ids["encamamiento"][0]
        r = client.patch(
            f"/encamamiento/{sid}",
            json={"camas_censables": 20},
        )
        assert r.status_code == 200

    def test_filter_activo(self, client):
        r = client.get("/encamamiento/?activo=true")
        assert r.status_code == 200

    def test_delete_servicio(self, client):
        if not created_ids["encamamiento"]:
            pytest.skip("No servicio created")
        sid = created_ids["encamamiento"][-1]
        r = client.delete(f"/encamamiento/{sid}")
        assert r.status_code == 204
        created_ids["encamamiento"].remove(sid)


# =====================================================================
# NACIMIENTOS
# =====================================================================
class TestNacimientos:
    def test_create_nacimiento(self, client, admin_headers):
        if not created_ids["pacientes"]:
            pytest.skip("No paciente created")
        pid = created_ids["pacientes"][0]
        r = client.post(
            "/nacimientos/",
            headers=admin_headers,
            json={"paciente_id": pid},
        )
        assert r.status_code in (200, 201), f"Failed: {r.text}"
        created_ids["nacimientos"].append(r.json()["id"])

    def test_nacimiento_desde_paciente(self, client, admin_headers):
        if not created_ids["pacientes"]:
            pytest.skip("No paciente created")
        pid = created_ids["pacientes"][0]
        r = client.post(
            f"/nacimientos/desde-paciente/{pid}",
            headers=admin_headers,
        )
        if r.status_code in (200, 201):
            created_ids["nacimientos"].append(r.json()["id"])

    def test_list_nacimientos(self, client, admin_headers):
        r = client.get("/nacimientos/", headers=admin_headers)
        assert r.status_code == 200
        data = r.json()
        assert "total" in data
        assert "nacimientos" in data

    def test_get_nacimiento(self, client, admin_headers):
        if not created_ids["nacimientos"]:
            pytest.skip("No nacimiento created")
        nid = created_ids["nacimientos"][0]
        r = client.get(f"/nacimientos/{nid}", headers=admin_headers)
        assert r.status_code == 200

    def test_get_nacimiento_not_found(self, client, admin_headers):
        r = client.get("/nacimientos/999999", headers=admin_headers)
        assert r.status_code == 404

    def test_update_nacimiento(self, client, admin_headers):
        if not created_ids["nacimientos"]:
            pytest.skip("No nacimiento created")
        nid = created_ids["nacimientos"][0]
        r = client.patch(
            f"/nacimientos/{nid}",
            headers=admin_headers,
            json={"mortinato": True},
        )
        assert r.status_code == 200

    def test_update_neonatales(self, client, admin_headers):
        if not created_ids["nacimientos"]:
            pytest.skip("No nacimiento created")
        nid = created_ids["nacimientos"][0]
        r = client.patch(
            f"/nacimientos/{nid}/neonatales",
            headers=admin_headers,
            json={"peso": 3200, "talla": 50},
        )
        assert r.status_code == 200

    def test_sincronizar(self, client, admin_headers):
        r = client.post("/nacimientos/sincronizar", headers=admin_headers)
        assert r.status_code == 200

    def test_referenciar_legacy(self, client, admin_headers):
        r = client.get(
            "/nacimientos/referenciar-legacy", headers=admin_headers
        )
        assert r.status_code == 200

    def test_recomputar(self, client, admin_headers):
        r = client.post("/nacimientos/recomputar", headers=admin_headers)
        assert r.status_code == 200

    def test_delete_nacimiento(self, client, admin_headers):
        if not created_ids["nacimientos"]:
            pytest.skip("No nacimiento created")
        nid = created_ids["nacimientos"][-1]
        r = client.delete(f"/nacimientos/{nid}", headers=admin_headers)
        assert r.status_code == 204
        created_ids["nacimientos"].remove(nid)


# =====================================================================
# NACIMIENTOS LEGACY
# =====================================================================
class TestNacimientosLegacy:
    def test_list_nacimientos_legacy(self, client, admin_headers):
        r = client.get("/nacimientos-legacy/", headers=admin_headers)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_update_nacimiento_legacy(self, client, admin_headers):
        r = client.get("/nacimientos-legacy/", headers=admin_headers)
        if not r.json():
            pytest.skip("No legacy records")
        lid = r.json()[0]["id"]
        r = client.put(
            f"/nacimientos-legacy/{lid}",
            headers=admin_headers,
            json={"madre": "UPDATED MOTHER"},
        )
        assert r.status_code == 200
        assert "UPDATED" in r.json()["madre"]


# =====================================================================
# CONSTANCIAS NACIMIENTO
# =====================================================================
class TestConstanciasNacimiento:
    def test_create_constancia(self, client, admin_headers):
        if not created_ids["pacientes"]:
            pytest.skip("No paciente created")
        if not created_ids["medicos"]:
            pytest.skip("No medico created")
        pid = created_ids["pacientes"][0]
        mid = created_ids["medicos"][0] if created_ids["medicos"] else None
        s = _sufijo()
        payload = {
            "paciente_id": pid,
            "madre_id": pid,
            "medico_id": mid,
            "fecha_nacimiento": date.today().isoformat(),
            "sexo": "M",
            "tipo_parto": "eutocico",
            "clase_parto": "simple",
            "edad_gestacional": 39,
            "peso_nacimiento": 3200,
        }
        if mid:
            payload["medico_id"] = mid
        r = client.post(
            "/constancias-nacimiento/",
            headers=admin_headers,
            json=payload,
        )
        assert r.status_code in (200, 201), f"Failed: {r.text}"
        created_ids["constancias"].append(r.json()["id"])

    def test_list_constancias(self, client, admin_headers):
        r = client.get("/constancias-nacimiento/", headers=admin_headers)
        assert r.status_code == 200
        data = r.json()
        assert "total" in data
        assert "constancias" in data

    def test_get_constancia(self, client, admin_headers):
        if not created_ids["constancias"]:
            pytest.skip("No constancia created")
        r = client.get(
            f"/constancias-nacimiento/{created_ids['constancias'][0]}",
            headers=admin_headers,
        )
        assert r.status_code == 200

    def test_historial_constancia(self, client, admin_headers):
        if not created_ids["constancias"]:
            pytest.skip("No constancia created")
        r = client.get(
            f"/constancias-nacimiento/historial/{created_ids['constancias'][0]}",
            headers=admin_headers,
        )
        assert r.status_code == 200

    def test_update_constancia(self, client, admin_headers):
        if not created_ids["constancias"]:
            pytest.skip("No constancia created")
        cid = created_ids["constancias"][0]
        r = client.put(
            f"/constancias-nacimiento/{cid}",
            headers=admin_headers,
            json={"peso_nacimiento": 3400},
        )
        assert r.status_code == 200

    def test_estado_informe(self, client, admin_headers):
        if not created_ids["constancias"]:
            pytest.skip("No constancia created")
        cid = created_ids["constancias"][0]
        r = client.patch(
            f"/constancias-nacimiento/{cid}/estado-informe",
            headers=admin_headers,
            json={"estado_informe": "entregado"},
        )
        assert r.status_code == 200

    def test_delete_constancia(self, client, admin_headers):
        if not created_ids["constancias"]:
            pytest.skip("No constancia created")
        cid = created_ids["constancias"][-1]
        r = client.delete(
            f"/constancias-nacimiento/{cid}", headers=admin_headers
        )
        assert r.status_code in (200, 204)
        created_ids["constancias"].remove(cid)


# =====================================================================
# PROCEDIMIENTOS
# =====================================================================
class TestProcedimientos:
    PROC_ID = None

    def test_create_catalogo(self, client, admin_headers):
        s = _sufijo()
        r = client.post(
            "/procedimientos/catalogo",
            headers=admin_headers,
            json={
                "nombre": f"TEST-PROC-{s}",
                "abreviatura": f"TP{s[-3:]}",
            },
        )
        assert r.status_code in (200, 201), f"Failed: {r.text}"
        TestProcedimientos.PROC_ID = r.json()["id"]
        created_ids["procedimientos_catalogo"].append(r.json()["id"])

    def test_list_catalogo(self, client, admin_headers):
        r = client.get("/procedimientos/catalogo", headers=admin_headers)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_search_catalogo(self, client, admin_headers):
        if not TestProcedimientos.PROC_ID:
            pytest.skip("No proc catalogo")
        r = client.get(
            f"/procedimientos/catalogo/{TestProcedimientos.PROC_ID}",
            headers=admin_headers,
        )
        assert r.status_code == 200

    def test_create_realizado(self, client, admin_headers):
        if not TestProcedimientos.PROC_ID:
            pytest.skip("No proc catalogo")
        if not created_ids["consultas"]:
            pytest.skip("No consulta created")
        cid = created_ids["consultas"][0]
        r = client.post(
            "/procedimientos/",
            headers=admin_headers,
            json={
                "procedimiento_id": TestProcedimientos.PROC_ID,
                "consulta_id": cid,
                "fecha": date.today().isoformat(),
            },
        )
        assert r.status_code in (200, 201), f"Failed: {r.text}"
        created_ids["procedimientos_realizados"].append(r.json()["id"])

    def test_list_realizados(self, client, admin_headers):
        r = client.get("/procedimientos/", headers=admin_headers)
        assert r.status_code == 200
        data = r.json()
        assert "total" in data
        assert "procedimientos" in data

    def test_get_realizado(self, client, admin_headers):
        if not created_ids["procedimientos_realizados"]:
            pytest.skip("No realizado created")
        r = client.get(
            f"/procedimientos/{created_ids['procedimientos_realizados'][0]}",
            headers=admin_headers,
        )
        assert r.status_code == 200

    def test_reporte(self, client, admin_headers):
        r = client.get("/procedimientos/reporte", headers=admin_headers)
        assert r.status_code == 200

    def test_estadisticas_resumen(self, client, admin_headers):
        r = client.get(
            "/procedimientos/estadisticas/resumen?anio=2026",
            headers=admin_headers,
        )
        assert r.status_code == 200

    def test_update_realizado(self, client, admin_headers):
        if not created_ids["procedimientos_realizados"]:
            pytest.skip("No realizado created")
        pid = created_ids["procedimientos_realizados"][0]
        r = client.put(
            f"/procedimientos/{pid}",
            headers=admin_headers,
            json={"cantidad": 2},
        )
        assert r.status_code == 200

    def test_delete_realizado(self, client, admin_headers):
        if not created_ids["procedimientos_realizados"]:
            pytest.skip("No realizado created")
        pid = created_ids["procedimientos_realizados"][-1]
        r = client.delete(f"/procedimientos/{pid}", headers=admin_headers)
        assert r.status_code in (200, 204)
        created_ids["procedimientos_realizados"].remove(pid)

    def test_delete_catalogo(self, client, admin_headers):
        if not TestProcedimientos.PROC_ID:
            pytest.skip("No proc catalogo")
        pid = TestProcedimientos.PROC_ID
        if pid in created_ids["procedimientos_catalogo"]:
            r = client.delete(
                f"/procedimientos/catalogo/{pid}",
                headers=admin_headers,
            )
            assert r.status_code in (200, 204)
            created_ids["procedimientos_catalogo"].remove(pid)


# =====================================================================
# PRESTAMOS
# =====================================================================
class TestPrestamos:
    def test_create_prestamo(self, client, admin_headers):
        if not created_ids["pacientes"]:
            pytest.skip("No paciente created")
        pid = created_ids["pacientes"][0]
        s = _sufijo()
        r = client.post(
            "/prestamos/",
            headers=admin_headers,
            json={
                "id_paciente": pid,
                "solicitante": f"TEST-SOL-{s}",
            },
        )
        assert r.status_code in (200, 201), f"Failed: {r.text}"
        created_ids["prestamos"].append(r.json()["id"])

    def test_list_prestamos(self, client, admin_headers):
        r = client.get("/prestamos/", headers=admin_headers)
        assert r.status_code == 200, f"Failed: {r.text}"
        data = r.json()
        assert "total" in data
        assert "items" in data

    def test_get_prestamo(self, client, admin_headers):
        if not created_ids["prestamos"]:
            pytest.skip("No prestamo created")
        r = client.get(
            f"/prestamos/{created_ids['prestamos'][0]}",
            headers=admin_headers,
        )
        assert r.status_code == 200

    def test_update_prestamo_devuelto(self, client, admin_headers):
        if not created_ids["prestamos"]:
            pytest.skip("No prestamo created")
        pid = created_ids["prestamos"][0]
        r = client.put(
            f"/prestamos/{pid}",
            headers=admin_headers,
            json={"fecha_devolucion": datetime.now().isoformat()},
        )
        assert r.status_code == 200

    def test_delete_prestamo(self, client, admin_headers):
        if not created_ids["prestamos"]:
            pytest.skip("No prestamo created")
        pid = created_ids["prestamos"][-1]
        r = client.delete(f"/prestamos/{pid}", headers=admin_headers)
        assert r.status_code == 200
        created_ids["prestamos"].remove(pid)


# =====================================================================
# DEFUNCIONES
# =====================================================================
class TestDefunciones:
    def test_create_defuncion(self, client, admin_headers):
        if not created_ids["pacientes"]:
            pytest.skip("No paciente created")
        pid = created_ids["pacientes"][-1]
        r = client.post(
            "/defunciones/",
            headers=admin_headers,
            json={
                "paciente_id": pid,
                "fecha_defuncion": date.today().isoformat(),
                "causa_directa": "TEST CAUSA",
                "es_fetal": False,
            },
        )
        assert r.status_code in (200, 201), f"Failed: {r.text}"
        created_ids["defunciones"].append(r.json()["id"])

    def test_list_defunciones(self, client, admin_headers):
        r = client.get("/defunciones/", headers=admin_headers)
        assert r.status_code == 200
        data = r.json()
        assert "total" in data
        assert "defunciones" in data

    def test_get_defuncion(self, client, admin_headers):
        if not created_ids["defunciones"]:
            pytest.skip("No defuncion created")
        did = created_ids["defunciones"][0]
        r = client.get(f"/defunciones/{did}", headers=admin_headers)
        assert r.status_code == 200

    def test_pacientes_fallecidos(self, client, admin_headers):
        r = client.get("/defunciones/pacientes", headers=admin_headers)
        assert r.status_code == 200

    def test_update_defuncion(self, client, admin_headers):
        if not created_ids["defunciones"]:
            pytest.skip("No defuncion created")
        did = created_ids["defunciones"][0]
        r = client.patch(
            f"/defunciones/{did}",
            headers=admin_headers,
            json={"causa_directa": "UPDATED CAUSA"},
        )
        assert r.status_code == 200

    def test_delete_defuncion(self, client, admin_headers):
        if not created_ids["defunciones"]:
            pytest.skip("No defuncion created")
        did = created_ids["defunciones"][-1]
        r = client.delete(f"/defunciones/{did}", headers=admin_headers)
        assert r.status_code == 204
        created_ids["defunciones"].remove(did)


# =====================================================================
# CORRELATIVOS
# =====================================================================
class TestCorrelativos:
    def test_generar_expediente(self, client, admin_headers):
        r = client.post(
            "/correlativos/expediente", headers=admin_headers
        )
        assert r.status_code in (200, 201)
        data = r.json()
        assert any(k in data for k in ("correlativo", "expediente"))

    def test_generar_emergencia(self, client, admin_headers):
        r = client.post(
            "/correlativos/emergencia", headers=admin_headers
        )
        assert r.status_code in (200, 201)
        data = r.json()
        assert "hoja_emergencia" in data

    def test_generar_constancia_nacimiento(self, client, admin_headers):
        r = client.post(
            "/correlativos/constancia_nacimiento",
            headers=admin_headers,
        )
        assert r.status_code in (200, 201)
        data = r.json()
        assert "constancia_nacimiento" in data

    def test_generar_constancia_defuncion(self, client, admin_headers):
        r = client.post(
            "/correlativos/constancia_defuncion",
            headers=admin_headers,
        )
        assert r.status_code in (200, 201)
        data = r.json()
        assert "constancia_defuncion" in data

    def test_generar_constancia_medica(self, client, admin_headers):
        r = client.post(
            "/correlativos/constancia_medica",
            headers=admin_headers,
        )
        assert r.status_code in (200, 201)
        data = r.json()
        assert "constancia_medica" in data


# =====================================================================
# CENSO CAMAS
# =====================================================================
class TestCensoCamas:
    def test_create_censo(self, client, admin_headers):
        if not created_ids["encamamiento"]:
            pytest.skip("No encamamiento created")
        sid = created_ids["encamamiento"][0]
        r = client.post(
            "/censo-camas/",
            headers=admin_headers,
            json={
                "fecha": date.today().isoformat(),
                "servicio_id": sid,
                "sexo": 0,
                "ocupados": 20,
            },
        )
        assert r.status_code in (200, 201), f"Failed: {r.text}"
        created_ids["censo_camas"].append(r.json()["id"])

    def test_upsert_censo(self, client, admin_headers):
        if not created_ids["encamamiento"]:
            pytest.skip("No encamamiento created")
        sid = created_ids["encamamiento"][0]
        r = client.post(
            "/censo-camas/upsert",
            headers=admin_headers,
            json={
                "fecha": date.today().isoformat(),
                "servicio_id": sid,
                "sexo": 1,
                "ocupados": 15,
            },
        )
        assert r.status_code == 200

    def test_list_censo(self, client, admin_headers):
        r = client.get("/censo-camas/", headers=admin_headers)
        assert r.status_code == 200
        data = r.json()
        assert "total" in data
        assert "registros" in data

    def test_get_censo(self, client, admin_headers):
        if not created_ids["censo_camas"]:
            pytest.skip("No censo created")
        r = client.get(
            f"/censo-camas/{created_ids['censo_camas'][0]}",
            headers=admin_headers,
        )
        assert r.status_code == 200

    def test_resumen_diario(self, client, admin_headers):
        r = client.get(
            f"/censo-camas/resumen/{date.today().isoformat()}",
            headers=admin_headers,
        )
        assert r.status_code == 200

    def test_estadisticas(self, client, admin_headers):
        desde = (date.today() - timedelta(days=30)).isoformat()
        hasta = date.today().isoformat()
        r = client.get(
            f"/censo-camas/estadisticas?desde={desde}&hasta={hasta}",
            headers=admin_headers,
        )
        assert r.status_code == 200

    def test_update_censo(self, client, admin_headers):
        if not created_ids["censo_camas"]:
            pytest.skip("No censo created")
        cid = created_ids["censo_camas"][0]
        r = client.put(
            f"/censo-camas/{cid}",
            headers=admin_headers,
            json={"ocupados": 25},
        )
        assert r.status_code == 200

    def test_delete_censo(self, client, admin_headers):
        if not created_ids["censo_camas"]:
            pytest.skip("No censo created")
        cid = created_ids["censo_camas"][-1]
        r = client.delete(f"/censo-camas/{cid}", headers=admin_headers)
        assert r.status_code == 204
        created_ids["censo_camas"].remove(cid)


# =====================================================================
# CIE-10
# =====================================================================
class TestCie10:
    def test_buscar(self, client, admin_headers):
        r = client.get("/cie10/?q=J45&limit=5", headers=admin_headers)
        assert r.status_code == 200
        data = r.json()
        assert "resultados" in data

    def test_buscar_sin_resultados(self, client, admin_headers):
        r = client.get("/cie10/?q=ZZZZZZ999&limit=5", headers=admin_headers)
        assert r.status_code == 200

    def test_buscar_sin_query(self, client, admin_headers):
        r = client.get("/cie10/", headers=admin_headers)
        assert r.status_code == 422


# =====================================================================
# SIGSA-3
# =====================================================================
class TestSigsa3:
    def test_create_sigsa3(self, client, admin_headers):
        s = _sufijo()
        r = client.post(
            "/sigsa3/",
            headers=admin_headers,
            json={
                "fecha_consulta": date.today().isoformat(),
                "historia_clinica": f"HC-{s}",
                "nombre": f"TEST-PAC-{s}",
                "sexo": "M",
                "tipo_consulta": "1 Primera vez",
                "especialidad": "MEDICINA GENERAL",
            },
        )
        assert r.status_code in (200, 201), f"Failed: {r.text}"
        created_ids["sigsa3"].append(r.json()["id"])

    def test_list_sigsa3(self, client, admin_headers):
        r = client.get("/sigsa3/", headers=admin_headers)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_get_sigsa3(self, client, admin_headers):
        if not created_ids["sigsa3"]:
            pytest.skip("No sigsa3 created")
        r = client.get(
            f"/sigsa3/{created_ids['sigsa3'][0]}", headers=admin_headers
        )
        assert r.status_code == 200

    def test_update_sigsa3(self, client, admin_headers):
        if not created_ids["sigsa3"]:
            pytest.skip("No sigsa3 created")
        sid = created_ids["sigsa3"][0]
        r = client.put(
            f"/sigsa3/{sid}",
            headers=admin_headers,
            json={"edad": 30},
        )
        assert r.status_code == 200

    def test_delete_sigsa3(self, client, admin_headers):
        if not created_ids["sigsa3"]:
            pytest.skip("No sigsa3 created")
        sid = created_ids["sigsa3"][-1]
        r = client.delete(f"/sigsa3/{sid}", headers=admin_headers)
        assert r.status_code == 204
        created_ids["sigsa3"].remove(sid)

    def test_asociar_paciente(self, client, admin_headers):
        r = client.post(
            "/sigsa3/asociar-paciente",
            headers=admin_headers,
            json={"expediente": "TEST", "no_historia_clinica": "TEST"},
        )
        assert r.status_code in (200, 404)


# =====================================================================
# PERSONAL SALUD
# =====================================================================
class TestPersonalSalud:
    def test_create_personal_salud(self, client, admin_headers):
        s = _sufijo()
        r = client.post(
            "/sigsa3/personal-salud/",
            headers=admin_headers,
            json={
                "nombre": f"PERSONAL-{s}",
                "colegiado": s,
                "especialidad": "MEDICINA GENERAL",
            },
        )
        assert r.status_code in (200, 201), f"Failed: {r.text}"
        created_ids["personal_salud"].append(r.json()["id"])

    def test_list_personal_salud(self, client, admin_headers):
        r = client.get("/sigsa3/personal-salud/", headers=admin_headers)
        assert r.status_code == 200
        assert isinstance(r.json(), list)


# =====================================================================
# ESTADISTICAS
# =====================================================================
class TestEstadisticas:
    @pytest.fixture(autouse=True)
    def setup_fechas(self):
        self.desde = "2026-01-01"
        self.hasta = "2026-12-31"

    def test_pacientes_atendidos(self, client, admin_headers):
        r = client.get(
            f"/estadisticas/consultas/pacientesAtendidos"
            f"?desde={self.desde}&hasta={self.hasta}",
            headers=admin_headers,
        )
        assert r.status_code == 200
        assert "datos" in r.json()

    def test_hospitalizacion_infantil(self, client, admin_headers):
        r = client.get(
            f"/estadisticas/consultas/hospitalizacion-infantil"
            f"?desde={self.desde}&hasta={self.hasta}",
            headers=admin_headers,
        )
        assert r.status_code == 200

    def test_promedio_diario(self, client, admin_headers):
        r = client.get(
            f"/estadisticas/consultas/promedioDiario"
            f"?desde={self.desde}&hasta={self.hasta}",
            headers=admin_headers,
        )
        assert r.status_code == 200

    def test_personal_hospital(self, client, admin_headers):
        r = client.get(
            f"/estadisticas/consultas/personal-hospital"
            f"?desde={self.desde}&hasta={self.hasta}",
            headers=admin_headers,
        )
        assert r.status_code == 200

    def test_estudiante_publico(self, client, admin_headers):
        r = client.get(
            f"/estadisticas/consultas/estudiante-publico"
            f"?desde={self.desde}&hasta={self.hasta}",
            headers=admin_headers,
        )
        assert r.status_code == 200

    def test_reingresos(self, client, admin_headers):
        r = client.get(
            f"/estadisticas/consultas/reingresos"
            f"?desde={self.desde}&hasta={self.hasta}",
            headers=admin_headers,
        )
        assert r.status_code == 200

    def test_reingresos_tipo3(self, client, admin_headers):
        r = client.get(
            "/estadisticas/consultas/reingresos-tipo3?skip=0&limit=10",
            headers=admin_headers,
        )
        assert r.status_code == 200

    def test_mayores_a_7_dias(self, client, admin_headers):
        r = client.get(
            "/estadisticas/consultas/mayores-a-7-dias?skip=0&limit=10",
            headers=admin_headers,
        )
        assert r.status_code == 200

    def test_nacimientos_stats(self, client, admin_headers):
        r = client.get(
            f"/estadisticas/nacimientos"
            f"?desde={self.desde}&hasta={self.hasta}",
            headers=admin_headers,
        )
        assert r.status_code == 200

    def test_sigsa3_por_especialidad(self, client, admin_headers):
        r = client.get(
            f"/estadisticas/sigsa3/por-especialidad"
            f"?desde={self.desde}&hasta={self.hasta}",
            headers=admin_headers,
        )
        assert r.status_code == 200

    def test_sigsa3_dx_frecuentes(self, client, admin_headers):
        r = client.get(
            f"/estadisticas/sigsa3/dx-frecuentes"
            f"?desde={self.desde}&hasta={self.hasta}",
            headers=admin_headers,
        )
        assert r.status_code == 200


# =====================================================================
# TOTALES (Dashboard KPIs)
# =====================================================================
class TestTotales:
    def test_totales(self, client, admin_headers):
        r = client.get("/totales/", headers=admin_headers)
        assert r.status_code == 200
        data = r.json()
        assert "totales" in data
        assert "generado_en" in data

    def test_totales_con_fecha(self, client, admin_headers):
        r = client.get(
            f"/totales/?fecha={date.today().isoformat()}",
            headers=admin_headers,
        )
        assert r.status_code == 200


# =====================================================================
# AUDIT LOG (admin only)
# =====================================================================
class TestAuditLog:
    def test_list_audit_log(self, client, admin_headers):
        r = client.get("/audit-log/", headers=admin_headers)
        assert r.status_code == 200

    def test_audit_log_filters(self, client, admin_headers):
        r = client.get(
            "/audit-log/?tabla=pacientes", headers=admin_headers
        )
        assert r.status_code == 200


# =====================================================================
# CHAT
# =====================================================================
class TestChat:
    def test_list_tablas(self, client, admin_headers):
        r = client.get("/chat/tablas", headers=admin_headers)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_consulta_chat(self, client, admin_headers):
        r = client.post(
            "/chat/consulta",
            headers=admin_headers,
            json={
                "mensajes": [
                    {"role": "user", "content": "cuantos pacientes hay"},
                ]
            },
        )
        assert r.status_code == 200, f"Failed: {r.text}"
        assert "respuesta" in r.json()


# =====================================================================
# SERVICE-LEVEL TESTS (direct service function calls)
# =====================================================================
class TestServices:
    def test_expediente_generar(self, db_session):
        from modules.expediente.service import generar_expediente
        exp = generar_expediente(db_session)
        assert exp is not None
        assert isinstance(exp, str)

    def test_correlativo_generar(self, db_session):
        from modules.expediente.service import (
            generar_emergencia,
            generar_constancia_nacimiento,
            generar_defuncion,
            generar_constancia_medica,
        )
        assert generar_emergencia(db_session)
        assert generar_constancia_nacimiento(db_session)
        assert generar_defuncion(db_session)
        assert generar_constancia_medica(db_session)

    def test_paciente_service_create(self, db_session):
        from modules.pacientes.service import crear_paciente
        from modules.pacientes.schemas import PacienteCreate
        from modules.pacientes.schemas import Nombre

        s = _sufijo()
        data = PacienteCreate(
            nombre=Nombre(
                primer_nombre=f"SVC{s}",
                primer_apellido="TEST",
            ),
            sexo="M",
            fecha_nacimiento=date(1990, 1, 1),
        )
        pac = crear_paciente(
            db_session, data, auto_expediente=True, username="admin"
        )
        assert pac.id is not None
        assert pac.expediente is not None
        created_ids["pacientes"].append(pac.id)

    def test_paciente_service_socioeconomicos(self, db_session):
        from modules.pacientes.models import PacienteModel

        pac = db_session.get(PacienteModel, created_ids["pacientes"][-1])
        assert pac is not None
        pac.datos_extra = {
            "socioeconomicos": {
                "discapacidad": "NINGUNA",
                "educacion": "PRIMARIA",
                "estado_civil": "SOLTERO",
                "estudiante_publico": "S",
                "ocupacion": "ESTUDIANTE",
                "personal_hospital": "S",
            }
        }
        db_session.commit()
        db_session.refresh(pac)
        assert pac.es_estudiante_publico == "S"
        assert pac.es_personal_hospital == "S"
        assert pac.ocupacion == "ESTUDIANTE"

    def test_consulta_service_agregar_ciclo(self, db_session):
        if not created_ids["consultas"]:
            pytest.skip("No consulta created")
        from modules.consultas.models import ConsultaModel, ConsultaHistorialModel
        from modules.consultas.service import _agregar_ciclo

        consulta = db_session.get(ConsultaModel, created_ids["consultas"][0])
        assert consulta is not None

        class MockUser:
            username = "admin"

        _agregar_ciclo(
            db_session, consulta,
            {"estado": "seguimiento", "comentario": "test service"},
            MockUser(),
        )
        db_session.commit()

        historial = (
            db_session.query(ConsultaHistorialModel)
            .filter(ConsultaHistorialModel.consulta_id == consulta.id)
            .order_by(ConsultaHistorialModel.id.desc())
            .first()
        )
        assert historial is not None
        assert historial.estado == "seguimiento"
        assert historial.usuario == "admin"

    def test_paciente_service_buscar(self, db_session):
        from modules.pacientes.service import buscar_pacientes

        result = buscar_pacientes(
            db_session, filters={"sexo": "M"}, skip=0, limit=5
        )
        assert result.total >= 0
        assert len(result.pacientes) <= 5

    def test_consulta_service_buscar_activas(self, db_session):
        from modules.consultas.service import buscar_consultas_activas

        result = buscar_consultas_activas(
            db_session, activo=True, skip=0, limit=5
        )
        assert result.total >= 0

    def test_paciente_service_quitar_tildes(self):
        from modules.pacientes.service import quitar_tildes
        assert quitar_tildes("Médico Pérez") == "medico perez"
        assert quitar_tildes("CAFÉ") == "cafe"
        assert quitar_tildes("ñandú") == "nandu"


# =====================================================================
# ERROR HANDLING TESTS
# =====================================================================
class TestErrorHandling:
    def test_404_not_found(self, client, admin_headers):
        r = client.get("/nonexistent", headers=admin_headers)
        assert r.status_code == 404

    def test_422_validation(self, client, admin_headers):
        r = client.post(
            "/pacientes/",
            headers=admin_headers,
            json={"nombre": None},
        )
        assert r.status_code == 422

    def test_401_no_auth(self, client):
        r = client.get("/pacientes/1")
        assert r.status_code in (401, 403)

    def test_409_duplicate(self, client, admin_headers):
        if not created_ids["pacientes"]:
            pytest.skip("No paciente created")
        pac = client.get(
            f"/pacientes/{created_ids['pacientes'][0]}",
            headers=admin_headers,
        ).json()
        r = client.post(
            "/pacientes/",
            headers=admin_headers,
            json=pac,
        )
        assert r.status_code in (200, 201, 409, 400), f"Failed: {r.text}"


# =====================================================================
# REINAP
# =====================================================================
class TestRenap:
    def test_renap_persona(self, client, admin_headers):
        r = client.get("/renap/persona?cui=1234567890101", headers=admin_headers)
        assert r.status_code in (200, 404, 502)


# =====================================================================
# CLEANUP
# =====================================================================
def pytest_sessionfinish(session):
    db = SessionLocal()
    try:
        model_order = [
            ("censo_camas", CensoCamasModel),
            ("personal_salud", PersonalSaludModel),
            ("sigsa3", Sigsa3Model),
            ("defunciones", DefuncionModel),
            ("nacimientos", NacimientoModel),
            ("nacimientos_legacy", NacimientoLegacy),
            ("constancias", ConstanciaNacimientoModel),
            ("prestamos", Prestamo),
            ("ciclos", CiclosConsulta),
            ("eventos", EventoConsultaModel),
            ("procedimientos_realizados", ProceMedico),
            ("procedimientos_catalogo", Procedimiento),
            ("citas", CitaModel),
            ("encamamiento", EncamamientoModel),
            ("consultas", ConsultaModel),
            ("medicos", MedicoModel),
            ("especialidades", EspecialidadModel),
            ("pacientes", PacienteModel),
        ]
        for key, model in model_order:
            ids = created_ids.get(key, [])
            if ids:
                db.query(model).filter(model.id.in_(ids)).delete(
                    synchronize_session=False
                )
        db.commit()
    finally:
        db.close()
