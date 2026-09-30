"""Contrato y agregación del resumen de indicadores de consultas."""

from datetime import date

import pytest
from fastapi import HTTPException

from modules.estadisticas.schemas import IndicadoresConsultasResponse
from modules.estadisticas.service import (
    INDICADORES_CONSULTA,
    _clasificar_valor_indicador,
    indicadores_consultas,
)


RANGO_VACIO = ("1990-01-01", "1990-01-31")


def test_catalogo_de_indicadores_cubre_las_doce_claves():
    assert len(INDICADORES_CONSULTA) == 12
    assert all(meta["etiqueta"] for meta in INDICADORES_CONSULTA.values())
    assert all(meta["tipo"] in ("booleano", "texto") for meta in INDICADORES_CONSULTA.values())


def test_los_indicadores_de_referencia_son_de_texto():
    texto = {k for k, m in INDICADORES_CONSULTA.items() if m["tipo"] == "texto"}
    assert texto == {"viene_referido", "fue_referido"}


@pytest.mark.parametrize(
    "valor,esperado",
    [
        ("true", "verdadero"),
        ("True", "verdadero"),
        ("S", "verdadero"),
        ("s", "verdadero"),
        ("1", "verdadero"),
        ("false", "falso"),
        ("N", "falso"),
        ("n", "falso"),
        ("0", "falso"),
        ("", "sin_valor"),
        ("   ", "sin_valor"),
        (None, "sin_valor"),
    ],
)
def test_clasificacion_respeta_las_dos_convenciones_de_valor(valor, esperado):
    """`personal_hospital` se guarda S/N y el resto booleanos: ambos deben caer igual."""
    assert _clasificar_valor_indicador(valor) == esperado


def test_texto_libre_no_se_confunde_con_una_bandera():
    assert _clasificar_valor_indicador("CAP DE PATZUN") == "texto"
    assert _clasificar_valor_indicador("coex de ginecologia") == "texto"


def test_rango_sin_consultas_devuelve_ceros(db_session):
    reporte = indicadores_consultas(db_session, *RANGO_VACIO)

    assert reporte["total_consultas"] == 0
    assert reporte["pacientes_distintos"] == 0
    assert reporte["dias_con_registros"] == 0
    assert reporte["datos"] == []
    assert reporte["referencias"] == []
    assert reporte["total_general"] == 0
    cobertura = reporte["cobertura"]
    assert cobertura["claves_distintas"] == 0
    assert cobertura["promedio_claves_por_consulta"] == 0.0


def test_fechas_invalidas_se_rechazan(db_session):
    with pytest.raises(HTTPException) as exc:
        indicadores_consultas(db_session, "2026-13-45", "2026-09-30")
    assert exc.value.status_code == 400


def test_rango_con_datos_cumple_el_contrato(db_session):
    """Sobre un mes con datos el reporte debe ser internamente consistente."""
    reporte = IndicadoresConsultasResponse.model_validate(
        indicadores_consultas(db_session, "2026-09-01", "2026-09-30")
    )

    total = reporte.total_consultas
    assert total > 0
    assert reporte.desde == date(2026, 9, 1)
    assert reporte.hasta == date(2026, 9, 30)

    assert {d.indicador for d in reporte.datos} <= set(INDICADORES_CONSULTA)
    for d in reporte.datos:
        # Los booleanos se reparten en verdadero/falso; los de texto, en con_texto.
        if d.tipo_dato == "texto":
            assert d.verdadero == 0 and d.falso == 0
            assert d.con_texto + d.sin_valor + d.clave_ausente == total
        else:
            assert d.con_texto == 0
            assert d.verdadero + d.falso + d.sin_valor + d.clave_ausente == total
            for t in d.por_tipo_consulta:
                assert 0 <= t.total <= d.verdadero
        assert d.pacientes <= reporte.pacientes_distintos

    # Orden descendente por magnitud.
    magnitudes = [
        d.con_texto if d.tipo_dato == "texto" else d.verdadero for d in reporte.datos
    ]
    assert magnitudes == sorted(magnitudes, reverse=True)


def test_el_filtro_por_tipo_de_consulta_acota_el_total(db_session):
    """El subconjunto de emergencia no puede superar al mes completo."""
    mes = indicadores_consultas(db_session, "2026-09-01", "2026-09-30")
    emergencia = indicadores_consultas(
        db_session, "2026-09-01", "2026-09-30", tipo_consulta=3
    )

    assert emergencia["total_consultas"] <= mes["total_consultas"]

    total_por_clave = {
        d["indicador"]: sum(t["total"] for t in d["por_tipo_consulta"])
        for d in mes["datos"]
    }
    emergencia_por_clave = {
        d["indicador"]: sum(t["total"] for t in d["por_tipo_consulta"])
        for d in emergencia["datos"]
    }
    for clave, total in emergencia_por_clave.items():
        assert total <= total_por_clave.get(clave, 0)


def test_endpoint_exige_autenticacion(client):
    resp = client.get("/estadisticas/consultas/indicadores?desde=2026-09-01&hasta=2026-09-30")
    assert resp.status_code in (401, 403)


def test_endpoint_exige_rango_de_fechas(client, auth_headers):
    resp = client.get(
        "/estadisticas/consultas/indicadores",
        headers=auth_headers,
    )
    assert resp.status_code == 422


def test_endpoint_rechaza_tipo_consulta_invalido(client, auth_headers):
    resp = client.get(
        "/estadisticas/consultas/indicadores",
        params={"desde": "2026-09-01", "hasta": "2026-09-30", "tipo_consulta": 9},
        headers=auth_headers,
    )
    assert resp.status_code == 422


def test_endpoint_responde_con_el_contrato(client, auth_headers):
    resp = client.get(
        "/estadisticas/consultas/indicadores",
        params={"desde": "2026-09-01", "hasta": "2026-09-30"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    cuerpo = resp.json()
    IndicadoresConsultasResponse.model_validate(cuerpo)
    assert cuerpo["titulo"] == "Resumen de Indicadores de Consultas"
    assert "estudiante_publico" in {d["indicador"] for d in cuerpo["datos"]}