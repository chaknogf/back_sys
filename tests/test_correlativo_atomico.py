"""Atomicidad de correlativos (Tarea 4).

- El servicio solo hace flush: un rollback del llamador deshace el incremento.
- Los endpoints standalone son el límite transaccional: cada llamada confirma
  y entrega un correlativo distinto.
"""

from datetime import datetime

from core.config import APP_TIMEZONE
from core.database import SessionLocal
from modules.expediente.models import CorrelativoControl
from modules.expediente.service import generar_expediente


def _anio() -> int:
    return int(datetime.now(APP_TIMEZONE).strftime("%y"))


def _valor_contador(tipo: str) -> int:
    s = SessionLocal()
    try:
        control = (
            s.query(CorrelativoControl)
            .filter(CorrelativoControl.tipo == tipo, CorrelativoControl.anio == _anio())
            .first()
        )
        return control.ultimo_correlativo if control else 0
    finally:
        s.close()


def test_servicio_no_confirma_y_rollback_revierte():
    antes = _valor_contador("expediente")
    s = SessionLocal()
    try:
        generar_expediente(s)
        s.rollback()
    finally:
        s.close()
    assert _valor_contador("expediente") == antes


def test_endpoint_confirma_y_entrega_correlativos_distintos(client, auth_headers):
    antes = _valor_contador("emergencia")
    r1 = client.post("/correlativos/emergencia", headers=auth_headers)
    r2 = client.post("/correlativos/emergencia", headers=auth_headers)
    assert r1.status_code == 201 and r2.status_code == 201
    assert r1.json()["hoja_emergencia"] != r2.json()["hoja_emergencia"]
    assert _valor_contador("emergencia") == antes + 2
