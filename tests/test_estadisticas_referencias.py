"""Lista y resumen de referencias (`viene_referido_de` / `va_referido_a`)."""

import unicodedata
from datetime import date

import pytest
from fastapi import HTTPException

from modules.estadisticas.schemas import ReferenciasResponse
from modules.estadisticas.service import referencias_consultas


RANGO_VACIO = ("1990-01-01", "1990-01-31")
RANGO_MES = ("2026-09-01", "2026-09-30")
RANGO_JSON_NULL = ("2026-05-01", "2026-05-31")


def _sin_acentos(texto: str) -> str:
    """Equivalente en Python de `unaccent()` de PostgreSQL para este test."""
    descompuesto = unicodedata.normalize("NFD", texto)
    return "".join(c for c in descompuesto if not unicodedata.combining(c))


def test_rango_sin_consultas_devuelve_ceros(db_session):
    reporte = referencias_consultas(db_session, *RANGO_VACIO)

    assert reporte["total_consultas"] == 0
    assert reporte["pacientes_distintos"] == 0
    assert reporte["dias_con_registros"] == 0
    assert reporte["lista"] == []
    assert reporte["resumen"] == []
    assert reporte["total_general"] == 0
    assert reporte["cobertura"]["porcentaje_con_referencia"] == 0.0


def test_fechas_invalidas_se_rechazan(db_session):
    with pytest.raises(HTTPException) as exc:
        referencias_consultas(db_session, "2026-13-45", "2026-09-30")
    assert exc.value.status_code == 400


def test_rango_con_datos_cumple_el_contrato(db_session):
    reporte = ReferenciasResponse.model_validate(
        referencias_consultas(db_session, *RANGO_MES)
    )

    assert reporte.total_consultas > 0
    assert reporte.desde == date(2026, 9, 1)
    assert reporte.hasta == date(2026, 9, 30)
    assert reporte.lista
    assert reporte.resumen


def test_sin_jsonb_uno_no_rompe_la_consulta(db_session):
    """202,479 filas guardan el jsonb como `null` literal, no como SQL NULL.

    `jsonb_each_text` aborta la transicion si no se las excluye, asi que el
    reporte debe contarlas en `sin_jsonb` en vez de fallar.
    """
    reporte = referencias_consultas(db_session, *RANGO_JSON_NULL)
    cobertura = reporte["cobertura"]

    assert reporte["total_consultas"] > 0
    assert cobertura["consultas_sin_jsonb"] > 0
    assert cobertura["consultas_con_jsonb"] + cobertura["consultas_sin_jsonb"] == reporte["total_consultas"]


def test_cobertura_es_internamente_consistente(db_session):
    """Los conteos se validan contra el total del rango, sin fijar cifras.

    La suite inserta consultas reales, asi que el total de septiembre cambia
    entre corridas y un valor fijo dejaria el test brittle.
    """
    reporte = referencias_consultas(db_session, *RANGO_MES)
    cobertura = reporte["cobertura"]
    total = reporte["total_consultas"]

    assert cobertura["consultas_con_jsonb"] + cobertura["consultas_sin_jsonb"] == total
    assert cobertura["consultas_con_referencia"] + cobertura["consultas_sin_referencia"] == total
    assert cobertura["consultas_con_referencia"] == reporte["total_general"]
    assert cobertura["ambos_sentidos"] <= min(cobertura["con_origen"], cobertura["con_destino"])
    assert 0 <= cobertura["porcentaje_con_referencia"] <= 100


def test_la_lista_solo_trae_consultas_con_referencia(db_session):
    """Una fila sin ningun texto de referencia no debe aparecer en la lista."""
    for fila in referencias_consultas(db_session, *RANGO_MES, limit=50)["lista"]:
        tiene_alguna = any(
            fila[c] for c in ("viene_referido_de", "va_referido_a", "viene_referido", "fue_referido")
        )
        assert tiene_alguna, f"consulta {fila['id']} no trae referencia"


def test_la_lista_acepta_las_cuatro_claves(db_session):
    """El resumen debe cubrir las dos convenciones de nombres sin duplicar filas."""
    reporte = referencias_consultas(db_session, *RANGO_MES, limit=100)

    for fila in reporte["lista"]:
        assert fila["viene_referido_de"] or fila["viene_referido"] or fila["va_referido_a"] or fila["fue_referido"]

    assert {f["direccion"] for f in reporte["resumen"]} <= {"viene", "va"}


def test_el_resumen_normaliza_mayusculas_y_acentos(db_session):
    """`cap de patzun` y `CAP DE PATZUN` deben sumar en una sola institucion."""
    claves = [f["referencia"] for f in referencias_consultas(db_session, *RANGO_MES)["resumen"]]

    assert claves == [k.upper() for k in claves]
    assert not any(ch in "".join(claves) for ch in "áéíóúÁÉÍÓÚñÑ")
    assert len(claves) == len(set(claves))


def test_las_variantes_exponen_el_texto_capturado(db_session):
    """Cada variante debe colapsar en la clave normalizada de su grupo.

    `TECPÁN` y `TECPAN` llegan como textos distintos y se unen en la clave,
    que es el motivo de exponer `variantes` al lado del conteo.
    """
    for fila in referencias_consultas(db_session, *RANGO_MES)["resumen"]:
        assert fila["variantes"], f"{fila['referencia']} sin variantes"
        assert sum(v["total"] for v in fila["variantes"]) == fila["total_consultas"]
        for variante in fila["variantes"]:
            assert variante["valor"].strip()
            assert _sin_acentos(variante["valor"]).upper() == fila["referencia"]


def test_el_resumen_ordena_por_magnitud(db_session):
    resumen = referencias_consultas(db_session, *RANGO_MES)["resumen"]
    por_direccion: dict[str, list[int]] = {}
    for fila in resumen:
        por_direccion.setdefault(fila["direccion"], []).append(fila["total_consultas"])

    for totales in por_direccion.values():
        assert totales == sorted(totales, reverse=True)


def test_paginacion_de_la_lista(db_session):
    completo = referencias_consultas(db_session, *RANGO_MES, skip=0, limit=1000)["lista"]
    primera = referencias_consultas(db_session, *RANGO_MES, skip=0, limit=5)["lista"]
    segunda = referencias_consultas(db_session, *RANGO_MES, skip=5, limit=5)["lista"]

    assert len(primera) == 5
    assert primera == completo[:5]
    assert segunda == completo[5:10]


def test_el_offset_mas_alla_del_total_devuelve_lista_vacia(db_session):
    reporte = referencias_consultas(db_session, *RANGO_MES, skip=999_999, limit=10)

    assert reporte["lista"] == []
    assert reporte["resumen"], "el resumen no debe depender de la paginacion de la lista"


def test_los_filtros_acotan_el_rango(db_session):
    total = referencias_consultas(db_session, *RANGO_MES)["total_consultas"]
    urgencia = referencias_consultas(db_session, *RANGO_MES, tipo_consulta=3)["total_consultas"]

    assert 0 < urgencia < total


def test_la_especialidad_desconocida_no_encuentra_registros(db_session):
    reporte = referencias_consultas(db_session, *RANGO_MES, especialidad="NO EXISTE XYZ")

    assert reporte["total_consultas"] == 0
    assert reporte["resumen"] == []


def test_endpoint_exige_autenticacion(client):
    resp = client.get("/estadisticas/consultas/referencias?desde=2026-09-01&hasta=2026-09-30")
    assert resp.status_code in (401, 403)


def test_endpoint_exige_rango_de_fechas(client, auth_headers):
    resp = client.get("/estadisticas/consultas/referencias", headers=auth_headers)
    assert resp.status_code == 422


def test_endpoint_rechaza_paginacion_invalida(client, auth_headers):
    resp = client.get(
        "/estadisticas/consultas/referencias",
        params={"desde": "2026-09-01", "hasta": "2026-09-30", "limit": 5000},
        headers=auth_headers,
    )
    assert resp.status_code == 422


def test_endpoint_responde_con_el_contrato(client, auth_headers):
    resp = client.get(
        "/estadisticas/consultas/referencias",
        params={"desde": "2026-09-01", "hasta": "2026-09-30", "limit": 5},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    cuerpo = resp.json()
    ReferenciasResponse.model_validate(cuerpo)
    assert cuerpo["titulo"] == "Referencias de Consultas (viene_referido_de / va_referido_a)"
    assert len(cuerpo["lista"]) == 5