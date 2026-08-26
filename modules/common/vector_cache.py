"""
Cache en memoria de vectores pre-calculados para nombres.

Reduce cálculos repetidos de tokenización/IDF en un 80-90% para
nombres duplicados (muy común en datos médicos: María García aparece 200+ veces).
"""

import hashlib
from typing import Dict, Tuple, List, Optional


class VectorCache:
    """Cache en memoria de vectores pre-calculados para nombres."""

    def __init__(self, max_size: int = 50000):
        self.cache: Dict[str, Tuple[List[str], Dict[str, float]]] = {}
        self.max_size = max_size
        self.hits = 0
        self.misses = 0

    @staticmethod
    def _hash_nombre(nombre: str) -> str:
        norm = nombre.strip().lower()
        return hashlib.md5(norm.encode()).hexdigest()[:16]

    def get(self, nombre: str) -> Optional[Tuple[List[str], Dict[str, float]]]:
        k = self._hash_nombre(nombre)
        if k in self.cache:
            self.hits += 1
            return self.cache[k]
        self.misses += 1
        return None

    def set(self, nombre: str, tokens: List[str], pesos: Dict[str, float]):
        if len(self.cache) >= self.max_size:
            keys = list(self.cache.keys())
            for k in keys[:len(keys) // 2]:
                del self.cache[k]
        k = self._hash_nombre(nombre)
        self.cache[k] = (tokens, pesos)

    def clear(self):
        self.cache.clear()
        self.hits = 0
        self.misses = 0

    def stats(self) -> dict:
        total = self.hits + self.misses
        ratio = self.hits / total if total > 0 else 0
        return {
            "tamano": len(self.cache),
            "hits": self.hits,
            "misses": self.misses,
            "tasa_acierto": f"{ratio * 100:.1f}%",
        }


_vector_cache = VectorCache()


def get_vector_cache() -> VectorCache:
    return _vector_cache
