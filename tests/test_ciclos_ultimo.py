from unittest.mock import MagicMock

from modules.ciclos.models import CiclosConsulta
from modules.ciclos.service import obtener_ultimo_ciclo_por_consulta


def _db_con_ciclo(ciclo):
    """Simula la cadena query().options().filter()...first() del ORM."""
    db = MagicMock()
    primera = (
        db.query.return_value.options.return_value
        .filter.return_value.filter.return_value
        .order_by.return_value.first
    )
    primera.return_value = ciclo
    return db


def test_ultimo_ciclo_devuelve_el_mas_reciente():
    ciclo = MagicMock(usuario="jperez")
    db = _db_con_ciclo(ciclo)

    resultado = obtener_ultimo_ciclo_por_consulta(5, True, db)

    assert resultado is ciclo
    # El nombre legible del usuario se adjunta a partir del username.
    assert resultado.usuario_nombre == db.query.return_value.filter.return_value.scalar.return_value


def test_ultimo_ciclo_none_cuando_no_hay_notas():
    db = _db_con_ciclo(None)

    assert obtener_ultimo_ciclo_por_consulta(5, True, db) is None


def test_ultimo_ciclo_sin_filtro_activo():
    """Con activo=None no se aplica el segundo filtro y sigue retornando el ciclo."""
    db = MagicMock()
    ciclo = MagicMock(usuario="jperez")
    (
        db.query.return_value.options.return_value
        .filter.return_value.order_by.return_value.first
    ).return_value = ciclo

    assert obtener_ultimo_ciclo_por_consulta(5, None, db) is ciclo


def test_ultimo_ciclo_ordenado_por_registro_desc():
    """Se delega el orden al ORM con registro DESC y id DESC como desempate."""
    db = _db_con_ciclo(MagicMock(usuario="u"))

    obtener_ultimo_ciclo_por_consulta(5, True, db)

    order_by = db.query.return_value.options.return_value.filter.return_value.filter.return_value.order_by
    order_by.assert_called_once()


def test_ultimo_ciclo_consulta_del_modelo_correcto():
    db = _db_con_ciclo(MagicMock(usuario="u"))

    obtener_ultimo_ciclo_por_consulta(7, True, db)

    # La primera query es sobre el modelo de ciclos.
    assert db.query.call_args_list[0].args[0] is CiclosConsulta
