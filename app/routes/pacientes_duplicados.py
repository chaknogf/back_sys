from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, text, or_, and_
from typing import Optional, Literal
from app.database.db import get_db
from app.models.pacientes import PacienteModel
from app.database.security import get_current_user
from app.models.user import UserModel

router = APIRouter(
    prefix="/pacientes",
    tags=["duplicados"]
)


# ============================================
# BÚSQUEDA POR NOMBRES SIMILARES
# ============================================
@router.get("/duplicados/nombres-similares")
def pacientes_nombres_similares(
    limit: int = Query(100, ge=1, le=500, description="Registros por página"),
    offset: int = Query(0, ge=0, description="Offset para paginación"),
    similitud_minima: float = Query(0.7, ge=0.1, le=1.0, description="Umbral de similitud (0.1-1.0)"),
    metodo: Literal["trigram", "soundex", "levenshtein"] = Query(
        "trigram", 
        description="Método de comparación: trigram (rápido), soundex (fonético), levenshtein (exacto)"
    ),
    incluir_fecha_nacimiento: bool = Query(
        True, 
        description="Considerar fecha de nacimiento en la comparación"
    ),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Encuentra pacientes con nombres similares usando diferentes algoritmos.
    
    Métodos:
    - trigram: Compara trigrams (muy rápido, bueno para typos)
    - soundex: Comparación fonética (bueno para nombres que suenan igual)
    - levenshtein: Distancia de edición (más preciso pero más lento)
    """
    
    # Habilitar extensiones necesarias
    db.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
    db.execute(text("CREATE EXTENSION IF NOT EXISTS fuzzystrmatch"))
    
    if metodo == "trigram":
        sql_query = text("""
            WITH nombres_completos AS (
                SELECT 
                    id,
                    expediente,
                    cui,
                    fecha_nacimiento,
                    estado,
                    UPPER(
                        TRIM(
                            COALESCE(nombre->>'primer_nombre', '') || ' ' ||
                            COALESCE(nombre->>'segundo_nombre', '') || ' ' ||
                            COALESCE(nombre->>'primer_apellido', '') || ' ' ||
                            COALESCE(nombre->>'segundo_apellido', '')
                        )
                    ) as nombre_completo
                FROM pacientes
                WHERE estado != 'I'
                    AND nombre IS NOT NULL
            ),
            similitudes AS (
                SELECT 
                    a.id as id_a,
                    b.id as id_b,
                    a.nombre_completo as nombre_a,
                    b.nombre_completo as nombre_b,
                    a.expediente as expediente_a,
                    b.expediente as expediente_b,
                    a.cui as cui_a,
                    b.cui as cui_b,
                    a.fecha_nacimiento as fecha_nac_a,
                    b.fecha_nacimiento as fecha_nac_b,
                    similarity(a.nombre_completo, b.nombre_completo) as similitud
                FROM nombres_completos a
                INNER JOIN nombres_completos b ON a.id < b.id
                WHERE similarity(a.nombre_completo, b.nombre_completo) >= :similitud_minima
                    AND (:incluir_fecha = false OR a.fecha_nacimiento = b.fecha_nacimiento OR a.fecha_nacimiento IS NULL OR b.fecha_nacimiento IS NULL)
            )
            SELECT 
                id_a,
                id_b,
                nombre_a,
                nombre_b,
                expediente_a,
                expediente_b,
                cui_a,
                cui_b,
                fecha_nac_a,
                fecha_nac_b,
                ROUND(similitud::numeric, 3) as similitud
            FROM similitudes
            ORDER BY similitud DESC, id_a, id_b
            LIMIT :limit OFFSET :offset
        """)
    
    elif metodo == "soundex":
        sql_query = text("""
            WITH nombres_completos AS (
                SELECT 
                    id,
                    expediente,
                    cui,
                    fecha_nacimiento,
                    estado,
                    UPPER(TRIM(
                        COALESCE(nombre->>'primer_nombre', '') || ' ' ||
                        COALESCE(nombre->>'primer_apellido', '')
                    )) as nombre_completo,
                    soundex(COALESCE(nombre->>'primer_nombre', '')) as soundex_nombre,
                    soundex(COALESCE(nombre->>'primer_apellido', '')) as soundex_apellido
                FROM pacientes
                WHERE estado != 'I' AND nombre IS NOT NULL
            )
            SELECT 
                a.id as id_a,
                b.id as id_b,
                a.nombre_completo as nombre_a,
                b.nombre_completo as nombre_b,
                a.expediente as expediente_a,
                b.expediente as expediente_b,
                a.cui as cui_a,
                b.cui as cui_b,
                a.fecha_nacimiento as fecha_nac_a,
                b.fecha_nacimiento as fecha_nac_b,
                1.0 as similitud
            FROM nombres_completos a
            INNER JOIN nombres_completos b ON a.id < b.id
            WHERE (
                a.soundex_nombre = b.soundex_nombre 
                AND a.soundex_apellido = b.soundex_apellido
            )
            AND (:incluir_fecha = false OR a.fecha_nacimiento = b.fecha_nacimiento OR a.fecha_nacimiento IS NULL OR b.fecha_nacimiento IS NULL)
            ORDER BY a.id, b.id
            LIMIT :limit OFFSET :offset
        """)
    
    else:  # levenshtein
        sql_query = text("""
            WITH nombres_completos AS (
                SELECT 
                    id,
                    expediente,
                    cui,
                    fecha_nacimiento,
                    estado,
                    UPPER(TRIM(
                        COALESCE(nombre->>'primer_nombre', '') || ' ' ||
                        COALESCE(nombre->>'segundo_nombre', '') || ' ' ||
                        COALESCE(nombre->>'primer_apellido', '') || ' ' ||
                        COALESCE(nombre->>'segundo_apellido', '')
                    )) as nombre_completo
                FROM pacientes
                WHERE estado != 'I' AND nombre IS NOT NULL
            )
            SELECT 
                a.id as id_a,
                b.id as id_b,
                a.nombre_completo as nombre_a,
                b.nombre_completo as nombre_b,
                a.expediente as expediente_a,
                b.expediente as expediente_b,
                a.cui as cui_a,
                b.cui as cui_b,
                a.fecha_nacimiento as fecha_nac_a,
                b.fecha_nacimiento as fecha_nac_b,
                ROUND(
                    1.0 - (levenshtein(a.nombre_completo, b.nombre_completo)::float / 
                    GREATEST(length(a.nombre_completo), length(b.nombre_completo))),
                    3
                ) as similitud
            FROM nombres_completos a
            INNER JOIN nombres_completos b ON a.id < b.id
            WHERE levenshtein(a.nombre_completo, b.nombre_completo) <= (
                GREATEST(length(a.nombre_completo), length(b.nombre_completo)) * (1 - :similitud_minima)
            )
            AND (:incluir_fecha = false OR a.fecha_nacimiento = b.fecha_nacimiento OR a.fecha_nacimiento IS NULL OR b.fecha_nacimiento IS NULL)
            ORDER BY similitud DESC, a.id, b.id
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
                "grupo": [
                    {
                        "id": r.id_a,
                        "nombre": r.nombre_a,
                        "expediente": r.expediente_a,
                        "cui": r.cui_a,
                        "fecha_nacimiento": r.fecha_nac_a.isoformat() if r.fecha_nac_a else None
                    },
                    {
                        "id": r.id_b,
                        "nombre": r.nombre_b,
                        "expediente": r.expediente_b,
                        "cui": r.cui_b,
                        "fecha_nacimiento": r.fecha_nac_b.isoformat() if r.fecha_nac_b else None
                    }
                ],
                "similitud": float(r.similitud),
                "metodo": metodo
            }
            for r in resultados
        ],
        "paginacion": {
            "limit": limit,
            "offset": offset,
            "total_resultados": len(resultados)
        },
        "filtros": {
            "metodo": metodo,
            "similitud_minima": similitud_minima,
            "incluir_fecha_nacimiento": incluir_fecha_nacimiento
        }
    }


# ============================================
# BÚSQUEDA COMBINADA: Nombre + Fecha Nacimiento
# ============================================
@router.get("/duplicados/nombre-fecha")
def duplicados_nombre_fecha_nacimiento(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    similitud_minima: float = Query(0.8, ge=0.5, le=1.0),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Encuentra duplicados con nombre similar Y misma fecha de nacimiento.
    Método más confiable para detectar duplicados reales.
    """
    
    db.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
    
    sql_query = text("""
        WITH nombres_completos AS (
            SELECT 
                id,
                expediente,
                cui,
                fecha_nacimiento,
                UPPER(TRIM(
                    COALESCE(nombre->>'primer_nombre', '') || ' ' ||
                    COALESCE(nombre->>'primer_apellido', '')
                )) as nombre_completo,
                nombre
            FROM pacientes
            WHERE estado != 'I' 
                AND nombre IS NOT NULL
                AND fecha_nacimiento IS NOT NULL
        )
        SELECT 
            a.id as id_a,
            b.id as id_b,
            a.nombre_completo as nombre_a,
            b.nombre_completo as nombre_b,
            a.expediente as expediente_a,
            b.expediente as expediente_b,
            a.cui as cui_a,
            b.cui as cui_b,
            a.fecha_nacimiento as fecha_nac,
            similarity(a.nombre_completo, b.nombre_completo) as similitud,
            a.nombre as nombre_json_a,
            b.nombre as nombre_json_b
        FROM nombres_completos a
        INNER JOIN nombres_completos b ON 
            a.id < b.id 
            AND a.fecha_nacimiento = b.fecha_nacimiento
        WHERE similarity(a.nombre_completo, b.nombre_completo) >= :similitud_minima
        ORDER BY a.fecha_nacimiento DESC, similitud DESC
        LIMIT :limit OFFSET :offset
    """)
    
    resultados = db.execute(
        sql_query,
        {"similitud_minima": similitud_minima, "limit": limit, "offset": offset}
    ).fetchall()
    
    return {
        "resultados": [
            {
                "grupo": [
                    {
                        "id": r.id_a,
                        "nombre": r.nombre_a,
                        "nombre_detalle": r.nombre_json_a,
                        "expediente": r.expediente_a,
                        "cui": r.cui_a
                    },
                    {
                        "id": r.id_b,
                        "nombre": r.nombre_b,
                        "nombre_detalle": r.nombre_json_b,
                        "expediente": r.expediente_b,
                        "cui": r.cui_b
                    }
                ],
                "fecha_nacimiento_comun": r.fecha_nac.isoformat(),
                "similitud_nombre": float(r.similitud)
            }
            for r in resultados
        ],
        "paginacion": {
            "limit": limit,
            "offset": offset,
            "total_resultados": len(resultados)
        }
    }


# ============================================
# GRUPOS DE NOMBRES SIMILARES
# ============================================
@router.get("/duplicados/grupos-nombres")
def grupos_nombres_similares(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    similitud_minima: float = Query(0.75, ge=0.5, le=1.0),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Agrupa pacientes con nombres muy similares.
    Útil para ver clusters de duplicados.
    """
    
    db.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
    
    sql_query = text("""
        WITH nombres_completos AS (
            SELECT 
                id,
                expediente,
                cui,
                fecha_nacimiento,
                UPPER(TRIM(
                    COALESCE(nombre->>'primer_nombre', '') || ' ' ||
                    COALESCE(nombre->>'primer_apellido', '')
                )) as nombre_completo
            FROM pacientes
            WHERE estado != 'I' AND nombre IS NOT NULL
        ),
        pares_similares AS (
            SELECT 
                a.id as id_a,
                b.id as id_b,
                a.nombre_completo,
                similarity(a.nombre_completo, b.nombre_completo) as sim
            FROM nombres_completos a
            INNER JOIN nombres_completos b ON a.id < b.id
            WHERE similarity(a.nombre_completo, b.nombre_completo) >= :similitud_minima
        ),
        grupos AS (
            SELECT 
                nombre_completo,
                array_agg(DISTINCT id_a) || array_agg(DISTINCT id_b) as ids
            FROM pares_similares
            GROUP BY nombre_completo
        )
        SELECT 
            g.nombre_completo,
            unnest(g.ids) as id_paciente,
            array_length(g.ids, 1) as total_similares
        FROM grupos g
        ORDER BY total_similares DESC, g.nombre_completo
        LIMIT :limit OFFSET :offset
    """)
    
    resultados = db.execute(
        sql_query,
        {"similitud_minima": similitud_minima, "limit": limit, "offset": offset}
    ).fetchall()
    
    # Agrupar por nombre
    grupos = {}
    for r in resultados:
        if r.nombre_completo not in grupos:
            grupos[r.nombre_completo] = {
                "nombre_representativo": r.nombre_completo,
                "total_similares": r.total_similares,
                "ids": []
            }
        grupos[r.nombre_completo]["ids"].append(r.id_paciente)
    
    return {
        "grupos": list(grupos.values()),
        "total_grupos": len(grupos),
        "paginacion": {
            "limit": limit,
            "offset": offset
        }
    }


# ============================================
# ESTADÍSTICAS DE NOMBRES SIMILARES
# ============================================
@router.get("/duplicados/nombres-similares/stats")
def stats_nombres_similares(
    similitud_minima: float = Query(0.8, ge=0.5, le=1.0),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Estadísticas rápidas de nombres similares.
    """
    
    db.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
    
    sql_query = text("""
        WITH nombres_completos AS (
            SELECT 
                id,
                UPPER(TRIM(
                    COALESCE(nombre->>'primer_nombre', '') || ' ' ||
                    COALESCE(nombre->>'primer_apellido', '')
                )) as nombre_completo
            FROM pacientes
            WHERE estado != 'I' AND nombre IS NOT NULL
        )
        SELECT 
            COUNT(DISTINCT a.id) as pacientes_con_similares,
            COUNT(*) as total_pares_similares
        FROM nombres_completos a
        INNER JOIN nombres_completos b ON a.id < b.id
        WHERE similarity(a.nombre_completo, b.nombre_completo) >= :similitud_minima
    """)
    
    stats = db.execute(sql_query, {"similitud_minima": similitud_minima}).fetchone()
    
    return {
        "pacientes_con_nombres_similares": stats.pacientes_con_similares or 0,
        "total_pares_similares": stats.total_pares_similares or 0,
        "umbral_similitud": similitud_minima
    }