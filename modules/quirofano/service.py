from sqlalchemy.orm import Session
from sqlalchemy import func, desc, text, inspect as sa_inspect
from fastapi import HTTPException, status
from datetime import date

from modules.especialidades.models import EspecialidadModel

from .models import (
    FormatoProcedimientoModel,
    EstadoCirugiaModel,
    RangoEspecialistaModel,
    ProcedenciaProcedimientoModel,
    ProcedimientoQuirofanoModel,
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
    ProcedimientoQuirofanoCreate,
    ProcedimientoQuirofanoUpdate,
    QuirofanoNumeroCreate,
    QuirofanoNumeroUpdate,
    IntervencionQuirurgicaCreate,
    IntervencionQuirurgicaUpdate,
)


# ========================
# Helpers genéricos
# ========================
def _pk_field(model) -> str | None:
    try:
        return sa_inspect(model).primary_key[0].key
    except Exception:  # noqa: BLE001
        return None


def _verificar_unicidad(db: Session, model, campo: str, valor: str, exclude_id: int = None):
    query = db.query(model).filter(getattr(model, campo) == valor)
    if exclude_id is not None:
        pk = _pk_field(model)
        if pk:
            query = query.filter(getattr(model, pk) != exclude_id)
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
# Procedimiento Quirófano
# ========================
def _obtener_especialidad_o_404(especialidad_id: int, db: Session) -> EspecialidadModel:
    esp = db.query(EspecialidadModel).filter(EspecialidadModel.id == especialidad_id).first()
    if not esp:
        raise HTTPException(status_code=404, detail="Especialidad no encontrada")
    return esp


def _verificar_duplicado_esp_nombre(
    db: Session, especialidad_id: int | None, nombre: str, exclude_id: int | None = None
) -> None:
    query = db.query(ProcedimientoQuirofanoModel).filter(
        func.lower(ProcedimientoQuirofanoModel.nombre) == nombre.strip().lower(),
    )
    if especialidad_id is None:
        query = query.filter(ProcedimientoQuirofanoModel.especialidad_id.is_(None))
        donde = "en 'Todas (mixta)'"
    else:
        query = query.filter(ProcedimientoQuirofanoModel.especialidad_id == especialidad_id)
        donde = "en esa especialidad"
    if exclude_id:
        query = query.filter(ProcedimientoQuirofanoModel.procedimiento_quirofano_id != exclude_id)
    if query.first():
        raise HTTPException(
            status_code=409,
            detail=f"El procedimiento '{nombre}' ya existe {donde}",
        )


def listar_procedimientos_quirofano(
    db: Session,
    solo_activos: bool = True,
    especialidad_id: int = None,
    incluir_mixtos: bool = False,
    q: str = None,
) -> list:
    query = db.query(ProcedimientoQuirofanoModel)
    if solo_activos:
        query = query.filter(ProcedimientoQuirofanoModel.activo == True)
    if especialidad_id:
        filtro = ProcedimientoQuirofanoModel.especialidad_id == especialidad_id
        if incluir_mixtos:
            filtro = filtro | ProcedimientoQuirofanoModel.especialidad_id.is_(None)
        query = query.filter(filtro)
    if q:
        search = f"%{q.lower()}%"
        query = query.filter(
            func.lower(ProcedimientoQuirofanoModel.nombre).like(search) |
            func.lower(ProcedimientoQuirofanoModel.codigo).like(search)
        )
    return query.order_by(ProcedimientoQuirofanoModel.codigo).all()


def obtener_procedimiento_quirofano(proc_id: int, db: Session) -> ProcedimientoQuirofanoModel:
    return _obtener_o_404(db, ProcedimientoQuirofanoModel, "procedimiento_quirofano_id", proc_id)


def _generar_codigo_procedimiento(especialidad: str | None, nombre: str, db: Session) -> str:
    ref = especialidad or "MIXTA"
    base = f"TP{abs(hash(f'{ref} || {nombre}')) % 1000000:06d}"
    codigo = base
    i = 1
    while db.query(ProcedimientoQuirofanoModel).filter(
        ProcedimientoQuirofanoModel.codigo == codigo
    ).first():
        codigo = f"{base}-{i}"[:10]
        i += 1
    return codigo


def crear_procedimiento_quirofano(data: ProcedimientoQuirofanoCreate, db: Session) -> ProcedimientoQuirofanoModel:
    esp = None
    if data.especialidad_id is not None:
        esp = _obtener_especialidad_o_404(data.especialidad_id, db)
    _verificar_duplicado_esp_nombre(db, data.especialidad_id, data.nombre)
    codigo = (data.codigo or "").strip()
    if codigo:
        _verificar_unicidad(db, ProcedimientoQuirofanoModel, "codigo", codigo)
    else:
        codigo = _generar_codigo_procedimiento(esp.nombre if esp else None, data.nombre, db)
    reg = ProcedimientoQuirofanoModel(
        codigo=codigo,
        nombre=data.nombre,
        especialidad_id=data.especialidad_id,
        activo=data.activo,
    )
    db.add(reg)
    db.commit()
    db.refresh(reg)
    return reg


def actualizar_procedimiento_quirofano(
    proc_id: int, data: ProcedimientoQuirofanoUpdate, db: Session
) -> ProcedimientoQuirofanoModel:
    reg = obtener_procedimiento_quirofano(proc_id, db)
    campos = data.model_dump(exclude_unset=True)

    if "especialidad_id" in campos:
        if campos["especialidad_id"] is not None:
            _obtener_especialidad_o_404(campos["especialidad_id"], db)
        reg.especialidad_id = campos["especialidad_id"]
    if "nombre" in campos:
        reg.nombre = campos["nombre"]

    if "especialidad_id" in campos or "nombre" in campos:
        _verificar_duplicado_esp_nombre(
            db, reg.especialidad_id, reg.nombre, exclude_id=proc_id
        )
    if "codigo" in campos:
        _verificar_unicidad(
            db, ProcedimientoQuirofanoModel, "codigo", campos["codigo"], exclude_id=proc_id
        )
        reg.codigo = campos["codigo"]
    if "activo" in campos:
        reg.activo = campos["activo"]
    db.commit()
    db.refresh(reg)
    return reg


def eliminar_procedimiento_quirofano(proc_id: int, db: Session) -> dict:
    reg = obtener_procedimiento_quirofano(proc_id, db)
    db.delete(reg)
    db.commit()
    return {"eliminado": True}


def importar_csv_procedimientos(contenido_csv: str, db: Session) -> dict:
    """Importa procedimientos de quirófano desde CSV.

    Columnas: `referencia_especialidad` (o su alias `especialidad`) y
    `procedimiento` (o su alias `procedimientos`). La especialidad debe existir en la tabla `especialidades`
    (se busca por nombre, sin acentos ni mayúsculas) y el `nombre` del procedimiento se guarda SOLO con el
    nombre del procedimiento. La especialidad es OPCIONAL: si viene vacía, `null` o no
    coincide con el catálogo, el procedimiento se guarda como "Todas (mixta)"
    (especialidad_id NULL). Es
    idempotente: la existencia se evalúa por (especialidad, nombre) sin
    distinguir mayúsculas.
    """
    import csv
    import io

    primera_linea = (contenido_csv or "").splitlines()
    primera_linea = primera_linea[0] if primera_linea else ""
    try:
        delimitador = csv.Sniffer().sniff(
            (contenido_csv or "")[:8192], delimiters="\t,;|"
        ).delimiter
    except csv.Error:
        delimitador = (
            "\t" if primera_linea.count("\t") > primera_linea.count(",")
            else (";" if primera_linea.count(";") > 0 else ",")
        )

    reader = csv.DictReader(io.StringIO(contenido_csv), delimiter=delimitador)
    fieldnames = [c for c in (reader.fieldnames or []) if c is not None]
    campos = {c.strip().strip('"').lower() for c in fieldnames}

    def _hallar_columna(*alias):
        for c in campos:
            if any(a in c for a in alias):
                return c
        return None

    col_ref = _hallar_columna("referencia_especialidad", "especialidad", "especial")
    col_proc = _hallar_columna("procedimiento")
    if col_ref is None or col_proc is None:
        if len(fieldnames) == 2:
            col_ref = (fieldnames[0] or "").strip().strip('"').lower()
            col_proc = (fieldnames[1] or "").strip().strip('"').lower()
        if not col_ref or not col_proc:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Faltan columnas en el CSV: "
                    "especialidad, procedimiento (referencia_especialidad, procedimiento)"
                ),
            )

    creados = 0
    omitidos = 0
    errores = []

    for i, row in enumerate(reader, start=2):
        try:
            norm = {k.strip().strip('"').lower(): v for k, v in row.items() if k}
            especialidad = " ".join((norm.get(col_ref) or "").split())
            if especialidad.lower() == "null":
                especialidad = ""
            procedimiento = " ".join((norm.get(col_proc) or "").split())
            if not procedimiento:
                errores.append({"fila": i, "error": "El procedimiento es obligatorio"})
                continue

            esp_id = None
            esp_nombre = None
            if especialidad:
                esp = db.query(EspecialidadModel).filter(
                    func.unaccent(func.lower(EspecialidadModel.nombre))
                    == func.unaccent(especialidad.lower())
                ).first()
                if esp:
                    esp_id = esp.id
                    esp_nombre = esp.nombre
                # Especialidad opcional: si el valor no coincide con el catálogo
                # (o viene vacío/null), el procedimiento se importa como mixta.

            existe_query = db.query(ProcedimientoQuirofanoModel).filter(
                func.lower(ProcedimientoQuirofanoModel.nombre) == procedimiento.lower(),
            )
            if esp_id is None:
                existe_query = existe_query.filter(
                    ProcedimientoQuirofanoModel.especialidad_id.is_(None)
                )
            else:
                existe_query = existe_query.filter(
                    ProcedimientoQuirofanoModel.especialidad_id == esp_id
                )
            if existe_query.first():
                omitidos += 1
                continue

            cod_proc = _generar_codigo_procedimiento(esp_nombre, procedimiento, db)
            db.add(ProcedimientoQuirofanoModel(
                codigo=cod_proc,
                nombre=procedimiento,
                especialidad_id=esp_id,
                activo=True,
            ))
            creados += 1
        except Exception as e:  # noqa: BLE001
            errores.append({"fila": i, "error": str(e)})

    db.commit()
    return {"creados": creados, "omitidos": omitidos, "errores": errores}


def truncar_procedimientos(db: Session) -> dict:
    """Elimina TODOS los procedimientos de quirófano."""
    db.execute(text("TRUNCATE TABLE procedimiento_quirofano RESTART IDENTITY CASCADE"))
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