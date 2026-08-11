"""Servicio de búsqueda de nombres similares (F5).

Capa de abstracción entre el router (`duplicados_router.py`) y el motor
nativo (`rust_engine`, PyO3). El router no conoce los detalles de PyO3:
aquí se decide en tiempo de ejecución si usar el motor Rust o un fallback
en Python puro, garantizando el mismo resultado (equivalencia bit a bit).

Flujo (idéntico al router original en semántica):

1. SQL genera los pares candidatos (mismo JOIN de siempre, sin `id_a < id_b`
   para mantener la semántica; se itera con cursor de servidor).
2. `tokenizar`/`perfil` se precomputan UNA vez por paciente (no por par).
3. Pre-filtro de bajo costo (F4.5) por par: descarta pares que no pueden
   superar el umbral sin calcular la similitud completa.
4. Similitud vectorial solo sobre los candidatos que sobreviven.

El pre-filtro (regla validada en F4.5 sobre los 7.4M pares reales) es:

    inter >= 3 OR tokens_equivalentes OR (inter >= 2 AND len_a <= 5 AND len_b <= 5)

con 0 falsos negativos y 0 falsos positivos vs. la evaluación total.

El pre-filtro se ejecuta SIEMPRE en Python puro: el costo dominante en el
caso real (7.4M de pares) es cruzar las listas de tokens hacia Rust vía
PyO3, que resulta más lento (36s) que iterar en Python (≈4s). La regla es
determinista e idéntica en ambos motores (validada en F4.5).
"""

from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Set, Tuple

from sqlalchemy import text
from sqlalchemy.orm import Session

from modules.common.vector_similarity import (
    perfil as _perfil_py,
    similitud_compuesta as _similitud_py,
    tokenizar as _tokenizar_py,
    tokens_equivalentes as _tokens_eq_py,
)

try:  # motor nativo (PyO3); si no está instalado cae al fallback Python puro
    import rust_engine as _rust
    _NATIVO = _rust.nativo_disponible()
except Exception:  # pragma: no cover - entorno sin el paquete instalado
    _rust = None
    _NATIVO = False

_SQL_PARES = """
    SELECT
        a.id, b.id
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
"""


def nativo_disponible() -> bool:
    """True si la similitud se computa con el motor Rust."""
    return _NATIVO


def _tokenizar_masivo(nombres: Iterable[str]) -> List[List[str]]:
    if _NATIVO:
        return _rust.tokenizar_masivo(list(nombres))
    return [_tokenizar_py(n) for n in nombres]


def _perfiles_masivo(nombres: Iterable[str]) -> List[dict]:
    if _NATIVO:
        return _rust.perfiles_masivo(list(nombres))
    return [_perfil_py(n) for n in nombres]


def _tokens_equivalentes(a: List[str], b: List[str]) -> bool:
    if _NATIVO:
        return _rust.tokens_equivalentes(a, b)
    return _tokens_eq_py(a, b)


def _similitud(a: dict, b: dict) -> float:
    if _NATIVO:
        return _rust.similitud_compuesta(a, b)
    return _similitud_py(a, b)


def _prefiltrar_par(ta: List[str], tb: List[str]) -> bool:
    if _tokens_eq_py(ta, tb):
        return True
    inter = len(set(ta) & set(tb))
    return inter >= 3 or (inter >= 2 and len(ta) <= 5 and len(tb) <= 5)


def buscar_ids_duplicados(
    db: Session,
    incluir_fecha: bool,
    similitud_minima: float,
) -> Set[int]:
    """Devuelve el conjunto de ids de pacientes duplicados (vectorial).

    Genera los pares con el mismo JOIN que el router original y aplica el
    pre-filtro F4.5 + similitud vectorial. El conjunto de ids es idéntico al
    del router original (verificado A/B/C bit a bit en F4.5/F5): son los ids
    individuales de todo paciente que participa en al menos un par duplicado.
    """
    # 1) Precompute UNA vez por paciente: tokens y perfiles.
    pacientes = db.execute(text("""
        SELECT id, nombre_completo
        FROM pacientes
        WHERE estado != 'I' AND nombre_completo IS NOT NULL
    """)).fetchall()
    ids_orden = [p[0] for p in pacientes]
    nombres = [p[1] for p in pacientes]
    tokens_por_id: Dict[int, List[str]] = dict(zip(
        ids_orden, _tokenizar_masivo(nombres)
    ))
    perfiles_por_id: Dict[int, dict] = dict(zip(
        ids_orden, _perfiles_masivo(nombres)
    ))

    ids: Set[int] = set()
    for id_a, id_b in _iterar_pares(db, incluir_fecha):
        ta = tokens_por_id[id_a]
        tb = tokens_por_id[id_b]
        if not _prefiltrar_par(ta, tb):
            continue
        if _tokens_equivalentes(ta, tb):
            ids.update((id_a, id_b))
            continue
        score = _similitud(perfiles_por_id[id_a], perfiles_por_id[id_b])
        if score >= similitud_minima:
            ids.update((id_a, id_b))
    return ids


def _iterar_pares(db: Session, incluir_fecha: bool):
    """Itera los pares (id_a, id_b) generados por el JOIN de siempre.

    Prefiere un cursor de servidor crudo (psycopg2) que es ~2x más rápido que
    iterar `Row` de SQLAlchemy sobre 7.4M de filas; si no está disponible
    (otro driver), cae a `stream_results` de SQLAlchemy. Ambas rutas devuelven
    exactamente los mismos pares (mismo JOIN).
    """
    sql = _SQL_PARES.replace(":incluir_fecha", "true" if incluir_fecha else "false")
    try:
        conn = db.connection().connection
        cur = conn.cursor(name="f5_pares")
        cur.itersize = 100_000
        try:
            cur.execute(sql)
            yield from cur
        finally:
            cur.close()
    except Exception:
        result = db.execute(
            text(sql),
            execution_options={"stream_results": True},
        )
        for fila in result:
            yield fila.id_a, fila.id_b


def ids_pares_duplicados(
    pares: Iterable[dict],
    similitud_minima: float,
) -> Set[Tuple[int, int]]:
    """Variante que opera sobre pares ya materializados (dicts).

    `pares`: iterable de dicts con las claves `id_a`, `nombre_a`, `id_b`,
    `nombre_b`. Útil para tests y benchmarks; el router usa
    `buscar_ids_duplicados` (que genera el SQL internamente).
    """
    pares = list(pares)
    if not pares:
        return set()

    ids_pendientes: Set[int] = set()
    nombre_por_id: Dict[int, str] = {}
    for p in pares:
        ids_pendientes.add(p["id_a"])
        ids_pendientes.add(p["id_b"])
        nombre_por_id.setdefault(p["id_a"], p["nombre_a"])
        nombre_por_id.setdefault(p["id_b"], p["nombre_b"])

    ids_orden = list(ids_pendientes)
    nombres = [nombre_por_id[i] for i in ids_orden]
    tokens_por_id = dict(zip(ids_orden, _tokenizar_masivo(nombres)))
    perfiles_por_id = dict(zip(ids_orden, _perfiles_masivo(nombres)))

    ids: Set[Tuple[int, int]] = set()
    for par in pares:
        ta = tokens_por_id[par["id_a"]]
        tb = tokens_por_id[par["id_b"]]
        if not _prefiltrar_par(ta, tb):
            continue
        if _tokens_equivalentes(ta, tb):
            ids.add((par["id_a"], par["id_b"]))
            continue
        score = _similitud(perfiles_por_id[par["id_a"]], perfiles_por_id[par["id_b"]])
        if score >= similitud_minima:
            ids.add((par["id_a"], par["id_b"]))
    return ids
