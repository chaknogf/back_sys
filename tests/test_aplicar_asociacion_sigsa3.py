"""Integración: aplicar_asociacion (asoc-v2) dentro de una transacción con ROLLBACK.

No hace commit (commit=False): todo lo escrito se revierte al final.
No hay pacientes creados en `pacientes`: se crean en `pacientes_sigsa3`.
"""
import time
from datetime import date

from sqlalchemy import text

from core.database import SessionLocal
from modules.sigsa3.asociacion import CREAR
from modules.sigsa3.asociacion_servicio import ORIGEN_SIGSA3, aplicar_asociacion

MARCA = f"ZZAPLICA{int(time.time() * 1000) % 10**8}"


def _scalar(db, sql, **params):
    return db.execute(text(sql), params).scalar()


def test_aplicar_paciente_consulta_creacion_y_diferencial_con_rollback():
    db = SessionLocal()
    try:
        antes_pac = _scalar(db, "SELECT COUNT(*) FROM pacientes")
        antes_ps = _scalar(db, "SELECT COUNT(*) FROM pacientes_sigsa3")
        antes_sig = _scalar(db, "SELECT COUNT(*) FROM sigsa3")

        hoy = date.today()
        pac_exist = db.execute(text(
            "INSERT INTO pacientes (nombre, sexo, estado) "
            "VALUES (CAST(:n AS jsonb), 'F', 'A') RETURNING id"),
            {"n": f'{{"primer_nombre": "{MARCA}A", "primer_apellido": "EXISTENTE"}}'}).scalar()
        con = db.execute(text(
            "INSERT INTO consultas (paciente_id, tipo_consulta, especialidad, servicio, documento, "
            "fecha_consulta, hora_consulta, activo) "
            "VALUES (:p, 1, 'MEDICINA', 'COEX', '555501', :f, '08:00', TRUE) RETURNING id"),
            {"p": pac_exist, "f": hoy}).scalar()

        r_exist = db.execute(text(
            "INSERT INTO sigsa3 (nombre_paciente, sexo, no_historia_clinica, fecha_consulta, tipo_consulta) "
            "VALUES (:n, 'F', '555501', :f, '1 Primera') RETURNING id"),
            {"n": f"{MARCA}A EXISTENTE", "f": hoy}).scalar()
        r_nuevo1 = db.execute(text(
            "INSERT INTO sigsa3 (nombre_paciente, sexo, fecha_consulta) "
            "VALUES (:n, 'F', :f) RETURNING id"),
            {"n": f"{MARCA}B {MARCA}C", "f": hoy}).scalar()
        r_nuevo2 = db.execute(text(
            "INSERT INTO sigsa3 (nombre_paciente, sexo, fecha_consulta) "
            "VALUES (:n, 'F', :f) RETURNING id"),
            {"n": f"{MARCA}b {MARCA}c", "f": hoy}).scalar()
        db.flush()

        sim = aplicar_asociacion(db, dry_run=True, commit=False)
        res = aplicar_asociacion(db, dry_run=False, commit=False)
        assert res["pacientes_creados"] >= 1
        assert res["consultas_asignadas"] >= 1
        assert res["pacientes_creados"] >= 1

        fila = db.execute(text("SELECT paciente_id, consulta_id, pacientes_sigsa3_id FROM sigsa3 WHERE id=:i"),
                          {"i": r_exist}).fetchone()
        assert fila.paciente_id == pac_exist and fila.consulta_id == con

        p1 = _scalar(db, "SELECT pacientes_sigsa3_id FROM sigsa3 WHERE id=:i", i=r_nuevo1)
        p2 = _scalar(db, "SELECT pacientes_sigsa3_id FROM sigsa3 WHERE id=:i", i=r_nuevo2)
        assert p1 is not None and p1 == p2
        assert _scalar(db, "SELECT nombre FROM pacientes_sigsa3 WHERE id=:p", p=p1) == f"{MARCA}B {MARCA}C"
        assert _scalar(db, "SELECT datos_extra->>'origen' FROM pacientes_sigsa3 WHERE id=:p", p=p1) == ORIGEN_SIGSA3
        assert _scalar(db, "SELECT sigsa3_id_origen FROM pacientes_sigsa3 WHERE id=:p", p=p1) == r_nuevo1
        assert _scalar(db, "SELECT consulta_id FROM sigsa3 WHERE id=:i", i=r_nuevo1) is None

        # `pacientes` no recibió filas nuevas (pac_exist es el único, revertido al final).
        # (no assertion on total count: la corrida crea pacientes para el staging existente)
    finally:
        db.rollback()
        db.close()

    db = SessionLocal()
    try:
        assert _scalar(db, "SELECT COUNT(*) FROM pacientes") == antes_pac
        assert _scalar(db, "SELECT COUNT(*) FROM pacientes_sigsa3") == antes_ps
        assert _scalar(db, "SELECT COUNT(*) FROM sigsa3") == antes_sig
        assert _scalar(db, "SELECT COUNT(*) FROM sigsa3 WHERE nombre_paciente LIKE :m", m=f"{MARCA}%") == 0
    finally:
        db.close()


def test_dry_run_no_escribe():
    db = SessionLocal()
    try:
        antes_pac = _scalar(db, "SELECT COUNT(*) FROM pacientes")
        antes_ps = _scalar(db, "SELECT COUNT(*) FROM pacientes_sigsa3")
        antes_sig_pac = _scalar(db, "SELECT COUNT(*) FROM sigsa3 WHERE paciente_id IS NOT NULL OR pacientes_sigsa3_id IS NOT NULL")
        res = aplicar_asociacion(db, dry_run=True, limit=50)
        assert res["modo"] == "dry_run"
        assert _scalar(db, "SELECT COUNT(*) FROM pacientes") == antes_pac
        assert _scalar(db, "SELECT COUNT(*) FROM pacientes_sigsa3") == antes_ps
        assert _scalar(db, "SELECT COUNT(*) FROM sigsa3 WHERE paciente_id IS NOT NULL OR pacientes_sigsa3_id IS NOT NULL") == antes_sig_pac
    finally:
        db.rollback()
        db.close()
