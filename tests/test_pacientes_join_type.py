"""Listados de expedientes: 'con' y 'sin' consultas recientes (paso join_type).

Antes, `join_type` se ignoraba y ambos listados usaban INNER JOIN, así que los
pacientes sin ninguna consulta nunca aparecían en 'sin consultas recientes'.
"""

from datetime import date

import pytest
from sqlalchemy import text

from modules.pacientes.service import (
    _unir_ultima_consulta,
    buscar_pacientes_con_consultas_recientes,
    buscar_pacientes_sin_consultas_recientes,
)


def _hace_un_anio() -> date:
    hoy = date.today()
    return date(hoy.year - 1, hoy.month, hoy.day)


def _conteo_sql(db, recientes: bool) -> int:
    corte = _hace_un_anio()
    ultima = """
        SELECT paciente_id, MAX(fecha_consulta) AS ultima
        FROM consultas WHERE activo IS TRUE GROUP BY paciente_id
    """
    condicion = "u.ultima > :corte" if recientes else "(u.ultima IS NULL OR u.ultima <= :corte)"
    sql = f"""
        SELECT COUNT(*) FROM pacientes p
        LEFT JOIN ({ultima}) u ON u.paciente_id = p.id
        WHERE p.estado <> 'I' AND p.expediente IS NOT NULL AND p.expediente <> ''
          AND {condicion}
    """
    if recientes:
        sql = sql.replace("LEFT JOIN", "JOIN", 1)
    return db.execute(text(sql), {"corte": corte}).scalar() or 0


def test_sin_recientes_incluye_pacientes_sin_consultas(db_session):
    total_servicio = buscar_pacientes_sin_consultas_recientes(db_session, limit=1).total
    assert total_servicio == _conteo_sql(db_session, recientes=False)


def test_con_recientes_solo_pacientes_con_consulta_reciente(db_session):
    total_servicio = buscar_pacientes_con_consultas_recientes(db_session, limit=1).total
    assert total_servicio == _conteo_sql(db_session, recientes=True)


def test_join_type_invalido_falla(db_session):
    from modules.pacientes.service import _build_ultima_consulta_subquery

    sub = _build_ultima_consulta_subquery(db_session)
    with pytest.raises(ValueError):
        _unir_ultima_consulta(db_session.query(sub.c.paciente_id), sub, "full")
