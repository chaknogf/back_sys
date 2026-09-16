import pytest
import time as _time
from datetime import date

from core.database import SessionLocal
from modules.pacientes.models import PacienteModel
from modules.medicos.models import MedicoModel
from modules.quirofano.models import (
    IntervencionQuirurgicaModel,
    QuirofanoNumeroModel,
    TipoProcedimientoModel,
    CategoriaProcedimientoModel,
)
from sqlalchemy import text


created_ids = {
    "medicos": [],
    "pacientes": [],
    "intervenciones": [],
    "quirofanos_numero": [],
    "tipos": [],
    "categorias": [],
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
        for tid in created_ids["tipos"]:
            db.query(TipoProcedimientoModel).filter(
                TipoProcedimientoModel.tipo_procedimiento_id == tid
            ).delete()
        for cid in created_ids["categorias"]:
            db.query(CategoriaProcedimientoModel).filter(
                CategoriaProcedimientoModel.categoria_procedimiento_id == cid
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
                t = db.query(TipoProcedimientoModel).filter(
                    TipoProcedimientoModel.nombre == nombre
                ).first()
                if t:
                    created_ids["tipos"].append(t.tipo_procedimiento_id)
        finally:
            db.close()

    def test_importar_csv_tipos(self, client, auth_headers):
        s = _sufijo()
        db = SessionLocal()
        try:
            cats_existentes = {c.nombre for c in db.query(CategoriaProcedimientoModel).all()}
        finally:
            db.close()

        csv_content = (
            "especialidad,procedimiento\n"
            f"Cirugía General,Procedimiento Test {s}\n"
            f"Cirugía General,Otro Test {s}\n"
        )
        r = client.post(
            "/quirofano/tipos/importar-csv",
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
            "/quirofano/tipos/importar-csv",
            headers=auth_headers,
            files={"file": ("tipos.csv", csv_content.encode("utf-8"), "text/csv")},
        )
        assert r.status_code == 200
        assert r.json()["omitidos"] == 2

        # El catálogo devuelve los importados con nombre "Especialidad - Procedimiento"
        r = client.get(
            "/quirofano/tipos/",
            headers=auth_headers,
            params={"q": f"Procedimiento Test {s}"},
        )
        assert r.status_code == 200
        nombres = [t["nombre"] for t in r.json()]
        assert f"Cirugía General - Procedimiento Test {s}" in nombres

        self._registrar_tipos_creados(
            [f"Cirugía General - Procedimiento Test {s}", f"Cirugía General - Otro Test {s}"]
        )

        db = SessionLocal()
        try:
            cat = db.query(CategoriaProcedimientoModel).filter(
                CategoriaProcedimientoModel.nombre == "Cirugía General"
            ).first()
            if cat and cat.nombre not in cats_existentes:
                created_ids["categorias"].append(cat.categoria_procedimiento_id)
        finally:
            db.close()

    def test_importar_csv_faltan_columnas(self, client, auth_headers):
        csv_content = "especialidad\nCirugía General\n"
        r = client.post(
            "/quirofano/tipos/importar-csv",
            headers=auth_headers,
            files={"file": ("tipos.csv", csv_content.encode("utf-8"), "text/csv")},
        )
        assert r.status_code == 400

    def test_importar_csv_archivo_invalido(self, client, auth_headers):
        r = client.post(
            "/quirofano/tipos/importar-csv",
            headers=auth_headers,
            files={"file": ("tipos.txt", b"especialidad,procedimiento\nX,Y", "text/plain")},
        )
        assert r.status_code == 400

    def test_truncar_tipos(self, client, auth_headers):
        # Snapshot para restaurar tras la truncada
        db = SessionLocal()
        try:
            cats = db.query(CategoriaProcedimientoModel).all()
            tips = db.query(TipoProcedimientoModel).all()
            snapshot_cats = [(c.categoria_procedimiento_id, c.codigo, c.nombre, c.activo) for c in cats]
            snapshot_tips = [
                (t.tipo_procedimiento_id, t.codigo, t.nombre, t.categoria_procedimiento_id, t.activo)
                for t in tips
            ]
        finally:
            db.close()

        r = client.delete("/quirofano/tipos/truncar", headers=auth_headers)
        assert r.status_code == 200
        assert r.json() == {"truncado": True}

        r = client.get(
            "/quirofano/tipos/",
            headers=auth_headers,
            params={"activos": False, "limit": 10000},
        )
        assert r.status_code == 200
        assert r.json() == []

        # Restaurar el catálogo (mismos ids) y secuencias
        db = SessionLocal()
        try:
            for cid, codigo, nombre, activo in snapshot_cats:
                db.add(CategoriaProcedimientoModel(
                    categoria_procedimiento_id=cid, codigo=codigo, nombre=nombre, activo=activo
                ))
            db.flush()
            for tid, codigo, nombre, cat_id, activo in snapshot_tips:
                db.add(TipoProcedimientoModel(
                    tipo_procedimiento_id=tid, codigo=codigo, nombre=nombre,
                    categoria_procedimiento_id=cat_id, activo=activo,
                ))
            db.execute(text(
                "SELECT setval(pg_get_serial_sequence('tipo_procedimiento','tipo_procedimiento_id'), "
                "(SELECT COALESCE(MAX(tipo_procedimiento_id),1) FROM tipo_procedimiento))"
            ))
            db.execute(text(
                "SELECT setval(pg_get_serial_sequence('categoria_procedimiento','categoria_procedimiento_id'), "
                "(SELECT COALESCE(MAX(categoria_procedimiento_id),1) FROM categoria_procedimiento))"
            ))
            db.commit()
        finally:
            db.close()

        r = client.get(
            "/quirofano/tipos/",
            headers=auth_headers,
            params={"activos": False},
        )
        assert r.status_code == 200
        assert len(r.json()) == len(snapshot_tips)

    def test_truncar_tipos_requiere_admin(self, client):
        r = client.delete("/quirofano/tipos/truncar")
        assert r.status_code in (401, 422, 403)
        r = client.post(
            "/quirofano/tipos/importar-csv",
            files={"file": ("tipos.csv", b"especialidad,procedimiento\nX,Y", "text/csv")},
        )
        assert r.status_code in (401, 422, 403)