from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Literal
from core.database import get_db
from core.security import get_current_user
from modules.users.models import UserModel
from modules.common.vector_similarity import perfil, similitud_compuesta, tokenizar, tokens_equivalentes

router = APIRouter(
    prefix="/pacientes",
    tags=["duplicados"]
)


@router.get("/duplicados/nombres-similares")
def pacientes_nombres_similares(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    similitud_minima: float = Query(0.85, ge=0.1, le=1.0),
    metodo: Literal["vectorial", "trigram", "soundex", "levenshtein"] = Query("vectorial"),
    incluir_fecha_nacimiento: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):

    if metodo == "vectorial":
        # El motor vectorial se evalúa en Python sobre pares ya bloqueados en
        # SQL por apellido, sexo y fecha; no se usa para fusionar registros.
        pares = db.execute(text("""
            SELECT
                a.id AS id_a, a.nombre_completo AS nombre_a, a.expediente AS expediente_a,
                a.cui AS cui_a, a.fecha_nacimiento AS fecha_nacimiento_a, a.sexo AS sexo_a,
                b.id AS id_b, b.nombre_completo AS nombre_b, b.expediente AS expediente_b,
                b.cui AS cui_b, b.fecha_nacimiento AS fecha_nacimiento_b, b.sexo AS sexo_b
            FROM pacientes a
            JOIN pacientes b ON a.id < b.id
              AND lower(unaccent(COALESCE(a.nombre->>'primer_apellido', '')))
                  = lower(unaccent(COALESCE(b.nombre->>'primer_apellido', '')))
              AND (
                  :incluir_fecha = false
                  OR a.fecha_nacimiento = b.fecha_nacimiento
                  OR a.fecha_nacimiento IS NULL
                  OR b.fecha_nacimiento IS NULL
              )
              AND (a.sexo IS NULL OR b.sexo IS NULL OR a.sexo = b.sexo)
            WHERE a.estado != 'I' AND b.estado != 'I'
              AND a.nombre_completo IS NOT NULL AND b.nombre_completo IS NOT NULL
        """), {"incluir_fecha": incluir_fecha_nacimiento}).mappings().all()

        ids = set()
        for par in pares:
            tokens_a, tokens_b = tokenizar(par["nombre_a"]), tokenizar(par["nombre_b"])
            score = 1.0 if tokens_equivalentes(tokens_a, tokens_b) else similitud_compuesta(
                perfil(par["nombre_a"]), perfil(par["nombre_b"])
            )
            if score >= similitud_minima:
                ids.update((par["id_a"], par["id_b"]))

        resultados = db.execute(text("""
            SELECT id, nombre_completo AS nombre, expediente, cui, fecha_nacimiento, sexo
            FROM pacientes
            WHERE id = ANY(:ids)
            ORDER BY nombre_completo
            LIMIT :limit OFFSET :offset
        """), {"ids": list(ids) or [-1], "limit": limit, "offset": offset}).fetchall()
        return {
            "resultados": [
                {
                    "id": r.id, "nombre": r.nombre, "expediente": r.expediente,
                    "cui": r.cui,
                    "fecha_nacimiento": r.fecha_nacimiento.isoformat() if r.fecha_nacimiento else None,
                    "sexo": r.sexo,
                }
                for r in resultados
            ],
            "filtros": {"metodo": metodo, "similitud_minima": similitud_minima,
                         "incluir_fecha_nacimiento": incluir_fecha_nacimiento},
            "paginacion": {"limit": limit, "offset": offset, "total_resultados": len(resultados)},
        }

    if metodo == "trigram":
        comparacion = """
            similarity(a.primer_nombre, b.primer_nombre) >= :similitud_minima
        """

    elif metodo == "soundex":
        comparacion = """
            a.soundex_nombre = b.soundex_nombre
        """

    else:
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
