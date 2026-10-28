"""Algoritmo de asociación SIGSA-3 → paciente (función pura, sin acceso a BD).

Separa la decisión de la persistencia: recibe registros y pacientes ya
cargados y devuelve una `Decision`. La escritura queda a cargo de
`asociacion_servicio`.

Etapas:
1. Identificador: NHC normalizado igual al expediente de pacientes existentes.
   - Un único paciente con nombre compatible → `exacto_verificado` / `auto_alta`.
   - Varios pacientes con nombre idéntico → `auto_duplicado` (el de pac_id menor).
   - Parentesco o sexo contradictorio → `conflicto_identificador`.
2. Nombre: candidatos por bloqueo de tokens y por firma exacta de tokens,
   puntuados con `similitud_compuesta` (TF-IDF coseno + Jaccard).
3. Evidencia: sexo contradictorio resta 0.25; parentesco distinto excluye.
4. Decisión:
   - score ≥ 0.90 y margen ≥ 0.10 → `auto_alta` (o `exacto_verificado`).
   - nombres idénticos empatados → `auto_duplicado`.
   - score 0.75–0.90 → `revision`; margen insuficiente → `ambiguo`.
   - sin ningún candidato parecido (máx. similitud < 0.50) y datos mínimos
     presentes → `crear_paciente`.
   - resto → `sin_candidato` o `revision`, sin escritura.

Los umbrales son valores iniciales. No están calibrados con datos reales
etiquetados; ver docs/algoritmo_asociacion.md.
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence

from modules.common.vector_similarity import (
    idf_por_token,
    pesado_por_idf,
    similitud_compuesta,
    tokenizar,
    tokens_equivalentes,
)

VERSION = "asoc-v2"

# Umbrales iniciales (a calibrar).
UMBRAL_AUTO = 0.90
MARGEN_MIN = 0.10
UMBRAL_REVISION = 0.75
UMBRAL_SIMILITUD_CREAR = 0.50  # por debajo de esto no hay nadie parecido → se puede crear
CASTIGO_SEXO_CONFLICTO = 0.25
# Tokens que aparecen en más pacientes que esto no sirven para bloquear.
LIMITE_TOKEN_COMUN = 2000

MARCAS_PARENTESCO = ("HO", "H", "HIJO", "HIJA", "RN", "NB", "RECIEN")

# Estados finales.
EXACTO = "exacto_verificado"
AUTO = "auto_alta"
AUTO_DUPLICADO = "auto_duplicado"
CREAR = "crear_paciente"
REVISION = "revision"
AMBIGUO = "ambiguo"
CONFLICTO = "conflicto_identificador"
SIN_CANDIDATO = "sin_candidato"

# Estados que asocian a un paciente existente o recién creado.
ESTADOS_ASOCIAN = frozenset({EXACTO, AUTO, AUTO_DUPLICADO, CREAR})


@dataclass(frozen=True)
class Paciente:
    pac_id: int
    nombre: str
    sexo: str = ""
    expediente: str = ""  # ya normalizado con normalizar_identificador
    creado: bool = False  # True si vive en pacientes_sigsa3


@dataclass(frozen=True)
class Registro:
    rid: int
    nombre: str
    sexo: str = ""
    nhc: str = ""  # ya normalizado con normalizar_identificador


@dataclass
class Decision:
    estado: str
    paciente_id: Optional[int] = None
    score: float = 0.0
    margen: float = 0.0
    metodo: str = ""
    candidatos: List[dict] = field(default_factory=list)
    motivo: str = ""
    version: str = VERSION


def normalizar_identificador(valor: Optional[str]) -> str:
    """NHC/expediente: solo dígitos, sin ceros a la izquierda. Vacío si no es válido."""
    if valor is None:
        return ""
    digitos = re.sub(r"\D", "", str(valor)).lstrip("0")
    return digitos if len(digitos) >= 3 else ""


def normalizar_sexo(valor: Optional[str]) -> str:
    if not isinstance(valor, str):
        return ""
    v = valor.strip().upper()
    return v if v in ("M", "F") else ""


def es_parentesco(nombre: str) -> bool:
    """True si el nombre lleva marca de parentesco (madre vs. recién nacido, etc.)."""
    texto = nombre.strip().upper()
    if texto.startswith(("HIJO", "HIJA", "HO/", "H/", "R.N", "RN ", "RN-")):
        return True
    return any(t.upper() in MARCAS_PARENTESCO for t in re.split(r"[^A-Za-z]+", nombre) if t)


class IndicePacientes:
    """Índice de bloqueo. Se puede ampliar con `agregar` durante una corrida."""

    def __init__(self, pacientes: Sequence[Paciente]):
        self.pacientes: List[Paciente] = []
        self.tokens: List[List[str]] = []
        self.pesos: List[Dict[str, float]] = []
        self.por_token: Dict[str, List[int]] = defaultdict(list)
        self.por_nhc: Dict[str, List[int]] = defaultdict(list)
        self.por_firma: Dict[tuple, List[int]] = defaultdict(list)
        # IDF fijo calculado con los pacientes iniciales. Los creados en la
        # corrida usan el mismo IDF (diferencia despreciable frente al corpus).
        self.idf = idf_por_token([tokenizar(p.nombre) for p in pacientes])
        for p in pacientes:
            self.agregar(p)

    def agregar(self, p: Paciente) -> int:
        i = len(self.pacientes)
        toks = tokenizar(p.nombre)
        self.pacientes.append(p)
        self.tokens.append(toks)
        self.pesos.append(pesado_por_idf(toks, self.idf))
        for t in set(toks):
            self.por_token[t].append(i)
        if p.expediente:
            self.por_nhc[p.expediente].append(i)
        self.por_firma[tuple(sorted(toks))].append(i)
        return i

    def candidatos(self, tokens: Iterable[str]) -> List[int]:
        """Pacientes con al menos un token no muy común, más los de firma idéntica."""
        vistos = set(self.por_firma.get(tuple(sorted(tokens)), []))
        for t in set(tokens):
            lista = self.por_token.get(t, [])
            if 0 < len(lista) <= LIMITE_TOKEN_COMUN:
                vistos.update(lista)
        return sorted(vistos)


def _ajustar(score: float, registro: Registro, paciente: Paciente) -> float:
    """Ajuste por evidencia. Un dato faltante no suma ni resta."""
    if registro.sexo and paciente.sexo and registro.sexo != paciente.sexo:
        score -= CASTIGO_SEXO_CONFLICTO
    return max(0.0, min(1.0, score))


def datos_minimos_para_crear(registro: Registro) -> Optional[str]:
    """None si el registro tiene datos suficientes para crear un paciente; si no, el motivo."""
    if len(tokenizar(registro.nombre)) < 2:
        return "nombre_incompleto"
    if not registro.sexo:
        return "sexo_faltante"
    if es_parentesco(registro.nombre):
        return "parentesco_no_creable"
    return None


def asociar(registro: Registro, indice: IndicePacientes) -> Decision:
    """Decide la asociación de un registro SIGSA-3. Función pura (no modifica el índice)."""
    tokens = tokenizar(registro.nombre)
    if len(tokens) < 2:
        return Decision(SIN_CANDIDATO, motivo="nombre_insuficiente")

    # Etapa 1: identificador.
    if registro.nhc:
        por_id = indice.por_nhc.get(registro.nhc, [])
        if len(por_id) > 1:
            if all(tokens_equivalentes(tokens, indice.tokens[i]) for i in por_id):
                elegido = min(por_id, key=lambda i: indice.pacientes[i].pac_id)
                return Decision(
                    AUTO_DUPLICADO, paciente_id=indice.pacientes[elegido].pac_id,
                    score=1.0, metodo="identificador_duplicado_identico",
                    motivo="duplicados_mismo_nombre_y_nhc",
                    candidatos=[_resumen(indice.pacientes[i]) for i in por_id],
                )
            return Decision(
                AMBIGUO, motivo="identificador_compartido",
                candidatos=[_resumen(indice.pacientes[i]) for i in por_id],
            )
        if len(por_id) == 1:
            i = por_id[0]
            p = indice.pacientes[i]
            sim = similitud_compuesta(pesado_por_idf(tokens, indice.idf), indice.pesos[i])
            if es_parentesco(registro.nombre) != es_parentesco(p.nombre):
                return Decision(CONFLICTO, motivo="parentesco_distinto", candidatos=[_resumen(p)])
            if registro.sexo and p.sexo and registro.sexo != p.sexo:
                return Decision(CONFLICTO, motivo="sexo_distinto_con_identificador",
                                candidatos=[_resumen(p)])
            if tokens_equivalentes(tokens, indice.tokens[i]):
                return Decision(EXACTO, paciente_id=p.pac_id, score=1.0,
                                metodo="identificador+nombre_exacto")
            if sim >= UMBRAL_REVISION:
                return Decision(AUTO if sim >= UMBRAL_AUTO else REVISION,
                                paciente_id=p.pac_id if sim >= UMBRAL_AUTO else None,
                                score=round(sim, 4),
                                metodo="identificador+nombre_similar",
                                candidatos=[_resumen(p)])
            return Decision(CONFLICTO, motivo="nombre_incompatible_con_identificador",
                            candidatos=[_resumen(p)])

    # Etapas 2 y 3: candidatos por nombre y ajuste por evidencia.
    pesos_q = pesado_por_idf(tokens, indice.idf)
    es_kin = es_parentesco(registro.nombre)
    max_base = 0.0
    puntuados = []
    for i in indice.candidatos(tokens):
        p = indice.pacientes[i]
        if es_kin != es_parentesco(p.nombre):
            continue
        base = similitud_compuesta(pesos_q, indice.pesos[i])
        max_base = max(max_base, base)
        if base < UMBRAL_REVISION:
            continue
        puntuados.append((_ajustar(base, registro, p), i))

    if not puntuados:
        # Diferencial: crear solo si nadie se parece; si hay parecidos moderados, revisión.
        if max_base >= UMBRAL_SIMILITUD_CREAR:
            return Decision(REVISION, score=round(max_base, 4), motivo="parecido_moderado_sin_asociar")
        faltante = datos_minimos_para_crear(registro)
        if faltante is None:
            return Decision(CREAR, metodo="sin_candidato_datos_minimos",
                            motivo="paciente_nuevo", score=round(max_base, 4))
        return Decision(SIN_CANDIDATO, motivo=f"sin_candidato_{faltante}", score=round(max_base, 4))

    puntuados.sort(key=lambda x: (-x[0], indice.pacientes[x[1]].pac_id))
    mejor_score, mi = puntuados[0]
    segundo = puntuados[1][0] if len(puntuados) > 1 else 0.0
    margen = round(mejor_score - segundo, 4)
    mejor = indice.pacientes[mi]
    resumen = [_resumen(indice.pacientes[i]) for _, i in puntuados[:5]]

    if margen < MARGEN_MIN:
        empatados = [i for s, i in puntuados if s >= mejor_score - 1e-9]
        if all(tokens_equivalentes(tokens, indice.tokens[i]) for i in empatados):
            elegido = min(empatados, key=lambda i: indice.pacientes[i].pac_id)
            return Decision(
                AUTO_DUPLICADO, paciente_id=indice.pacientes[elegido].pac_id,
                score=round(mejor_score, 4), margen=margen,
                metodo="nombre_duplicado_identico", motivo="duplicados_mismo_nombre",
                candidatos=resumen,
            )
        return Decision(AMBIGUO, score=round(mejor_score, 4), margen=margen,
                        motivo="margen_insuficiente", candidatos=resumen)

    if mejor_score >= UMBRAL_AUTO:
        exacto = tokens_equivalentes(tokens, indice.tokens[mi])
        return Decision(
            EXACTO if exacto else AUTO, paciente_id=mejor.pac_id,
            score=round(mejor_score, 4), margen=margen,
            metodo="nombre_exacto" if exacto else "nombre_similar",
            candidatos=resumen,
        )

    return Decision(REVISION, score=round(mejor_score, 4), margen=margen,
                    motivo="score_zona_gris", candidatos=resumen)


def _resumen(p: Paciente) -> dict:
    return {"pac_id": p.pac_id, "nombre": p.nombre, "sexo": p.sexo, "expediente": p.expediente}


# ── Asociación de consulta (función pura) ───────────────────────────────────

from datetime import date as _date  # noqa: E402


@dataclass(frozen=True)
class ConsultaRef:
    consulta_id: int
    paciente_id: int
    fecha: _date
    tipo: Optional[int]  # 1 primera, 2 reconsulta, 3 emergencia (catálogo de consultas)
    documento: str = ""  # ya normalizado con normalizar_identificador


_TIPO_SIGSA3 = {"1": 1, "2": 2, "3": 3}  # "4 Interconsulta" no tiene equivalente en consultas


def tipo_sigsa3_a_codigo(texto: Optional[str]) -> Optional[int]:
    if not isinstance(texto, str) or not texto.strip():
        return None
    return _TIPO_SIGSA3.get(texto.strip()[0])


def asociar_consulta(fecha: Optional[_date], tipo_sigsa3: Optional[str], nhc: str,
                     consultas: Sequence[ConsultaRef]) -> tuple[Optional[int], str]:
    """Elige la consulta del paciente que corresponde al registro SIGSA-3.

    Reglas, en orden:
    1. Sin fecha en SIGSA-3 → no se asocia.
    2. Candidatas: consultas del paciente con la misma fecha; si no hay ninguna,
       con fecha ±1 día.
    3. El documento de la consulta igual al NHC del registro es evidencia fuerte
       y, si es único, decide.
    4. Si no, se filtra por tipo (solo cuando el tipo de SIGSA-3 tiene equivalente).
    5. Única candidata → asociada. Varias → ambigua (no se asocia). Ninguna → sin consulta.
    """
    if fecha is None:
        return None, "sin_fecha"
    exactas = [c for c in consultas if c.fecha == fecha]
    cercanas = exactas or [c for c in consultas if abs((c.fecha - fecha).days) <= 1]
    if not cercanas:
        return None, "sin_consulta_en_fecha"

    if nhc:
        por_doc = [c for c in cercanas if c.documento and c.documento == nhc]
        if len(por_doc) == 1:
            return por_doc[0].consulta_id, "documento_y_fecha"

    tipo = tipo_sigsa3_a_codigo(tipo_sigsa3)
    if tipo is not None:
        por_tipo = [c for c in cercanas if c.tipo == tipo]
        if por_tipo:
            cercanas = por_tipo

    if len(cercanas) == 1:
        return cercanas[0].consulta_id, "fecha_tipo" if exactas else "fecha_cercana"
    return None, "ambigua_misma_fecha"
