"""Endpoints del catálogo y de los procedimientos registrados por personal médico."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, text
from typing import List, Optional
from datetime import datetime, date, time, timedelta
from core.database import get_db
from modules.users.models import UserModel
from modules.procedimientos.models import ProceMedico as ProceMedicoModel
from modules.procedimientos.models import CatalogoProcedimiento as CatalogoProcedimientoModel
from modules.especialidades.models import EspecialidadModel
from modules.procedimientos.schemas import (
    ProceMedicoBase,
    ProceMedicoCreate,
    ProceMedicoUpdate,
    ProceMedicoOut,
    ProceMedicoInDB,
    ProceMedicoResponse,
    ProcedimientosListResponse,
    CATEGORIAS_EDAD,
)
from core.security import get_current_user, get_current_admin_user

router = APIRouter(
    prefix="/procedimientos",
    tags=["Procedimientos"]
)


def _filtro_categoria(categoria: str):
    """Registros con al menos una persona de la categoría etaria (niño/adulto)."""
    if categoria == "nino":
        return (ProceMedicoModel.nino_m + ProceMedicoModel.nino_f) > 0
    return (ProceMedicoModel.adulto_m + ProceMedicoModel.adulto_f) > 0


def _filtro_sexo(sexo: str):
    """Registros con cantidad de ese sexo en cualquier categoría (incluye históricos)."""
    if sexo == "M":
        return (ProceMedicoModel.nino_m + ProceMedicoModel.adulto_m + ProceMedicoModel.sin_edad_m) > 0
    return (ProceMedicoModel.nino_f + ProceMedicoModel.adulto_f + ProceMedicoModel.sin_edad_f) > 0


@router.get("/", response_model=ProcedimientosListResponse)
def listar_procedimientos_medicos(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    especialidad: Optional[str] = Query(None),
    especialidad_id: Optional[int] = Query(None),
    lugar_servicio: Optional[str] = Query(None),
    id_catalogo_procedimiento: Optional[int] = Query(None),
    id_area_cuerpo_intervenida: Optional[int] = Query(None),
    categoria: Optional[str] = Query(None, pattern="^(nino|adulto)$"),
    sexo: Optional[str] = Query(None, pattern="^[MF]$"),
    mes: Optional[int] = Query(None, ge=1, le=12),
    anio: Optional[int] = Query(None, ge=2000, le=2100),
    fecha_inicio: Optional[date] = Query(None),
    fecha_fin: Optional[date] = Query(None)
):
    query = (
        db.query(ProceMedicoModel)
        .options(joinedload(ProceMedicoModel.catalogo))
        .options(joinedload(ProceMedicoModel.area_cuerpo))
    )

    if especialidad:
        query = query.filter(
            ProceMedicoModel.especialidad == especialidad
        )
    if especialidad_id is not None:
        query = query.filter(
            ProceMedicoModel.especialidad_id == especialidad_id
        )

    if lugar_servicio:
        query = query.filter(
            ProceMedicoModel.lugar_servicio == lugar_servicio
        )

    if id_catalogo_procedimiento:
        query = query.filter(
            ProceMedicoModel.id_catalogo_procedimiento == id_catalogo_procedimiento
        )

    if id_area_cuerpo_intervenida:
        query = query.filter(
            ProceMedicoModel.id_area_cuerpo_intervenida == id_area_cuerpo_intervenida
        )

    if categoria:
        query = query.filter(_filtro_categoria(categoria))

    if sexo:
        query = query.filter(_filtro_sexo(sexo))

    if fecha_inicio:
        query = query.filter(
            ProceMedicoModel.fecha >= fecha_inicio
        )

    if fecha_fin:
        query = query.filter(
            ProceMedicoModel.fecha <= fecha_fin
        )

    if mes and anio:
        fecha_inicio_mes = date(anio, mes, 1)

        if mes == 12:
            fecha_fin_mes = date(anio + 1, 1, 1)
        else:
            fecha_fin_mes = date(anio, mes + 1, 1)

        query = query.filter(
            ProceMedicoModel.fecha >= fecha_inicio_mes,
            ProceMedicoModel.fecha < fecha_fin_mes
        )

    elif anio:
        query = query.filter(
            ProceMedicoModel.fecha >= date(anio, 1, 1),
            ProceMedicoModel.fecha <= date(anio, 12, 31)
        )

    total = query.count()

    procedimientos = (
        query.order_by(ProceMedicoModel.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return ProcedimientosListResponse(
        total=total,
        procedimientos=procedimientos
    )


@router.get("/reporte")
def reporte_proce_medicos(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
    desde: Optional[date] = Query(None, description="Fecha inicio"),
    hasta: Optional[date] = Query(None, description="Fecha fin"),
    especialidad: Optional[str] = Query(None),
    lugar_servicio: Optional[str] = Query(None),
    sexo: Optional[str] = Query(None, pattern="^[MF]$"),
):
    """Agrupa cantidades por especialidad, servicio y sexo.

    Las cantidades por sexo salen del desglose niño/adulto × sexo (más los
    históricos sin edad). La anestesia se cuenta una sola vez por registro.
    """
    filtros = []
    params = {}

    if desde:
        filtros.append("pm.fecha >= :desde")
        params["desde"] = desde
    if hasta:
        filtros.append("pm.fecha <= :hasta")
        params["hasta"] = hasta
    if especialidad:
        filtros.append("pm.especialidad = :especialidad")
        params["especialidad"] = especialidad
    if lugar_servicio:
        filtros.append("pm.lugar_servicio = :lugar_servicio")
        params["lugar_servicio"] = lugar_servicio
    if sexo:
        columnas = ("nino_m", "adulto_m", "sin_edad_m") if sexo == "M" else ("nino_f", "adulto_f", "sin_edad_f")
        filtros.append("(" + " + ".join(f"COALESCE(pm.{c},0)" for c in columnas) + ") > 0")

    where_sql = " AND ".join(filtros) if filtros else "TRUE"

    registros = db.execute(text(f"""
        SELECT
            pm.especialidad,
            pm.lugar_servicio,
            SUM(COALESCE(pm.nino_m, 0) + COALESCE(pm.adulto_m, 0) + COALESCE(pm.sin_edad_m, 0)) AS total_m,
            SUM(COALESCE(pm.nino_f, 0) + COALESCE(pm.adulto_f, 0) + COALESCE(pm.sin_edad_f, 0)) AS total_f,
            SUM(CASE WHEN COALESCE(pm.nino_m, 0) + COALESCE(pm.adulto_m, 0) + COALESCE(pm.sin_edad_m, 0) > 0 THEN 1 ELSE 0 END) AS registros_m,
            SUM(CASE WHEN COALESCE(pm.nino_f, 0) + COALESCE(pm.adulto_f, 0) + COALESCE(pm.sin_edad_f, 0) > 0 THEN 1 ELSE 0 END) AS registros_f,
            SUM(COALESCE(pm.anestesia, 0)) AS total_anestesia,
            SUM(COALESCE(pm.nino_m, 0) + COALESCE(pm.nino_f, 0) + COALESCE(pm.adulto_m, 0) + COALESCE(pm.adulto_f, 0) + COALESCE(pm.sin_edad_m, 0) + COALESCE(pm.sin_edad_f, 0)) AS total_cantidad,
            COUNT(*) AS total_registros
        FROM proce_medicos pm
        WHERE {where_sql}
        GROUP BY pm.especialidad, pm.lugar_servicio
    """), params).fetchall()

    grupos: dict[tuple, dict] = {}
    gran_total_cantidad = 0
    gran_total_anestesia = 0
    gran_total_registros = 0

    for r in registros:
        m = r._mapping
        for sexo_key, amount_key, count_key in (
            ("M", "total_m", "registros_m"),
            ("F", "total_f", "registros_f"),
        ):
            cantidad = int(m[amount_key] or 0)
            if cantidad <= 0:
                continue
            clave = (m["especialidad"], m["lugar_servicio"], sexo_key)
            grupos[clave] = {
                "especialidad": m["especialidad"],
                "lugar_servicio": m["lugar_servicio"],
                "sexo": sexo_key,
                "total_cantidad": cantidad,
                "total_anestesia": int(m["total_anestesia"] or 0),
                "total_registros": int(m[count_key] or 0),
            }

        gran_total_anestesia += int(m["total_anestesia"] or 0)
        gran_total_registros += int(m["total_registros"] or 0)
        gran_total_cantidad += int(m["total_cantidad"] or 0)

    return {
        "grupos": sorted(
            grupos.values(),
            key=lambda g: (g["especialidad"] or "", g["lugar_servicio"] or "", g["sexo"])
        ),
        "totales": {
            "total_cantidad": gran_total_cantidad,
            "total_anestesia": gran_total_anestesia,
            "total_registros": gran_total_registros,
        },
    }


@router.get("/mas-usados")
def listar_mas_usados(
    especialidad_id: Optional[int] = Query(None, description="Especialidad; si se omite, agrupa por todas"),
    desde: Optional[date] = Query(None),
    hasta: Optional[date] = Query(None),
    limite: int = Query(10, ge=1, le=100),
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Procedimientos más usados por especialidad, según la cantidad registrada.

    Se apoya en el catálogo maestro (`id_catalogo_procedimiento`). La especialidad
    se toma del propio registro, no del catálogo, para que un mismo procedimiento
    no se duplique al cambiar de especialidad en el catálogo.
    """
    filtros = ["pm.id_catalogo_procedimiento IS NOT NULL", "pm.fecha IS NOT NULL"]

    if especialidad_id is not None:
        filtros.append("pm.especialidad_id = :especialidad_id")
    if desde:
        filtros.append("pm.fecha >= :desde")
    if hasta:
        filtros.append("pm.fecha <= :hasta")

    params = {}
    if especialidad_id is not None:
        params["especialidad_id"] = especialidad_id
    if desde:
        params["desde"] = desde
    if hasta:
        params["hasta"] = hasta

    rows = db.execute(text(f"""
        WITH uso AS (
            SELECT
                pm.especialidad_id,
                esp.abreviatura AS especialidad,
                esp.nombre AS especialidad_nombre,
                cat.id AS id_catalogo_procedimiento,
                cat.abreviatura,
                cat.nombre,
                SUM(pm.cantidad) AS total_cantidad,
                COUNT(*) AS total_registros,
                SUM(pm.anestesia) AS total_anestesia,
                MAX(pm.lugar_servicio) AS lugar_servicio,
                ROW_NUMBER() OVER (
                    PARTITION BY pm.especialidad_id
                    ORDER BY SUM(pm.cantidad) DESC, COUNT(*) DESC, cat.nombre
                ) AS posicion
            FROM proce_medicos pm
            JOIN catalogo_procedimientos cat
              ON cat.id = pm.id_catalogo_procedimiento
            LEFT JOIN especialidades esp
              ON esp.id = pm.especialidad_id
            WHERE {" AND ".join(filtros)}
            GROUP BY pm.especialidad_id, esp.abreviatura, esp.nombre,
                     cat.id, cat.abreviatura, cat.nombre
        )
        SELECT * FROM uso
        WHERE posicion <= :limite
        ORDER BY especialidad, posicion
    """), {**params, "limite": limite}).fetchall()

    grupos = []
    for r in rows:
        m = r._mapping
        grupos.append({
            "especialidad_id": m["especialidad_id"],
            "especialidad": m["especialidad"],
            "especialidad_nombre": m["especialidad_nombre"],
            "id_catalogo_procedimiento": m["id_catalogo_procedimiento"],
            "abreviatura": m["abreviatura"],
            "nombre": m["nombre"],
            "total_cantidad": int(m["total_cantidad"] or 0),
            "total_registros": int(m["total_registros"] or 0),
            "total_anestesia": int(m["total_anestesia"] or 0),
            "posicion": int(m["posicion"]),
            "lugar_servicio": m["lugar_servicio"] if m["lugar_servicio"] else "",
        })

    return {
        "procedimientos": grupos,
        "total": len(grupos),
    }


def _cantidades_por_sexo(m) -> dict:
    """Cantidades M/F de una fila: suma de las categorías etarias por sexo."""
    return {
        "M": int(m["nino_m"] or 0) + int(m["adulto_m"] or 0) + int(m["sin_edad_m"] or 0),
        "F": int(m["nino_f"] or 0) + int(m["adulto_f"] or 0) + int(m["sin_edad_f"] or 0),
    }


@router.get("/grupos-edad")
def listar_grupos_edad(current_user: UserModel = Depends(get_current_user)):
    """Devuelve las categorías etarias (corte a los 18 años) admitidas."""
    return [
        {"codigo": codigo, "nombre": nombre}
        for codigo, nombre in CATEGORIAS_EDAD.items()
    ]


@router.get("/{id:int}", response_model=ProceMedicoResponse)
def obtener_procedimiento_medico(
    id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    procedimiento = (
        db.query(ProceMedicoModel)
        .options(joinedload(ProceMedicoModel.catalogo))
        .options(joinedload(ProceMedicoModel.area_cuerpo))
        .filter(ProceMedicoModel.id == id)
        .first()
    )

    if not procedimiento:
        raise HTTPException(
            status_code=404,
            detail="Procedimiento médico no encontrado"
        )

    return procedimiento


@router.post("/", response_model=ProceMedicoOut, status_code=201)
def crear_procedimiento_medico(
    datos: ProceMedicoCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Registra el desglose niño/adulto × sexo y calcula el total y la anestesia."""
    catalogo = None
    if datos.id_catalogo_procedimiento:
        catalogo = db.get(CatalogoProcedimientoModel, datos.id_catalogo_procedimiento)
        if not catalogo:
            raise HTTPException(status_code=404, detail="Procedimiento no encontrado")

    data = datos.model_dump(exclude={'created_by', 'anestesia'})
    nuevo = ProceMedicoModel(
        **data,
        cantidad=datos.total_cantidad,
        created_by=current_user.username[:10] if current_user.username else None
    )
    nuevo.anestesia = (catalogo.anestesia or 0) * nuevo.cantidad if catalogo else 0

    # Mantiene sincronizado el código legacy de especialidad para reportes
    if nuevo.especialidad_id and not nuevo.especialidad:
        esp = db.get(EspecialidadModel, nuevo.especialidad_id)
        nuevo.especialidad = esp.abreviatura if esp else None

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    return nuevo


@router.put("/{id:int}", response_model=ProceMedicoOut)
def actualizar_procedimiento_medico(
    id: int,
    datos: ProceMedicoUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Recalcula cantidad y anestesia desde el desglose y el catálogo."""
    procedimiento = (
        db.query(ProceMedicoModel)
        .filter(ProceMedicoModel.id == id)
        .first()
    )

    if not procedimiento:
        raise HTTPException(
            status_code=404,
            detail="Procedimiento médico no encontrado"
        )

    for campo, valor in datos.model_dump(
        exclude_unset=True, exclude={'anestesia'}
    ).items():
        setattr(procedimiento, campo, valor)

    catalogo = None
    if procedimiento.id_catalogo_procedimiento:
        catalogo = db.get(CatalogoProcedimientoModel, procedimiento.id_catalogo_procedimiento)
        if not catalogo:
            raise HTTPException(
                status_code=404,
                detail="Procedimiento no encontrado"
            )

    procedimiento.cantidad = (
        procedimiento.nino_m + procedimiento.nino_f
        + procedimiento.adulto_m + procedimiento.adulto_f
        + procedimiento.sin_edad_m + procedimiento.sin_edad_f
    )
    procedimiento.anestesia = (catalogo.anestesia or 0) * procedimiento.cantidad if catalogo else 0

    # Mantiene sincronizado el código legacy de especialidad para reportes
    if procedimiento.especialidad_id and not procedimiento.especialidad:
        esp = db.get(EspecialidadModel, procedimiento.especialidad_id)
        procedimiento.especialidad = esp.abreviatura if esp else None

    db.commit()
    db.refresh(procedimiento)

    return procedimiento


@router.delete("/{id:int}")
def eliminar_procedimiento_medico(
    id: int,
    current_user: UserModel = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    procedimiento = (
        db.query(ProceMedicoModel)
        .filter(ProceMedicoModel.id == id)
        .first()
    )

    if not procedimiento:
        raise HTTPException(
            status_code=404,
            detail="Procedimiento médico no encontrado"
        )

    db.delete(procedimiento)
    db.commit()

    return {
        "message": "Procedimiento médico eliminado"
    }


@router.get("/estadisticas/resumen")
def obtener_estadisticas(
    anio: Optional[int] = Query(None, ge=2000, le=2100),
    mes: Optional[int] = Query(None, ge=1, le=12),
    desde: Optional[date] = Query(None),
    hasta: Optional[date] = Query(None),
    especialidad: Optional[str] = Query(None),
    lugar_servicio: Optional[str] = Query(None),
    sexo: Optional[str] = Query(None),
    nombre: Optional[str] = Query(None),
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(ProceMedicoModel)

    if desde and hasta:
        fecha_inicio = desde
        fecha_fin = hasta
    elif anio:
        if mes:
            fecha_inicio = date(anio, mes, 1)
            if mes == 12:
                fecha_fin = date(anio + 1, 1, 1) - timedelta(days=1)
            else:
                fecha_fin = date(anio, mes + 1, 1) - timedelta(days=1)
        else:
            fecha_inicio = date(anio, 1, 1)
            fecha_fin = date(anio, 12, 31)
    else:
        hoy = date.today()
        fecha_inicio = date(hoy.year, 1, 1)
        fecha_fin = date(hoy.year, 12, 31)

    query = query.filter(
        ProceMedicoModel.fecha >= fecha_inicio,
        ProceMedicoModel.fecha <= fecha_fin
    )

    if especialidad:
        query = query.filter(ProceMedicoModel.especialidad.ilike(f"%{especialidad}%"))
    if lugar_servicio:
        query = query.filter(ProceMedicoModel.lugar_servicio.ilike(f"%{lugar_servicio}%"))
    if sexo:
        query = query.filter(_filtro_sexo(sexo))
    if nombre:
        query = query.join(CatalogoProcedimientoModel, CatalogoProcedimientoModel.id == ProceMedicoModel.id_catalogo_procedimiento)
        query = query.filter(CatalogoProcedimientoModel.nombre.ilike(f"%{nombre}%"))

    total_procedimientos = query.count()
    total_cantidad = query.with_entities(func.sum(ProceMedicoModel.cantidad)).scalar() or 0

    top_query = (
        db.query(
            CatalogoProcedimientoModel.nombre,
            func.count(ProceMedicoModel.id).label('total'),
            func.coalesce(func.sum(ProceMedicoModel.cantidad), 0).label('total_cantidad'),
            func.coalesce(func.sum(ProceMedicoModel.anestesia), 0).label('total_anestesia')
        )
        .join(ProceMedicoModel, ProceMedicoModel.id_catalogo_procedimiento == CatalogoProcedimientoModel.id)
        .filter(
            ProceMedicoModel.fecha >= fecha_inicio,
            ProceMedicoModel.fecha <= fecha_fin
        )
    )
    if especialidad:
        top_query = top_query.filter(ProceMedicoModel.especialidad.ilike(f"%{especialidad}%"))
    if lugar_servicio:
        top_query = top_query.filter(ProceMedicoModel.lugar_servicio.ilike(f"%{lugar_servicio}%"))
    if sexo:
        top_query = top_query.filter(_filtro_sexo(sexo))
    if nombre:
        top_query = top_query.filter(CatalogoProcedimientoModel.nombre.ilike(f"%{nombre}%"))

    top_procedimientos = (
        top_query
        .group_by(CatalogoProcedimientoModel.id, CatalogoProcedimientoModel.nombre)
        .order_by(func.coalesce(func.sum(ProceMedicoModel.cantidad), 0).desc())
        .limit(5)
        .all()
    )

    usg_gine_query = (
        db.query(
            func.count(ProceMedicoModel.id).label('total_registros'),
            func.coalesce(func.sum(ProceMedicoModel.cantidad), 0).label('total_cantidad')
        )
        .join(CatalogoProcedimientoModel, CatalogoProcedimientoModel.id == ProceMedicoModel.id_catalogo_procedimiento)
        .filter(
            ProceMedicoModel.fecha >= fecha_inicio,
            ProceMedicoModel.fecha <= fecha_fin,
            ProceMedicoModel.especialidad == 'GINE',
            CatalogoProcedimientoModel.nombre.ilike('%ultrasonido%')
        )
        .first()
    )

    return {
        "anio": anio,
        "mes": mes,
        "nombre": nombre,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "total_registros": total_procedimientos,
        "total_cantidad_procedimientos": total_cantidad,
        "top_procedimientos": [
            {
                "nombre": p.nombre,
                "total": p.total,
                "total_cantidad": int(p.total_cantidad or 0),
                "total_anestesia": int(p.total_anestesia or 0)
            }
            for p in top_procedimientos
        ],
        "usg_gine": {
            "total_registros": usg_gine_query.total_registros if usg_gine_query else 0,
            "total_cantidad": int(usg_gine_query.total_cantidad) if usg_gine_query else 0
        },
        "resumen": [
            {
                "nombre": p.nombre,
                "total_cantidad": int(p.total_cantidad or 0),
                "total_anestesia": int(p.total_anestesia or 0)
            }
            for p in top_procedimientos
        ]
    }
