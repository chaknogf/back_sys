"""Router agregador del módulo de insumos (catálogo, almacén, flujos, atenciones)."""

from fastapi import APIRouter

from modules.insumos.catalogo_router import router as catalogo_router
from modules.insumos.almacen_router import router as almacen_router
from modules.insumos.flujo_router import router as flujo_router
from modules.insumos.atencion_router import router as atencion_router

# Sin tag propio: cada sub-router ya declara el suyo ("Insumos — Catálogo",
# etc.). Un tag aquí se acumularía al del sub-router y duplicaría cada
# endpoint en la documentación (una entrada por tag).
router = APIRouter(prefix="/insumos")

# El catálogo va al final: expone GET /{insumo_id} (comodín) que, si se
# registrara antes, interceptaría rutas literales de los otros routers.
router.include_router(almacen_router)
router.include_router(flujo_router)
router.include_router(atencion_router)
router.include_router(catalogo_router)
