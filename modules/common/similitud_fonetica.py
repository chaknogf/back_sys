"""
Similitud fonética / tolerancia a typos para nombres.

Extiende el pipeline de normalización (normalizar_texto/tokenizar) para
tolerar ERRORES DE TIPEO: letras faltantes, de más, cambiadas o transpuestas.

El problema que resuelve:

    coseno(["rodrigez"], ["rodriguez"]) == 0.0   # tokens distintos como string
    "grcia" vs "garcia"                 == 0.0   # ídem

La comparación exacta de tokens (por igualdad de string) no detecta que
son "casi la misma palabra". Aquí usamos distancia de Levenshtein para
medir cuán parecidos son dos tokens, y una alineación greedy para
comparar dos listas de tokens (nombres) tolerando 1-2 letras de error.

No requiere librerías externas (rapidfuzz, etc.) — solo stdlib.

ADVERTENCIA IMPORTANTE — LEER ANTES DE INTEGRAR:
=================================================
La tolerancia a typos basada en distancia de edición NO puede distinguir
"typo del mismo nombre" de "nombre distinto que se parece":

    Maria  <-> Marta   (distancia=1, similitud=0.80)  <- personas DISTINTAS
    Grcia  <-> Garcia  (distancia=1, similitud=0.83)  <- típico typo

Ambos casos son estructuralmente idénticos para el algoritmo. NO existe
forma de diferenciarlos solo con edición de caracteres.

REGLA DE INTEGRACIÓN RECOMENDADA (consistente con la filosofía de
"minimizar falsos positivos" del pipeline SIGSA-3 -> pacientes):

1. Nunca asociar (auto-match) basándose SOLO en similitud fuzzy.
2. Usar el score fuzzy como candidato adicional para el paso de
   submatch/zona-gris existente (donde ya se corrobora con
   expediente/sexo antes de decidir).
3. Si no hay corroboración de expediente ni de sexo, el resultado va
   SIEMPRE a `revision` con tipo="typo_probable", nunca a asociaciones
   directas -- igual que ya se hace con "submatch_bajo_score".
4. Aplicar tolerancia SOLO al apellido, no al primer nombre. Un error
   de tipeo en el apellido (Rodrigez/Rodriguez) es más seguro de
   aceptar que uno en el primer nombre (Maria/Marta), porque el
   universo de apellidos es mucho más disperso que el de nombres
   comunes, y hay menos colisión con nombres "vecinos" reales.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Dict, List, Optional, Tuple


# ============================================================
# 1. Distancia de edición (Levenshtein) a nivel de token
# ============================================================

@lru_cache(maxsize=100_000)
def distancia_levenshtein(a: str, b: str) -> int:
    """
    Distancia de edición clásica (inserción/borrado/sustitución = costo 1).
    Cacheada porque en un linkage se repiten muchas comparaciones de los
    mismos tokens (apellidos comunes, etc.).
    """
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)

    # DP con una sola fila (O(min(len)) en memoria)
    if len(a) < len(b):
        a, b = b, a  # b siempre la más corta -> fila más chica

    fila_prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        fila_actual = [i] + [0] * len(b)
        for j, cb in enumerate(b, start=1):
            costo_sub = fila_prev[j - 1] + (ca != cb)
            costo_ins = fila_actual[j - 1] + 1
            costo_del = fila_prev[j] + 1
            fila_actual[j] = min(costo_sub, costo_ins, costo_del)
        fila_prev = fila_actual
    return fila_prev[-1]


def similitud_edicion(a: str, b: str) -> float:
    """
    Similitud normalizada en [0,1]: 1.0 = idénticos, 0.0 = totalmente distintos.
    """
    if not a and not b:
        return 1.0
    dist = distancia_levenshtein(a, b)
    largo_max = max(len(a), len(b))
    return 1.0 - (dist / largo_max) if largo_max else 1.0


def tokens_similares(a: str, b: str, umbral: float = 0.75, tolerancia_abs: int = 2) -> bool:
    """
    ¿Son 'a' y 'b' el mismo token con error de tipeo?

    Combina dos criterios (para evitar falsos positivos con palabras cortas):
    - similitud relativa >= umbral (por defecto 75%)
    - distancia absoluta <= tolerancia_abs (por defecto 2 ediciones)

    Ejemplos:
        "grcia"/"garcia" (dist=1, sim=0.83)     -> True
        "jose"/"juan"    (dist=3, sim=0.25)     -> False
        "a"/"e"          (dist=1, sim=0.0)      -> False (palabra muy corta)
    """
    if a == b:
        return True
    if len(a) < 3 or len(b) < 3:
        # Tokens muy cortos (iniciales, nexos): exigir igualdad exacta
        return False
    dist = distancia_levenshtein(a, b)
    if dist > tolerancia_abs:
        return False
    return similitud_edicion(a, b) >= umbral


# ============================================================
# 2. Alineación de listas de tokens (nombres completos)
# ============================================================

def _mejor_pareja(token: str, candidatos: List[str], usados: set) -> Optional[Tuple[str, float]]:
    """Busca en `candidatos` (no usados aún) el más parecido a `token`."""
    mejor = None
    mejor_score = 0.0
    for c in candidatos:
        if c in usados:
            continue
        if c == token:
            return (c, 1.0)  # atajo: exacto gana siempre
        score = similitud_edicion(token, c)
        if score > mejor_score:
            mejor_score = score
            mejor = c
    return (mejor, mejor_score) if mejor else None


def similitud_tokens_fuzzy(
    tokens_a: List[str],
    tokens_b: List[str],
    umbral_token: float = 0.75,
    pesos: Optional[Dict[str, float]] = None,
) -> float:
    """
    Similitud entre dos listas de tokens (nombres) tolerando typos,
    vía alineación voraz (greedy matching) token-a-token.

    Cada token de `tokens_a` se empareja con el más parecido disponible
    en `tokens_b`. Solo cuenta si supera `umbral_token`. El resultado es
    la fracción de "peso" (IDF si se provee, si no cuenta simple) que
    logró emparejarse, sobre el total de ambos lados (tipo Jaccard suave).

    Ejemplo:
        similitud_tokens_fuzzy(["maria","grcia"], ["maria","garcia"])
        -> 1.0  (ambos tokens encuentran pareja válida)
    """
    if not tokens_a and not tokens_b:
        return 1.0
    if not tokens_a or not tokens_b:
        return 0.0

    pesos = pesos or {}

    def peso(t: str) -> float:
        return pesos.get(t, 1.0)

    usados_b: set = set()
    peso_emparejado = 0.0
    for ta in tokens_a:
        pareja = _mejor_pareja(ta, tokens_b, usados_b)
        if pareja is not None:
            cand, score = pareja
            if score >= umbral_token or ta == cand:
                usados_b.add(cand)
                # Peso ponderado por qué tan buena fue la coincidencia
                peso_emparejado += peso(ta) * score

    peso_total = sum(peso(t) for t in tokens_a) + sum(peso(t) for t in tokens_b)
    if peso_total == 0:
        return 0.0
    # *2 porque contamos el emparejamiento una sola vez pero el total suma ambos lados
    return min(1.0, (2 * peso_emparejado) / peso_total)


# ============================================================
# 3. Integración con el pipeline existente (tokenizar + idf)
# ============================================================

def similitud_con_tolerancia_typos(
    nombre_a: str,
    nombre_b: str,
    tokenizar_fn,
    idf: Optional[Dict[str, float]] = None,
    umbral_token: float = 0.75,
) -> float:
    """
    Punto de entrada recomendado: usa TU `tokenizar()` real (con NFD,
    títulos, stopwords) y luego compara con tolerancia a errores de tipeo.

    Uso:
        from normalizacion import tokenizar, idf_por_token
        from similitud_fonetica import similitud_con_tolerancia_typos

        score = similitud_con_tolerancia_typos(
            "Jose Rodrigez", "Jose Rodriguez", tokenizar, idf
        )
    """
    tokens_a = tokenizar_fn(nombre_a)
    tokens_b = tokenizar_fn(nombre_b)
    return similitud_tokens_fuzzy(tokens_a, tokens_b, umbral_token=umbral_token, pesos=idf)


# ============================================================
# 4. Helper para integración en pipeline SIGSA-3 -> pacientes
# ============================================================

def _es_apellido_probable_typo(tokens_a_apellido: list, tokens_b_apellido: list) -> bool:
    """
    Tolerancia a typos aplicada SOLO al/los apellido(s), no al nombre.
    Requiere score alto (>=0.82) porque no hay otra evidencia corroborando.
    """
    score = similitud_tokens_fuzzy(tokens_a_apellido, tokens_b_apellido, umbral_token=0.8)
    return score >= 0.82


def intentar_match_por_typo(
    nombre_sigsa: str,
    candidatos_pacientes: list,   # [(pid, nombre_completo, sexo, expediente, estado), ...]
    no_historia_sigsa: str,
    sexo_sigsa: str,
    tokenizar_fn,
    pacientes_pre_tokenizados: dict = None,  # {pid: (tokens_sorted_list, nombre, sexo, expo, estado)}
):
    """
    Último recurso: se llama SOLO cuando el match exacto y el submatch por
    firma (⊆ tokens) ya fallaron. Nunca auto-asocia sin corroboración.

    Devuelve:
        (pid, motivo) si hay corroboración suficiente -> puede ir a asociaciones
        (None, ficha_revision) si es solo sospecha -> va a revision, no a match directo
        (None, None) si no hay candidatos

    Si se provee pacientes_pre_tokenizados, se usa en vez de tokenizar cada nombre.
    """
    tokens_sigsa = tokenizar_fn(nombre_sigsa)
    if len(tokens_sigsa) < 2:
        return None, None  # sin apellido claro, no arriesgar

    # Heurística simple: último token = apellido principal
    # (el tokenizar ya elimina stopwords, así que el último suele ser el apellido)
    nombre_sigsa_tokens, apellido_sigsa = tokens_sigsa[:-1], [tokens_sigsa[-1]]
    sorted_nombre_sigsa = tuple(sorted(nombre_sigsa_tokens))

    mejores = []
    if pacientes_pre_tokenizados is not None:
        # Modo batch: buscar por nombre de pila exacto primero, luego verificar typo
        # agrupar candidatos por nombre de pila (tokens sorted)
        # El pre-tokenizado tiene pid -> (tokens_sorted, nombre, sexo, expo, estado)
        for pid, (tokens_pac_tuple, nombre_pac, sexo_pac, expo_pac, estado_pac) in pacientes_pre_tokenizados.items():
            if len(tokens_pac_tuple) < 2:
                continue
            nombre_pac_tokens = list(tokens_pac_tuple[:-1])
            apellido_pac = [tokens_pac_tuple[-1]]

            # 1) El nombre de pila debe ser EXACTO (no fuzzy) -> evita Maria/Marta
            if tuple(sorted(nombre_pac_tokens)) != sorted_nombre_sigsa:
                continue

            # 2) El apellido puede tener typo
            if not _es_apellido_probable_typo(apellido_sigsa, apellido_pac):
                continue

            mejores.append((pid, nombre_pac, sexo_pac, expo_pac, estado_pac))
    else:
        for pid, nombre_pac, sexo_pac, expo_pac, estado_pac in candidatos_pacientes:
            tokens_pac = tokenizar_fn(nombre_pac)
            if len(tokens_pac) < 2:
                continue
            nombre_pac_tokens, apellido_pac = tokens_pac[:-1], [tokens_pac[-1]]

            # 1) El nombre de pila debe ser EXACTO (no fuzzy) -> evita Maria/Marta
            if sorted(nombre_pac_tokens) != sorted_nombre_sigsa:
                continue

            # 2) El apellido puede tener typo
            if not _es_apellido_probable_typo(apellido_sigsa, apellido_pac):
                continue

            mejores.append((pid, nombre_pac, sexo_pac, expo_pac, estado_pac))

    if not mejores:
        return None, None

    if len(mejores) > 1:
        # Ambiguo entre varios -> siempre a revisión, nunca autoasociar
        return None, {
            "tipo": "typo_probable_ambiguo",
            "nombre_sigsa": nombre_sigsa,
            "candidatos": [m[1] for m in mejores],
        }

    pid, nombre_pac, sexo_pac, expo_pac, _estado = mejores[0]

    # Corroboración: expediente exacto o sexo coincide -> suficiente para asociar
    hist_coincide = bool(no_historia_sigsa) and str(no_historia_sigsa).strip().lower() == str(expo_pac).strip().lower()
    sexo_coincide = bool(sexo_sigsa) and bool(sexo_pac) and sexo_sigsa == sexo_pac

    if hist_coincide or sexo_coincide:
        return pid, "typo_corroborado"

    # Sin corroboración -> a revisión humana, NO se autoasocia
    return None, {
        "tipo": "typo_sin_corroborar",
        "nombre_sigsa": nombre_sigsa,
        "nombre_paciente": nombre_pac,
        "sugerido": pid,
    }


# ============================================================
# 5. Tests básicos (ejecutar con: python -m modules.common.similitud_fonetica)
# ============================================================

if __name__ == "__main__":
    # Test distancia Levenshtein
    assert distancia_levenshtein("", "") == 0
    assert distancia_levenshtein("a", "") == 1
    assert distancia_levenshtein("", "a") == 1
    assert distancia_levenshtein("garcia", "garcia") == 0
    assert distancia_levenshtein("grcia", "garcia") == 1
    assert distancia_levenshtein("rodrigez", "rodriguez") == 1
    assert distancia_levenshtein("perez", "perez") == 0
    print("✓ distancia_levenshtein")

    # Test similitud_edicion
    assert similitud_edicion("garcia", "garcia") == 1.0
    assert abs(similitud_edicion("grcia", "garcia") - 0.8333) < 0.01
    assert abs(similitud_edicion("rodrigez", "rodriguez") - 0.8889) < 0.01
    print("✓ similitud_edicion")

    # Test tokens_similares
    assert tokens_similares("grcia", "garcia") is True
    assert tokens_similares("jose", "juan") is False
    assert tokens_similares("a", "e") is False  # muy corto
    assert tokens_similares("rodrigez", "rodriguez") is True
    print("✓ tokens_similares")

    # Test similitud_tokens_fuzzy
    score = similitud_tokens_fuzzy(["maria", "grcia"], ["maria", "garcia"])
    assert score > 0.9, f"score={score}"
    assert similitud_tokens_fuzzy(["maria", "grcia"], ["maria", "garcia"], umbral_token=0.9) < 1.0
    assert similitud_tokens_fuzzy(["maria", "garcia"], ["maria", "garcia"]) == 1.0
    assert similitud_tokens_fuzzy([], []) == 1.0
    assert similitud_tokens_fuzzy([], ["a"]) == 0.0
    print("✓ similitud_tokens_fuzzy")

    # Test integración con tokenizar real
    from modules.common.vector_similarity import tokenizar
    score = similitud_con_tolerancia_typos("Jose Rodrigez", "Jose Rodriguez", tokenizar)
    assert score > 0.9, f"score={score}"
    print("✓ similitud_con_tolerancia_typos (integración)")

    # Test intentar_match_por_typo (mock)
    candidatos = [
        (1, "María García", "F", "1001", "V"),
        (2, "María Torres", "F", "1002", "V"),
    ]
    # Caso 1: typo de apellido + expediente coincide -> debe asociar
    pid, motivo = intentar_match_por_typo("María Grcia", candidatos, "1001", "F", tokenizar)
    assert pid == 1 and motivo == "typo_corroborado", f"Caso 1 falló: {pid}, {motivo}"
    # Caso 2: typo de apellido SIN corroboración -> debe ir a revisión
    pid, motivo = intentar_match_por_typo("María Grcia", candidatos, "", "", tokenizar)
    assert pid is None and motivo and motivo.get("tipo") == "typo_sin_corroborar", f"Caso 2 falló: {pid}, {motivo}"
    # Caso 3: nombre de pila distinto (Marta vs Maria) -> nunca debe matchear
    pid, motivo = intentar_match_por_typo("Marta García", candidatos, "1001", "F", tokenizar)
    assert pid is None and motivo is None, f"Caso 3 falló (debería ser None): {pid}, {motivo}"
    print("✓ intentar_match_por_typo (lógica de integración)")

    print("\n✅ Todos los tests pasaron")