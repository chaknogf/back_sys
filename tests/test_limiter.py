"""Tests del rate limiter compartido (Fase 1 escalabilidad)."""

import core.limiter as limiter_mod


class _FakeRequest:
    def __init__(self, xff=None, host="10.0.0.1"):
        self.headers = {"x-forwarded-for": xff} if xff else {}
        self.client = type("C", (), {"host": host})()


class TestKeyFunc:
    def test_usa_x_forwarded_for(self):
        req = _FakeRequest(xff="203.0.113.5, 10.0.0.1")
        assert limiter_mod._client_ip(req) == "203.0.113.5"

    def test_fallback_a_host(self):
        req = _FakeRequest(host="198.51.100.9")
        assert limiter_mod._client_ip(req) == "198.51.100.9"

    def test_sin_cliente(self):
        class _SinClient:
            headers = {}
            client = None

        assert limiter_mod._client_ip(_SinClient()) == "unknown"


class TestBuildLimiter:
    def test_degrada_a_memoria_sin_redis(self, monkeypatch):
        monkeypatch.setattr(limiter_mod, "REDIS_URL", "")
        lim = limiter_mod._build_limiter()
        assert lim is not None

    def test_usa_redis_cuando_disponible(self, monkeypatch):
        monkeypatch.setattr(limiter_mod, "REDIS_URL", "redis://fake:6379/0")
        monkeypatch.setattr(limiter_mod, "_redis_disponible", lambda: True)
        lim = limiter_mod._build_limiter()
        assert lim is not None
