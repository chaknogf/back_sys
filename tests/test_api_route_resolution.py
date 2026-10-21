"""Pruebas de contrato para rutas estáticas y seguridad de listas nuevas."""


def test_recent_resources_resolve_before_id_routes(client, auth_headers):
    pacientes = client.get("/pacientes/ultimos?limit=1", headers=auth_headers)
    assert pacientes.status_code == 200, pacientes.text
    assert {"total", "pacientes"} <= pacientes.json().keys()

    consultas = client.get("/consultas/ultimos?limit=1", headers=auth_headers)
    assert consultas.status_code == 200, consultas.text
    assert {"total", "consultas"} <= consultas.json().keys()


def test_shared_patient_search_supports_consultation_document_filter(client, auth_headers):
    response = client.get(
        "/pacientes/buscar",
        params={"documento": "documento-no-existente", "limit": 1},
        headers=auth_headers,
    )
    assert response.status_code == 200, response.text
    assert {"total", "pacientes"} <= response.json().keys()
    assert response.json()["pacientes"] == []


def test_sensitive_routes_require_authentication():
    from main import app

    spec = app.openapi()
    deliberately_public = {
        ("get", "/health"),
        ("post", "/auth/login"),
        ("post", "/users/recuperar/solicitar"),
        ("post", "/users/recuperar/confirmar"),
        ("get", "/municipios/"),
        ("get", "/municipios/departamentos"),
        ("get", "/paises/"),
        ("get", "/paises/select"),
        ("get", "/paises/{codigo}"),
    }
    unauthenticated = {
        (method, path)
        for path, methods in spec["paths"].items()
        for method, operation in methods.items()
        if "security" not in operation
    }
    assert unauthenticated == deliberately_public


def test_duplicate_search_and_catalog_routes_are_removed_from_openapi(client, auth_headers):
    from main import app

    paths = app.openapi()["paths"]
    assert "get" not in paths["/pacientes/"]
    assert "/consultas/buscarpaciente" not in paths
    assert "/procedimientos/catalogo" not in paths
    assert "/catalogo-procedimientos/" in paths
    assert client.get("/consultas/buscarpaciente", headers=auth_headers).status_code == 404
    assert client.get("/procedimientos/catalogo", headers=auth_headers).status_code == 404
    assert client.get("/pacientes/", headers=auth_headers).status_code == 405


def test_removed_duplicate_paths_are_not_captured_as_ids(client, auth_headers):
    assert client.get("/consultas/buscarpaciente", headers=auth_headers).status_code == 404
    assert client.get("/procedimientos/catalogo", headers=auth_headers).status_code == 404
