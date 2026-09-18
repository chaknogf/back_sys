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
            "/medicos/",
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
                "medico_id": medico["id"],
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
        assert data["medico_id"] == medico["id"]
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