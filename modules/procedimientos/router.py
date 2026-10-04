"""Endpoints del catálogo y de los procedimientos registrados por personal médico."""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi_cache.decorator import cache
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, or_, text, Integer
from typing import List, Optional
from datetime import datetime, date, time, timedelta
from core.database import get_db
from modules.users.models import UserModel
from modules.procedimientos.models import Procedimiento as ProcedimientoModel
from modules.procedimientos.models import ProceMedico as ProceMedicoModel
from modules.procedimientos.models import CatalogoProcedimiento as CatalogoProcedimientoModel
from modules.especialidades.models import EspecialidadModel
from modules.procedimientos.schemas import (
    ProcedimientoBase,
    ProcedimientoCreate,
    ProcedimientoUpdate,
    ProcedimientoOut,
    ProcedimientoResponse,
    ProceMedicoBase,
    ProceMedicoCreate,
    ProceMedicoUpdate,
    ProceMedicoOut,
    ProceMedicoInDB,
    ProceMedicoResponse,
ProcedimientosListResponse,
    GRUPOS_EDAD
)
from core.security import get_current_user

router = APIRouter(
    prefix="/procedimientos",
    tags=["Procedimientos"]
)


def _detalle_json(detalle) -> Optional[dict]:
    """Convierte el desglose validado a un JSONB simple {"NEO": {"m": 2, "f": 1}}."""
    if not detalle:
        return None
    return {
        codigo: {"m": int(cantidades.m), "f": int(cantidades.f)}
        for codigo, cantidades in detalle.items()
    }


def _filtro_grupo_edad(grupo_edad: str):
    """Registros cuyo grupo etario tiene cantidad en M o en F."""
    columna = ProceMedicoModel.grupo_edad_detalle
    return or_(
        columna[grupo_edad]["m"].astext.cast(Integer) > 0,
        columna[grupo_edad]["f"].astext.cast(Integer) > 0,
    )


def _filtro_sexo(sexo: str):
    """Registros con cantidad de ese sexo en cualquier grupo etario, más los históricos."""
    columna = ProceMedicoModel.grupo_edad_detalle
    clave = "m" if sexo == "M" else "f"
    return or_(
        *[
            columna[codigo][clave].astext.cast(Integer) > 0
            for codigo in GRUPOS_EDAD
        ],
        and_(
            columna.is_(None),
            ProceMedicoModel.sexo == sexo,
        ),
    )


@router.get("/catalogo", response_model=list[ProcedimientoOut])
@cache(expire=900)
def listar_procedimientos(
    abreviatura: Optional[str] = Query(None, description="Filtrar por abreviatura exacta"),
    nombre: Optional[str] = Query(None, description="Filtrar por nombre (búsqueda parcial)"),
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
    ):
    query = db.query(ProcedimientoModel)
    if abreviatura:
        query = query.filter(ProcedimientoModel.abreviatura == abreviatura)
    if nombre:
        query = query.filter(ProcedimientoModel.nombre.ilike(f"%{nombre}%"))
    return query.order_by(ProcedimientoModel.nombre).all()
    
@router.get("/catalogo/{id}", response_model=ProcedimientoOut)
def obtener_procedimiento(
    id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
    ):
    procedimiento = (
        db.query(ProcedimientoModel)
        .filter(ProcedimientoModel.id == id)
        .first()
    )

    if not procedimiento:
        raise HTTPException(
            status_code=404,
            detail="Procedimiento no encontrado"
        )

    return procedimiento

@router.post("/catalogo", response_model=ProcedimientoOut)
def crear_procedimiento(
    datos: ProcedimientoCreate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    unique_filters = [ProcedimientoModel.nombre == datos.nombre]
    if datos.abreviatura is not None:
        unique_filters.append(ProcedimientoModel.abreviatura == datos.abreviatura)
    existing = db.query(ProcedimientoModel).filter(
        or_(*unique_filters)
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Ya existe un procedimiento con ese nombre o abreviatura"
        )
    
    procedimiento = ProcedimientoModel(
        **datos.model_dump()
    )

    db.add(procedimiento)
    db.commit()
    db.refresh(procedimiento)

    return procedimiento

@router.put("/catalogo/{id}", response_model=ProcedimientoOut)
def actualizar_procedimiento(
    id: int,
    datos: ProcedimientoUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    procedimiento = (
        db.query(ProcedimientoModel)
        .filter(ProcedimientoModel.id == id)
        .first()
    )

    if not procedimiento:
        raise HTTPException(
            status_code=404,
            detail="Procedimiento no encontrado"
        )
    
    conflict_filters = []
    if datos.nombre is not None:
        conflict_filters.append(ProcedimientoModel.nombre == datos.nombre)
    if datos.abreviatura is not None:
        conflict_filters.append(ProcedimientoModel.abreviatura == datos.abreviatura)
    if conflict_filters:
        conflict = db.query(ProcedimientoModel).filter(
            ProcedimientoModel.id != id,
            or_(*conflict_filters)
        ).first()
        if conflict:
            raise HTTPException(
                status_code=400,
                detail="Ya existe otro procedimiento con ese nombre o abreviatura"
            )

    for key, value in datos.model_dump(exclude_unset=True).items():
        setattr(procedimiento, key, value)

    db.commit()
    db.refresh(procedimiento)

    return procedimiento

@router.delete("/catalogo/{id}")
def eliminar_procedimiento(
    id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Impide borrar un elemento del catálogo mientras existan registros asociados."""
    procedimiento = (
        db.query(ProcedimientoModel)
        .filter(ProcedimientoModel.id == id)
        .first()
    )

    if not procedimiento:
        raise HTTPException(
            status_code=404,
            detail="Procedimiento no encontrado"
        )
    
    count = db.query(ProceMedicoModel).filter(
        ProceMedicoModel.id_procedimiento == id
    ).count()
    
    if count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"No se puede eliminar el procedimiento porque tiene {count} registros asociados"
        )

    db.delete(procedimiento)
    db.commit()

    return {
        "message": "Procedimiento eliminado"
    }
    
    
@router.get("/", response_model=ProcedimientosListResponse)
def listar_procedimientos_medicos(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100000),
    especialidad: Optional[str] = Query(None),
    especialidad_id: Optional[int] = Query(None),
    lugar_servicio: Optional[str] = Query(None),
    id_procedimiento: Optional[int] = Query(None),
    id_catalogo_procedimiento: Optional[int] = Query(None),
    id_area_cuerpo_intervenida: Optional[int] = Query(None),
    grupo_edad: Optional[str] = Query(None, pattern="^(NEO|LAC|PRI|SEG|ADO|ADU|ADM)$"),
    sexo: Optional[str] = Query(None, pattern="^[MF]$"),
    mes: Optional[int] = Query(None, ge=1, le=12),
    anio: Optional[int] = Query(None, ge=2000, le=2100),
    fecha_inicio: Optional[date] = Query(None),
    fecha_fin: Optional[date] = Query(None)
):
    query = (
        db.query(ProceMedicoModel)
        .options(joinedload(ProceMedicoModel.procedimiento))
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

    if id_procedimiento:
        query = query.filter(
            ProceMedicoModel.id_procedimiento == id_procedimiento
        )

    if id_catalogo_procedimiento:
        query = query.filter(
            ProceMedicoModel.id_catalogo_procedimiento == id_catalogo_procedimiento
        )

    if id_area_cuerpo_intervenida:
        query = query.filter(
            ProceMedicoModel.id_area_cuerpo_intervenida == id_area_cuerpo_intervenida
        )

    if grupo_edad:
        query = query.filter(_filtro_grupo_edad(grupo_edad))

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

    Las cantidades por sexo salen del desglose `grupo_edad_detalle`; los registros
    históricos, que no tienen desglose, aportan su columna `sexo`. La anestesia se
    cuenta una sola vez por registro, no una vez por sexo.
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
        clave = "m" if sexo == "M" else "f"
        condiciones = [
            f"COALESCE((pm.grupo_edad_detalle->>'{codigo}'->>'{clave}')::int, 0) > 0"
            for codigo in GRUPOS_EDAD
        ]
        # Los registros históricos no tienen desglose, así que se filtran por su sexo
        condiciones.append("(pm.grupo_edad_detalle IS NULL AND pm.sexo = :sexo)")
        filtros.append("(" + " OR ".join(condiciones) + ")")
        params["sexo"] = sexo

    where_sql = " AND ".join(filtros) if filtros else "TRUE"

    registros = db.execute(text(f"""
        SELECT
            pm.especialidad,
            pm.lugar_servicio,
            pm.sexo,
            pm.cantidad,
            pm.anestesia,
            pm.grupo_edad_detalle
        FROM proce_medicos pm
        LEFT JOIN procedimientos p ON p.id = pm.id_procedimiento
        WHERE {where_sql}
    """), params).fetchall()

    grupos: dict[tuple, dict] = {}
    gran_total_cantidad = 0
    gran_total_anestesia = 0
    gran_total_registros = 0

    for r in registros:
        m = r._mapping
        cantidad_por_sexo = _cantidades_por_sexo(m["grupo_edad_detalle"], m["sexo"], m["cantidad"])

        for sx, cant in cantidad_por_sexo.items():
            if cant <= 0:
                continue
            clave = (m["especialidad"], m["lugar_servicio"], sx)
            g = grupos.setdefault(clave, {
                "especialidad": m["especialidad"],
                "lugar_servicio": m["lugar_servicio"],
                "sexo": sx,
                "total_cantidad": 0,
                "total_anestesia": 0,
                "total_registros": 0,
            })
            g["total_cantidad"] += cant
            g["total_registros"] += 1

        # La anestesia corresponde al registro completo, no a cada sexo
        gran_total_anestesia += int(m["anestesia"] or 0)
        gran_total_registros += 1
        gran_total_cantidad += sum(cantidad_por_sexo.values())

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


def _cantidades_por_sexo(detalle, sexo_legacy, cantidad) -> dict:
    """Cantidades M/F de un registro: desde el JSONB o, si no hay, de su sexo histórico."""
    if detalle:
        return {
            "M": sum(int(v.get("m", 0) or 0) for v in detalle.values()),
            "F": sum(int(v.get("f", 0) or 0) for v in detalle.values()),
        }
    if sexo_legacy in ("M", "F"):
        return {"M": int(cantidad or 0) if sexo_legacy == "M" else 0,
                "F": int(cantidad or 0) if sexo_legacy == "F" else 0}
    return {"M": 0, "F": 0}


@router.get("/grupos-edad")
def listar_grupos_edad(current_user: UserModel = Depends(get_current_user)):
    """Devuelve los grupos de edad (IMCI/OMS) admitidos en los registros."""
    return [
        {"codigo": codigo, "nombre": nombre}
        for codigo, nombre in GRUPOS_EDAD.items()
    ]


@router.get("/{id}", response_model=ProceMedicoResponse)
def obtener_procedimiento_medico(
    id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
    include_procedimiento: bool = Query(False, description="Incluir información del procedimiento")
):
    query = db.query(ProceMedicoModel)
    
    if include_procedimiento:
        query = query.options(joinedload(ProceMedicoModel.procedimiento))
    
    procedimiento = query.filter(ProceMedicoModel.id == id).first()

    if not procedimiento:
        raise HTTPException(
            status_code=404,
            detail="Procedimiento médico no encontrado"
        )
    
    response = ProceMedicoResponse.model_validate(procedimiento)
    
    if include_procedimiento and procedimiento.procedimiento:
        response.procedimiento_info = ProcedimientoOut.model_validate(procedimiento.procedimiento)

    return response


@router.post("/", response_model=ProceMedicoOut, status_code=201)
def crear_procedimiento_medico(
    datos: ProceMedicoCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Registra el desglose por grupo de edad/sexo y calcula el total y la anestesia."""
    catalogo = None
    if datos.id_catalogo_procedimiento:
        catalogo = db.get(CatalogoProcedimientoModel, datos.id_catalogo_procedimiento)
        if not catalogo:
            raise HTTPException(status_code=404, detail="Procedimiento no encontrado")
    elif datos.id_procedimiento:
        legacy = db.get(ProcedimientoModel, datos.id_procedimiento)
        if not legacy:
            raise HTTPException(status_code=404, detail="Procedimiento no encontrado")

    data = datos.model_dump(exclude={'created_by'})
    nuevo = ProceMedicoModel(
        **data,
        sexo=None,
        cantidad=datos.total_cantidad,
        created_by=current_user.username[:10] if current_user.username else None
    )
    nuevo.grupo_edad_detalle = _detalle_json(datos.grupo_edad_detalle)
    nuevo.anestesia = 0

    # Mantiene sincronizado el código legacy de especialidad para reportes
    if nuevo.especialidad_id and not nuevo.especialidad:
        esp = db.get(EspecialidadModel, nuevo.especialidad_id)
        nuevo.especialidad = esp.abreviatura if esp else None

    if catalogo:
        nuevo.anestesia = (catalogo.anestesia or 0) * nuevo.cantidad

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    return nuevo


@router.put("/{id}", response_model=ProceMedicoOut)
def actualizar_procedimiento_medico(
    id: int,
    datos: ProceMedicoUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Recalcula anestesia desde catálogo y cantidad, sin aceptar ese valor del cliente."""
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

    cat_id = datos.id_catalogo_procedimiento or procedimiento.id_catalogo_procedimiento
    proc_id = datos.id_procedimiento or procedimiento.id_procedimiento
    catalogo = None
    if cat_id:
        catalogo = db.get(CatalogoProcedimientoModel, cat_id)
        if not catalogo:
            raise HTTPException(
                status_code=404,
                detail="Procedimiento no encontrado"
            )
    elif proc_id:
        catalogo = (
            db.query(ProcedimientoModel)
            .filter(
                ProcedimientoModel.id == proc_id
            )
            .first()
        )

        if not catalogo:
            raise HTTPException(
                status_code=404,
                detail="Procedimiento no encontrado"
            )

    for campo, valor in datos.model_dump(
        exclude_unset=True, exclude={'anestesia'}
    ).items():
        if campo == 'grupo_edad_detalle':
            continue
        setattr(procedimiento, campo, valor)

    if datos.grupo_edad_detalle is not None:
        procedimiento.grupo_edad_detalle = _detalle_json(datos.grupo_edad_detalle)
        procedimiento.cantidad = datos.total_cantidad
        procedimiento.sexo = None

    if catalogo:
        procedimiento.anestesia = (catalogo.anestesia or 0) * procedimiento.cantidad

    # Mantiene sincronizado el código legacy de especialidad para reportes
    if procedimiento.especialidad_id and not procedimiento.especialidad:
        esp = db.get(EspecialidadModel, procedimiento.especialidad_id)
        procedimiento.especialidad = esp.abreviatura if esp else None

    db.commit()
    db.refresh(procedimiento)

    return procedimiento


@router.delete("/{id}")
def eliminar_procedimiento_medico(
    id: int,
    current_user: UserModel = Depends(get_current_user),
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
        query = query.join(ProcedimientoModel, ProcedimientoModel.id == ProceMedicoModel.id_procedimiento)
        query = query.filter(ProcedimientoModel.nombre.ilike(f"%{nombre}%"))

    total_procedimientos = query.count()
    total_cantidad = query.with_entities(func.sum(ProceMedicoModel.cantidad)).scalar() or 0

    top_query = (
        db.query(
            ProcedimientoModel.nombre,
            func.count(ProceMedicoModel.id).label('total'),
            func.coalesce(func.sum(ProceMedicoModel.cantidad), 0).label('total_cantidad'),
            func.coalesce(func.sum(ProceMedicoModel.anestesia), 0).label('total_anestesia')
        )
        .join(ProceMedicoModel, ProceMedicoModel.id_procedimiento == ProcedimientoModel.id)
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
        top_query = top_query.filter(ProcedimientoModel.nombre.ilike(f"%{nombre}%"))

    top_procedimientos = (
        top_query
        .group_by(ProcedimientoModel.id, ProcedimientoModel.nombre)
        .order_by(func.coalesce(func.sum(ProceMedicoModel.cantidad), 0).desc())
        .limit(5)
        .all()
    )

    usg_gine_query = (
        db.query(
            func.count(ProceMedicoModel.id).label('total_registros'),
            func.coalesce(func.sum(ProceMedicoModel.cantidad), 0).label('total_cantidad')
        )
        .join(ProcedimientoModel, ProcedimientoModel.id == ProceMedicoModel.id_procedimiento)
        .filter(
            ProceMedicoModel.fecha >= fecha_inicio,
            ProceMedicoModel.fecha <= fecha_fin,
            ProceMedicoModel.especialidad == 'GINE',
            ProcedimientoModel.nombre.ilike('%ultrasonido%')
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
