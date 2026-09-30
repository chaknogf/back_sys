"""Contrato del importador transversal: la hoja de censo en formato matriz.

La hoja real trae dos filas de encabezado (sexo y servicio) y una fila por
variable, con el servicio y el sexo como columnas. Ginecología y Maternidad
ocupan una sola columna.
"""

from datetime import date
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from modules.censo_camas.service import (
    _columnas_transversal,
    _parse_fecha_censo,
    _resolver_servicios_transversal,
    importar_csv_transversal,
)

CATALOGO = [
    (5, "CANGURO"), (12, "UCIA"), (6, "MEDI"), (2, "CIRU"), (3, "CIRU PEDIA"),
    (4, "TRAUMA"), (11, "TRAUMA PEDIA"), (8, "GINE"), (15, "MATER"),
    (9, "PEDIA"), (7, "NEO"), (13, "UCIN"), (1, "CRN"),
]
CANGURO, UCIA, MEDI, CIRU, CIRU_PEDIA = 5, 12, 6, 2, 3
TRAUMA, TRAUMA_PEDIA, GINE, MATER = 4, 11, 8, 15
PEDIA, NEO, UCIN, CRN = 9, 7, 13, 1

SERVICIOS = "\t".join([
    "FECHA", "VARIABLE", "MADRE CANGURO", "MADRE CANGURO", "UCIA", "UCIA",
    "Medicina", "Medicina", "CIRUGIA", "CIRUGIA", "PEDIATRIA CIRUGIA",
    "PEDIATRIA CIRUGIA", "TRAUMATOLOGIA", "TRAUMATOLOGIA", "PEDIATRIA TRAUMA",
    "PEDIATRIA TRAUMA", "GINECOLOGIA", "MATERNIDAD", "PEDIATRIA", "PEDIATRIA",
    "NEONATOS", "NEONATOS", "UCIN", "UCIN", "CRN", "CRN",
])

# Fila de sexo tal como la exporta la hoja, con FECHA y VARIABLE vacíos.
SEXO = "\t\t" + "\t".join([
    "Masculino", "Femenino", "Masculino", "Femenino", "Masculino", "Femenino",
    "Masculino", "Femenino", "Masculino", "Femenino", "Masculino", "Femenino",
    "Masculino", "Femenino", "Femenino", "Femenino", "Masculino", "Femenino",
    "Masculino", "Femenino", "Masculino", "Femenino", "Masculino", "Femenino",
])

VACIA = "\t" * 24
DATOS = [
    "1/01/2026\tCama Ocupada\t0\t0\t1\t5\t4\t7\t11\t3\t0\t0\t6\t3\t4\t1\t3\t7\t13\t8\t3\t0\t5\t6\t3\t18",
    "1/01/2026\tOcupados\t1\t0\t1\t2\t3\t6\t3\t1\t0\t0\t4\t3\t2\t1\t1\t3\t10\t5\t2\t0\t3\t4\t1\t6",
    "1/01/2026\tEgresos Totales\t1\t0\t0\t1\t1\t1\t2\t0\t0\t0\t0\t0\t0\t0\t0\t4\t1\t1\t1\t0\t0\t0\t0\t0",
    "1/01/2026\tEgresos\t1\t0\t0\t1\t1\t1\t2\t0\t0\t0\t0\t0\t0\t0\t0\t4\t1\t1\t1\t0\t0\t0\t0\t0",
    "1/01/2026\tFallecidos" + VACIA,
    "1/01/2026\tReferido" + VACIA,
    "1/01/2026\tTraslado" + VACIA,
    "1/01/2026\tContraindicados" + VACIA,
    "1/01/2026\tOtro Ingresos\t0\t0\t0\t2\t1\t1\t5\t1\t0\t0\t1\t0\t1\t0\t1\t4\t2\t2\t1\t0\t1\t1\t1\t6",
    "1/01/2026\tIngresos\t0\t0\t0\t2\t1\t1\t5\t1\t0\t0\t1\t0\t1\t0\t1\t4\t2\t2\t1\t0\t1\t1\t1\t6",
    "1/01/2026\tHuespedes" + VACIA,
    "1/01/2026\tEmergencia" + VACIA,
    "1/01/2026\tTotal\t" + "\t".join(["99"] * 24),
]

CSV_HOJA = "\n".join([SEXO, SERVICIOS] + DATOS)


class _Query:
    def __init__(self, db):
        self._db = db

    def filter(self, *args):
        return self

    def all(self):
        return self._db.resultados

    def first(self):
        return self._db.existente


class _Db:
    def __init__(self, existente=None):
        self.creados = []
        self.existente = existente
        self.resultados = [
            SimpleNamespace(id=i, nombre_servicio=n, activo=True) for i, n in CATALOGO
        ]

    def query(self, model):
        return _Query(self)

    def add(self, row):
        self.creados.append(row)

    def commit(self):
        pass


def _importar(texto, db=None):
    db = db or _Db()
    return importar_csv_transversal(texto, db), db


def test_encabezado_resuelve_sexo_por_bloque_y_avisa_de_columnas_sueltas():
    filas = [linea.split("\t") for linea in CSV_HOJA.split("\n")]
    columnas, unicolumna = _columnas_transversal(filas)

    assert len(columnas) == 24
    for servicio in ("MADRE CANGURO", "UCIA", "Medicina", "CIRUGIA", "UCIN", "CRN"):
        sexos = [sexo for nombre, sexo, _ in columnas if nombre == servicio]
        assert sexos == ["masculino", "femenino"], servicio
    assert [sexo for nombre, sexo, _ in columnas if nombre == "GINECOLOGIA"] == ["femenino"]
    assert [sexo for nombre, sexo, _ in columnas if nombre == "MATERNIDAD"] == ["femenino"]
    assert unicolumna == []


def test_fila_de_sexo_recortada_no_rompe_el_parseo():
    """La hoja puede venir con la fila de sexo desalineada; el bloque manda."""
    desalineada = "\t".join(SEXO.split("\t")[1:])
    filas = [linea.split("\t") for linea in "\n".join([desalineada, SERVICIOS] + DATOS).split("\n")]
    assert len(filas[0]) != len(filas[1]), "el fixture debe estar desalineado"

    columnas, unicolumna = _columnas_transversal(filas)

    assert len(columnas) == 24
    assert [sexo for nombre, sexo, _ in columnas if nombre == "CRN"] == ["masculino", "femenino"]
    # Sin una fila de sexo utilizable, Ginecología y Maternidad caen al valor por
    # defecto y se reportan para que el usuario lo confirme.
    assert sorted(unicolumna) == ["GINECOLOGIA", "MATERNIDAD"]


def test_nombres_largos_se_resuelven_contra_el_catalogo_de_encamamiento():
    filas = [linea.split("\t") for linea in CSV_HOJA.split("\n")]
    columnas, _ = _columnas_transversal(filas)

    resueltos, faltantes = _resolver_servicios_transversal(
        [nombre for nombre, _, _ in columnas], _Db()
    )

    assert faltantes == []
    assert resueltos["madre canguro"] == CANGURO
    assert resueltos["medicina"] == MEDI
    assert resueltos["cirugia"] == CIRU
    assert resueltos["pediatria cirugia"] == CIRU_PEDIA
    assert resueltos["pediatria trauma"] == TRAUMA_PEDIA
    assert resueltos["ginecologia"] == GINE
    assert resueltos["maternidad"] == MATER
    assert resueltos["neonatos"] == NEO


def test_una_fila_por_fecha_y_servicio():
    resultado, db = _importar(CSV_HOJA)

    assert resultado["creados"] == 13
    assert resultado["actualizados"] == 0
    assert resultado["fechas"] == 1
    assert resultado["errores"] == []
    assert len(db.creados) == 13
    assert {row.servicio_id for row in db.creados} == {i for i, _ in CATALOGO}


def test_los_valores_caen_en_el_servicio_y_el_sexo_correctos():
    _, db = _importar(CSV_HOJA)
    por_id = {row.servicio_id: row for row in db.creados}

    canguro = por_id[CANGURO]
    assert (canguro.ocupados_masculino, canguro.ocupados_femenino) == (1, 0)
    assert (canguro.egresos_masculino, canguro.egresos_femenino) == (1, 0)

    ucia = por_id[UCIA]
    assert (ucia.ocupados_masculino, ucia.ocupados_femenino) == (1, 2)
    assert (ucia.ingresos_masculino, ucia.ingresos_femenino) == (0, 2)
    assert (ucia.otro_ingresos_masculino, ucia.otro_ingresos_femenino) == (0, 2)

    # Ginecología y Maternidad solo tienen columna Femenino.
    assert por_id[GINE].ocupados_masculino == 0
    assert por_id[GINE].ocupados_femenino == 1
    assert por_id[MATER].ocupados_masculino == 0
    assert por_id[MATER].ocupados_femenino == 3

    # Cough/Surgical-Pediatrics no se confunde con Surgical ni Surgical-Trauma.
    assert (por_id[CIRU].ocupados_masculino, por_id[CIRU].ocupados_femenino) == (3, 1)
    assert (por_id[TRAUMA].ocupados_masculino, por_id[TRAUMA].ocupados_femenino) == (4, 3)
    assert (por_id[TRAUMA_PEDIA].ocupados_masculino, por_id[TRAUMA_PEDIA].ocupados_femenino) == (2, 1)

    # Las filas sin datos quedan en cero, no en null.
    assert por_id[PEDIA].fallecidos_masculino == 0
    assert por_id[PEDIA].referido_femenino == 0
    assert por_id[PEDIA].huespedes_masculino == 0
    assert por_id[PEDIA].emergencia_femenino == 0


def test_camas_ocupadas_se_derivan_y_coinciden_con_la_columna_de_la_hoja():
    """La hoja trae su propia columna 'Cama Ocupada'; aquí se recalcula."""
    _, db = _importar(CSV_HOJA)
    por_id = {row.servicio_id: row for row in db.creados}

    # Mismos valores que la fila "Cama Ocupada" de la hoja.
    esperado = {
        CANGURO: 0, UCIA: 6, MEDI: 11, CIRU: 14, CIRU_PEDIA: 0, TRAUMA: 9,
        TRAUMA_PEDIA: 5, GINE: 3, MATER: 7, PEDIA: 21, NEO: 3, UCIN: 11, CRN: 21,
    }
    for servicio_id, camas in esperado.items():
        assert por_id[servicio_id].camas_ocupadas == camas, servicio_id

    # Y "Egresos Totales" también coincide con la hoja.
    assert por_id[UCIA].egresos_totales == 1
    assert por_id[MATER].egresos_totales == 4


def test_la_fila_total_se_ignora():
    _, db = _importar(CSV_HOJA)
    por_id = {row.servicio_id: row for row in db.creados}

    assert por_id[PEDIA].ocupados_masculino == 10
    assert por_id[UCIA].ocupados_femenino == 2


@pytest.mark.parametrize("separador", ["\t", ";", ","])
def test_separadores_tabulador_punto_y_coma_y_coma(separador):
    resultado, _ = _importar(CSV_HOJA.replace("\t", separador))
    assert resultado["creados"] == 13


def test_acepta_la_fecha_de_la_hoja_y_la_iso():
    resultado, _ = _importar(CSV_HOJA.replace("1/01/2026", "2026-01-01"))
    assert resultado["creados"] == 13
    assert _parse_fecha_censo("1/01/2026") == date(2026, 1, 1)
    assert _parse_fecha_censo("1/1/26") == date(2026, 1, 1)
    assert _parse_fecha_censo("ayer") is None


def test_varios_dias_en_un_archivo():
    segundo = "\n".join(linea.replace("1/01/2026", "2/01/2026") for linea in DATOS)
    resultado, _ = _importar(CSV_HOJA + "\n" + segundo)

    assert resultado["creados"] == 26
    assert resultado["fechas"] == 2


def test_reimportar_actualiza_en_lugar_de_duplicar():
    from modules.censo_camas.models import CensoCamasModel

    existente = CensoCamasModel(fecha=date(2026, 1, 1), servicio_id=1)
    resultado, db = _importar(CSV_HOJA, _Db(existente=existente))

    assert (resultado["creados"], resultado["actualizados"]) == (0, 13)
    assert db.creados == []


def test_un_servicio_desconocido_se_avisa_y_no_rompe_la_importacion():
    resultado, _ = _importar(CSV_HOJA.replace("UCIA\tUCIA", "SALA X\tSALA X"))

    assert resultado["creados"] == 12
    assert resultado["errores"] == []
    assert any("SALA X" in aviso for aviso in resultado["advertencias"])


def test_una_variable_desconocida_se_avisa_con_el_texto_original():
    resultado, _ = _importar(CSV_HOJA.replace("1/01/2026\tHuespedes", "1/01/2026\tHuéspedes Rep."))

    assert resultado["creados"] == 13
    assert resultado["errores"] == []
    assert any("Huéspedes Rep." in aviso for aviso in resultado["advertencias"])


def test_una_celda_no_numerica_se_reporta():
    resultado, _ = _importar(CSV_HOJA.replace("1/01/2026\tIngresos\t0", "1/01/2026\tIngresos\tN/A"))

    assert any("no numéricas" in aviso for aviso in resultado["advertencias"])


@pytest.mark.parametrize(
    "contenido",
    [
        pytest.param("a\tb\n1\t2\n3\t4", id="sin_dos_encabezados"),
        pytest.param("a\tb\tc\na\tb\tc\n1\t2\t3", id="sin_columna_fecha_variable"),
        pytest.param("   \n  \n", id="vacio"),
        pytest.param("", id="sin_contenido"),
    ],
)
def test_archivos_que_no_son_la_hoja_se_rechazan(contenido):
    with pytest.raises(HTTPException) as exc:
        importar_csv_transversal(contenido, _Db())

    assert exc.value.status_code == 400
