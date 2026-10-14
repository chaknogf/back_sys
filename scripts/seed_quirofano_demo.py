"""
Deja registros de prueba (demo) en `intervenciones_quirurgicas` para poder ver
el reporte de quirófano (`/quirofano/reportes/resumen`) y descargar el Excel con
datos reales.

Las filas se insertan en una ventana reciente (hoy-21 → hoy-1), repartidas entre
los dos quirófanos activos, con estados Finalizada/Cancelada y horarios de
anestesia/intervención/limpieza. Todas quedan marcadas en `observaciones` con la
etiqueta `[DEMO]` para poder identificarlas y eliminarlas.

Idempotente: si ya existen filas `[DEMO]`, se omiten (use `--limpiar` primero
para regenerarlas).

Uso:
    python -m scripts.seed_quirofano_demo            # inserta la demo
    python -m scripts.seed_quirofano_demo --limpiar  # borra las filas [DEMO]
"""

import argparse
from datetime import date, time, timedelta

from sqlalchemy import text

from core.database import SessionLocal
import main  # noqa: F401  # registra todos los modelos y configura los mappers
from modules.quirofano.models import IntervencionQuirurgicaModel

ETIQUETA = "[DEMO]"

# (paciente_id, personal_atencion_id, especialidad_id, quirofano_numero_id,
#  procedimiento_principal, procedimiento_2, area_id, estado_id, formato_id,
#  procedencia_id, rango_id, dia_offset,
#  anestesia, inicio_int, fin_int, fin_limpieza)
FILAS = [
    (133814, 164, 3, 1, "Apendicectomía", None, 5, 1, 1, 1, 1, 20,
     "07:45", "08:00", "09:30", "10:00"),
    (21145, 165, 5, 2, "Cesárea", None, 5, 1, 1, 2, 1, 18,
     "08:15", "08:40", "09:50", "10:20"),
    (127552, 166, 3, 1, "Colecistectomía laparoscópica", None, 5, 1, 2, 2, 1, 15,
     "07:30", "07:55", "09:40", "10:05"),
    (133836, 167, 6, 2, "Reducción de fractura", "Colocación de clavo", 4, 1, 5, 1, 2, 12,
     "09:00", "09:20", "10:50", "11:15"),
    (120482, 10, 1, 1, "Drenaje de absceso", None, 5, 1, 1, 1, 2, 10,
     "07:50", "08:05", "09:00", "09:20"),
    (133814, 14, 3, 2, "Herniorrafia inguinal", None, 5, 1, 1, 2, 1, 8,
     "08:00", "08:25", "10:00", "10:30"),
    (21145, 164, 5, 1, "Legrado uterino", None, 5, 1, 3, 2, 2, 7,
     "07:40", "08:00", "08:50", "09:10"),
    (127552, 165, 3, 2, "Laparotomía exploradora", None, 5, 1, 1, 1, 1, 6,
     "10:00", "10:20", "12:30", "12:55"),
    (133836, 166, 4, 1, "Circuncisión", None, 1, 1, 4, 2, 3, 5,
     "08:10", "08:25", "09:05", "09:25"),
    (120482, 167, 6, 2, "Artroscopia de rodilla", None, 4, 1, 4, 2, 1, 4,
     "07:55", "08:15", "09:45", "10:10"),
    (133814, 10, 1, 1, "Biopsia de piel", None, 1, 1, 1, 1, 2, 3,
     "11:00", "11:15", "11:45", "12:00"),
    (21145, 14, 3, 2, "Apendicectomía", None, 5, 2, 1, 1, 1, 2,
     None, None, None, None),
    (127552, 164, 5, 1, "Cesárea", None, 5, 2, 1, 3, 1, 1,
     None, None, None, None),
    (133836, 165, 3, 2, "Colecistectomía laparoscópica", None, 5, 1, 2, 2, 1, 1,
     "07:35", "08:00", "09:30", "09:55"),
]


def _hora(v: str | None):
    if not v:
        return None
    hh, mm = v.split(":")
    return time(int(hh), int(mm))


def limpiar(db) -> int:
    borradas = (
        db.query(IntervencionQuirurgicaModel)
        .filter(IntervencionQuirurgicaModel.observaciones.like(f"%{ETIQUETA}%"))
        .delete(synchronize_session=False)
    )
    db.commit()
    return borradas


def sembrar(db) -> int:
    hoy = date.today()
    creadas = 0
    for (
        paciente_id, personal_id, esp_id, quirofano_id,
        proc1, proc2, area_id, estado_id, formato_id,
        procedencia_id, rango_id, offset,
        anestesia, inicio, fin, limpieza,
    ) in FILAS:
        db.add(IntervencionQuirurgicaModel(
            paciente_id=paciente_id,
            personal_atencion_id=personal_id,
            especialidad_id=esp_id,
            quirofano_numero_id=quirofano_id,
            procedimiento_principal=proc1,
            procedimiento_2=proc2,
            area_cuerpo_intervenida=None,
            id_area_cuerpo_intervenida=area_id,
            estado_cirugia_id=estado_id,
            formato_procedimiento_id=formato_id,
            procedencia_procedimiento_id=procedencia_id,
            rango_especialista_id=rango_id,
            fecha=hoy - timedelta(days=offset),
            hora_inicio_anestesia=_hora(anestesia),
            hora_inicio_intervencion=_hora(inicio),
            hora_finaliza_intervencion=_hora(fin),
            hora_finaliza_limpieza_prepara_quirofano=_hora(limpieza),
            observaciones=f"Caso de prueba {ETIQUETA}",
            activo=True,
        ))
        creadas += 1
    db.commit()
    return creadas


def main():
    parser = argparse.ArgumentParser(description="Deja registros de prueba en intervenciones_quirurgicas.")
    parser.add_argument("--limpiar", action="store_true", help="Borra las filas con la etiqueta [DEMO].")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        if args.limpiar:
            print(f"Filas [DEMO] eliminadas: {limpiar(db)}")
            return

        existentes = (
            db.query(IntervencionQuirurgicaModel)
            .filter(IntervencionQuirurgicaModel.observaciones.like(f"%{ETIQUETA}%"))
            .count()
        )
        if existentes:
            print(f"Ya existen {existentes} filas {ETIQUETA}; se omite. Use --limpiar para regenerar.")
            return

        print(f"Filas {ETIQUETA} creadas: {sembrar(db)}")
        print(f"Total en intervenciones_quirurgicas: "
              f"{db.query(IntervencionQuirurgicaModel).count()}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
