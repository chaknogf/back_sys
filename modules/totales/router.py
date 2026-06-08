from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, cast, String, text, or_
from sqlalchemy.exc import IntegrityError
from typing import Optional, List
from datetime import date, datetime

from core.database import get_db
from modules.totales.schemas import TotalesResponse, TotalesItem
from core.security import get_current_user
from modules.users.models import UserModel

router = APIRouter(prefix="/totales", tags=["totales"])

@router.get(
    "/",
    response_model=TotalesResponse,
    summary="Indicadores clave del hospital",
    description="""
    KPIs en tiempo real o de una fecha específica:
    - Total de pacientes registrados y activos
    - Total de consultas realizadas
    - Consultas del día seleccionado
    - COEX, Hospitalizaciones y Emergencias del día
    
    Parámetro opcional: fecha (formato: YYYY-MM-DD)
    Si no se proporciona, usa la fecha actual
    """
)
def obtener_totales(
    fecha: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    try:
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
            SELECT entidad, total FROM (
                SELECT 'pacientes' AS entidad, COUNT(*) AS total, 1 AS orden
                FROM pacientes
                
                UNION ALL
                
                SELECT 'pacientes_activos' AS entidad, COUNT(*) AS total, 2 AS orden
                FROM pacientes
                WHERE estado = 'ACTIVO'
                
                UNION ALL
                
                SELECT 'consultas' AS entidad, COUNT(*) AS total, 3 AS orden
                FROM consultas
                
                UNION ALL
                
                SELECT 'consultas_fecha' AS entidad, COUNT(*) AS total, 4 AS orden
                FROM consultas
                WHERE fecha_consulta = :fecha
                
                UNION ALL
                
                SELECT 'coex_fecha' AS entidad, COUNT(*) AS total, 5 AS orden
                FROM consultas
                WHERE tipo_consulta = 1 
                  AND fecha_consulta = :fecha
                
                UNION ALL
                
                SELECT 'hospitalizaciones_fecha' AS entidad, COUNT(*) AS total, 6 AS orden
                FROM consultas
                WHERE tipo_consulta = 2 
                  AND fecha_consulta = :fecha
                
                UNION ALL
                
                SELECT 'emergencias_fecha' AS entidad, COUNT(*) AS total, 7 AS orden
                FROM consultas
                WHERE tipo_consulta = 3 
                  AND fecha_consulta = :fecha
            ) AS totales_ordenados
            ORDER BY orden;
        """)
        
        resultado = db.execute(query, {"fecha": fecha_consulta}).fetchall()

        iconos_map = {
            'pacientes': 'users',
            'pacientes_activos': 'user-check',
            'consultas': 'file-medical',
            'consultas_fecha': 'calendar-check',
            'coex_fecha': 'stethoscope',
            'hospitalizaciones_fecha': 'bed',
            'emergencias_fecha': 'ambulance'
        }
        
        colores_map = {
            'pacientes': 'blue',
            'pacientes_activos': 'purple',
            'consultas': 'green',
            'consultas_fecha': 'teal',
            'coex_fecha': 'cyan',
            'hospitalizaciones_fecha': 'orange',
            'emergencias_fecha': 'red'
        }

        es_hoy = fecha_consulta == date.today()
        sufijo = "Hoy" if es_hoy else fecha_consulta.strftime("%d/%m/%Y")
        
        nombres_map = {
            'pacientes': 'Pacientes Totales',
            'pacientes_activos': 'Pacientes Activos',
            'consultas': 'Consultas Totales',
            'consultas_fecha': f'Consultas {sufijo}',
            'coex_fecha': f'COEX {sufijo}',
            'hospitalizaciones_fecha': f'Hospitalizaciones {sufijo}',
            'emergencias_fecha': f'Emergencias {sufijo}'
        }

        totales = [
            TotalesItem(
                entidad=nombres_map.get(row.entidad, row.entidad.capitalize()),
                total=row.total,
                icono=iconos_map.get(row.entidad, "bar-chart"),
                color=colores_map.get(row.entidad, "gray")
            )
            for row in resultado
        ]

        return TotalesResponse(
            totales=totales,
            generado_en=datetime.now().isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en obtener_totales: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener indicadores del dashboard: {str(e)}"
        )
