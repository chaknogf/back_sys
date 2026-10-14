from unittest.mock import MagicMock

from modules.ciclos.models import CiclosConsulta
from modules.ciclos.schemas import CicloConsultaBase, CicloResumen
from modules.ciclos.service import crear_ciclo, obtener_historia_clinica
from modules.consultas.models import ConsultaModel
from modules.pacientes.models import PacienteModel

UISAU = {
    "estado_paciente": {"estadio": 3, "cama": 12, "especialidad": "MEDI"},
    "informacion_contacto": {"contacto": "María López", "parentesco": 1, "telefono": 55512345},
    "nota_clinica": {"nota": "Paciente estable", "evolucion": "Mejoría"},
}


def test_ciclo_base_acepta_uisau():
    data = CicloConsultaBase(consulta_id=10, uisau=UISAU)
    assert data.uisau == UISAU


def test_ciclo_resumen_expone_uisau():
    resumen = CicloResumen.model_validate({"id": 1, "numero": 1, "uisau": UISAU})
    assert resumen.uisau["nota_clinica"]["nota"] == "Paciente estable"


def test_crear_ciclo_persiste_uisau():
    db = MagicMock()
    db.get.return_value = object()  # la consulta existe
    db.query.return_value.filter.return_value.scalar.return_value = 0

    data = CicloConsultaBase(consulta_id=7, uisau=UISAU)
    user = MagicMock(username="uisau_user")

    ciclo = crear_ciclo(data, db, user)

    assert isinstance(ciclo, CiclosConsulta)
    assert ciclo.uisau == UISAU
    db.add.assert_called_once_with(ciclo)
    db.commit.assert_called_once()


def _db_historia(consulta, ciclo):
    db = MagicMock()
    db.get.return_value = MagicMock(nombre_completo="Juan Pérez", expediente="EXP-1")

    consulta_query = MagicMock()
    consulta_query.filter.return_value.order_by.return_value.all.return_value = [consulta]

    ciclo_query = MagicMock()
    ciclo_query.filter.return_value.order_by.return_value.all.return_value = [ciclo]

    db.query.side_effect = lambda *args: consulta_query if args[0] is ConsultaModel else ciclo_query
    return db


def test_historia_clinica_incluye_uisau():
    consulta = MagicMock(
        id=5,
        tipo_consulta=1,
        especialidad="MEDI",
        fecha_consulta=None,
        hora_consulta=None,
        ultimo_estado="activo",
    )
    ciclo = MagicMock(
        consulta_id=5,
        id=99,
        numero=1,
        registro=None,
        usuario=None,
        especialidad="MEDI",
        servicio="HOSP",
        datos_medicos={},
        uisau=UISAU,
    )

    resultado = obtener_historia_clinica(5, _db_historia(consulta, ciclo))

    assert resultado["consultas"][0]["ciclos"][0]["uisau"] == UISAU


def test_historia_clinica_uisau_none_cuando_no_hay():
    consulta = MagicMock(
        id=5,
        tipo_consulta=1,
        especialidad="MEDI",
        fecha_consulta=None,
        hora_consulta=None,
        ultimo_estado="activo",
    )
    ciclo = MagicMock(
        consulta_id=5,
        id=99,
        numero=1,
        registro=None,
        usuario=None,
        especialidad="MEDI",
        servicio="HOSP",
        datos_medicos={},
        uisau=None,
    )

    resultado = obtener_historia_clinica(5, _db_historia(consulta, ciclo))

    assert resultado["consultas"][0]["ciclos"][0]["uisau"] is None
