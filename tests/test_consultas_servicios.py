"""Pestañas por servicio de /consultas: /consultas/servicios y filtro excluir_estados."""

ESTADOS_SALIDA = "egreso,archivo,referido,fallecido,recepcion"


def test_servicios_por_tipo_devuelve_conteos(client, auth_headers):
    r = client.get(
        "/consultas/servicios",
        params={"tipo_consulta": 2, "excluir_estados": ESTADOS_SALIDA},
        headers=auth_headers,
    )
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert data, "debería haber al menos un servicio de tipo 2"
    for row in data:
        assert set(row.keys()) == {"servicio", "total"}
        assert row["total"] > 0


def test_servicios_por_tipo_excluye_estados_de_salida(client, auth_headers):
    sin_excluir = client.get(
        "/consultas/servicios",
        params={"tipo_consulta": 2},
        headers=auth_headers,
    ).json()
    con_excluir = client.get(
        "/consultas/servicios",
        params={"tipo_consulta": 2, "excluir_estados": ESTADOS_SALIDA},
        headers=auth_headers,
    ).json()

    total_sin = sum(r["total"] for r in sin_excluir)
    total_con = sum(r["total"] for r in con_excluir)
    assert total_con <= total_sin


def test_excluir_estados_no_devuelve_consultas_egresadas(client, auth_headers):
    r = client.get(
        "/consultas/",
        params={
            "tipo_consulta": 2,
            "archivo": False,
            "excluir_estados": ESTADOS_SALIDA,
            "limit": 50,
        },
        headers=auth_headers,
    )
    assert r.status_code == 200
    estados = {c.get("ultimo_estado") for c in r.json()["consultas"]}
    assert not (estados & {"egreso", "archivo", "referido", "fallecido", "recepcion"})


def test_filtro_servicio_devuelve_solo_ese_servicio(client, auth_headers):
    r = client.get(
        "/consultas/",
        params={
            "tipo_consulta": 2,
            "servicio": "NEON",
            "archivo": False,
            "excluir_estados": ESTADOS_SALIDA,
            "limit": 20,
        },
        headers=auth_headers,
    )
    assert r.status_code == 200
    for c in r.json()["consultas"]:
        assert c.get("servicio") == "NEON"


def test_servicios_sin_tipo_consulta(client, auth_headers):
    r = client.get("/consultas/servicios", headers=auth_headers)
    assert r.status_code == 200
    assert isinstance(r.json(), list)
