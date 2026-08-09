"""Tests del agente estadístico (NL→SQL determinístico) y su API."""
from datetime import datetime

import pytest

from modules.agente.interpreter import PlanInvalido, generar_consulta


# ---------------------------------------------------------------------------
# Unit tests del intérprete (sin BD)
# ---------------------------------------------------------------------------

HOY = datetime(2026, 8, 9).date()


@pytest.mark.parametrize("pregunta,entidad,medida", [
    ("¿Cuántos pacientes hay?", "pacientes", "count"),
    ("¿Cuántas consultas hubo?", "consultas", "count"),
    ("listado de citas de hoy", "citas", "list"),
    ("promedio de edad de pacientes", "pacientes", "avg_edad"),
    ("top 5 diagnósticos sigsa", "sigsa3", "top"),
    ("¿cuántos médicos por especialidad?", "medicos", "count"),
    ("suma de cantidad de camas", "censo_camas", "sum_cantidad"),
])
def test_genera_plan_valido(pregunta, entidad, medida):
    plan = generar_consulta(pregunta, hoy=HOY)
    assert plan["entidad"] == entidad
    assert plan["medida"] == medida
    assert plan["sql"].lstrip().upper().startswith("SELECT")
    assert ":desde" not in plan["params"] or isinstance(plan["params"].get("desde"), str)


def test_plan_invalido_pregunta_desconocida():
    with pytest.raises(PlanInvalido):
        generar_consulta("¿cuál es el clima en Guatemala?", hoy=HOY)


def test_agrupacion_por_sexo():
    plan = generar_consulta("pacientes por sexo este año", hoy=HOY)
    assert plan["agrupacion"] == "sexo"
    assert plan["params"]["desde"] == f"{HOY.year}-01-01"


def test_agrupacion_sexo_en_entidad_con_join_paciente():
    # grupo por sexo (sin filtro de sexo) debe incluir el JOIN a pacientes
    plan = generar_consulta("consultas por sexo este mes", hoy=HOY)
    assert plan["agrupacion"] == "sexo"
    assert "consultas c" in plan["sql"]
    assert "LEFT JOIN pacientes p" in plan["sql"]
    assert "GROUP BY COALESCE(p.sexo" in plan["sql"]


def test_filtro_estado_fallecidos_prioriza_pacientes():
    plan = generar_consulta("¿cuántos pacientes fallecidos hay?", hoy=HOY)
    assert plan["entidad"] == "pacientes"
    assert plan["filtros"]["estado"] == "F"


def test_prestamos_por_tipo_documento():
    plan = generar_consulta("prestamos por tipo de documento", hoy=HOY)
    assert plan["entidad"] == "prestamos"
    assert plan["agrupacion"] == "tipo_documento"


def test_diagnosticos_frecuentes_sigsa3():
    plan = generar_consulta("¿Cuáles son los diagnósticos más frecuentes?", hoy=HOY)
    assert plan["entidad"] == "sigsa3"
    assert "diagnostico" in plan["sql"]
    assert plan["params"]["limite_top"] == 10


def test_sexo_filtro():
    plan = generar_consulta("pacientes mujeres", hoy=HOY)
    assert plan["filtros"]["sexo"] == "F"


def test_fechas_relativas():
    plan = generar_consulta("consultas de los ultimos 7 dias", hoy=HOY)
    assert plan["filtros"]["rango"] is not None
    desde = datetime.fromisoformat(plan["filtros"]["rango"][0]).date()
    assert (HOY - desde).days == 6


def test_sinonimo_aprendido():
    plan = generar_consulta("cuántos 'units' hay", reglas_extra={"units": "medicos"},
                            hoy=HOY)
    assert plan["entidad"] == "medicos"


def test_fecha_con_dia_y_mes():
    plan = generar_consulta("consultas del 1 de agosto 2026", hoy=HOY)
    assert plan["filtros"]["rango"] == ["2026-08-01", "2026-08-02"]


def test_filtro_especialidad():
    plan = generar_consulta("cuantas consultas de cirugia hubieron",
                            hoy=HOY, especialidades=["Cirugía", "Medicina General"])
    assert plan["filtros"]["especialidad"] == "Cirugía"
    assert "e.nombre = :especialidad" in plan["sql"]
    assert plan["params"]["especialidad"] == "Cirugía"


def test_especialidad_prefiere_nombre_largo():
    plan = generar_consulta("cuantas consultas de medicina general hay",
                            hoy=HOY, especialidades=["Cirugía", "Medicina General"])
    assert plan["filtros"]["especialidad"] == "Medicina General"


def test_fecha_dia_sin_anio_usa_anio_actual():
    plan = generar_consulta("citas del 5 de junio", hoy=HOY)
    assert plan["filtros"]["rango"] == [f"{HOY.year}-06-05", f"{HOY.year}-06-06"]


def test_sql_no_catena_texto_usuario():
    plan = generar_consulta("cuántos pacientes 'o'); DROP TABLE pacientes; -- hay",
                            hoy=HOY)
    assert "DROP" not in plan["sql"]
    assert ";" not in plan["sql"].rstrip("; ").split("DROP")[0]