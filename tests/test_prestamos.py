"""Pruebas unitarias del módulo de préstamos (service).

La lógica de negocio se prueba de forma aislada con mocks de la sesión
(sin depender de una BD real), salvo un smoke test de integración del
filtro por nombre de paciente que sí usa la BD.
"""
import pytest
from datetime import datetime, timezone, date
from unittest.mock import MagicMock

from fastapi import HTTPException

from modules.prestamos.schemas import PrestamoCreate, PrestamoUpdate
from modules.prestamos.service import (
    _normalizar_opcional,
    crear_prestamo,
    actualizar_prestamo,
    listar_prestamos,
)


def _as_datetime(d: date) -> datetime:
    return datetime(d.year, d.month, d.day, 0, 0, 0)


# =====================================================================
# _normalizar_opcional
# =====================================================================
class TestNormalizarOpcional:
    def test_none_se_mantiene(self):
        assert _normalizar_opcional(None) is None

    def test_string_vacia_se_vuelve_none(self):
        assert _normalizar_opcional("   ") is None

    def test_string_con_espacios_se_limpia(self):
        assert _normalizar_opcional("  hola  ") == "hola"

    def test_no_string_pasa_tal_cual(self):
        assert _normalizar_opcional(42) == 42


# =====================================================================
# Crear préstamo
# =====================================================================
class TestCrearPrestamo:
    def test_rechaza_paciente_inexistente(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc:
            crear_prestamo(PrestamoCreate(id_paciente=999, solicitante="Juan"), "t", db)
        assert exc.value.status_code == 404

    def test_crea_y_llama_commit(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = MagicMock(id=1)

        nuevo = crear_prestamo(
            PrestamoCreate(
                id_paciente=1,
                solicitante="  Dra. Ana  ",
                expediente="  EXP-1 ",
                motivo="   ",
            ),
            "admin",
            db,
        )

        db.add.assert_called_once()
        db.commit.assert_called_once()
        db.refresh.assert_called_once()


# =====================================================================
# Actualizar préstamo
# =====================================================================
class TestActualizarPrestamo:
    def test_devolucion_marca_inactivo_y_usuario(self):
        prestamo = MagicMock()
        prestamo.id = 1
        prestamo.activo = True
        prestamo.usuario_recibe = None
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = prestamo

        actualizar_prestamo(
            1, PrestamoUpdate(fecha_devolucion=datetime.now(timezone.utc)), "admin", db
        )

        assert prestamo.activo is False
        assert prestamo.usuario_recibe == "admin"

    def test_quitar_devolucion_reactiva(self):
        prestamo = MagicMock()
        prestamo.id = 1
        prestamo.activo = False
        prestamo.usuario_recibe = "otro"
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = prestamo

        actualizar_prestamo(1, PrestamoUpdate(fecha_devolucion=None), "admin", db)

        assert prestamo.activo is True
        assert prestamo.usuario_recibe is None

    def test_404_si_no_existe(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc:
            actualizar_prestamo(999, PrestamoUpdate(motivo="x"), "admin", db)
        assert exc.value.status_code == 404


# =====================================================================
# Listar — filtro por nombre de paciente (integración BD real)
# =====================================================================
class TestListarPrestamosNombre:
    def test_filtro_nombre_no_rompe_con_bd(self):
        """Solo cuando la BD esté disponible: el filtro por nombre_paciente
        no debe fallar por columnas inexistentes."""
        try:
            import modules.pacientes.models  # noqa: F401
            import modules.consultas.models  # noqa: F401
            import modules.citas.models  # noqa: F401
            import modules.ciclos.models  # noqa: F401
            import modules.medicos.models  # noqa: F401
            import modules.users.models  # noqa: F401
            import modules.prestamos.models  # noqa: F401
            import modules.procedimientos.models  # noqa: F401
            import modules.eventos.models  # noqa: F401
            import modules.constancias_nacimiento.models  # noqa: F401
            import modules.nacimientos.models  # noqa: F401
            import modules.encamamiento.models  # noqa: F401
            import modules.sigsa3.models  # noqa: F401
            from core.database import SessionLocal
        except Exception:
            pytest.skip("No se pudo cargar los modelos DB en este entorno")

        db = SessionLocal()
        try:
            r = listar_prestamos(db=db, nombre_paciente="null", activo=None)
            assert isinstance(r, dict)
            assert "total" in r and "items" in r
        finally:
            db.close()

    def test_filtro_por_rango_fechas_no_rompe_con_bd(self):
        """El filtro por fecha_desde/fecha_hasta no debe fallar con la BD real;
        el rango debe acotar correctamente los resultados dentro del periodo."""
        try:
            import modules.pacientes.models  # noqa: F401
            import modules.users.models  # noqa: F401
            import modules.prestamos.models  # noqa: F401
            from core.database import SessionLocal
        except Exception:
            pytest.skip("No se pudo cargar los modelos DB en este entorno")

        from datetime import date

        db = SessionLocal()
        try:
            # Sin filtros de fecha: totales de referencia
            base = listar_prestamos(db=db, activo=None, limit=100)
            todos = base["total"]

            # Rango finito en el pasado lejano → debe acotar la consulta
            acotado = listar_prestamos(
                db=db, activo=None, limit=1,
                fecha_desde=date(2000, 1, 1), fecha_hasta=date(2000, 1, 31),
            )
            assert "total" in acotado and "items" in acotado
            assert acotado["total"] <= todos
            for item in acotado["items"]:
                if item.fecha_prestamo is not None:
                    assert item.fecha_prestamo >= _as_datetime(date(2000, 1, 1))
                    assert item.fecha_prestamo < _as_datetime(date(2000, 2, 1))

            # Con un rango amplio actual debería devolver el total general
            amplio = listar_prestamos(
                db=db, activo=None, limit=1,
                fecha_desde=date(1970, 1, 1), fecha_hasta=date(2100, 12, 31),
            )
            assert amplio["total"] >= acotado["total"]
        finally:
            db.close()

    def test_filtro_por_fecha_simple_no_rompe(self):
        """Solo fecha_desde o solo fecha_hasta como date deben funcionar."""
        try:
            import modules.pacientes.models  # noqa: F401
            import modules.users.models  # noqa: F401
            import modules.prestamos.models  # noqa: F401
            from core.database import SessionLocal
        except Exception:
            pytest.skip("No se pudo cargar los modelos DB en este entorno")

        from datetime import date

        db = SessionLocal()
        try:
            r = listar_prestamos(db=db, activo=None, fecha_desde=date(2020, 1, 1))
            assert isinstance(r, dict) and "items" in r
            r2 = listar_prestamos(db=db, activo=None, fecha_hasta=date(2030, 12, 31))
            assert isinstance(r2, dict) and "items" in r2
        finally:
            db.close()