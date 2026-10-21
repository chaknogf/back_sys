"""Catálogo de insumos y presentaciones + importación desde CSV (espejo Excel)."""

from typing import Optional

from fastapi import APIRouter, Depends, Query, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import get_current_user, get_current_admin_user
from core.uploads import read_upload_limited
from modules.users.models import UserModel
from modules.insumos.schemas import (
    InsumoCreate,
    InsumoUpdate,
    Insumo,
    InsumoDetalle,
    InsumoListResponse,
    PresentacionCreate,
    PresentacionUpdate,
    Presentacion,
    PresentacionListResponse,
    ImportarCsvResultado,
)
from modules.insumos import service
from modules.insumos.service import contar_insumos

router = APIRouter(tags=["Insumos — Catálogo"])


# ---------------------------------------------------------------------------
# Insumos
# ---------------------------------------------------------------------------

@router.get("/", response_model=InsumoListResponse)
def listar_insumos(
    q: Optional[str] = Query(None, description="Nombre o código (parcial)"),
    renglon: Optional[str] = Query(None, max_length=3, description="Ej. '261', '011'"),
    codigo: Optional[str] = Query(None, description="Código exacto de insumo"),
    activo: Optional[bool] = Query(True),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
    _: UserModel = Depends(get_current_user),
):
    return service.listar_insumos(
        db=db, q=q, renglon=renglon, codigo=codigo,
        activo=activo, skip=skip, limit=limit,
    )


@router.get("/contar", response_model=dict)
def contar_catalogo(
    db: Session = Depends(get_db),
    _: UserModel = Depends(get_current_user),
):
    return contar_insumos(db)


@router.post("/importar-csv", response_model=ImportarCsvResultado)
async def importar_csv(
    file: UploadFile = File(..., description="CSV del catálogo (7 columnas del Excel)"),
    db: Session = Depends(get_db),
    _: UserModel = Depends(get_current_user),
):
    """Importa el catálogo espejo: upsert por código de insumo y de presentación.

    Errores de fila se acumulan en `errores`; el resto de filas se aplica.
    """
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="El archivo debe ser un CSV (.csv)")
    crudo = await read_upload_limited(file, max_bytes=25 * 1024 * 1024)
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            contenido = crudo.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise HTTPException(
            status_code=400, detail="No se pudo decodificar el CSV (codificación desconocida)"
        )
    return service.importar_csv(contenido, db)


@router.post("/", response_model=Insumo, status_code=201)
def crear_insumo(
    data: InsumoCreate,
    db: Session = Depends(get_db),
    _: UserModel = Depends(get_current_user),
):
    return service.crear_insumo(data, db)


@router.put("/{insumo_id}", response_model=Insumo)
def actualizar_insumo(
    insumo_id: int,
    data: InsumoUpdate,
    db: Session = Depends(get_db),
    _: UserModel = Depends(get_current_user),
):
    return service.actualizar_insumo(insumo_id, data, db)


@router.delete("/{insumo_id}")
def eliminar_insumo(
    insumo_id: int,
    db: Session = Depends(get_db),
    _: UserModel = Depends(get_current_admin_user),
):
    return service.eliminar_insumo(insumo_id, db)


# ---------------------------------------------------------------------------
# Presentaciones
# ---------------------------------------------------------------------------

@router.get("/presentaciones", response_model=PresentacionListResponse)
def listar_presentaciones(
    insumo_id: Optional[int] = Query(None),
    codigo: Optional[str] = Query(None, description="Código exacto de presentación"),
    q: Optional[str] = Query(None, description="Nombre, cantidad/unidad o código (parcial)"),
    activo: Optional[bool] = Query(True),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
    _: UserModel = Depends(get_current_user),
):
    return service.listar_presentaciones(
        db=db, insumo_id=insumo_id, codigo=codigo, q=q,
        activo=activo, skip=skip, limit=limit,
    )


@router.post("/presentaciones", response_model=Presentacion, status_code=201)
def crear_presentacion(
    data: PresentacionCreate,
    db: Session = Depends(get_db),
    _: UserModel = Depends(get_current_user),
):
    return service.crear_presentacion(data, db)


@router.get("/presentaciones/{presentacion_id}", response_model=Presentacion)
def obtener_presentacion(
    presentacion_id: int,
    db: Session = Depends(get_db),
    _: UserModel = Depends(get_current_user),
):
    return service.obtener_presentacion(presentacion_id, db)


@router.put("/presentaciones/{presentacion_id}", response_model=Presentacion)
def actualizar_presentacion(
    presentacion_id: int,
    data: PresentacionUpdate,
    db: Session = Depends(get_db),
    _: UserModel = Depends(get_current_user),
):
    return service.actualizar_presentacion(presentacion_id, data, db)


@router.delete("/presentaciones/{presentacion_id}")
def eliminar_presentacion(
    presentacion_id: int,
    db: Session = Depends(get_db),
    _: UserModel = Depends(get_current_admin_user),
):
    return service.eliminar_presentacion(presentacion_id, db)


# ---------------------------------------------------------------------------
# Detalle (al final: /{insumo_id} es comodín de un segmento)
# ---------------------------------------------------------------------------

@router.get("/{insumo_id}", response_model=InsumoDetalle)
def obtener_insumo(
    insumo_id: int,
    db: Session = Depends(get_db),
    _: UserModel = Depends(get_current_user),
):
    return service.obtener_insumo(insumo_id, db)
