from modules.ciclos.schemas import CicloResumen
from modules.ciclos.service import _extraer_odontologia, _extraer_resumen, obtener_ultimo_odontograma
from modules.consultas.models import ConsultaModel

from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException


def test_resumen_ciclo_prioriza_el_diagnostico_odontologico():
    datos = {
        "impresion_clinica": "",
        "odontologia": {
            "motivo_consulta": "Dolor al masticar",
            "diagnostico": "Caries oclusal",
        },
    }

    assert _extraer_resumen(datos) == "Caries oclusal"


def test_resumen_odontologico_incluye_piezas_afectadas_y_es_compatible_con_schema():
    datos = {
        "odontologia": {
            "motivo_consulta": "Dolor dental",
            "diagnostico": "Caries",
            "plan_tratamiento": "Restauración",
            "odontograma": {
                "denticion": "permanente",
                "dientes": {
                    "16": {"superficies": {"oclusal": "caries"}},
                    "24": {"estado": "ausente", "superficies": {}},
                },
            },
        },
    }

    resumen = _extraer_odontologia(datos)
    assert resumen == {
        "motivo_consulta": "Dolor dental",
        "diagnostico": "Caries",
        "plan_tratamiento": "Restauración",
        "procedimientos": None,
        "piezas_afectadas": ["16", "24"],
    }
    ciclo = CicloResumen.model_validate({"id": 1, "numero": 1, "odontologia": resumen})
    assert ciclo.odontologia["piezas_afectadas"] == ["16", "24"]


def test_identifica_notas_odontologicas_anteriores_sin_odontograma_estructurado():
    resumen = _extraer_odontologia({"impresion_clinica": "Pulpitis"}, "ODON")
    assert resumen["diagnostico"] == "Pulpitis"
    assert resumen["piezas_afectadas"] == []
    assert _extraer_odontologia({}, "Odontología") is not None


def _db_odontograma(consultas_ids, ciclos):
    """Construye un doble de sesión para obtener_ultimo_odontograma."""
    db = MagicMock()
    db.get.return_value = object()  # el paciente existe

    consulta_query = MagicMock()
    consulta_query.filter.return_value.all.return_value = consultas_ids

    ciclo_query = MagicMock()
    ciclo_query.filter.return_value.order_by.return_value.all.return_value = ciclos

    db.query.side_effect = lambda model: consulta_query if model is ConsultaModel.id else ciclo_query
    return db


def test_ultimo_odontograma_devuelve_el_mas_reciente_con_piezas():
    sin_odontologia = MagicMock(datos_medicos={"impresion_clinica": "Control"})
    odontograma_vacio = MagicMock(datos_medicos={"odontologia": {"odontograma": {"denticion": "permanente", "dientes": {}}}})
    con_piezas = MagicMock(datos_medicos={"odontologia": {"odontograma": {"denticion": "temporal", "dientes": {"55": {"estado": "caries"}}}}})

    db = _db_odontograma([(1,), (2,)], [sin_odontologia, odontograma_vacio, con_piezas])

    # Ignora los ciclos sin odontografía útil y salta el odontograma vacío.
    assert obtener_ultimo_odontograma(77, db) == {
        "denticion": "temporal",
        "dientes": {"55": {"estado": "caries"}},
    }


def test_ultimo_odontograma_none_cuando_no_hay_registros():
    db = _db_odontograma([], [])
    assert obtener_ultimo_odontograma(77, db) is None


def test_ultimo_odontograma_404_si_paciente_no_existe():
    db = MagicMock()
    db.get.return_value = None
    with pytest.raises(HTTPException) as exc:
        obtener_ultimo_odontograma(999, db)
    assert exc.value.status_code == 404
