from __future__ import annotations

import math
import re
import unicodedata
from typing import Dict, Iterable, List, Optional

TITULOS = {
    "dr": "doctor",
    "dra": "doctor",
    "doctor": "doctor",
    "doctora": "doctor",
    "doc": "doctor",
    "md": "medico",
    "medico": "medico",
    "lic": "licenciado",
    "licdo": "licenciado",
    "licda": "licenciado",
    "licenciado": "licenciado",
    "licenciada": "licenciado",
    "ing": "ingeniero",
    "inga": "ingeniero",
    "ingeniero": "ingeniero",
    "ingeniera": "ingeniero",
    "tec": "tecnico",
    "tecnico": "tecnico",
    "tecnica": "tecnico",
    "enfermero": "enfermero",
    "enfermera": "enfermero",
    "obstetra": "obstetra",
    "obstetriz": "obstetra",
    "auxiliar": "auxiliar",
    "residente": "residente",
}

STOPWORDS = {
    "de", "del", "la", "el", "los", "las", "y", "e", "o", "u", "a", "al",
    "en", "un", "una", "unos", "unas", "con", "por", "para", "su", "sus",
    "mi", "mis", "san", "don", "hospital", "centro", "clinica", "unidad",
}

# Títulos/cargos: no son características discriminantes de identidad.
_TITULOS_CANONICOS = set(TITULOS.values())

UMBRAL_EXACTO = 1.0 - 1e-9
CONFIANZA_ALTA = 0.90
CONFIANZA_MEDIA = 0.75


def normalizar_texto(texto: Optional[str]) -> str:
    """Normaliza case y acentos, conservando letras/dígitos/espacios."""
    if texto is None:
        return ""
    t = texto.strip().lower()
    t = unicodedata.normalize("NFD", t)
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    t = re.sub(r"[^a-z0-9 ]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def token_normalizado(token: str) -> str:
    token = token.strip().lower()
    token = unicodedata.normalize("NFD", token)
    token = "".join(c for c in token if unicodedata.category(c) != "Mn")
    token = re.sub(r"[^a-z0-9]", "", token)
    if not token:
        return ""
    return TITULOS.get(token, token)


def tokenizar(texto: Optional[str]) -> List[str]:
    if not texto:
        return []
    out: List[str] = []
    for parte in re.split(r"[^a-z0-9]+", normalizar_texto(texto)):
        t = token_normalizado(parte)
        if t and t not in STOPWORDS and t not in _TITULOS_CANONICOS:
            out.append(t)
    return out


def vector_frecuencias(tokens: Iterable[str]) -> Dict[str, int]:
    frec: Dict[str, int] = {}
    for t in tokens:
        frec[t] = frec.get(t, 0) + 1
    return frec


def idf_por_token(corpus: Iterable[List[str]]) -> Dict[str, float]:
    """TF-IDF inverso calculado sobre un corpus de listas de tokens."""
    n_docs = 0
    conteo_docs: Dict[str, int] = {}
    for tokens in corpus:
        n_docs += 1
        for t in set(tokens):
            conteo_docs[t] = conteo_docs.get(t, 0) + 1
    if n_docs == 0:
        return {}
    return {t: math.log((1 + n_docs) / (1 + cf)) + 1.0 for t, cf in conteo_docs.items()}


def pesado_por_idf(tokens: Iterable[str], idf: Optional[Dict[str, float]] = None) -> Dict[str, float]:
    idf = idf or {}
    pesos: Dict[str, float] = {}
    for t, f in vector_frecuencias(tokens).items():
        pesos[t] = f * idf.get(t, 1.0)
    return pesos


def _norma(v: Dict[str, float]) -> float:
    return math.sqrt(sum(w * w for w in v.values()))


def coseno(a: Dict[str, float], b: Dict[str, float]) -> float:
    if not a or not b:
        return 0.0
    na, nb = _norma(a), _norma(b)
    if na == 0 or nb == 0:
        return 0.0
    producto = 0.0
    for t, w in a.items():
        if t in b:
            producto += w * b[t]
    return producto / (na * nb)


def jaccard(a: Dict[str, float], b: Dict[str, float]) -> float:
    ca, cb = set(a), set(b)
    if not ca and not cb:
        return 1.0
    u = ca | cb
    return len(ca & cb) / len(u) if u else 0.0


def tokens_identicos(a: List[str], b: List[str]) -> bool:
    return sorted(a) == sorted(b)


def tokens_equivalentes(a: List[str], b: List[str]) -> bool:
    """Dos textos son 'exactos' cuando sus conjuntos normalizados de tokens
    (multi-conjunto) coinciden, absorbiendo títulos/sinónimos y stopwords."""
    return sorted(a) == sorted(b)


def mejor_candidato_confianza(score: float, exacto: bool) -> float:
    return confianza_desde_score(score, exacto)


def similitud_compuesta(a: Dict[str, float], b: Dict[str, float], peso_cos: float = 0.7, peso_jaccard: float = 0.3) -> float:
    if peso_cos == 0 and peso_jaccard == 0:
        return 0.0
    return peso_cos * coseno(a, b) + peso_jaccard * jaccard(a, b)


def confianza_desde_score(score: float, exacto: bool) -> float:
    """Índice de confianza (0..1). Un match 'exacto' normalizado vale 1.0;
    en caso contrario, la confianza acompaña a la similitud calculada."""
    if exacto or score >= UMBRAL_EXACTO:
        return 1.0
    return round(score, 4)


def nivel_para(confianza: float) -> str:
    if confianza >= UMBRAL_EXACTO:
        return "exacto"
    if confianza >= CONFIANZA_ALTA:
        return "similitud_alta"
    if confianza >= CONFIANZA_MEDIA:
        return "similitud_media"
    return "baja"

def perfil(texto: Optional[str], idf: Optional[Dict[str, float]] = None) -> Dict[str, float]:
    return pesado_por_idf(tokenizar(texto), idf)


def mejor_candidato(
    texto: str,
    candidatos: List[str],
    idf: Optional[Dict[str, float]] = None,
    umbral: float = CONFIANZA_MEDIA,
    margen_minimo: float = 0.0,
) -> Optional[Dict]:
    """Encuentra el mejor candidato por similitud vectorial.

    Devuelve dict {candidato, score, confianza, nivel, tokens, exacto}
    o None si ninguno supera el umbral. NO decide por el usuario si la
    similitud es suficiente para una relación real: siempre expone confianza.
    """
    q_tokens = tokenizar(texto)
    if not q_tokens:
        return None
    q_pesos = pesado_por_idf(q_tokens, idf)

    mejor: Optional[str] = None
    mejor_score = -1.0
    mejor_exacto = False
    segundo_score = -1.0

    for cand in candidatos:
        c_tokens = tokenizar(cand)
        if not c_tokens:
            continue
        c_pesos = pesado_por_idf(c_tokens, idf)
        exacto = tokens_equivalentes(q_tokens, c_tokens)
        score = 1.0 if exacto else similitud_compuesta(q_pesos, c_pesos)
        if score > mejor_score:
            segundo_score = mejor_score
            mejor_score = score
            mejor = cand
            mejor_exacto = exacto
        elif score > segundo_score:
            segundo_score = score

    if mejor is None:
        return None

    score_efectivo = 1.0 if mejor_exacto else mejor_score
    if mejor_exacto:
        confianza = 1.0
    elif score_efectivo < umbral:  # no supera el umbral de confianza
        return None
    else:
        confianza = mejor_candidato_confianza(score_efectivo, exacto=mejor_exacto)

    margen = score_efectivo - max(segundo_score, 0.0)
    if margen < margen_minimo:
        return None

    return {
        "candidato": mejor,
        "score": round(score_efectivo, 4),
        "confianza": confianza,
        "nivel": nivel_para(confianza),
        "exacto": mejor_exacto,
        "segundo_score": round(max(segundo_score, 0.0), 4),
        "margen": round(margen, 4),
    }
