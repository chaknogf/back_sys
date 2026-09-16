from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import HTTPException, status

from modules.totales.schemas import TotalesResponse, TotalesItem


def get_totales(db: Session, fecha: str | None = None) -> TotalesResponse:
    if fecha:
        try:
            fecha_consulta = datetime.strptime(fecha, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de fecha inválido. Use YYYY-MM-DD (ej: 2025-01-17)"
            )
    else:
        fecha_consulta = date.today()

    query = text("""
        WITH occupancy AS (
            SELECT COALESCE(SUM(cc.camas_ocupadas), 0) AS ocupadas
            FROM censo_camas cc
            WHERE cc.fecha = :fecha
        ),
        capacity AS (
            SELECT COALESCE(SUM(camas_censables), 0) AS total_camas
            FROM encamamiento
            WHERE activo = true
        )
        SELECT entidad, total FROM (
            SELECT 'pacientes_activos' AS entidad, COUNT(*) AS total, 1 AS orden
            FROM pacientes
            WHERE estado = 'A'

            UNION ALL

            SELECT 'coex_hoy' AS entidad, COUNT(*) AS total, 2 AS orden
            FROM consultas
            WHERE tipo_consulta = 1
              AND fecha_consulta = :fecha

            UNION ALL

            SELECT 'hospitalizaciones_hoy' AS entidad, COUNT(*) AS total, 3 AS orden
            FROM consultas
            WHERE tipo_consulta = 2
              AND fecha_consulta = :fecha

            UNION ALL

            SELECT 'emergencias_hoy' AS entidad, COUNT(*) AS total, 4 AS orden
            FROM consultas
            WHERE tipo_consulta = 3
              AND fecha_consulta = :fecha

            UNION ALL

            SELECT 'porcentaje_ocupacional' AS entidad,
                   ROUND(occupancy.ocupadas * 100.0 / NULLIF(capacity.total_camas, 0), 1)::float AS total,
                   5 AS orden
            FROM occupancy, capacity
        ) AS totales_ordenados
        ORDER BY orden;
    """)

    resultado = db.execute(query, {"fecha": fecha_consulta}).fetchall()

    es_hoy = fecha_consulta == date.today()
    sufijo = "Hoy" if es_hoy else fecha_consulta.strftime("%d/%m/%Y")

    iconos_map = {
        'pacientes_activos': 'user-check',
        'coex_hoy': 'stethoscope',
        'hospitalizaciones_hoy': 'bed',
        'emergencias_hoy': 'ambulance',
        'porcentaje_ocupacional': 'bed',
    }

    colores_map = {
        'pacientes_activos': 'purple',
        'coex_hoy': 'cyan',
        'hospitalizaciones_hoy': 'orange',
        'emergencias_hoy': 'red',
        'porcentaje_ocupacional': 'green',
    }

    nombres_map = {
        'pacientes_activos': 'Pacientes Activos',
        'coex_hoy': f'COEX {sufijo}',
        'hospitalizaciones_hoy': f'Hospitalizaciones {sufijo}',
        'emergencias_hoy': f'Emergencias {sufijo}',
        'porcentaje_ocupacional': f'Ocupación Camas {sufijo}',
    }

    totales = [
        TotalesItem(
            entidad=nombres_map.get(row.entidad, row.entidad.capitalize()),
            total=float(row.total) if row.entidad == 'porcentaje_ocupacional' else int(row.total),
            icono=iconos_map.get(row.entidad, "bar-chart"),
            color=colores_map.get(row.entidad, "gray"),
        )
        for row in resultado
    ]

    return TotalesResponse(
        totales=totales,
        generado_en=datetime.now().isoformat(),
    )
