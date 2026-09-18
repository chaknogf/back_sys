"""
Siembra el catálogo de procedimientos quirúrgicos del Quirófano.

Fuente de datos: data/quirofano_procedimientos.csv
Columnas: referencia_especialidad,procedimiento

La referencia_especialidad debe coincidir con un nombre de la tabla canónica
`especialidades`. Cada procedimiento genera un procedimiento_quirofano cuyo
`nombre` es SOLO el procedimiento. Los códigos se derivan del hash de
"especialidad || procedimiento", por lo que dos procedimientos homónimos en
distintas especialidades no colisionan.

Idempotente: la existencia se evalúa por (especialidad, nombre).

Uso:
    python -m scripts.seed_quirofano_procedimientos            # solo agrega faltantes
    python -m scripts.seed_quirofano_procedimientos --vaciar   # vacía el catálogo y re-siembra
"""

import argparse
import csv
from pathlib import Path

from sqlalchemy import text

from core.database import SessionLocal
import main  # noqa: F401  # registra todos los modelos y configura los mappers
from modules.especialidades.models import EspecialidadModel
from modules.quirofano.models import ProcedimientoQuirofanoModel

CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "quirofano_procedimientos.csv"


def _normalizar(s: str | None) -> str:
    return " ".join((s or "").split())


def _leer_pares() -> list[tuple[str, str]]:
    with CSV_PATH.open(encoding="utf-8") as fh:
        lineas = [ln for ln in fh if not ln.lstrip().startswith("#")]
    reader = csv.DictReader(lineas)
    campos = {c.strip().lower() for c in (reader.fieldnames or [])}
    if not {"procedimiento"} <= campos:
        raise ValueError(f"El CSV debe tener la columna 'procedimiento'. Encontradas: {reader.fieldnames}")
    if not ({"referencia_especialidad"} & campos):
        raise ValueError(
            "El CSV debe tener la columna 'referencia_especialidad'. "
            f"Encontradas: {reader.fieldnames}"
        )
    pares: list[tuple[str, str]] = []
    for fila in reader:
        ref = _normalizar(fila.get("referencia_especialidad") or fila.get("especialidad"))
        proc = _normalizar(fila.get("procedimiento"))
        if not proc:
            continue
        if not ref:
            raise ValueError(f"Procedimiento sin referencia_especialidad: {proc!r}")
        pares.append((ref, proc))
    return pares


def main():
    parser = argparse.ArgumentParser(description="Siembra el catálogo de procedimientos de Quirófano.")
    parser.add_argument("--vaciar", action="store_true", help="Vacía el catálogo antes de sembrar.")
    args = parser.parse_args()

    pares = _leer_pares()

    db = SessionLocal()
    try:
        if args.vaciar:
            db.execute(text("TRUNCATE TABLE procedimiento_quirofano RESTART IDENTITY CASCADE"))
            db.commit()

        especialidades = {
            e.nombre: e for e in db.query(EspecialidadModel).all()
        }
        no_mapeadas = sorted({ref for ref, _ in pares if ref not in especialidades})
        if no_mapeadas:
            raise SystemExit(
                "Referencias sin especialidad en la tabla `especialidades`: "
                + ", ".join(no_mapeadas)
            )

        creados = 0
        omitidos = 0

        for ref, proc in pares:
            esp = especialidades[ref]
            existe = db.query(ProcedimientoQuirofanoModel).filter(
                ProcedimientoQuirofanoModel.especialidad_id == esp.id,
                ProcedimientoQuirofanoModel.nombre == proc,
            ).first()
            if existe:
                omitidos += 1
                continue

            cod_tipo = f"TP{abs(hash(f'{esp.nombre} || {proc}')) % 1000000:06d}"
            db.add(ProcedimientoQuirofanoModel(
                codigo=cod_tipo,
                nombre=proc,
                especialidad_id=esp.id,
                activo=True,
            ))
            creados += 1

        db.commit()
        db.execute(text(
            "SELECT setval("
            "pg_get_serial_sequence('procedimiento_quirofano', 'procedimiento_quirofano_id'), "
            "(SELECT COALESCE(MAX(procedimiento_quirofano_id), 1) FROM procedimiento_quirofano))"
        ))
        db.commit()
        print(f"Procedimientos creados: {creados}")
        print(f"Procedimientos omitidos (ya existían): {omitidos}")
        print(f"Total filas: {len(pares)}")
    finally:
        db.close()


if __name__ == "__main__":
    main()