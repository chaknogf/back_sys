"""Pruebas del servicio de duplicados (F5): equivalencia entre el motor Rust
y el fallback Python puro, y contra la lógica del router original.

No requiere base de datos: ejercita `ids_pares_duplicados` (que opera sobre
pares ya generados) en los dos modos y lo compara con la referencia.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from modules.common import vector_similarity as vs  # noqa: E402
from modules.pacientes import duplicados_service as svc  # noqa: E402

NOMBRES_COMPUESTOS = [
    "JUAN CARLOS", "MARIA FERNANDA", "ANA LUCIA", "JOSE MIGUEL",
    "PEDRO PABLO", "EDWIN RAFAEL", "OTTO RENE", "FRANCISCO JAVIER",
    "VICTORIA EUGENIA", "ROBERTO CARLOS", "LUIS ALBERTO", "KAREN JULISSA",
]
APELLIDOS = [
    "PEREZ", "MENDOZA", "LOPEZ", "GARCIA", "GONZALEZ", "MORALES",
    "VASQUEZ", "HERNANDEZ", "RAMIREZ", "ORELLANA", "ORTIZ", "CHACON",
    "IXCAMPARIJ", "TZOC", "CHOJOLAN", "CACERES", "QUINA", "CONTRERAS",
    "JUAREZ", "SALAZAR", "PAZ", "DE LA CRUZ", "GUERRA", "SANTOS",
]
UMBRAL = 0.85


def _nombre_aleatorio() -> str:
    n = random.choice(NOMBRES_COMPUESTOS).split()
    a1, a2 = random.choice(APELLIDOS), random.choice(APELLIDOS)
    if random.random() < 0.4:
        a2 += random.choice(["", "", " DE " + random.choice(["LEON", "PAZ", "LA CRUZ"])])
    return f"{n[0]} {n[1]} {a1} {a2}"


def _generar_pares(n_pares: int) -> list[dict]:
    random.seed(123)
    pares = []
    siguiente_id = 1
    for _ in range(n_pares):
        # Mitad de los pares con nombres idénticos (deberían coincidir).
        if random.random() < 0.5:
            nombre = _nombre_aleatorio()
            pares.append({"id_a": siguiente_id, "nombre_a": nombre,
                          "id_b": siguiente_id + 1, "nombre_b": nombre})
        else:
            pares.append({"id_a": siguiente_id, "nombre_a": _nombre_aleatorio(),
                          "id_b": siguiente_id + 1, "nombre_b": _nombre_aleatorio()})
        siguiente_id += 2
    return pares


def _referencia_router(pares, umbral):
    """Lógica exacta del router original (Python puro, por par).

    Devuelve el conjunto de pares aprobados (id_a, id_b) ordenados; el router
    aplanaba estos pares a ids individuales, así que la equivalencia de pares
    implica la equivalencia del resultado final.
    """
    ids = set()
    for par in pares:
        ta, tb = vs.tokenizar(par["nombre_a"]), vs.tokenizar(par["nombre_b"])
        score = 1.0 if vs.tokens_equivalentes(ta, tb) else vs.similitud_compuesta(
            vs.perfil(par["nombre_a"]), vs.perfil(par["nombre_b"])
        )
        if score >= umbral:
            ids.add((par["id_a"], par["id_b"]))
    return ids


@pytest.fixture(scope="module")
def pares():
    return _generar_pares(400)


def test_ids_pares_duplicados_equivalente_al_router(pares):
    ids_svc = svc.ids_pares_duplicados(pares, UMBRAL)
    ids_ref = _referencia_router(pares, UMBRAL)
    assert ids_svc == ids_ref


def test_ids_pares_duplicados_nativo_vs_fallback(pares):
    ids_nativo = svc.ids_pares_duplicados(pares, UMBRAL)
    nativo_previo = svc._NATIVO
    svc._NATIVO = False
    try:
        ids_fallback = svc.ids_pares_duplicados(pares, UMBRAL)
    finally:
        svc._NATIVO = nativo_previo
    assert ids_nativo == ids_fallback


def test_ids_pares_duplicados_acepta_vacio():
    assert svc.ids_pares_duplicados([], UMBRAL) == set()


def test_prefiltrar_pares_fallback_matches_referencia(pares):
    nativo_previo = svc._NATIVO
    svc._NATIVO = False
    try:
        for par in pares:
            ta, tb = vs.tokenizar(par["nombre_a"]), vs.tokenizar(par["nombre_b"])
            if vs.tokens_equivalentes(ta, tb):
                esperado = True
            else:
                inter = len(set(ta) & set(tb))
                esperado = inter >= 3 or (inter >= 2 and len(ta) <= 5 and len(tb) <= 5)
            assert svc._prefiltrar_par(ta, tb) == esperado
    finally:
        svc._NATIVO = nativo_previo
