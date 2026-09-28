from datetime import date, datetime, timezone
from types import SimpleNamespace

from modules.censo_camas.schemas import CensoCamasCreate, CensoCamasOut
from modules.censo_camas.service import _RAW_FIELDS, _build_model, _to_out, importar_csv


def test_create_defaults_raw_counts_for_each_sex():
    data = CensoCamasCreate(
        fecha=date(2026, 9, 27),
        servicio_id=4,
        masculino={"ocupados": 3},
        femenino={},
    )

    model_values = _build_model(data)

    assert model_values["ocupados_masculino"] == 3
    assert model_values["ocupados_femenino"] == 0
    assert model_values["emergencia_masculino"] == 0
    assert model_values["emergencia_femenino"] == 0
    assert model_values["ocupados"] == 3
    assert model_values["camas_ocupadas"] == 3
    assert "sexo" not in model_values


def test_output_calculates_sex_and_combined_totals():
    values = {
        "id": 12,
        "fecha": date(2026, 9, 27),
        "servicio_id": 4,
        "ocupados": 7,
        "camas_ocupadas": 7,
        "egresos_totales": 3,
        "egresos": 1,
        "fallecidos": 1,
        "referido": 1,
        "traslado": 0,
        "contraindicados": 0,
        "otro_ingresos": 0,
        "ingresos": 3,
        "huespedes": 0,
        "emergencia": 0,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    values.update({f"{field}_{sex}": 0 for field in _RAW_FIELDS for sex in ("masculino", "femenino")})
    values.update({
        "ocupados_masculino": 4,
        "ingresos_masculino": 2,
        "egresos_masculino": 1,
        "referido_masculino": 1,
        "ocupados_femenino": 3,
        "ingresos_femenino": 1,
        "fallecidos_femenino": 1,
    })

    output = _to_out(SimpleNamespace(**values))
    validated = CensoCamasOut.model_validate(output)

    assert validated.masculino.egresos_totales == 2
    assert validated.masculino.camas_ocupadas == 4
    assert validated.femenino.egresos_totales == 1
    assert validated.femenino.camas_ocupadas == 3
    assert validated.ocupados == 7
    assert validated.egresos == 1
    assert validated.fallecidos == 1
    assert validated.referido == 1
    assert validated.traslado == 0
    assert validated.contraindicados == 0
    assert validated.otro_ingresos == 0
    assert validated.ingresos == 3
    assert validated.huespedes == 0
    assert validated.emergencia == 0
    assert validated.egresos_totales == 3
    assert validated.camas_ocupadas == 7
    assert validated.totales.ocupados == 7
    assert validated.totales.egresos == 1
    assert validated.totales.egresos_totales == 3
    assert validated.totales.camas_ocupadas == 7


def test_legacy_csv_sex_rows_are_combined_before_persistence():
    from modules.censo_camas.models import CensoCamasModel
    from modules.encamamiento.models import EncamamientoModel

    class Query:
        def __init__(self, results):
            self.results = results

        def filter(self, *_args):
            return self

        def all(self):
            return self.results

        def first(self):
            return None

    class Db:
        def __init__(self):
            self.created = []

        def query(self, model):
            if model is EncamamientoModel:
                return Query([SimpleNamespace(id=9, nombre_servicio="Pediatría")])
            return Query([])

        def add(self, row):
            self.created.append(row)

        def commit(self):
            pass

    csv_data = """fecha,servicio_nombre,sexo,ocupados,egresos,fallecidos,referido,traslado,contraindicados,otro_ingresos,ingresos,huespedes,emergencia
2026-09-27,Pediatría,0,4,1,0,0,0,0,0,2,0,0
2026-09-27,Pediatría,1,3,0,1,0,0,0,0,1,0,0
"""
    db = Db()

    result = importar_csv(csv_data, db)

    assert result == {"creados": 1, "actualizados": 0, "errores": []}
    assert len(db.created) == 1
    row = db.created[0]
    assert isinstance(row, CensoCamasModel)
    assert row.ocupados_masculino == 4
    assert row.ocupados_femenino == 3
    assert row.fallecidos_femenino == 1
    assert row.ocupados == 7
    assert row.egresos_totales == 2
    assert row.camas_ocupadas == 8
