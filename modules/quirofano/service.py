from sqlalchemy.orm import Session
from sqlalchemy import func, desc, text
from fastapi import HTTPException, status
from datetime import date

from .models import (
    FormatoProcedimientoModel,
    EstadoCirugiaModel,
    RangoEspecialistaModel,
    ProcedenciaProcedimientoModel,
    CategoriaProcedimientoModel,
    TipoProcedimientoModel,
    QuirofanoNumeroModel,
    IntervencionQuirurgicaModel,
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
    QuirofanoNumeroCreate,
    QuirofanoNumeroUpdate,
    IntervencionQuirurgicaCreate,
    IntervencionQuirurgicaUpdate,
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


def importar_csv_tipos(contenido_csv: str, db: Session) -> dict:
    """Importa tipos de procedimiento desde CSV (columnas: especialidad, procedimiento).

    Crea la categoría (especialidad) si no existe y genera el nombre
    "Especialidad - Procedimiento". Es idempotente: los registros cuyo nombre
    ya existe se omiten.
    """
    import csv
    import io

    reader = csv.DictReader(io.StringIO(contenido_csv))
    campos = set(reader.fieldnames or [])
    requeridos = {"especialidad", "procedimiento"}
    if not requeridos.issubset(campos):
        faltantes = requeridos - campos
        raise HTTPException(
            status_code=400,
            detail=f"Faltan columnas en el CSV: {', '.join(sorted(faltantes))} (especialidad, procedimiento)",
        )

    creados = 0
    omitidos = 0
    errores = []

    for i, row in enumerate(reader, start=2):
        try:
            especialidad = " ".join((row.get("especialidad") or "").split())
            procedimiento = " ".join((row.get("procedimiento") or "").split())
            if not especialidad or not procedimiento:
                errores.append({"fila": i, "error": "Especialidad y procedimiento son obligatorios"})
                continue

            nombre = f"{especialidad} - {procedimiento}"

            # Categoría (especialidad)
            cat = db.query(CategoriaProcedimientoModel).filter(
                CategoriaProcedimientoModel.nombre == especialidad
            ).first()
            if not cat:
                cod_cat = f"CAT{abs(hash(especialidad)) % 1000000:06d}"
                cat = CategoriaProcedimientoModel(codigo=cod_cat, nombre=especialidad, activo=True)
                db.add(cat)
                db.flush()

            existe = db.query(TipoProcedimientoModel).filter(
                TipoProcedimientoModel.nombre == nombre
            ).first()
            if existe:
                omitidos += 1
                continue

            cod_tipo = f"TP{abs(hash(nombre)) % 1000000:06d}"
            db.add(TipoProcedimientoModel(
                codigo=cod_tipo,
                nombre=nombre,
                categoria_procedimiento_id=cat.categoria_procedimiento_id,
                activo=True,
            ))
            creados += 1
        except Exception as e:  # noqa: BLE001
            errores.append({"fila": i, "error": str(e)})

    db.commit()
    return {"creados": creados, "omitidos": omitidos, "errores": errores}


def truncar_tipos(db: Session) -> dict:
    """Elimina TODOS los tipos y categorías de procedimiento del quirófano."""
    db.execute(text("TRUNCATE TABLE tipo_procedimiento RESTART IDENTITY CASCADE"))
    db.execute(text("TRUNCATE TABLE categoria_procedimiento RESTART IDENTITY CASCADE"))
    db.commit()
    return {"truncado": True}


# ========================
# Número de Quirófano
# ========================
def listar_quirofanos_numero(db: Session, solo_activos: bool = True) -> list:
    query = db.query(QuirofanoNumeroModel)
    if solo_activos:
        query = query.filter(QuirofanoNumeroModel.activo == True)
    return query.order_by(QuirofanoNumeroModel.numero).all()


def obtener_quirofano_numero(qn_id: int, db: Session) -> QuirofanoNumeroModel:
    return _obtener_o_404(db, QuirofanoNumeroModel, "quirofano_numero_id", qn_id)


def crear_quirofano_numero(data: QuirofanoNumeroCreate, db: Session) -> QuirofanoNumeroModel:
    if db.query(QuirofanoNumeroModel).filter(QuirofanoNumeroModel.numero == data.numero).first():
        raise HTTPException(status_code=409, detail=f"El número de quirófano '{data.numero}' ya existe")
    reg = QuirofanoNumeroModel(numero=data.numero, nombre=data.nombre, activo=data.activo)
    db.add(reg)
    db.commit()
    db.refresh(reg)
    return reg


def actualizar_quirofano_numero(qn_id: int, data: QuirofanoNumeroUpdate, db: Session) -> QuirofanoNumeroModel:
    reg = obtener_quirofano_numero(qn_id, db)
    campos = data.model_dump(exclude_unset=True)
    if "numero" in campos and campos["numero"] is not None:
        if db.query(QuirofanoNumeroModel).filter(
            QuirofanoNumeroModel.numero == campos["numero"],
            QuirofanoNumeroModel.quirofano_numero_id != qn_id,
        ).first():
            raise HTTPException(status_code=409, detail=f"El número de quirófano '{campos['numero']}' ya existe")
    for campo, valor in campos.items():
        setattr(reg, campo, valor)
    db.commit()
    db.refresh(reg)
    return reg


def eliminar_quirofano_numero(qn_id: int, db: Session) -> dict:
    reg = obtener_quirofano_numero(qn_id, db)
    db.delete(reg)
    db.commit()
    return {"eliminado": True}


# ========================
# Intervención Quirúrgica
# ========================

def _resolve_intervencion(row) -> dict:
    """Convierte una fila con joins en dict serializable."""
    interv, paciente, medico, estado, formato, procedencia, rango, quirofano = row
    paciente_nombre = getattr(paciente, "nombre_completo", None) if paciente else None
    medico_nombre = getattr(medico, "nombre", None) if medico else None
    estado_nombre = getattr(estado, "nombre", None) if estado else None
    formato_nombre = getattr(formato, "nombre", None) if formato else None
    procedencia_nombre = getattr(procedencia, "nombre", None) if procedencia else None
    rango_nombre = getattr(rango, "nombre", None) if rango else None
    quirofano_nombre = getattr(quirofano, "nombre", None) if quirofano else None

    return {
        "intervencion_id": interv.intervencion_id,
        "paciente_id": interv.paciente_id,
        "paciente_nombre": paciente_nombre,
        "expediente": interv.expediente,
        "medico_id": interv.medico_id,
        "medico_nombre": medico_nombre,
        "procedimiento_principal": interv.procedimiento_principal,
        "procedimiento_2": interv.procedimiento_2,
        "procedimiento_3": interv.procedimiento_3,
        "procedimiento_4": interv.procedimiento_4,
        "procedimiento_5": interv.procedimiento_5,
        "area_cuerpo_intervenida": interv.area_cuerpo_intervenida,
        "estado_cirugia_id": interv.estado_cirugia_id,
        "estado_cirugia_nombre": estado_nombre,
        "formato_procedimiento_id": interv.formato_procedimiento_id,
        "formato_procedimiento_nombre": formato_nombre,
        "procedencia_procedimiento_id": interv.procedencia_procedimiento_id,
        "procedencia_procedimiento_nombre": procedencia_nombre,
        "rango_especialista_id": interv.rango_especialista_id,
        "rango_especialista_nombre": rango_nombre,
        "quirofano_numero_id": interv.quirofano_numero_id,
        "quirofano_numero_nombre": quirofano_nombre,
        "fecha": interv.fecha.isoformat() if interv.fecha else None,
        "hora_inicio_anestesia": interv.hora_inicio_anestesia.strftime("%H:%M") if interv.hora_inicio_anestesia else None,
        "hora_inicio_intervencion": interv.hora_inicio_intervencion.strftime("%H:%M") if interv.hora_inicio_intervencion else None,
        "hora_finaliza_intervencion": interv.hora_finaliza_intervencion.strftime("%H:%M") if interv.hora_finaliza_intervencion else None,
        "hora_finaliza_limpieza_prepara_quirofano": interv.hora_finaliza_limpieza_prepara_quirofano.strftime("%H:%M") if interv.hora_finaliza_limpieza_prepara_quirofano else None,
        "observaciones": interv.observaciones,
        "activo": interv.activo,
        "created_at": interv.created_at.isoformat() if interv.created_at else None,
        "updated_at": interv.updated_at.isoformat() if interv.updated_at else None,
    }


def _base_query_intervenciones(db: Session):
    from modules.pacientes.models import PacienteModel
    from modules.medicos.models import MedicoModel

    return db.query(
        IntervencionQuirurgicaModel,
        PacienteModel,
        MedicoModel,
        EstadoCirugiaModel,
        FormatoProcedimientoModel,
        ProcedenciaProcedimientoModel,
        RangoEspecialistaModel,
        QuirofanoNumeroModel,
    ).select_from(IntervencionQuirurgicaModel).outerjoin(
        PacienteModel, PacienteModel.id == IntervencionQuirurgicaModel.paciente_id
    ).outerjoin(
        MedicoModel, MedicoModel.id == IntervencionQuirurgicaModel.medico_id
    ).outerjoin(
        EstadoCirugiaModel, EstadoCirugiaModel.estado_cirugia_id == IntervencionQuirurgicaModel.estado_cirugia_id
    ).outerjoin(
        FormatoProcedimientoModel, FormatoProcedimientoModel.formato_procedimiento_id == IntervencionQuirurgicaModel.formato_procedimiento_id
    ).outerjoin(
        ProcedenciaProcedimientoModel, ProcedenciaProcedimientoModel.procedencia_procedimiento_id == IntervencionQuirurgicaModel.procedencia_procedimiento_id
    ).outerjoin(
        RangoEspecialistaModel, RangoEspecialistaModel.rango_especialista_id == IntervencionQuirurgicaModel.rango_especialista_id
    ).outerjoin(
        QuirofanoNumeroModel, QuirofanoNumeroModel.quirofano_numero_id == IntervencionQuirurgicaModel.quirofano_numero_id
    )


def listar_intervenciones(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 50,
    expediente: str | None = None,
    fecha_desde: str | None = None,
    fecha_hasta: str | None = None,
    activo: bool | None = True,
    q: str | None = None,
) -> dict:
    from modules.pacientes.models import PacienteModel

    q_base = _base_query_intervenciones(db)

    if activo is not None:
        q_base = q_base.filter(IntervencionQuirurgicaModel.activo == activo)
    if expediente:
        q_base = q_base.filter(
            func.lower(IntervencionQuirurgicaModel.expediente).like(f"%{expediente.lower()}%")
        )
    if fecha_desde:
        q_base = q_base.filter(IntervencionQuirurgicaModel.fecha >= fecha_desde)
    if fecha_hasta:
        q_base = q_base.filter(IntervencionQuirurgicaModel.fecha <= fecha_hasta)
    if q:
        like = f"%{q.lower()}%"
        q_base = q_base.filter(
            func.lower(PacienteModel.nombre_completo).like(like)
            | func.lower(IntervencionQuirurgicaModel.expediente).like(like)
        )

    total = q_base.count()
    rows = (
        q_base
        .order_by(desc(IntervencionQuirurgicaModel.fecha))
        .offset(skip)
        .limit(limit)
        .all()
    )

    return {
        "total": total,
        "intervenciones": [_resolve_intervencion(row) for row in rows],
    }


def obtener_intervencion(intervencion_id: int, db: Session) -> dict:
    row = _base_query_intervenciones(db).filter(
        IntervencionQuirurgicaModel.intervencion_id == intervencion_id,
        IntervencionQuirurgicaModel.activo == True,
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail="Intervención no encontrada")
    return _resolve_intervencion(row)


def crear_intervencion(data: IntervencionQuirurgicaCreate, db: Session, created_by: str | None = None) -> dict:
    # Validar paciente existe
    from modules.pacientes.models import PacienteModel
    paciente = db.query(PacienteModel).filter(PacienteModel.id == data.paciente_id).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    # Validar catálogos si se pasaron
    if data.estado_cirugia_id and not db.query(EstadoCirugiaModel).filter(
        EstadoCirugiaModel.estado_cirugia_id == data.estado_cirugia_id
    ).first():
        raise HTTPException(status_code=404, detail="Estado de cirugía no encontrado")
    if data.quirofano_numero_id and not db.query(QuirofanoNumeroModel).filter(
        QuirofanoNumeroModel.quirofano_numero_id == data.quirofano_numero_id
    ).first():
        raise HTTPException(status_code=404, detail="Número de quirófano no encontrado")
    if data.medico_id:
        from modules.medicos.models import MedicoModel
        if not db.query(MedicoModel).filter(MedicoModel.id == data.medico_id).first():
            raise HTTPException(status_code=404, detail="Médico no encontrado")

    reg = IntervencionQuirurgicaModel(
        paciente_id=data.paciente_id,
        expediente=data.expediente or paciente.expediente,
        procedimiento_principal=data.procedimiento_principal,
        procedimiento_2=data.procedimiento_2,
        procedimiento_3=data.procedimiento_3,
        procedimiento_4=data.procedimiento_4,
        procedimiento_5=data.procedimiento_5,
        area_cuerpo_intervenida=data.area_cuerpo_intervenida,
        estado_cirugia_id=data.estado_cirugia_id,
        formato_procedimiento_id=data.formato_procedimiento_id,
        procedencia_procedimiento_id=data.procedencia_procedimiento_id,
        rango_especialista_id=data.rango_especialista_id,
        quirofano_numero_id=data.quirofano_numero_id,
        medico_id=data.medico_id,
        fecha=data.fecha,
        hora_inicio_anestesia=data.hora_inicio_anestesia,
        hora_inicio_intervencion=data.hora_inicio_intervencion,
        hora_finaliza_intervencion=data.hora_finaliza_intervencion,
        hora_finaliza_limpieza_prepara_quirofano=data.hora_finaliza_limpieza_prepara_quirofano,
        observaciones=data.observaciones,
        activo=True,
    )
    db.add(reg)
    db.commit()
    db.refresh(reg)
    return obtener_intervencion(reg.intervencion_id, db)


def actualizar_intervencion(intervencion_id: int, data: IntervencionQuirurgicaUpdate, db: Session) -> dict:
    reg = db.query(IntervencionQuirurgicaModel).filter(
        IntervencionQuirurgicaModel.intervencion_id == intervencion_id
    ).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Intervención no encontrada")

    campos = data.model_dump(exclude_unset=True)
    for campo, valor in campos.items():
        setattr(reg, campo, valor)
    db.commit()
    db.refresh(reg)
    return obtener_intervencion(reg.intervencion_id, db)


def eliminar_intervencion(intervencion_id: int, db: Session) -> dict:
    reg = db.query(IntervencionQuirurgicaModel).filter(
        IntervencionQuirurgicaModel.intervencion_id == intervencion_id
    ).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Intervención no encontrada")
    reg.activo = False
    db.commit()
    return {"eliminado": True}