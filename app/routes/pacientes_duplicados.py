from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Literal
from app.database.db import get_db
from app.database.security import get_current_user
from app.models.user import UserModel

router = APIRouter(
    prefix="/pacientes",
    tags=["duplicados"]
)


@router.get("/duplicados/nombres-similares")
def pacientes_nombres_similares(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    similitud_minima: float = Query(0.7, ge=0.1, le=1.0),
    metodo: Literal["trigram", "soundex", "levenshtein"] = Query("trigram"),
    incluir_fecha_nacimiento: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):

    if metodo == "trigram":
        comparacion = """
            similarity(a.primer_nombre, b.primer_nombre) >= :similitud_minima
        """

    elif metodo == "soundex":
        comparacion = """
            a.soundex_nombre = b.soundex_nombre
        """

    else:  # levenshtein
        comparacion = """
            levenshtein(a.primer_nombre, b.primer_nombre) <= (
                GREATEST(length(a.primer_nombre), length(b.primer_nombre))
                * (1 - :similitud_minima)
            )
        """

    sql_query = text(f"""
        WITH datos_normalizados AS (
            SELECT 
                id,
                expediente,
                cui,
                fecha_nacimiento,
                sexo,
                UPPER(TRIM(COALESCE(nombre->>'primer_nombre', ''))) as primer_nombre,
                UPPER(TRIM(COALESCE(nombre->>'primer_apellido', ''))) as primer_apellido,
                soundex(COALESCE(nombre->>'primer_nombre', '')) as soundex_nombre
            FROM pacientes
            WHERE estado != 'I'
              AND nombre IS NOT NULL
        ),
        pares AS (
            SELECT 
                a.id as id_a,
                b.id as id_b
            FROM datos_normalizados a
            JOIN datos_normalizados b 
                ON a.id < b.id
                AND a.primer_apellido = b.primer_apellido
                AND {comparacion}
                AND (
                    :incluir_fecha = false
                    OR a.fecha_nacimiento = b.fecha_nacimiento
                    OR a.fecha_nacimiento IS NULL
                    OR b.fecha_nacimiento IS NULL
                )
        )
        SELECT * FROM (
            SELECT DISTINCT 
                d.id,
                (d.primer_nombre || ' ' || d.primer_apellido) as nombre,
                d.primer_nombre,
                d.primer_apellido,
                d.expediente,
                d.cui,
                d.fecha_nacimiento,
                d.sexo
            FROM datos_normalizados d
            JOIN (
                SELECT id_a as id FROM pares
                UNION
                SELECT id_b as id FROM pares
            ) ids_similares ON d.id = ids_similares.id
        ) sub
        ORDER BY primer_apellido, primer_nombre
        LIMIT :limit OFFSET :offset
    """)

    resultados = db.execute(
        sql_query,
        {
            "similitud_minima": similitud_minima,
            "incluir_fecha": incluir_fecha_nacimiento,
            "limit": limit,
            "offset": offset
        }
    ).fetchall()

    return {
        "resultados": [
            {
                "id": r.id,
                "nombre": r.nombre,
                "expediente": r.expediente,
                "cui": r.cui,
                "fecha_nacimiento": r.fecha_nacimiento.isoformat() if r.fecha_nacimiento else None,
                "sexo": r.sexo
            }
            for r in resultados
        ],
        "filtros": {
            "metodo": metodo,
            "similitud_minima": similitud_minima,
            "incluir_fecha_nacimiento": incluir_fecha_nacimiento
        },
        "paginacion": {
            "limit": limit,
            "offset": offset,
            "total_resultados": len(resultados)
        }
    }