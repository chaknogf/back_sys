"""Un procedimiento del catálogo puede habilitarse para varias especialidades.

Cubre `/catalogo-procedimientos/`: creación con lista, actualización que
reemplaza la lista, y filtro por especialidad apoyado en la relación N:M
(`catalogo_procedimientos_especialidades`).
"""

import uuid

import pytest

from modules.catalogo_procedimientos.models import CatalogoProcedimiento
from modules.procedimientos.models import CatalogoProcedimientoEspecialidad
from modules.especialidades.models import EspecialidadModel

PREFIJO = "TEST_MULTI_"


@pytest.fixture()
def dos_especialidades(db_session):
    esp = (
        db_session.query(EspecialidadModel)
        .filter(EspecialidadModel.estado.is_(True))
        .order_by(EspecialidadModel.id)
        .limit(2)
        .all()
    )
    if len(esp) < 2:
        pytest.skip("Se necesitan al menos 2 especialidades activas")
    return esp


@pytest.fixture(autouse=True)
def _limpiar(db_session):
    yield
    regs = (
        db_session.query(CatalogoProcedimiento)
        .filter(CatalogoProcedimiento.nombre.like(f"{PREFIJO}%"))
        .all()
    )
    for r in regs:
        db_session.query(CatalogoProcedimientoEspecialidad).filter(
            CatalogoProcedimientoEspecialidad.id_catalogo_procedimiento == r.id
        ).delete(synchronize_session=False)
        db_session.delete(r)
    db_session.commit()


def _crear(client, auth_headers, nombre, especialidades_ids=None):
    body = {"nombre": nombre, "activo": True}
    if especialidades_ids is not None:
        body["especialidades_ids"] = especialidades_ids
    r = client.post("/catalogo-procedimientos/", json=body, headers=auth_headers)
    assert r.status_code == 201, r.text
    return r.json()


def test_crear_con_varias_especialidades(client, auth_headers, dos_especialidades):
    ids = [e.id for e in dos_especialidades]
    data = _crear(client, auth_headers, f"{PREFIJO}{uuid.uuid4().hex[:8]}", ids)
    assert sorted(data["especialidades_ids"]) == sorted(ids)
    assert data["especialidad_ref"] == ids[0]


def test_actualizar_reemplaza_especialidades(client, auth_headers, dos_especialidades):
    ids = [e.id for e in dos_especialidades]
    creado = _crear(client, auth_headers, f"{PREFIJO}{uuid.uuid4().hex[:8]}", ids)

    r = client.patch(
        f"/catalogo-procedimientos/{creado['id']}",
        json={"especialidades_ids": [ids[1]]},
        headers=auth_headers,
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["especialidades_ids"] == [ids[1]]
    assert data["especialidad_ref"] == ids[1]


def test_filtro_por_especialidad_usa_relacion_n_m(client, auth_headers, dos_especialidades):
    ids = [e.id for e in dos_especialidades]
    creado = _crear(client, auth_headers, f"{PREFIJO}{uuid.uuid4().hex[:8]}", ids)

    r = client.get(
        "/catalogo-procedimientos/",
        params={"especialidad_ref": ids[1], "limit": 500},
        headers=auth_headers,
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert "total" in data and "items" in data
    encontrados = [c for c in data["items"] if c["id"] == creado["id"]]
    assert encontrados, "debe aparecer por su segunda especialidad"
    assert ids[1] in encontrados[0]["especialidades_ids"]


def test_crear_sin_especialidades_deja_lista_vacia(client, auth_headers):
    data = _crear(client, auth_headers, f"{PREFIJO}{uuid.uuid4().hex[:8]}")
    assert data["especialidades_ids"] == []
    assert data["especialidad_ref"] is None
