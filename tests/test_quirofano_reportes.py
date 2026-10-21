"""Pruebas del reporte/resumen de quirófanos y de la exportación a Excel."""

import io
import time as _time
from datetime import date

import openpyxl
import pytest

from core.database import SessionLocal
from modules.pacientes.models import PacienteModel
from modules.medicos.models import MedicoModel
from modules.especialidades.models import EspecialidadModel
from modules.quirofano.models import (
    IntervencionQuirurgicaModel,
    QuirofanoNumeroModel,
    EstadoCirugiaModel,
    QuirofanoConfigPeriodoModel,
)

# Período aislado (año futuro) para que otros tests no contaminen las aserciones.
DESDE = "2099-06-01"
HASTA = "2099-06-30"


created_ids = {
    "intervenciones": [],
    "pacientes": [],
    "medicos": [],
    "quirofanos_numero": [],
    "config": [],
}


def _sufijo():
    return str(int(_time.time() * 1000000))[-6:]


def cleanup():
    db = SessionLocal()
    try:
        for iid in created_ids["intervenciones"]:
            db.query(IntervencionQuirurgicaModel).filter(
                IntervencionQuirurgicaModel.intervencion_id == iid
            ).delete()
        for qid in created_ids["quirofanos_numero"]:
            db.query(QuirofanoConfigPeriodoModel).filter(
                QuirofanoConfigPeriodoModel.quirofano_numero_id == qid
            ).delete()
            db.query(QuirofanoNumeroModel).filter(
                QuirofanoNumeroModel.quirofano_numero_id == qid
            ).delete()
        for pid in created_ids["pacientes"]:
            db.query(PacienteModel).filter(PacienteModel.id == pid).delete()
        for mid in created_ids["medicos"]:
            db.query(MedicoModel).filter(MedicoModel.id == mid).delete()
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


class TestQuirofanoReportes:
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        yield
        cleanup()

    # -------- helpers --------
    def _crear_paciente(self, client, auth_headers):
        s = _sufijo()
        r = client.post(
            "/pacientes/?auto_expediente=true",
            headers=auth_headers,
            json={
                "nombre": {"primer_nombre": f"Rep{s}", "primer_apellido": f"Quiro{s}"},
                "sexo": "M",
                "fecha_nacimiento": "1980-01-01",
            },
        )
        assert r.status_code == 201, r.text
        created_ids["pacientes"].append(r.json()["id"])
        return r.json()

    def _crear_medico(self, client, auth_headers):
        s = _sufijo()
        r = client.post(
            "/personal-atencion/", headers=auth_headers,
            json={"nombre": f"Dr. Reporte {s}", "colegiado": str(s)}
        )
        assert r.status_code in (200, 201)
        created_ids["medicos"].append(r.json()["id"])
        return r.json()

    def _crear_quirofano(self, client, auth_headers):
        s = _sufijo()
        r = client.post(
            "/quirofano/quirofanos-numero/",
            headers=auth_headers,
            json={"numero": int(s), "nombre": f"Quirófano Reporte {int(s)}"},
        )
        assert r.status_code == 201, r.text
        data = r.json()
        created_ids["quirofanos_numero"].append(data["quirofano_numero_id"])
        return data

    def _estado_id(self, codigo: str) -> int:
        db = SessionLocal()
        try:
            return (
                db.query(EstadoCirugiaModel)
                .filter(EstadoCirugiaModel.codigo == codigo)
                .first()
                .estado_cirugia_id
            )
        finally:
            db.close()

    def _crear_intervencion(self, client, auth_headers, **kwargs):
        payload = {"paciente_id": kwargs.pop("paciente_id"), "fecha": DESDE}
        payload.update(kwargs)
        r = client.post("/quirofano/intervenciones/", headers=auth_headers, json=payload)
        assert r.status_code == 201, r.text
        created_ids["intervenciones"].append(r.json()["intervencion_id"])
        return r.json()

    # -------- reporte --------
    def test_reporte_resumen_kpis(self, client, auth_headers):
        paciente = self._crear_paciente(client, auth_headers)
        medico = self._crear_medico(client, auth_headers)
        qf = self._crear_quirofano(client, auth_headers)
        qid = qf["quirofano_numero_id"]
        fin, can = self._estado_id("FIN"), self._estado_id("CAN")
        esp_id = SessionLocal().query(EspecialidadModel).first().id

        # 2 finalizadas (una 08:00–10:00 y otra 11:00–12:00) + 1 cancelada
        self._crear_intervencion(
            client, auth_headers, paciente_id=paciente["id"], quirofano_numero_id=qid,
            estado_cirugia_id=fin, especialidad_id=esp_id, personal_atencion_id=medico["id"],
            procedimiento_principal="Apendicectomía",
            hora_inicio_anestesia="07:45", hora_inicio_intervencion="08:00",
            hora_finaliza_intervencion="10:00",
            hora_finaliza_limpieza_prepara_quirofano="10:30",
        )
        self._crear_intervencion(
            client, auth_headers, paciente_id=paciente["id"], quirofano_numero_id=qid,
            estado_cirugia_id=fin, especialidad_id=esp_id, personal_atencion_id=medico["id"],
            procedimiento_principal="Herniorrafia",
            hora_inicio_anestesia="10:45", hora_inicio_intervencion="11:00",
            hora_finaliza_intervencion="12:00",
            hora_finaliza_limpieza_prepara_quirofano="12:15",
        )
        self._crear_intervencion(
            client, auth_headers, paciente_id=paciente["id"], quirofano_numero_id=qid,
            estado_cirugia_id=can, especialidad_id=esp_id, personal_atencion_id=medico["id"],
            procedimiento_principal="Colecistectomía",
        )

        r = client.get(
            "/quirofano/reportes/resumen",
            headers=auth_headers,
            params={"fecha_desde": DESDE, "fecha_hasta": HASTA, "quirofano_numero_id": qid},
        )
        assert r.status_code == 200, r.text
        data = r.json()

        kg = data["kpi_global"]
        assert kg["total_intervenciones"] == 3
        assert kg["finalizadas"] == 2
        assert kg["canceladas"] == 1
        assert kg["procedimientos_total"] == 3
        # duración intervención: (120 + 60) min -> promedio 90 min = 5400 s
        assert kg["tiempo_promedio_intervencion_seg"] == 5400
        # uso quirófano: 150 y 75 min -> promedio 112.5 -> 6750 s
        assert kg["tiempo_promedio_uso_quirofano_seg"] == 6750
        assert kg["tasa_cancelacion"] == pytest.approx(1 / 3, abs=1e-4)
        # disponibilidad: apertura 07:45 (min anestesia), cierre 12:15 (max limpieza)
        # = 4.5 h * 2 días distintos (06-01) -> 1 día -> 4.5h = 16200 s
        assert kg["dias_abiertos"] == 1
        assert kg["porcentaje_uso"] == pytest.approx(13500 / 16200, abs=1e-4)

        assert len(data["por_quirofano"]) == 1
        detalle = data["por_quirofano"][0]
        assert detalle["kpi"]["quirofano_numero_id"] == qid
        assert len(detalle["intervenciones"]) == 3
        procs = {p["procedimiento"]: p["cantidad"] for p in data["procedimientos"]}
        assert procs["Apendicectomía"] == 1
        assert procs["Herniorrafia"] == 1

    def test_reporte_validaciones(self, client, auth_headers):
        r = client.get(
            "/quirofano/reportes/resumen",
            headers=auth_headers,
            params={"fecha_desde": "2099-06-30", "fecha_hasta": "2099-06-01"},
        )
        assert r.status_code == 422

        r = client.get(
            "/quirofano/reportes/resumen",
            headers=auth_headers,
            params={"fecha_desde": "2090-01-01", "fecha_hasta": "2099-01-01"},
        )
        assert r.status_code == 422

    def test_reporte_requiere_auth(self, client):
        r = client.get(
            "/quirofano/reportes/resumen",
            params={"fecha_desde": DESDE, "fecha_hasta": HASTA},
        )
        assert r.status_code in (401, 403)

    # -------- excel --------
    def test_reporte_excel(self, client, auth_headers):
        paciente = self._crear_paciente(client, auth_headers)
        qf = self._crear_quirofano(client, auth_headers)
        qid = qf["quirofano_numero_id"]
        fin = self._estado_id("FIN")
        self._crear_intervencion(
            client, auth_headers, paciente_id=paciente["id"], quirofano_numero_id=qid,
            estado_cirugia_id=fin, procedimiento_principal="Apendicectomía",
            hora_inicio_intervencion="08:00", hora_finaliza_intervencion="09:00",
            hora_finaliza_limpieza_prepara_quirofano="09:20",
        )

        r = client.get(
            "/quirofano/reportes/excel",
            headers=auth_headers,
            params={"fecha_desde": DESDE, "fecha_hasta": HASTA, "quirofano_numero_id": qid},
        )
        assert r.status_code == 200, r.text
        assert "spreadsheetml" in r.headers["content-type"]
        assert "attachment" in r.headers["content-disposition"]
        assert r.content[:2] == b"PK"

        wb = openpyxl.load_workbook(io.BytesIO(r.content))
        assert f"Q{qf['numero']}" in wb.sheetnames
        assert wb.sheetnames[-1] == "Resumen"
        hoja = wb[f"Q{qf['numero']}"]
        assert hoja["B6"].value == f"QUIRÓFANO #{qf['numero']}"
        assert hoja["A14"].value == 1
        assert hoja["I14"].value == "Apendicectomía"

    # -------- configuración de jornada --------
    def test_config_periodo(self, client, auth_headers):
        qf = self._crear_quirofano(client, auth_headers)
        qid = qf["quirofano_numero_id"]

        r = client.get("/quirofano/config-periodo", headers=auth_headers)
        assert r.status_code == 200
        assert any(c["quirofano_numero_id"] == qid for c in r.json())

        r = client.put(
            f"/quirofano/config-periodo/{qid}",
            headers=auth_headers,
            json={"hora_apertura": "06:30", "hora_cierre": "15:30", "dias_habiles": 20},
        )
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["hora_apertura"] == "06:30:00"
        assert data["hora_cierre"] == "15:30:00"
        assert data["dias_habiles"] == 20

        r = client.get("/quirofano/config-periodo", headers=auth_headers)
        config = [c for c in r.json() if c["quirofano_numero_id"] == qid][0]
        assert config["hora_apertura"] == "06:30:00"
        assert config["dias_habiles"] == 20

    def test_config_periodo_cierre_invalido(self, client, auth_headers):
        qf = self._crear_quirofano(client, auth_headers)
        qid = qf["quirofano_numero_id"]
        r = client.put(
            f"/quirofano/config-periodo/{qid}",
            headers=auth_headers,
            json={"hora_apertura": "16:00", "hora_cierre": "08:00"},
        )
        assert r.status_code == 422
