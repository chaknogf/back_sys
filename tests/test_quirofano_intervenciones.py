import pytest
import time as _time
from datetime import date

from core.database import SessionLocal
from modules.pacientes.models import PacienteModel
from modules.medicos.models import MedicoModel
from modules.especialidades.models import EspecialidadModel
from modules.quirofano.models import (
    IntervencionQuirurgicaModel,
    QuirofanoNumeroModel,
    ProcedimientoQuirofanoModel,
)
from modules.procedimientos.models import CatalogoProcedimiento, AreaCuerpoIntervenida
from sqlalchemy import text


created_ids = {
    "medicos": [],
    "pacientes": [],
    "intervenciones": [],
    "quirofanos_numero": [],
    "procedimientos_quirofano": [],
}


def cleanup():
    db = SessionLocal()
    try:
        for iid in created_ids["intervenciones"]:
            db.query(IntervencionQuirurgicaModel).filter(
                IntervencionQuirurgicaModel.intervencion_id == iid
            ).delete()
        for pid in created_ids["pacientes"]:
            db.query(PacienteModel).filter(PacienteModel.id == pid).delete()
        for mid in created_ids["medicos"]:
            db.query(MedicoModel).filter(MedicoModel.id == mid).delete()
        for qid in created_ids["quirofanos_numero"]:
            db.query(QuirofanoNumeroModel).filter(
                QuirofanoNumeroModel.quirofano_numero_id == qid
            ).delete()
        for tid in created_ids["procedimientos_quirofano"]:
            db.query(ProcedimientoQuirofanoModel).filter(
                ProcedimientoQuirofanoModel.procedimiento_quirofano_id == tid
            ).delete()
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


def _sufijo():
    return str(int(_time.time() * 1000000))[-6:]


class TestIntervencionesQuirurgicas:
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        yield
        cleanup()

    def _crear_medico(self, client):
        s = _sufijo()
        r = client.post(
            "/personal-atencion/",
            json={
                "nombre": f"Dr. Cirujano {s}",
                "colegiado": str(s),
            },
        )
        assert r.status_code in (200, 201)
        data = r.json()
        created_ids["medicos"].append(data["id"])
        return data

    def _crear_paciente(self, client, auth_headers):
        s = _sufijo()
        r = client.post(
            "/pacientes/?auto_expediente=true",
            headers=auth_headers,
            json={
                "nombre": {
                    "primer_nombre": f"Paciente{s}",
                    "primer_apellido": f"Quirofano{s}",
                },
                "sexo": "M",
                "fecha_nacimiento": "1985-05-15",
            },
        )
        assert r.status_code == 201
        data = r.json()
        created_ids["pacientes"].append(data["id"])
        return data

    def _crear_quirofano(self, client, auth_headers):
        s = _sufijo()
        r = client.post(
            "/quirofano/quirofanos-numero/",
            headers=auth_headers,
            json={"numero": int(s), "nombre": f"Quirófano {int(s)}"},
        )
        assert r.status_code == 201
        data = r.json()
        created_ids["quirofanos_numero"].append(data["quirofano_numero_id"])
        return data

    def test_listar_quirofanos_numero(self, client, auth_headers):
        r = client.get("/quirofano/quirofanos-numero/", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert len(data) >= 2
        assert all("numero" in q and "nombre" in q for q in data)

    def test_crear_quirofano_numero(self, client, auth_headers):
        s = _sufijo()
        r = client.post(
            "/quirofano/quirofanos-numero/",
            headers=auth_headers,
            json={"numero": int(s), "nombre": f"Quirófano {int(s)}"},
        )
        assert r.status_code == 201
        data = r.json()
        assert data["numero"] == int(s)
        assert data["activo"] is True
        qid = data["quirofano_numero_id"]
        created_ids["quirofanos_numero"].append(qid)

        r = client.put(
            f"/quirofano/quirofanos-numero/{qid}",
            headers=auth_headers,
            json={"nombre": f"Quirófano Modificado {s}"},
        )
        assert r.status_code == 200
        assert r.json()["nombre"] == f"Quirófano Modificado {s}"

    def test_quirofano_numero_requiere_admin(self, client):
        r = client.post(
            "/quirofano/quirofanos-numero/",
            json={"numero": 99, "nombre": "Quirófano 99"},
        )
        assert r.status_code in (401, 422, 403)

    def test_crear_intervencion(self, client, auth_headers):
        paciente = self._crear_paciente(client, auth_headers)
        medico = self._crear_medico(client)
        quirofano = self._crear_quirofano(client, auth_headers)

        r = client.post(
            "/quirofano/intervenciones/",
            headers=auth_headers,
            json={
                "paciente_id": paciente["id"],
                "personal_atencion_id": medico["id"],
                "quirofano_numero_id": quirofano["quirofano_numero_id"],
                "procedimiento_principal": "Apendicectomía",
                "procedimiento_2": "Lavado de cavidad",
                "area_cuerpo_intervenida": "Abdomen",
                "hora_inicio_anestesia": "07:45",
                "hora_inicio_intervencion": "08:10",
                "hora_finaliza_intervencion": "09:25",
                "hora_finaliza_limpieza_prepara_quirofano": "09:50",
                "observaciones": "Apendicectomía de urgencia",
            },
        )
        assert r.status_code == 201
        data = r.json()
        assert data["paciente_id"] == paciente["id"]
        assert data["personal_atencion_id"] == medico["id"]
        assert data["quirofano_numero_id"] == quirofano["quirofano_numero_id"]
        assert data["quirofano_numero_nombre"] == quirofano["nombre"]
        assert data["procedimiento_principal"] == "Apendicectomía"
        assert data["procedimiento_2"] == "Lavado de cavidad"
        assert data["area_cuerpo_intervenida"] == "Abdomen"
        assert data["hora_inicio_anestesia"] == "07:45:00"
        assert data["hora_inicio_intervencion"] == "08:10:00"
        assert data["hora_finaliza_intervencion"] == "09:25:00"
        assert data["hora_finaliza_limpieza_prepara_quirofano"] == "09:50:00"
        assert data["observaciones"] == "Apendicectomía de urgencia"
        assert data["activo"] is True
        created_ids["intervenciones"].append(data["intervencion_id"])

    def test_listar_intervenciones(self, client, auth_headers):
        paciente = self._crear_paciente(client, auth_headers)
        r = client.post(
            "/quirofano/intervenciones/",
            headers=auth_headers,
            json={
                "paciente_id": paciente["id"],
                "fecha": date.today().isoformat(),
            },
        )
        assert r.status_code == 201
        created_ids["intervenciones"].append(r.json()["intervencion_id"])

        r = client.get("/quirofano/intervenciones/", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert "total" in data
        assert "intervenciones" in data
        assert any(
            i["intervencion_id"] in created_ids["intervenciones"]
            for i in data["intervenciones"]
        )

    def test_filtrar_por_expediente(self, client, auth_headers):
        paciente = self._crear_paciente(client, auth_headers)
        r = client.post(
            "/quirofano/intervenciones/",
            headers=auth_headers,
            json={
                "paciente_id": paciente["id"],
                "fecha": date.today().isoformat(),
            },
        )
        data = r.json()
        created_ids["intervenciones"].append(data["intervencion_id"])
        expediente = data["expediente"]

        r = client.get(
            "/quirofano/intervenciones/",
            headers=auth_headers,
            params={"expediente": expediente},
        )
        assert r.status_code == 200
        resp = r.json()
        assert all(
            i["expediente"] == expediente for i in resp["intervenciones"]
        )

    def test_actualizar_intervencion(self, client, auth_headers):
        paciente = self._crear_paciente(client, auth_headers)
        r = client.post(
            "/quirofano/intervenciones/",
            headers=auth_headers,
            json={
                "paciente_id": paciente["id"],
                "fecha": date.today().isoformat(),
                "observaciones": "antes",
            },
        )
        data = r.json()
        created_ids["intervenciones"].append(data["intervencion_id"])
        iid = data["intervencion_id"]

        r = client.put(
            f"/quirofano/intervenciones/{iid}",
            headers=auth_headers,
            json={"observaciones": "después", "hora_inicio_intervencion": "10:15"},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["observaciones"] == "después"
        assert data["hora_inicio_intervencion"] == "10:15:00"

    def test_eliminar_intervencion(self, client, auth_headers):
        paciente = self._crear_paciente(client, auth_headers)
        r = client.post(
            "/quirofano/intervenciones/",
            headers=auth_headers,
            json={"paciente_id": paciente["id"], "fecha": date.today().isoformat()},
        )
        data = r.json()
        created_ids["intervenciones"].append(data["intervencion_id"])
        iid = data["intervencion_id"]

        r = client.delete(f"/quirofano/intervenciones/{iid}", headers=auth_headers)
        assert r.status_code == 200
        assert r.json() == {"eliminado": True}

        r = client.get(f"/quirofano/intervenciones/{iid}", headers=auth_headers)
        assert r.status_code == 404

    def test_intervencion_paciente_inexistente(self, client, auth_headers):
        r = client.post(
            "/quirofano/intervenciones/",
            headers=auth_headers,
            json={"paciente_id": 999999999, "fecha": date.today().isoformat()},
        )
        assert r.status_code == 404

    def test_crear_intervencion_todos_los_campos(self, client, auth_headers):
        """Llena absolutamente todos los campos: médico, FKs de catálogos, 5 procedimientos y tiempos."""
        from modules.quirofano.models import (
            EstadoCirugiaModel,
            FormatoProcedimientoModel,
            ProcedenciaProcedimientoModel,
            RangoEspecialistaModel,
        )

        db = SessionLocal()
        try:
            cats = (
                db.query(CatalogoProcedimiento)
                .order_by(CatalogoProcedimiento.id)
                .limit(5)
                .all()
            )
            area = db.query(AreaCuerpoIntervenida).order_by(AreaCuerpoIntervenida.id).first()
            especialidad = db.query(EspecialidadModel).order_by(EspecialidadModel.id).first()
            estado = db.query(EstadoCirugiaModel).first()
            formato = db.query(FormatoProcedimientoModel).first()
            procedencia = db.query(ProcedenciaProcedimientoModel).first()
            rango = db.query(RangoEspecialistaModel).first()
            assert len(cats) == 5
            assert all([area, especialidad, estado, formato, procedencia, rango])
            cat_ids = [c.id for c in cats]
            cat_nombres = {c.id: c.nombre for c in cats}
            estado_id, estado_nombre = estado.estado_cirugia_id, estado.nombre
            formato_id, formato_nombre = formato.formato_procedimiento_id, formato.nombre
            proc_id, proc_nombre = procedencia.procedencia_procedimiento_id, procedencia.nombre
            rango_id, rango_nombre = rango.rango_especialista_id, rango.nombre
            area_id, area_nombre = area.id, area.nombre
            esp_id, esp_nombre = especialidad.id, especialidad.nombre
        finally:
            db.close()

        paciente = self._crear_paciente(client, auth_headers)
        medico = self._crear_medico(client)
        quirofano = self._crear_quirofano(client, auth_headers)

        r = client.post(
            "/quirofano/intervenciones/",
            headers=auth_headers,
            json={
                "paciente_id": paciente["id"],
                "personal_atencion_id": medico["id"],
                "estado_cirugia_id": estado_id,
                "formato_procedimiento_id": formato_id,
                "procedencia_procedimiento_id": proc_id,
                "rango_especialista_id": rango_id,
                "especialidad_id": esp_id,
                "quirofano_numero_id": quirofano["quirofano_numero_id"],
                "procedimiento_principal": "Apendicectomía",
                "procedimiento_2": "Lavado de cavidad",
                "procedimiento_3": "Drenaje",
                "procedimiento_4": "Sutura",
                "procedimiento_5": "Cierre",
                "procedimiento_principal_id": cat_ids[0],
                "procedimiento_2_id": cat_ids[1],
                "procedimiento_3_id": cat_ids[2],
                "procedimiento_4_id": cat_ids[3],
                "procedimiento_5_id": cat_ids[4],
                "area_cuerpo_intervenida": area_nombre,
                "id_area_cuerpo_intervenida": area_id,
                "hora_inicio_anestesia": "07:30",
                "hora_inicio_intervencion": "08:00",
                "hora_finaliza_intervencion": "09:30",
                "hora_finaliza_limpieza_prepara_quirofano": "10:00",
                "observaciones": "Prueba integral de todos los campos",
            },
        )
        assert r.status_code == 201, r.text
        d = r.json()
        created_ids["intervenciones"].append(d["intervencion_id"])

        # Médico: se guarda el id y se devuelve el nombre
        assert d["personal_atencion_id"] == medico["id"]
        assert d["personal_atencion_nombre"] == medico["nombre"]
        # FKs de catálogos con sus nombres resueltos
        assert d["estado_cirugia_id"] == estado_id
        assert d["estado_cirugia_nombre"] == estado_nombre
        assert d["formato_procedimiento_id"] == formato_id
        assert d["formato_procedimiento_nombre"] == formato_nombre
        assert d["procedencia_procedimiento_id"] == proc_id
        assert d["procedencia_procedimiento_nombre"] == proc_nombre
        assert d["rango_especialista_id"] == rango_id
        assert d["rango_especialista_nombre"] == rango_nombre
        assert d["especialidad_id"] == esp_id
        assert d["especialidad_nombre"] == esp_nombre
        assert d["quirofano_numero_id"] == quirofano["quirofano_numero_id"]
        assert d["quirofano_numero_nombre"] == quirofano["nombre"]
        # Los 5 procedimientos: id + nombre del catálogo
        claves = [
            "procedimiento_principal",
            "procedimiento_2",
            "procedimiento_3",
            "procedimiento_4",
            "procedimiento_5",
        ]
        for clave, cid in zip(claves, cat_ids):
            assert d[f"{clave}_id"] == cid
            assert d[f"{clave}_catalogo_nombre"] == cat_nombres[cid]
        # Área, tiempos y observaciones
        assert d["area_cuerpo_intervenida"] == area_nombre
        assert d["id_area_cuerpo_intervenida"] == area_id
        assert d["area_cuerpo_intervenida_nombre"] == area_nombre
        assert d["hora_inicio_anestesia"] == "07:30:00"
        assert d["hora_inicio_intervencion"] == "08:00:00"
        assert d["hora_finaliza_intervencion"] == "09:30:00"
        assert d["hora_finaliza_limpieza_prepara_quirofano"] == "10:00:00"
        assert d["observaciones"] == "Prueba integral de todos los campos"

        # Relectura (GET) idéntica
        r = client.get(
            f"/quirofano/intervenciones/{d['intervencion_id']}", headers=auth_headers
        )
        assert r.status_code == 200
        g = r.json()
        assert g["personal_atencion_nombre"] == medico["nombre"]
        assert g["procedimiento_5_catalogo_nombre"] == cat_nombres[cat_ids[4]]
        assert g["estado_cirugia_nombre"] == estado_nombre

    def test_crear_intervencion_con_catalogo(self, client, auth_headers):
        """Llena los FKs al catálogo maestro y verifica que los nombres se resuelvan."""
        db = SessionLocal()
        try:
            cat = (
                db.query(CatalogoProcedimiento)
                .filter(CatalogoProcedimiento.activo == True)
                .order_by(CatalogoProcedimiento.id)
                .first()
            )
            cat2 = (
                db.query(CatalogoProcedimiento)
                .filter(CatalogoProcedimiento.id != cat.id)
                .order_by(CatalogoProcedimiento.id)
                .first()
            )
            area = db.query(AreaCuerpoIntervenida).order_by(AreaCuerpoIntervenida.id).first()
            assert cat is not None and cat2 is not None and area is not None
            cat_id, cat_nombre, cat2_id, area_nombre = cat.id, cat.nombre, cat2.id, area.nombre
        finally:
            db.close()

        paciente = self._crear_paciente(client, auth_headers)
        r = client.post(
            "/quirofano/intervenciones/",
            headers=auth_headers,
            json={
                "paciente_id": paciente["id"],
                "procedimiento_principal_id": cat_id,
                "procedimiento_2_id": cat2_id,
                "area_cuerpo_intervenida": area_nombre,
                "hora_inicio_intervencion": "09:00",
                "hora_finaliza_intervencion": "10:00",
            },
        )
        assert r.status_code == 201, r.text
        data = r.json()
        created_ids["intervenciones"].append(data["intervencion_id"])
        assert data["procedimiento_principal_id"] == cat_id
        assert data["procedimiento_2_id"] == cat2_id
        assert data["procedimiento_principal_catalogo_nombre"] == cat_nombre
        # sin texto enviado, el nombre se resuelve desde el catálogo
        assert data["procedimiento_principal"] == cat_nombre
        assert data["area_cuerpo_intervenida"] == area_nombre

        r = client.get(
            f"/quirofano/intervenciones/{data['intervencion_id']}", headers=auth_headers
        )
        assert r.status_code == 200
        assert r.json()["procedimiento_principal_catalogo_nombre"] == cat_nombre

    def test_catalogo_procedimiento_id_inexistente(self, client, auth_headers):
        paciente = self._crear_paciente(client, auth_headers)
        r = client.post(
            "/quirofano/intervenciones/",
            headers=auth_headers,
            json={
                "paciente_id": paciente["id"],
                "procedimiento_principal_id": 999999999,
            },
        )
        # FK inexistente: la DB lo rechaza (IntegrityError -> 409/500) pero nunca debe crear
        assert r.status_code != 201

    def test_area_cuerpo_id_inexistente(self, client, auth_headers):
        paciente = self._crear_paciente(client, auth_headers)
        r = client.post(
            "/quirofano/intervenciones/",
            headers=auth_headers,
            json={
                "paciente_id": paciente["id"],
                "id_area_cuerpo_intervenida": 999999999,
            },
        )
        assert r.status_code == 404

    def test_especialidad_id_inexistente(self, client, auth_headers):
        paciente = self._crear_paciente(client, auth_headers)
        r = client.post(
            "/quirofano/intervenciones/",
            headers=auth_headers,
            json={
                "paciente_id": paciente["id"],
                "especialidad_id": 999999999,
            },
        )
        assert r.status_code == 404

    def _registrar_tipos_creados(self, nombres: list):
        db = SessionLocal()
        try:
            for nombre in nombres:
                for t in db.query(ProcedimientoQuirofanoModel).filter(
                    ProcedimientoQuirofanoModel.nombre == nombre
                ).all():
                    created_ids["procedimientos_quirofano"].append(t.procedimiento_quirofano_id)
        finally:
            db.close()

    def test_importar_csv_procedimientos(self, client, auth_headers):
        s = _sufijo()
        csv_content = (
            "referencia_especialidad,procedimiento\n"
            f"Cirugía,Procedimiento Test {s}\n"
            f"Cirugía,Otro Test {s}\n"
        )
        r = client.post(
            "/quirofano/procedimientos-quirofano/importar-csv",
            headers=auth_headers,
            files={"file": ("tipos.csv", csv_content.encode("utf-8"), "text/csv")},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["creados"] == 2
        assert data["omitidos"] == 0
        assert data["errores"] == []

        # Idempotente: segunda importación omite los ya existentes
        r = client.post(
            "/quirofano/procedimientos-quirofano/importar-csv",
            headers=auth_headers,
            files={"file": ("tipos.csv", csv_content.encode("utf-8"), "text/csv")},
        )
        assert r.status_code == 200
        assert r.json()["omitidos"] == 2

        # El catálogo guarda SOLO el nombre del procedimiento
        r = client.get(
            "/quirofano/procedimientos-quirofano/",
            headers=auth_headers,
            params={"q": f"Procedimiento Test {s}"},
        )
        assert r.status_code == 200
        nombres = [t["nombre"] for t in r.json()]
        assert f"Procedimiento Test {s}" in nombres

        self._registrar_tipos_creados(
            [f"Procedimiento Test {s}", f"Otro Test {s}"]
        )

    def test_importar_csv_especialidad_sin_acentos_null_mixta(self, client, auth_headers):
        s = _sufijo()
        csv_content = (
            "especialidad,procedimientos\n"
            f"cirugia,Acento Insensible {s}\n"
            f"NULL,NULL Sin Acento {s}\n"
        )
        r = client.post(
            "/quirofano/procedimientos-quirofano/importar-csv",
            headers=auth_headers,
            files={"file": ("tipos.csv", csv_content.encode("utf-8"), "text/csv")},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["creados"] == 2
        assert data["errores"] == []

        r = client.get(
            "/quirofano/procedimientos-quirofano/", headers=auth_headers, params={"q": "Acento"}
        )
        assert r.status_code == 200
        registros = {t["nombre"]: t for t in r.json()}
        assert "Acento Insensible " + s in registros
        assert registros["Acento Insensible " + s]["especialidad_nombre"] == "Cirugía"
        assert registros["NULL Sin Acento " + s]["especialidad_id"] is None

        self._registrar_tipos_creados([f"Acento Insensible {s}", f"NULL Sin Acento {s}"])

    def test_importar_csv_faltan_columnas(self, client, auth_headers):
        csv_content = "procedimiento\nApendicectomía\n"
        r = client.post(
            "/quirofano/procedimientos-quirofano/importar-csv",
            headers=auth_headers,
            files={"file": ("tipos.csv", csv_content.encode("utf-8"), "text/csv")},
        )
        assert r.status_code == 400

    def test_importar_csv_homonimos_distintas_especialidades(self, client, auth_headers):
        s = _sufijo()
        proc = f"Circuncisión Test {s}"
        csv_content = (
            "referencia_especialidad,procedimiento\n"
            f"Cirugía,{proc}\n"
            f"Traumatología,{proc}\n"
        )
        r = client.post(
            "/quirofano/procedimientos-quirofano/importar-csv",
            headers=auth_headers,
            files={"file": ("tipos.csv", csv_content.encode("utf-8"), "text/csv")},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["creados"] == 2
        assert data["omitidos"] == 0
        assert data["errores"] == []

        # Ambos homónimos existen, cada uno en su especialidad
        r = client.get("/quirofano/procedimientos-quirofano/", headers=auth_headers, params={"q": proc})
        assert r.status_code == 200
        registros = [t for t in r.json() if t["nombre"] == proc]
        assert len(registros) == 2
        assert len({t["especialidad_id"] for t in registros}) == 2

        self._registrar_tipos_creados([proc, proc])

    def test_importar_csv_especialidad_inexistente_es_opcional(self, client, auth_headers):
        s = _sufijo()
        csv_content = (
            "referencia_especialidad,procedimiento\n"
            f"Especialidad Fantasma {s},Procedimiento Fantasma {s}\n"
        )
        r = client.post(
            "/quirofano/procedimientos-quirofano/importar-csv",
            headers=auth_headers,
            files={"file": ("tipos.csv", csv_content.encode("utf-8"), "text/csv")},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["creados"] == 1
        assert data["errores"] == []

        r = client.get(
            "/quirofano/procedimientos-quirofano/", headers=auth_headers, params={"q": f"Procedimiento Fantasma {s}"}
        )
        assert r.status_code == 200
        registros = [t for t in r.json() if t["nombre"] == f"Procedimiento Fantasma {s}"]
        assert len(registros) == 1
        assert registros[0]["especialidad_id"] is None

        self._registrar_tipos_creados([f"Procedimiento Fantasma {s}"])

    def test_crear_procedimiento_quirofano_codigo_automatico(self, client, auth_headers):
        db = SessionLocal()
        try:
            esp = db.query(EspecialidadModel).first()
            esp_id = esp.id
        finally:
            db.close()
        assert esp_id is not None

        s = _sufijo()
        r = client.post(
            "/quirofano/procedimientos-quirofano/",
            headers=auth_headers,
            json={"nombre": f"Procedimiento Autocódigo {s}", "especialidad_id": esp_id},
        )
        assert r.status_code == 201
        data = r.json()
        assert data["codigo"].startswith("TP")
        assert data["especialidad_id"] == esp_id
        created_ids["procedimientos_quirofano"].append(data["procedimiento_quirofano_id"])

    def test_crear_procedimiento_quirofano_especialidad_inexistente(self, client, auth_headers):
        r = client.post(
            "/quirofano/procedimientos-quirofano/",
            headers=auth_headers,
            json={"nombre": f"Procedimiento Fantasma {_sufijo()}", "especialidad_id": 999999999},
        )
        assert r.status_code == 404

    def test_crear_procedimiento_quirofano_mixta(self, client, auth_headers):
        s = _sufijo()
        nombre = f"Procedimiento Mixto {s}"
        r = client.post(
            "/quirofano/procedimientos-quirofano/",
            headers=auth_headers,
            json={"nombre": nombre, "especialidad_id": None},
        )
        assert r.status_code == 201
        data = r.json()
        created_ids["procedimientos_quirofano"].append(data["procedimiento_quirofano_id"])
        assert data["especialidad_id"] is None
        assert data["especialidad_nombre"] is None

        # Duplicado en 'Todas (mixta)' -> 409
        r = client.post(
            "/quirofano/procedimientos-quirofano/",
            headers=auth_headers,
            json={"nombre": nombre, "especialidad_id": None},
        )
        assert r.status_code == 409

        # Homónimo en una especialidad concreta SÍ se permite
        db = SessionLocal()
        try:
            esp_id = db.query(EspecialidadModel).first().id
        finally:
            db.close()
        r = client.post(
            "/quirofano/procedimientos-quirofano/",
            headers=auth_headers,
            json={"nombre": nombre, "especialidad_id": esp_id},
        )
        assert r.status_code == 201
        created_ids["procedimientos_quirofano"].append(r.json()["procedimiento_quirofano_id"])

    def test_actualizar_procedimiento_quirofano_a_mixta(self, client, auth_headers):
        db = SessionLocal()
        try:
            esp_id = db.query(EspecialidadModel).first().id
        finally:
            db.close()

        s = _sufijo()
        nombre = f"Procedimiento Concreto {s}"
        r = client.post(
            "/quirofano/procedimientos-quirofano/",
            headers=auth_headers,
            json={"nombre": nombre, "especialidad_id": esp_id},
        )
        assert r.status_code == 201
        proc_id = r.json()["procedimiento_quirofano_id"]
        created_ids["procedimientos_quirofano"].append(proc_id)

        # PUT con especialidad_id NULL explícito -> mixta
        r = client.put(
            f"/quirofano/procedimientos-quirofano/{proc_id}",
            headers=auth_headers,
            json={"especialidad_id": None},
        )
        assert r.status_code == 200
        assert r.json()["especialidad_id"] is None
        assert r.json()["especialidad_nombre"] is None

    def test_importar_csv_sin_referencia_crea_mixta(self, client, auth_headers):
        s = _sufijo()
        nombre = f"Sin Especialidad Test {s}"
        csv_content = (
            "referencia_especialidad,procedimiento\n"
            f",{nombre}\n"
        )
        r = client.post(
            "/quirofano/procedimientos-quirofano/importar-csv",
            headers=auth_headers,
            files={"file": ("tipos.csv", csv_content.encode("utf-8"), "text/csv")},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["creados"] == 1
        assert data["errores"] == []

        r = client.get(
            "/quirofano/procedimientos-quirofano/", headers=auth_headers, params={"q": nombre}
        )
        assert r.status_code == 200
        registros = [t for t in r.json() if t["nombre"] == nombre]
        assert len(registros) == 1
        assert registros[0]["especialidad_id"] is None
        assert registros[0]["especialidad_nombre"] is None

        self._registrar_tipos_creados([nombre])

    def test_importar_csv_encabezados_alias_especialidad_procedimientos(self, client, auth_headers):
        s = _sufijo()
        nombre = f"Alias Headers Test {s}"
        csv_content = (
            "especialidad,procedimientos\n"
            f",{nombre}\n"
        )
        r = client.post(
            "/quirofano/procedimientos-quirofano/importar-csv",
            headers=auth_headers,
            files={"file": ("tipos.csv", csv_content.encode("utf-8"), "text/csv")},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["creados"] == 1
        assert data["errores"] == []

        r = client.get(
            "/quirofano/procedimientos-quirofano/", headers=auth_headers, params={"q": nombre}
        )
        assert r.status_code == 200
        registros = [t for t in r.json() if t["nombre"] == nombre]
        assert len(registros) == 1
        assert registros[0]["especialidad_id"] is None
        assert registros[0]["especialidad_nombre"] is None

        self._registrar_tipos_creados([nombre])

    def test_importar_csv_cp1252(self, client, auth_headers):
        s = _sufijo()
        nombre = f"Cp1252 Test {s}"
        csv_content = (
            "especialidad,procedimientos\n"
            f",{nombre} — con guión\n"
        )
        r = client.post(
            "/quirofano/procedimientos-quirofano/importar-csv",
            headers=auth_headers,
            files={"file": ("tipos.csv", csv_content.encode("cp1252"), "text/csv")},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["creados"] == 1
        assert data["errores"] == []

        r = client.get(
            "/quirofano/procedimientos-quirofano/", headers=auth_headers, params={"q": nombre}
        )
        assert r.status_code == 200
        registros = [t for t in r.json() if t["nombre"] == f"{nombre} — con guión"]
        assert len(registros) == 1
        assert registros[0]["especialidad_id"] is None

        self._registrar_tipos_creados([f"{nombre} — con guión"])

    def test_importar_csv_separado_por_tabulador(self, client, auth_headers):
        s = _sufijo()
        nombre = f"TSV Test {s}"
        csv_content = (
            "especialidad\tprocedimientos\n"
            f"\t{nombre}\n"
        )
        r = client.post(
            "/quirofano/procedimientos-quirofano/importar-csv",
            headers=auth_headers,
            files={"file": ("tipos.csv", csv_content.encode("utf-8"), "text/csv")},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["creados"] == 1
        assert data["errores"] == []

        r = client.get(
            "/quirofano/procedimientos-quirofano/", headers=auth_headers, params={"q": nombre}
        )
        assert r.status_code == 200
        registros = [t for t in r.json() if t["nombre"] == nombre]
        assert len(registros) == 1
        assert registros[0]["especialidad_id"] is None

        self._registrar_tipos_creados([nombre])

    def test_importar_csv_encabezados_entre_comillas_y_bom(self, client, auth_headers):
        s = _sufijo()
        nombre = f"Quoted Headers Test {s}"
        csv_content = (
            '\ufeff"especialidad"\t"procedimientos"\n'
            f'null\t"{nombre}"\n'
        )
        r = client.post(
            "/quirofano/procedimientos-quirofano/importar-csv",
            headers=auth_headers,
            files={"file": ("tipos.csv", csv_content.encode("utf-8"), "text/csv")},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["creados"] == 1
        assert data["errores"] == []
        assert data["omitidos"] == 0

        r = client.get(
            "/quirofano/procedimientos-quirofano/", headers=auth_headers, params={"q": nombre}
        )
        assert r.status_code == 200
        registros = [t for t in r.json() if t["nombre"] == nombre]
        assert len(registros) == 1
        assert registros[0]["especialidad_id"] is None

        self._registrar_tipos_creados([nombre])

    def test_importar_csv_archivo_invalido(self, client, auth_headers):
        r = client.post(
            "/quirofano/procedimientos-quirofano/importar-csv",
            headers=auth_headers,
            files={"file": ("tipos.txt", b"especialidad,procedimiento\nX,Y", "text/plain")},
        )
        assert r.status_code == 400

    def test_truncar_procedimientos_quirofano(self, client, auth_headers):
        # Snapshot para restaurar tras la truncada
        db = SessionLocal()
        try:
            tips = db.query(ProcedimientoQuirofanoModel).all()
            snapshot_tips = [
                (t.procedimiento_quirofano_id, t.codigo, t.nombre, t.especialidad_id, t.activo)
                for t in tips
            ]
        finally:
            db.close()

        r = client.delete("/quirofano/procedimientos-quirofano/truncar", headers=auth_headers)
        assert r.status_code == 200
        assert r.json() == {"truncado": True}

        r = client.get(
            "/quirofano/procedimientos-quirofano/",
            headers=auth_headers,
            params={"activos": False, "limit": 10000},
        )
        assert r.status_code == 200
        assert r.json() == []

        # Restaurar el catálogo (mismos ids) y secuencias
        db = SessionLocal()
        try:
            for tid, codigo, nombre, esp_id, activo in snapshot_tips:
                db.add(ProcedimientoQuirofanoModel(
                    procedimiento_quirofano_id=tid, codigo=codigo, nombre=nombre,
                    especialidad_id=esp_id, activo=activo,
                ))
            # autoflush=False: forzar el INSERT antes de calcular el MAX
            db.flush()
            db.execute(text(
                "SELECT setval(pg_get_serial_sequence('procedimiento_quirofano','procedimiento_quirofano_id'), "
                "(SELECT COALESCE(MAX(procedimiento_quirofano_id),1) FROM procedimiento_quirofano))"
            ))
            db.commit()
        finally:
            db.close()

        r = client.get(
            "/quirofano/procedimientos-quirofano/",
            headers=auth_headers,
            params={"activos": False},
        )
        assert r.status_code == 200
        assert len(r.json()) == len(snapshot_tips)

    def test_truncar_procedimientos_quirofano_requiere_admin(self, client):
        r = client.delete("/quirofano/procedimientos-quirofano/truncar")
        assert r.status_code in (401, 422, 403)
        r = client.post(
            "/quirofano/procedimientos-quirofano/importar-csv",
            files={"file": ("tipos.csv", b"especialidad,procedimiento\nX,Y", "text/csv")},
        )
        assert r.status_code in (401, 422, 403)