from unittest.mock import MagicMock

from modules.ciclos.models import CiclosConsulta
from modules.ciclos.service import obtener_ciclos_por_consulta


def _db_con_ciclos(ciclos, nombres):
    """Simula la cadena del ORM para listar ciclos y resolver autores."""
    db = MagicMock()
    (
        db.query.return_value.options.return_value.filter.return_value
        .filter.return_value.order_by.return_value.offset.return_value
        .limit.return_value.all
    ).return_value = ciclos
    db.query.return_value.filter.return_value.all.return_value = nombres
    return db


def test_devuelve_los_ciclos_de_la_consulta():
    ciclos = [MagicMock(usuario="jperez"), MagicMock(usuario="jperez")]
    db = _db_con_ciclos(ciclos, [("jperez", "Juan Pérez")])

    resultado = obtener_ciclos_por_consulta(5, True, db)

    assert resultado == ciclos
    assert db.query.call_args_list[0].args[0] is CiclosConsulta


def test_adjunta_usuario_nombre_en_una_sola_query():
    ciclos = [MagicMock(usuario="jperez"), MagicMock(usuario="mlopez")]
    db = _db_con_ciclos(ciclos, [("jperez", "Juan Pérez"), ("mlopez", "María López")])

    obtener_ciclos_por_consulta(5, True, db)

    assert ciclos[0].usuario_nombre == "Juan Pérez"
    assert ciclos[1].usuario_nombre == "María López"
    # Una query para los ciclos y otra para los nombres: no N+1 por ciclo.
    assert db.query.call_count == 2


def test_no_consulta_nombres_si_no_hay_autores():
    db = _db_con_ciclos([], [])

    assert obtener_ciclos_por_consulta(5, True, db) == []
    assert db.query.call_count == 1
