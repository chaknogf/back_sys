# app/routes/paises_iso.py
"""
Router de países ISO 3166-1
- Lista completa de países (público, sin autenticación)
- Autocomplete para formularios
- Cacheable (ideal para CDN o frontend)
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database.db import get_db
from app.models.paises_iso import PaisIsoModel
from app.schemas.paises_iso import PaisOut, PaisSelect, PaisListResponse


router = APIRouter(prefix="/paises", tags=["Países ISO"])


# =============================================================================
# LISTA COMPLETA DE PAÍSES (PÚBLICO - SIN LOGIN)
# =============================================================================
@router.get(
    "/",
    response_model=List[PaisOut],
    summary="Lista completa de países ISO 3166-1",
    description="Devuelve todos los países del mundo. Endpoint público (no requiere token)."
)
def listar_paises(db: Session = Depends(get_db)):
    return db.query(PaisIsoModel).order_by(PaisIsoModel.nombre).all()


# =============================================================================
# AUTOCOMPLETE - IDEAL PARA <select> EN FORMULARIOS
# =============================================================================
@router.get(
    "/select",
    response_model=List[PaisSelect],
    summary="Países para <select> o autocomplete",
    description="Formato optimizado para React-Select, Vue-Select, etc."
)
def paises_para_select(
    q: Optional[str] = Query(None, min_length=1, description="Buscar por nombre o código"),
    db: Session = Depends(get_db)
):
    query = db.query(PaisIsoModel).order_by(PaisIsoModel.nombre)

    if q:
        q = q.strip().upper()
        query = query.filter(
            PaisIsoModel.nombre.ilike(f"%{q}%") |
            PaisIsoModel.codigo_iso2.ilike(f"%{q}%") |
            PaisIsoModel.codigo_iso3.ilike(f"%{q}%")
        )

    resultados = query.limit(50).all()
    return [PaisSelect.from_orm(p) for p in resultados]


# =============================================================================
# OBTENER UN PAÍS POR CÓDIGO (ISO2 o ISO3)
# =============================================================================
@router.get("/{codigo}", response_model=PaisOut)
def pais_por_codigo(codigo: str, db: Session = Depends(get_db)):
    codigo = codigo.upper()
    pais = db.query(PaisIsoModel).filter(
        (PaisIsoModel.codigo_iso2 == codigo) |
        (PaisIsoModel.codigo_iso3 == codigo)
    ).first()

    if not pais:
        raise HTTPException(status_code=404, detail="País no encontrado")

    return pais