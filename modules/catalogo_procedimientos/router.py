"""Router FastAPI para el catálogo maestro y áreas del cuerpo."""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_user, get_current_admin_user
from modules.users.models import UserModel
from modules.catalogo_procedimientos import schemas, service


# Router 1: catálogo de procedimientos (prefijo dedicado)
router = APIRouter(
    prefix="/catalogo-procedimientos",
    tags=["Catálogo de Procedimientos"],
)


@router.get("/", response_model=schemas.CatalogoProcedimientoListResponse)
def listar(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
    q: Optional[str] = Query(None),
    especialidad_ref: Optional[int] = Query(None),
    activo: Optional[bool] = Query(True),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
):
    return service.listar_catalogo(db, q, especialidad_ref, activo, skip, limit)


@router.get("/{cat_id}", response_model=schemas.CatalogoProcedimientoOut)
def detalle(
    cat_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return service.obtener_catalogo(cat_id, db)


@router.post("/", response_model=schemas.CatalogoProcedimientoOut, status_code=201)
def crear(
    data: schemas.CatalogoProcedimientoCreate,
    db: Session = Depends(get_db),
    # current_user: UserModel = Depends(get_current_admin_user),
):
    return service.crear_catalogo(data, db)


@router.patch("/{cat_id}", response_model=schemas.CatalogoProcedimientoOut)
def actualizar(
    cat_id: int,
    data: schemas.CatalogoProcedimientoUpdate,
    db: Session = Depends(get_db),
    # current_user: UserModel = Depends(get_current_admin_user),
):
    return service.actualizar_catalogo(cat_id, data, db)


@router.delete("/{cat_id}")
def eliminar(
    cat_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user),
):
    return service.eliminar_catalogo(cat_id, db)


# Router 2: áreas del cuerpo (prefijo separado)
router_areas = APIRouter(
    prefix="/areas-cuerpo",
    tags=["Áreas del Cuerpo Intervenidas"],
)


@router_areas.get("/", response_model=schemas.AreaCuerpoListResponse)
def listar_areas(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
    activo: Optional[bool] = Query(True),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    return service.listar_areas(db, activo, skip, limit)


@router_areas.get("/{area_id}", response_model=schemas.AreaCuerpoOut)
def detalle_area(
    area_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return service.obtener_area(area_id, db)


@router_areas.post("/", response_model=schemas.AreaCuerpoOut, status_code=201)
def crear_area(
    data: schemas.AreaCuerpoCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user),
):
    return service.crear_area(data, db)


@router_areas.patch("/{area_id}", response_model=schemas.AreaCuerpoOut)
def actualizar_area(
    area_id: int,
    data: schemas.AreaCuerpoUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user),
):
    return service.actualizar_area(area_id, data, db)


@router_areas.delete("/{area_id}")
def eliminar_area(
    area_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user),
):
    return service.eliminar_area(area_id, db)
