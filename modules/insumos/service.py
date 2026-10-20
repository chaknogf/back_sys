"""Catálogo de insumos/presentaciones e importación desde CSV (fuente: Excel).

El CSV tiene 7 columnas:
  RENGLÓN | CÓDIGO DE INSUMO | NOMBRE | CARACTERÍSTICAS |
  NOMBRE DE LA PRESENTACIÓN | CANTIDAD Y UNIDAD DE MEDIDA DE LA PRESENTACIÓN |
  CÓDIGO DE PRESENTACIÓN

Las columnas 1-4 se agrupan por CÓDIGO DE INSUMO (upsert en `insumos`);
las columnas 5-7 por CÓDIGO DE PRESENTACIÓN (upsert en `presentaciones`).
Todos los textos se guardan CRUDOS tal cual el CSV; el parseo a JSONB de
características y de cantidad/unidad queda pendiente de revisar datos.
"""

import csv
import io
import unicodedata

from fastapi import HTTPException
from sqlalchemy import or_, func
from sqlalchemy.orm import Session, joinedload

from modules.insumos.models import Insumo, Presentacion
from modules.insumos.schemas import (
    InsumoCreate,
    InsumoUpdate,
    PresentacionCreate,
    PresentacionUpdate,
)
from modules.insumos.helpers import validar_existe, obtener_o_404, paginar


# ---------------------------------------------------------------------------
# Helpers de encabezados CSV
# ---------------------------------------------------------------------------

def _norm(texto: str) -> str:
    """Normaliza encabezados: quita BOM, acentos, comillas y colapsa espacios."""
    if texto is None:
        return ""
    t = str(texto).lstrip("\ufeff")
    t = unicodedata.normalize("NFKD", t)
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = t.lower().strip().strip('"').rstrip(":").strip()
    return " ".join(t.split())


# Cada campo canónico acepta estos encabezados (ya normalizados con `_norm`).
_COLUMNAS = {
    "renglon": {"renglon", "ren"},
    "codigo_insumo": {
        "codigo de insumo", "codigo insumo", "cod de insumo",
        "cod insumo", "codigo_insumo", "codigo",
    },
    "nombre": {"nombre", "nombre del insumo", "insumo"},
    "caracteristicas": {"caracteristicas", "caracteristica", "caracteristicas del insumo"},
    "nombre_presentacion": {
        "nombre de la presentacion", "presentacion", "nombre presentacion",
    },
    "cantidad_unidad": {
        "cantidad y unidad de medida de la presentacion",
        "cantidad y unidad de medida", "cantidad y unidad",
        "cantidad/unidad", "cantidad y unid de medida de la presentacion",
    },
    "codigo_presentacion": {
        "codigo de presentacion", "codigo presentacion", "cod de presentacion",
        "codigo_pres", "codigo",
    },
}


def _detectar_delimitador(contenido: str) -> str:
    """Elige entre tab, ';' y ',' según lo que domine en la primera línea."""
    primera = contenido.splitlines()[0] if contenido else ""
    conteos = {"\t": primera.count("\t"), ";": primera.count(";"), ",": primera.count(",")}
    mejor = max(conteos, key=conteos.get)
    return mejor if conteos[mejor] > 0 else ","


def _mapear_encabezados(fieldnames: list) -> dict:
    """Mapa campo canónico → nombre real de columna del CSV."""
    normalizados = {_norm(f): f for f in fieldnames if f is not None}
    mapeo: dict = {}
    faltantes = []
    for canonico, alias in _COLUMNAS.items():
        encontrado = None
        for a in alias:
            if a in normalizados:
                encontrado = normalizados[a]
                break
        if encontrado is not None:
            mapeo[canonico] = encontrado
        else:
            faltantes.append(canonico)
    # 'codigo' es ambiguo: si no se resolvió código de presentación, puede ser él.
    if "codigo_presentacion" in faltantes and "codigo" in normalizados and mapeo.get("codigo_insumo"):
        if normalizados["codigo"] != mapeo.get("codigo_insumo"):
            mapeo["codigo_presentacion"] = normalizados["codigo"]
            faltantes.remove("codigo_presentacion")
    if faltantes:
        raise HTTPException(
            status_code=400,
            detail=(
                "No se reconocieron las columnas del CSV: "
                + ", ".join(faltantes)
                + ". Encabezados esperados: RENGLÓN, CÓDIGO DE INSUMO, NOMBRE, "
                "CARACTERÍSTICAS, NOMBRE DE LA PRESENTACIÓN, CANTIDAD Y UNIDAD "
                "DE MEDIDA DE LA PRESENTACIÓN, CÓDIGO DE PRESENTACIÓN"
            ),
        )
    return mapeo


# ---------------------------------------------------------------------------
# Importación CSV
# ---------------------------------------------------------------------------

_BLOQUE_IN = 1000


def _en_bloques(query, columna, valores):
    """Itera filas cuyo `columna IN valores`, en bloques (límite de parámetros)."""
    valores = list(valores)
    for inicio in range(0, len(valores), _BLOQUE_IN):
        bloque = valores[inicio:inicio + _BLOQUE_IN]
        yield from query.filter(columna.in_(bloque)).all()


def importar_csv(contenido: str, db: Session) -> dict:
    """Importa el catálogo desde CSV; upsert por código de insumo/presentación.

    Las filas inválidas se acumulan en `errores` sin abortar la importación;
    ante un error de base de datos se revierte todo (todo-o-nada).
    """
    if not contenido or not contenido.strip():
        raise HTTPException(status_code=400, detail="El archivo CSV está vacío")

    delim = _detectar_delimitador(contenido)
    reader = csv.DictReader(io.StringIO(contenido), delimiter=delim)
    if not reader.fieldnames:
        raise HTTPException(status_code=400, detail="El CSV no tiene encabezados")

    col = _mapear_encabezados(reader.fieldnames)

    # 1) Parseo en memoria (sin ORM) para validar filas y conocer los códigos
    #    presentes. Así solo consultamos a la BD los códigos del CSV, no el
    #    catálogo entero (que puede tener cientos de miles de filas).
    filas = 0
    errores: list[dict] = []
    parseadas: list[dict] = []
    codigos_insumo: set[str] = set()
    codigos_presentacion: set[str] = set()

    for num_fila, row in enumerate(reader, start=2):
        # Fila totalmente vacía: se ignora.
        if not any((v or "").strip() for v in row.values()):
            continue
        filas += 1

        renglon = (row.get(col["renglon"]) or "").strip()
        codigo_insumo = (row.get(col["codigo_insumo"]) or "").strip()
        nombre = (row.get(col["nombre"]) or "").strip()
        # Características y cantidad/unidad van CRUDOS (con sus espacios del Excel).
        caracteristicas = row.get(col["caracteristicas"]) or ""
        nombre_presentacion = (row.get(col["nombre_presentacion"]) or "").strip()
        cantidad_unidad = row.get(col["cantidad_unidad"]) or ""
        codigo_presentacion = (row.get(col["codigo_presentacion"]) or "").strip()

        if not renglon or not codigo_insumo or not nombre:
            errores.append({
                "fila": num_fila,
                "error": "Faltan RENGLÓN, CÓDIGO DE INSUMO o NOMBRE",
            })
            continue
        if len(renglon) > 3:
            errores.append({
                "fila": num_fila,
                "error": f"RENGLÓN demasiado largo (máx. 3): '{renglon}'",
            })
            continue
        if not codigo_presentacion:
            errores.append({
                "fila": num_fila,
                "error": "Falta CÓDIGO DE PRESENTACIÓN",
            })
            continue

        codigos_insumo.add(codigo_insumo)
        codigos_presentacion.add(codigo_presentacion)
        parseadas.append({
            "num_fila": num_fila,
            "renglon": renglon,
            "codigo_insumo": codigo_insumo,
            "nombre": nombre,
            "caracteristicas": caracteristicas,
            "nombre_presentacion": nombre_presentacion,
            "cantidad_unidad": cantidad_unidad,
            "codigo_presentacion": codigo_presentacion,
        })

    # 2) Precarga acotada: solo los códigos que aparecen en este CSV.
    insumos_existentes: dict[str, Insumo] = {}
    for i in _en_bloques(db.query(Insumo), Insumo.codigo_insumo, codigos_insumo):
        insumos_existentes[i.codigo_insumo] = i
    presentaciones_existentes: dict[str, Presentacion] = {}
    for p in _en_bloques(db.query(Presentacion), Presentacion.codigo_presentacion, codigos_presentacion):
        presentaciones_existentes[p.codigo_presentacion] = p

    insumos_creados = insumos_actualizados = 0
    presentaciones_creadas = presentaciones_actualizadas = 0

    for datos in parseadas:
        num_fila = datos["num_fila"]
        try:
            insumo = insumos_existentes.get(datos["codigo_insumo"])
            if insumo is None:
                insumo = Insumo(
                    renglon=datos["renglon"],
                    codigo_insumo=datos["codigo_insumo"],
                    nombre=datos["nombre"],
                    caracteristicas=datos["caracteristicas"],
                )
                db.add(insumo)
                insumos_existentes[datos["codigo_insumo"]] = insumo
                insumos_creados += 1
            else:
                cambiado = False
                if insumo.renglon != datos["renglon"]:
                    insumo.renglon = datos["renglon"]
                    cambiado = True
                if insumo.nombre != datos["nombre"]:
                    insumo.nombre = datos["nombre"]
                    cambiado = True
                if insumo.caracteristicas != datos["caracteristicas"]:
                    insumo.caracteristicas = datos["caracteristicas"]
                    cambiado = True
                if cambiado:
                    insumos_actualizados += 1

            presentacion = presentaciones_existentes.get(datos["codigo_presentacion"])
            if presentacion is None:
                # Relación ORM (no insumo_id): el FK se resuelve en el flush final,
                # evitando un flush por fila.
                presentacion = Presentacion(
                    insumo=insumo,
                    nombre=datos["nombre_presentacion"] or "Envase",
                    cantidad_unidad=datos["cantidad_unidad"],
                    codigo_presentacion=datos["codigo_presentacion"],
                )
                db.add(presentacion)
                presentaciones_existentes[datos["codigo_presentacion"]] = presentacion
                presentaciones_creadas += 1
            else:
                cambiado = False
                insumo_actual = presentacion.insumo
                if insumo_actual is not insumo and (
                    insumo_actual is None
                    or insumo_actual.codigo_insumo != datos["codigo_insumo"]
                ):
                    # Reasignación a su insumo correcto según el CSV actual.
                    errores.append({
                        "fila": num_fila,
                        "error": (
                            f"La presentación {datos['codigo_presentacion']} ya pertenece a otro "
                            f"insumo; se conserva la relación existente"
                        ),
                    })
                if datos["nombre_presentacion"] and presentacion.nombre != datos["nombre_presentacion"]:
                    presentacion.nombre = datos["nombre_presentacion"]
                    cambiado = True
                if presentacion.cantidad_unidad != datos["cantidad_unidad"]:
                    presentacion.cantidad_unidad = datos["cantidad_unidad"]
                    cambiado = True
                if cambiado:
                    presentaciones_actualizadas += 1

        except HTTPException:
            raise
        except Exception as e:  # noqa: BLE001 — se reporta por fila
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error guardando la fila {num_fila}: {e}",
            )

    try:
        db.commit()
    except HTTPException:
        raise
    except Exception as e:  # noqa: BLE001 — se revierte todo (todo-o-nada)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error guardando el catálogo: {e}")

    return {
        "filas": filas,
        "insumos_creados": insumos_creados,
        "insumos_actualizados": insumos_actualizados,
        "presentaciones_creadas": presentaciones_creadas,
        "presentaciones_actualizadas": presentaciones_actualizadas,
        "errores": errores,
    }


# ---------------------------------------------------------------------------
# CRUD insumos
# ---------------------------------------------------------------------------

def listar_insumos(
    db: Session,
    q: str | None = None,
    renglon: str | None = None,
    codigo: str | None = None,
    activo: bool | None = True,
    skip: int = 0,
    limit: int = 20,
) -> dict:
    query = db.query(Insumo)
    if activo is not None:
        query = query.filter(Insumo.activo == activo)
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(or_(Insumo.nombre.ilike(like), Insumo.codigo_insumo.ilike(like)))
    if renglon:
        query = query.filter(Insumo.renglon == renglon.strip())
    if codigo:
        query = query.filter(Insumo.codigo_insumo == codigo.strip())
    return paginar(query, skip, limit, [Insumo.nombre, Insumo.id])


def obtener_insumo(insumo_id: int, db: Session) -> Insumo:
    insumo = (
        db.query(Insumo)
        .options(joinedload(Insumo.presentaciones))
        .filter(Insumo.id == insumo_id)
        .first()
    )
    if not insumo:
        raise HTTPException(status_code=404, detail="Insumo no encontrado")
    return insumo


def _verificar_codigo_insumo(db: Session, codigo: str, excluir_id: int | None = None) -> None:
    query = db.query(Insumo.id).filter(Insumo.codigo_insumo == codigo)
    if excluir_id is not None:
        query = query.filter(Insumo.id != excluir_id)
    if query.first():
        raise HTTPException(
            status_code=409, detail=f"Ya existe un insumo con código '{codigo}'",
        )


def crear_insumo(data: InsumoCreate, db: Session) -> Insumo:
    _verificar_codigo_insumo(db, data.codigo_insumo.strip())
    insumo = Insumo(
        renglon=data.renglon.strip(),
        codigo_insumo=data.codigo_insumo.strip(),
        nombre=data.nombre.strip(),
        caracteristicas=data.caracteristicas or "",
        activo=data.activo if data.activo is not None else True,
    )
    db.add(insumo)
    db.commit()
    db.refresh(insumo)
    return insumo


def actualizar_insumo(insumo_id: int, data: InsumoUpdate, db: Session) -> Insumo:
    insumo = obtener_o_404(db, Insumo, insumo_id, "Insumo no encontrado")

    campos = data.model_dump(exclude_unset=True)
    if "codigo_insumo" in campos:
        nuevo = campos["codigo_insumo"].strip()
        _verificar_codigo_insumo(db, nuevo, excluir_id=insumo_id)
        campos["codigo_insumo"] = nuevo
    if "renglon" in campos:
        campos["renglon"] = campos["renglon"].strip()
    if "nombre" in campos:
        campos["nombre"] = campos["nombre"].strip()

    for key, value in campos.items():
        setattr(insumo, key, value)
    db.commit()
    db.refresh(insumo)
    return insumo


def eliminar_insumo(insumo_id: int, db: Session) -> dict:
    """Baja lógica: el insumo y sus presentaciones dejan de listarse por defecto."""
    insumo = obtener_o_404(db, Insumo, insumo_id, "Insumo no encontrado")
    insumo.activo = False
    db.query(Presentacion).filter(
        Presentacion.insumo_id == insumo_id
    ).update({"activo": False}, synchronize_session=False)
    db.commit()
    return {"id": insumo_id, "activo": False}


# ---------------------------------------------------------------------------
# CRUD presentaciones
# ---------------------------------------------------------------------------

def listar_presentaciones(
    db: Session,
    insumo_id: int | None = None,
    codigo: str | None = None,
    q: str | None = None,
    activo: bool | None = True,
    skip: int = 0,
    limit: int = 20,
) -> dict:
    query = db.query(Presentacion)
    if activo is not None:
        query = query.filter(Presentacion.activo == activo)
    if insumo_id is not None:
        query = query.filter(Presentacion.insumo_id == insumo_id)
    if codigo:
        query = query.filter(Presentacion.codigo_presentacion == codigo.strip())
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(
            or_(
                Presentacion.nombre.ilike(like),
                Presentacion.cantidad_unidad.ilike(like),
                Presentacion.codigo_presentacion.ilike(like),
            )
        )
    return paginar(query, skip, limit, Presentacion.id)


def obtener_presentacion(presentacion_id: int, db: Session) -> Presentacion:
    presentacion = (
        db.query(Presentacion)
        .options(joinedload(Presentacion.insumo))
        .filter(Presentacion.id == presentacion_id)
        .first()
    )
    if not presentacion:
        raise HTTPException(status_code=404, detail="Presentación no encontrada")
    return presentacion


def _verificar_codigo_presentacion(
    db: Session, codigo: str, excluir_id: int | None = None
) -> None:
    query = db.query(Presentacion.id).filter(Presentacion.codigo_presentacion == codigo)
    if excluir_id is not None:
        query = query.filter(Presentacion.id != excluir_id)
    if query.first():
        raise HTTPException(
            status_code=409, detail=f"Ya existe una presentación con código '{codigo}'",
        )


def crear_presentacion(data: PresentacionCreate, db: Session) -> Presentacion:
    validar_existe(db, Insumo, data.insumo_id, "El insumo indicado no existe")
    _verificar_codigo_presentacion(db, data.codigo_presentacion.strip())
    presentacion = Presentacion(
        insumo_id=data.insumo_id,
        nombre=data.nombre.strip() or "Envase",
        cantidad_unidad=data.cantidad_unidad or "",
        codigo_presentacion=data.codigo_presentacion.strip(),
        activo=data.activo if data.activo is not None else True,
    )
    db.add(presentacion)
    db.commit()
    db.refresh(presentacion)
    return presentacion


def actualizar_presentacion(
    presentacion_id: int, data: PresentacionUpdate, db: Session
) -> Presentacion:
    presentacion = obtener_o_404(
        db, Presentacion, presentacion_id, "Presentación no encontrada"
    )

    campos = data.model_dump(exclude_unset=True)
    if "insumo_id" in campos:
        validar_existe(db, Insumo, campos["insumo_id"], "El insumo indicado no existe")
    if "codigo_presentacion" in campos:
        nuevo = campos["codigo_presentacion"].strip()
        _verificar_codigo_presentacion(db, nuevo, excluir_id=presentacion_id)
        campos["codigo_presentacion"] = nuevo

    for key, value in campos.items():
        setattr(presentacion, key, value)
    db.commit()
    db.refresh(presentacion)
    return presentacion


def eliminar_presentacion(presentacion_id: int, db: Session) -> dict:
    presentacion = obtener_o_404(
        db, Presentacion, presentacion_id, "Presentación no encontrada"
    )
    presentacion.activo = False
    db.commit()
    return {"id": presentacion_id, "activo": False}


def contar_insumos(db: Session) -> dict:
    """Conteos rápidos del catálogo."""
    total_insumos = db.query(func.count(Insumo.id)).filter(Insumo.activo == True).scalar() or 0
    total_presentaciones = (
        db.query(func.count(Presentacion.id)).filter(Presentacion.activo == True).scalar() or 0
    )
    return {"insumos": int(total_insumos), "presentaciones": int(total_presentaciones)}
