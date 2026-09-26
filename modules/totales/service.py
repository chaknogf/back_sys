"""Cálculo SQL de indicadores para el panel hospitalario."""

from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import HTTPException, status
from core.config import APP_TIMEZONE

from modules.totales.schemas import TotalesResponse, TotalesItem


def get_totales(db: Session, fecha: str | None = None) -> TotalesResponse:
    """Valida la fecha, calcula KPIs y usa el censo del día previo como ocupación de apertura."""
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

    # Fecha anterior para el censo de camas (refleja cómo amaneció)
    fecha_censo = fecha_consulta - __import__('datetime').timedelta(days=1)

    query = text("""
        SELECT entidad, total FROM (
            SELECT 'consultas_activas' AS entidad, COUNT(*) AS total, 1 AS orden
            FROM consultas
            WHERE COALESCE(ultimo_estado, '') NOT IN ('egreso', 'archivo', 'referido')
              AND COALESCE(condicion_egreso, '') != 'fallecido'

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

            SELECT 'ocupacion_actual' AS entidad,
                   COUNT(*) AS total,
                   5 AS orden
            FROM consultas
            WHERE tipo_consulta = 2
              AND COALESCE(ultimo_estado, '') NOT IN ('egreso', 'archivo', 'referido')
              AND COALESCE(condicion_egreso, '') != 'fallecido'

            UNION ALL

            SELECT 'censo_camas_hoy' AS entidad,
                   ROUND(
                       COALESCE(SUM(cc.camas_ocupadas), 0) * 100.0 /
                       NULLIF(
                           (SELECT COALESCE(SUM(camas_censables), 0)
                            FROM encamamiento WHERE activo = true),
                           0
                       ), 1
                   )::float AS total,
                   6 AS orden
            FROM censo_camas cc
            WHERE cc.fecha = :fecha_censo

        ) AS totales_ordenados
        ORDER BY orden;
    """)

    resultado = db.execute(query, {"fecha": fecha_consulta, "fecha_censo": fecha_censo}).fetchall()

    es_hoy = fecha_consulta == date.today()
    sufijo = "Hoy" if es_hoy else fecha_consulta.strftime("%d/%m/%Y")

    iconos_map = {
        'consultas_activas': 'user-check',
        'coex_hoy': 'stethoscope',
        'hospitalizaciones_hoy': 'bed',
        'emergencias_hoy': 'ambulance',
        'ocupacion_actual': 'activity',
        'censo_camas_hoy': 'bed',
    }

    colores_map = {
        'consultas_activas': 'purple',
        'coex_hoy': 'cyan',
        'hospitalizaciones_hoy': 'orange',
        'emergencias_hoy': 'red',
        'ocupacion_actual': 'blue',
        'censo_camas_hoy': 'green',
    }

    nombres_map = {
        'consultas_activas': 'Consultas Activas',
        'coex_hoy': f'COEX {sufijo}',
        'hospitalizaciones_hoy': f'Hospitalizaciones {sufijo}',
        'emergencias_hoy': f'Emergencias {sufijo}',
        'ocupacion_actual': 'Ocupación Actual',
        'censo_camas_hoy': f'Censo Camas {sufijo}',
    }

    totales = [
        TotalesItem(
            entidad=nombres_map.get(row.entidad, row.entidad.capitalize()),
            total=int(row.total),
            icono=iconos_map.get(row.entidad, "bar-chart"),
            color=colores_map.get(row.entidad, "gray"),
        )
        for row in resultado
    ]

    return TotalesResponse(
        totales=totales,
        generado_en=datetime.now(APP_TIMEZONE).isoformat(),
    )
