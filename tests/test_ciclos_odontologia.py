from modules.ciclos.schemas import CicloResumen
from modules.ciclos.service import _extraer_odontologia, _extraer_resumen


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
