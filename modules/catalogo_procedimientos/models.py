"""Modelos del catálogo maestro.

Los modelos `CatalogoProcedimiento` y `AreaCuerpoIntervenida`
viven en `modules/procedimientos/models.py` para evitar
duplicidad de mapeos SQLAlchemy. Este archivo queda como
re-exports para mantener imports estables.
"""

from modules.procedimientos.models import (
    CatalogoProcedimiento,
    AreaCuerpoIntervenida,
)

__all__ = ["CatalogoProcedimiento", "AreaCuerpoIntervenida"]