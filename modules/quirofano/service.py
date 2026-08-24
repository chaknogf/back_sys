from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status

from .models import (
    FormatoProcedimientoModel,
    EstadoCirugiaModel,
    RangoEspecialistaModel,
    ProcedenciaProcedimientoModel,
    CategoriaProcedimientoModel,
    TipoProcedimientoModel,
)
from .schemas import (
    FormatoProcedimientoCreate,
    FormatoProcedimientoUpdate,
    EstadoCirugiaCreate,
    EstadoCirugiaUpdate,
    RangoEspecialistaCreate,
    RangoEspecialistaUpdate,
    ProcedenciaProcedimientoCreate,
    ProcedenciaProcedimientoUpdate,
    CategoriaProcedimientoCreate,
    CategoriaProcedimientoUpdate,
    TipoProcedimientoCreate,
    TipoProcedimientoUpdate,
)


# ========================
# Helpers genéricos
# ========================
def _verificar_unicidad(db: Session, model, campo: str, valor: str, exclude_id: int = None):
    query = db.query(model).filter(getattr(model, campo) == valor)
    if exclude_id:
        query = query.filter(model.id != exclude_id) if hasattr(model, 'id') else query
    if query.first():
        raise HTTPException(status_code=409, detail=f"El {campo} '{valor}' ya existe")


def _obtener_o_404(db: Session, model, pk_field: str, pk_value: int):
    reg = db.query(model).filter(getattr(model, pk_field) == pk_value).first()
    if not reg:
        raise HTTPException(status_code=404, detail=f"{model.__tablename__} no encontrado")
    return reg


# ========================
# Formato Procedimiento
# ========================
def listar_formatos(db: Session, solo_activos: bool = True) -> list:
    query = db.query(FormatoProcedimientoModel)
    if solo_activos:
        query = query.filter(FormatoProcedimientoModel.activo == True)
    return query.order_by(FormatoProcedimientoModel.codigo).all()


def obtener_formato(formato_id: int, db: Session) -> FormatoProcedimientoModel:
    return _obtener_o_404(db, FormatoProcedimientoModel, "formato_procedimiento_id", formato_id)


def crear_formato(data: FormatoProcedimientoCreate, db: Session) -> FormatoProcedimientoModel:
    _verificar_unicidad(db, FormatoProcedimientoModel, "codigo", data.codigo)
    reg = FormatoProcedimientoModel(codigo=data.codigo, nombre=data.nombre, activo=data.activo)
    db.add(reg)
    db.commit()
    db.refresh(reg)
    return reg


def actualizar_formato(formato_id: int, data: FormatoProcedimientoUpdate, db: Session) -> FormatoProcedimientoModel:
    reg = obtener_formato(formato_id, db)
    if data.codigo is not None:
        _verificar_unicidad(db, FormatoProcedimientoModel, "codigo", data.codigo, exclude_id=formato_id)
        reg.codigo = data.codigo
    if data.nombre is not None:
        reg.nombre = data.nombre
    if data.activo is not None:
        reg.activo = data.activo
    db.commit()
    db.refresh(reg)
    return reg


def eliminar_formato(formato_id: int, db: Session) -> dict:
    reg = obtener_formato(formato_id, db)
    db.delete(reg)
    db.commit()
    return {"eliminado": True}


# ========================
# Estado Cirugía
# ========================
def listar_estados_cirugia(db: Session, solo_activos: bool = True) -> list:
    query = db.query(EstadoCirugiaModel)
    if solo_activos:
        query = query.filter(EstadoCirugiaModel.activo == True)
    return query.order_by(EstadoCirugiaModel.codigo).all()


def obtener_estado_cirugia(estado_id: int, db: Session) -> EstadoCirugiaModel:
    return _obtener_o_404(db, EstadoCirugiaModel, "estado_cirugia_id", estado_id)


def crear_estado_cirugia(data: EstadoCirugiaCreate, db: Session) -> EstadoCirugiaModel:
    _verificar_unicidad(db, EstadoCirugiaModel, "codigo", data.codigo)
    reg = EstadoCirugiaModel(codigo=data.codigo, nombre=data.nombre, activo=data.activo)
    db.add(reg)
    db.commit()
    db.refresh(reg)
    return reg


def actualizar_estado_cirugia(estado_id: int, data: EstadoCirugiaUpdate, db: Session) -> EstadoCirugiaModel:
    reg = obtener_estado_cirugia(estado_id, db)
    if data.codigo is not None:
        _verificar_unicidad(db, EstadoCirugiaModel, "codigo", data.codigo, exclude_id=estado_id)
        reg.codigo = data.codigo
    if data.nombre is not None:
        reg.nombre = data.nombre
    if data.activo is not None:
        reg.activo = data.activo
    db.commit()
    db.refresh(reg)
    return reg


def eliminar_estado_cirugia(estado_id: int, db: Session) -> dict:
    reg = obtener_estado_cirugia(estado_id, db)
    db.delete(reg)
    db.commit()
    return {"eliminado": True}


# ========================
# Rango Especialista
# ========================
def listar_rangos_especialista(db: Session, solo_activos: bool = True) -> list:
    query = db.query(RangoEspecialistaModel)
    if solo_activos:
        query = query.filter(RangoEspecialistaModel.activo == True)
    return query.order_by(RangoEspecialistaModel.codigo).all()


def obtener_rango_especialista(rango_id: int, db: Session) -> RangoEspecialistaModel:
    return _obtener_o_404(db, RangoEspecialistaModel, "rango_especialista_id", rango_id)


def crear_rango_especialista(data: RangoEspecialistaCreate, db: Session) -> RangoEspecialistaModel:
    _verificar_unicidad(db, RangoEspecialistaModel, "codigo", data.codigo)
    reg = RangoEspecialistaModel(codigo=data.codigo, nombre=data.nombre, activo=data.activo)
    db.add(reg)
    db.commit()
    db.refresh(reg)
    return reg


def actualizar_rango_especialista(rango_id: int, data: RangoEspecialistaUpdate, db: Session) -> RangoEspecialistaModel:
    reg = obtener_rango_especialista(rango_id, db)
    if data.codigo is not None:
        _verificar_unicidad(db, RangoEspecialistaModel, "codigo", data.codigo, exclude_id=rango_id)
        reg.codigo = data.codigo
    if data.nombre is not None:
        reg.nombre = data.nombre
    if data.activo is not None:
        reg.activo = data.activo
    db.commit()
    db.refresh(reg)
    return reg


def eliminar_rango_especialista(rango_id: int, db: Session) -> dict:
    reg = obtener_rango_especialista(rango_id, db)
    db.delete(reg)
    db.commit()
    return {"eliminado": True}


# ========================
# Procedencia Procedimiento
# ========================
def listar_procedencias(db: Session, solo_activos: bool = True) -> list:
    query = db.query(ProcedenciaProcedimientoModel)
    if solo_activos:
        query = query.filter(ProcedenciaProcedimientoModel.activo == True)
    return query.order_by(ProcedenciaProcedimientoModel.codigo).all()


def obtener_procedencia(procedencia_id: int, db: Session) -> ProcedenciaProcedimientoModel:
    return _obtener_o_404(db, ProcedenciaProcedimientoModel, "procedencia_procedimiento_id", procedencia_id)


def crear_procedencia(data: ProcedenciaProcedimientoCreate, db: Session) -> ProcedenciaProcedimientoModel:
    _verificar_unicidad(db, ProcedenciaProcedimientoModel, "codigo", data.codigo)
    reg = ProcedenciaProcedimientoModel(codigo=data.codigo, nombre=data.nombre, activo=data.activo)
    db.add(reg)
    db.commit()
    db.refresh(reg)
    return reg


def actualizar_procedencia(procedencia_id: int, data: ProcedenciaProcedimientoUpdate, db: Session) -> ProcedenciaProcedimientoModel:
    reg = obtener_procedencia(procedencia_id, db)
    if data.codigo is not None:
        _verificar_unicidad(db, ProcedenciaProcedimientoModel, "codigo", data.codigo, exclude_id=procedencia_id)
        reg.codigo = data.codigo
    if data.nombre is not None:
        reg.nombre = data.nombre
    if data.activo is not None:
        reg.activo = data.activo
    db.commit()
    db.refresh(reg)
    return reg


def eliminar_procedencia(procedencia_id: int, db: Session) -> dict:
    reg = obtener_procedencia(procedencia_id, db)
    db.delete(reg)
    db.commit()
    return {"eliminado": True}


# ========================
# Categoría Procedimiento
# ========================
def listar_categorias(db: Session, solo_activos: bool = True) -> list:
    query = db.query(CategoriaProcedimientoModel)
    if solo_activos:
        query = query.filter(CategoriaProcedimientoModel.activo == True)
    return query.order_by(CategoriaProcedimientoModel.codigo).all()


def obtener_categoria(categoria_id: int, db: Session) -> CategoriaProcedimientoModel:
    return _obtener_o_404(db, CategoriaProcedimientoModel, "categoria_procedimiento_id", categoria_id)


def crear_categoria(data: CategoriaProcedimientoCreate, db: Session) -> CategoriaProcedimientoModel:
    _verificar_unicidad(db, CategoriaProcedimientoModel, "codigo", data.codigo)
    reg = CategoriaProcedimientoModel(codigo=data.codigo, nombre=data.nombre, activo=data.activo)
    db.add(reg)
    db.commit()
    db.refresh(reg)
    return reg


def actualizar_categoria(categoria_id: int, data: CategoriaProcedimientoUpdate, db: Session) -> CategoriaProcedimientoModel:
    reg = obtener_categoria(categoria_id, db)
    if data.codigo is not None:
        _verificar_unicidad(db, CategoriaProcedimientoModel, "codigo", data.codigo, exclude_id=categoria_id)
        reg.codigo = data.codigo
    if data.nombre is not None:
        reg.nombre = data.nombre
    if data.activo is not None:
        reg.activo = data.activo
    db.commit()
    db.refresh(reg)
    return reg


def eliminar_categoria(categoria_id: int, db: Session) -> dict:
    reg = obtener_categoria(categoria_id, db)
    # Verificar si tiene tipos asociados
    count = db.query(func.count(TipoProcedimientoModel.tipo_procedimiento_id)).filter(
        TipoProcedimientoModel.categoria_procedimiento_id == categoria_id
    ).scalar()
    if count > 0:
        raise HTTPException(status_code=409, detail=f"No se puede eliminar: tiene {count} tipo(s) de procedimiento asociados")
    db.delete(reg)
    db.commit()
    return {"eliminado": True}


# ========================
# Tipo Procedimiento
# ========================
def listar_tipos_procedimiento(
    db: Session,
    solo_activos: bool = True,
    categoria_id: int = None,
    q: str = None,
) -> list:
    query = db.query(TipoProcedimientoModel)
    if solo_activos:
        query = query.filter(TipoProcedimientoModel.activo == True)
    if categoria_id:
        query = query.filter(TipoProcedimientoModel.categoria_procedimiento_id == categoria_id)
    if q:
        search = f"%{q.lower()}%"
        query = query.filter(
            func.lower(TipoProcedimientoModel.nombre).like(search) |
            func.lower(TipoProcedimientoModel.codigo).like(search)
        )
    return query.order_by(TipoProcedimientoModel.codigo).all()


def obtener_tipo_procedimiento(tipo_id: int, db: Session) -> TipoProcedimientoModel:
    return _obtener_o_404(db, TipoProcedimientoModel, "tipo_procedimiento_id", tipo_id)


def crear_tipo_procedimiento(data: TipoProcedimientoCreate, db: Session) -> TipoProcedimientoModel:
    _verificar_unicidad(db, TipoProcedimientoModel, "codigo", data.codigo)
    # Verificar que la categoría existe
    cat = db.query(CategoriaProcedimientoModel).filter(
        CategoriaProcedimientoModel.categoria_procedimiento_id == data.categoria_procedimiento_id
    ).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Categoría de procedimiento no encontrada")
    reg = TipoProcedimientoModel(
        codigo=data.codigo,
        nombre=data.nombre,
        categoria_procedimiento_id=data.categoria_procedimiento_id,
        activo=data.activo,
    )
    db.add(reg)
    db.commit()
    db.refresh(reg)
    return reg


def actualizar_tipo_procedimiento(tipo_id: int, data: TipoProcedimientoUpdate, db: Session) -> TipoProcedimientoModel:
    reg = obtener_tipo_procedimiento(tipo_id, db)
    if data.codigo is not None:
        _verificar_unicidad(db, TipoProcedimientoModel, "codigo", data.codigo, exclude_id=tipo_id)
        reg.codigo = data.codigo
    if data.nombre is not None:
        reg.nombre = data.nombre
    if data.categoria_procedimiento_id is not None:
        cat = db.query(CategoriaProcedimientoModel).filter(
            CategoriaProcedimientoModel.categoria_procedimiento_id == data.categoria_procedimiento_id
        ).first()
        if not cat:
            raise HTTPException(status_code=404, detail="Categoría de procedimiento no encontrada")
        reg.categoria_procedimiento_id = data.categoria_procedimiento_id
    if data.activo is not None:
        reg.activo = data.activo
    db.commit()
    db.refresh(reg)
    return reg


def eliminar_tipo_procedimiento(tipo_id: int, db: Session) -> dict:
    reg = obtener_tipo_procedimiento(tipo_id, db)
    db.delete(reg)
    db.commit()
    return {"eliminado": True}