import re
import unicodedata
from datetime import date, datetime, timedelta, timezone
from typing import Optional
from sqlalchemy.orm import Session, load_only
from sqlalchemy import and_, func, cast, Integer, String, or_, desc, case
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from modules.pacientes.models import PacienteModel
from modules.pacientes.schemas import PacienteCreate, PacienteUpdate, PacienteListResponse, PacientesResumen
from modules.expediente.service import generar_expediente


def quitar_tildes(texto: str) -> str:
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    ).lower()


def agregar_evento(paciente, usuario, accion, expediente_duplicado: bool | None = None, detalle: str = ""):
    evento = {
        "usuario": usuario or "sistema",
        "registro": datetime.now(timezone.utc).isoformat(),
        "accion": accion,
        "expediente_duplicado": expediente_duplicado,
        "detalle": detalle
    }
    if paciente.metadatos is None:
        paciente.metadatos = []
    paciente.metadatos.append(evento)


def normalizar_metadatos(paciente):
    if not paciente.metadatos:
        return
    for m in paciente.metadatos:
        if not m.get("accion"):
            m["accion"] = "ACTUALIZADO"
        if not m.get("usuario"):
            m["usuario"] = "sistema"
        if m.get("registro") and not isinstance(m["registro"], str):
            m["registro"] = m["registro"].isoformat()


nombre_completo_col = func.f_unaccent(func.lower(PacienteModel.nombre_completo))


def filtro_nombre_campo(campo: str, valor: str):
    columna = func.unaccent(
        func.lower(
            func.jsonb_extract_path_text(PacienteModel.nombre, campo)
        )
    )
    return columna.ilike(f"%{quitar_tildes(valor)}%")


def buscar_neonatales(db: Session, filters: dict, skip: int = 0, limit: int = 50):
    _LIST_COLS = [
        PacienteModel.id, PacienteModel.cui, PacienteModel.expediente,
        PacienteModel.pasaporte, PacienteModel.nombre, PacienteModel.nombre_completo,
        PacienteModel.sexo, PacienteModel.fecha_nacimiento, PacienteModel.estado,
        PacienteModel.datos_extra, PacienteModel.es_personal_hospital,
    ]
    query = db.query(PacienteModel).options(load_only(*_LIST_COLS)).order_by(desc(PacienteModel.id))
    query = query.filter(PacienteModel.estado != "I")
    query = query.filter(
        func.jsonb_extract_path_text(PacienteModel.datos_extra, 'neonatales', 'extrahositalario') == 'false'
    )

    nombre = filters.get("nombre")
    if nombre:
        palabras = [quitar_tildes(p) for p in nombre.split() if p.strip()]
        filtros = [nombre_completo_col.ilike(f"%{p}%") for p in palabras]
        query = query.filter(and_(*filtros))

    expediente = filters.get("expediente")
    if expediente:
        query = query.filter(PacienteModel.expediente == expediente)

    pid = filters.get("id_paciente")
    if pid:
        query = query.filter(PacienteModel.id == pid)

    sexo = filters.get("sexo")
    if sexo:
        query = query.filter(PacienteModel.sexo == sexo.upper())

    estado = filters.get("estado")
    if estado:
        query = query.filter(PacienteModel.estado == estado.upper())

    fecha_nac = filters.get("fecha_nacimiento")
    if fecha_nac:
        try:
            query = query.filter(PacienteModel.fecha_nacimiento == fecha_nac)
        except:
            pass

    exp_madre = filters.get("expediente_madre")
    if exp_madre:
        query = query.filter(
            func.jsonb_extract_path_text(PacienteModel.datos_extra, 'neonatales', 'expediente_madre') == exp_madre
        )

    total = query.count()
    pacientes = query.offset(skip).limit(limit).all()
    return PacienteListResponse(total=total, pacientes=pacientes)


def buscar_personal_hospital(db: Session, filters: dict | None = None, skip: int = 0, limit: int = 50):
    _LIST_COLS = [
        PacienteModel.id, PacienteModel.cui, PacienteModel.expediente,
        PacienteModel.pasaporte, PacienteModel.nombre, PacienteModel.nombre_completo,
        PacienteModel.sexo, PacienteModel.fecha_nacimiento, PacienteModel.estado,
        PacienteModel.datos_extra,
    ]
    query = db.query(PacienteModel).options(load_only(*_LIST_COLS)).order_by(desc(PacienteModel.id))
    query = query.filter(PacienteModel.estado != "I")
    query = query.filter(PacienteModel.es_personal_hospital == 'S')

    filters = filters or {}
    for campo in ["primer_nombre", "segundo_nombre", "primer_apellido", "segundo_apellido"]:
        val = filters.get(campo)
        if val:
            query = query.filter(filtro_nombre_campo(campo, val))

    cui = filters.get("cui")
    if cui:
        if cui.isdigit():
            query = query.filter(PacienteModel.cui == int(cui))
        else:
            query = query.filter(cast(PacienteModel.cui, String).ilike(f"%{cui}%"))

    expediente = filters.get("expediente")
    if expediente:
        query = query.filter(PacienteModel.expediente == expediente)

    total = query.count()
    pacientes = query.offset(skip).limit(limit).all()
    return PacienteListResponse(total=total, pacientes=pacientes)


def buscar_pacientes(db: Session, filters: dict, skip: int = 0, limit: int = 50):
    from modules.prestamos.models import Prestamo

    _LIST_COLS = [
        PacienteModel.id, PacienteModel.cui, PacienteModel.expediente,
        PacienteModel.pasaporte, PacienteModel.nombre, PacienteModel.nombre_completo,
        PacienteModel.sexo, PacienteModel.fecha_nacimiento, PacienteModel.estado,
        PacienteModel.datos_extra,
    ]

    # JOIN con prestamos activos por paciente_id — último préstamo activo por paciente
    # prestamos.id_paciente = pacientes.id AND prestamos.activo = true
    latest_loan_subq = (
        db.query(
            Prestamo.id_paciente,
            func.max(Prestamo.fecha_prestamo).label("max_fecha"),
        )
        .filter(Prestamo.activo.is_(True))
        .group_by(Prestamo.id_paciente)
        .subquery()
    )
    loan_subq = (
        db.query(
            Prestamo.id_paciente,
            Prestamo.fecha_prestamo,
            Prestamo.solicitante,
        )
        .filter(Prestamo.activo.is_(True))
        .subquery("loan_activo")
    )

    def _apply_filters(q):
        q = q.filter(PacienteModel.estado != "I")
        v = filters.get("q")
        if v:
            termino = v.strip()
            palabras = [quitar_tildes(p) for p in termino.split() if p.strip()]
            filtros_nombre = [nombre_completo_col.ilike(f"%{palabra}%") for palabra in palabras]
            q = q.filter(
                or_(
                    cast(PacienteModel.cui, String).ilike(f"%{termino}%"),
                    PacienteModel.expediente.ilike(f"%{termino}%"),
                    and_(*filtros_nombre),
                )
            )
        v = filters.get("nombre")
        if v:
            palabras = [quitar_tildes(p) for p in v.split() if p.strip()]
            filtros = [nombre_completo_col.ilike(f"%{p}%") for p in palabras]
            q = q.filter(and_(*filtros))
        for campo in ["primer_nombre", "segundo_nombre", "primer_apellido", "segundo_apellido"]:
            val = filters.get(campo)
            if val:
                q = q.filter(filtro_nombre_campo(campo, val))
        v = filters.get("cui")
        if v:
            if v.isdigit():
                q = q.filter(PacienteModel.cui == int(v))
            else:
                q = q.filter(cast(PacienteModel.cui, String).ilike(f"%{v}%"))
        v = filters.get("expediente")
        if v:
            q = q.filter(PacienteModel.expediente == v)
        v = filters.get("id")
        if v:
            q = q.filter(PacienteModel.id == v)
        v = filters.get("sexo")
        if v:
            q = q.filter(PacienteModel.sexo == v.upper())
        v = filters.get("estado")
        if v:
            q = q.filter(PacienteModel.estado == v.upper())
        v = filters.get("fecha_nac")
        if v:
            try:
                q = q.filter(PacienteModel.fecha_nacimiento == v)
            except:
                pass
        return q

    # Query para total (solo pacientes, no duplica por join)
    count_q = db.query(func.count(func.distinct(PacienteModel.id))).select_from(PacienteModel).outerjoin(
        latest_loan_subq, PacienteModel.id == latest_loan_subq.c.id_paciente
    ).outerjoin(
        loan_subq,
        and_(
            loan_subq.c.id_paciente == PacienteModel.id,
            loan_subq.c.fecha_prestamo == latest_loan_subq.c.max_fecha,
        ),
    )
    count_q = _apply_filters(count_q)
    total = count_q.scalar() or 0

    # Query para datos — JOIN que trae fecha_prestamo + solicitante del préstamo activo
    data_q = (
        db.query(PacienteModel, loan_subq.c.fecha_prestamo, loan_subq.c.solicitante)
        .select_from(PacienteModel)
        .outerjoin(latest_loan_subq, PacienteModel.id == latest_loan_subq.c.id_paciente)
        .outerjoin(
            loan_subq,
            and_(
                loan_subq.c.id_paciente == PacienteModel.id,
                loan_subq.c.fecha_prestamo == latest_loan_subq.c.max_fecha,
            ),
        )
        .options(load_only(*_LIST_COLS))
        .order_by(desc(PacienteModel.id))
    )
    data_q = _apply_filters(data_q)
    rows = data_q.offset(skip).limit(limit).all()

    result_pacientes = []
    for paciente, fecha_prestamo, solicitante in rows:
        # Inyectar campos de préstamo para que PacientesResumen los lea vía from_attributes
        paciente.fecha_prestamo = fecha_prestamo
        paciente.solicitante = solicitante
        result_pacientes.append(PacientesResumen.model_validate(paciente))

    return PacienteListResponse(total=total, pacientes=result_pacientes)


def obtener_paciente(db: Session, paciente_id: int):
    paciente = db.get(PacienteModel, paciente_id)
    if not paciente:
        raise HTTPException(status_code=404, detail=f"Paciente con ID {paciente_id} no encontrado")
    if paciente.metadatos:
        for m in paciente.metadatos:
            if not m.get("accion"):
                m["accion"] = "ACTUALIZADO"
            if not m.get("usuario"):
                m["usuario"] = "sistema"
            registro = m.get("registro")
            if registro is None:
                m["registro"] = datetime.now(timezone.utc).isoformat()
            elif isinstance(registro, datetime):
                m["registro"] = registro.isoformat()
            elif not isinstance(registro, str):
                m["registro"] = str(registro)
    return paciente


def crear_paciente(db: Session, paciente_in: PacienteCreate, auto_expediente: bool, username: str):
    data = paciente_in.model_dump()
    for field in ("cui", "expediente", "pasaporte"):
        if not data.get(field) or str(data.get(field)).strip() == "":
            data[field] = None

    nombre_dict = paciente_in.nombre.model_dump()
    for campo in ["primer_nombre", "segundo_nombre", "otro_nombre",
                  "primer_apellido", "segundo_apellido", "apellido_casada"]:
        if nombre_dict.get(campo):
            nombre_dict[campo] = nombre_dict[campo].strip().title()
    existente = db.query(PacienteModel).filter(
        PacienteModel.nombre == nombre_dict,
        PacienteModel.sexo == paciente_in.sexo,
        PacienteModel.fecha_nacimiento == paciente_in.fecha_nacimiento
    ).first()
    if existente:
        raise HTTPException(
            status_code=409,
            detail="Ya existe un paciente registrado con el mismo nombre, sexo y fecha de nacimiento"
        )

    if auto_expediente and not data.get("expediente"):
        data["expediente"] = generar_expediente(db)
    try:
        nuevo = PacienteModel(**data)
        agregar_evento(nuevo, usuario=username, accion="CREADO")
        db.add(nuevo)
        db.commit()
        db.refresh(nuevo)
        return nuevo
    except IntegrityError as e:
        db.rollback()
        error_msg = str(e.orig).lower()
        if "cui" in error_msg:
            raise HTTPException(status_code=400, detail=f"Ya existe un paciente con el CUI: {data.get('cui')}")
        elif "expediente" in error_msg:
            raise HTTPException(status_code=400, detail=f"Ya existe un paciente con el expediente: {data.get('expediente')}")
        else:
            raise HTTPException(status_code=400, detail="Datos duplicados o inválidos")


def _build_ultima_consulta_subquery(db: Session):
    from modules.consultas.models import ConsultaModel
    return (
        db.query(
            ConsultaModel.paciente_id,
            func.max(ConsultaModel.fecha_consulta).label("ultima_fecha"),
        )
        .filter(ConsultaModel.activo.is_(True))
        .group_by(ConsultaModel.paciente_id)
        .subquery()
    )


_LIST_COLS = [
    PacienteModel.id, PacienteModel.cui, PacienteModel.expediente,
    PacienteModel.pasaporte, PacienteModel.nombre, PacienteModel.nombre_completo,
    PacienteModel.sexo, PacienteModel.fecha_nacimiento, PacienteModel.estado,
    PacienteModel.datos_extra,
]


def _apply_q_filter(query, q):
    if not q:
        return query
    palabras = [quitar_tildes(p) for p in q.split() if p.strip()]
    filtros_nombre = [nombre_completo_col.ilike(f"%{palabra}%") for palabra in palabras]
    return query.filter(
        or_(
            PacienteModel.expediente.ilike(f"%{q.strip()}%"),
            and_(*filtros_nombre),
        )
    )


def _parse_expediente_ref(val: str):
    """'25A-10' → (25, 10), '105' → (None, 105)"""
    m = re.match(r'^(\d{2})[A-Z]-(\d+)$', val)
    if m:
        return int(m.group(1)), int(m.group(2))
    m = re.search(r'(\d+)$', val)
    if m:
        return None, int(m.group(1))
    return None, None


def _apply_expediente_range(query, desde: Optional[str], hasta: Optional[str]):
    if not desde and not hasta:
        return query

    num_part = cast(func.substring(PacienteModel.expediente, r'(\d+)$'), Integer)
    anio_part = cast(func.substring(PacienteModel.expediente, r'^(\d{2})A-'), Integer)

    if desde:
        d_anio, d_num = _parse_expediente_ref(desde)
        if d_num is not None:
            cond = [num_part >= d_num]
            if d_anio is not None:
                cond.append(or_(anio_part.is_(None), anio_part == d_anio))
            query = query.filter(and_(*cond))

    if hasta:
        h_anio, h_num = _parse_expediente_ref(hasta)
        if h_num is not None:
            cond = [num_part <= h_num]
            if h_anio is not None:
                cond.append(or_(anio_part.is_(None), anio_part == h_anio))
            query = query.filter(and_(*cond))

    return query


def _exec_expedientes_query(
    db: Session,
    ultima_consulta,
    join_type: str,
    extra_filter,
    q: Optional[str],
    skip: int,
    limit: int,
    expediente_desde: Optional[str] = None,
    expediente_hasta: Optional[str] = None,
):
    hace_un_anio = date(date.today().year - 1, date.today().month, date.today().day)

    count_query = (
        db.query(PacienteModel.id)
        .join(ultima_consulta, PacienteModel.id == ultima_consulta.c.paciente_id)
        .filter(PacienteModel.estado != "I")
        .filter(PacienteModel.expediente.isnot(None))
        .filter(PacienteModel.expediente != "")
    )
    count_query = _apply_expediente_range(count_query, expediente_desde, expediente_hasta)
    if extra_filter == "reciente":
        count_query = count_query.filter(ultima_consulta.c.ultima_fecha > hace_un_anio)
    else:
        count_query = count_query.filter(
            or_(
                ultima_consulta.c.ultima_fecha.is_(None),
                ultima_consulta.c.ultima_fecha <= hace_un_anio,
            )
        )
    count_query = _apply_q_filter(count_query, q)
    total = count_query.count()

    data_query = (
        db.query(PacienteModel, ultima_consulta.c.ultima_fecha)
        .options(load_only(*_LIST_COLS))
        .join(ultima_consulta, PacienteModel.id == ultima_consulta.c.paciente_id)
        .filter(PacienteModel.estado != "I")
        .filter(PacienteModel.expediente.isnot(None))
        .filter(PacienteModel.expediente != "")
    )
    data_query = _apply_expediente_range(data_query, expediente_desde, expediente_hasta)
    if extra_filter == "reciente":
        data_query = data_query.filter(ultima_consulta.c.ultima_fecha > hace_un_anio)
    else:
        data_query = data_query.filter(
            or_(
                ultima_consulta.c.ultima_fecha.is_(None),
                ultima_consulta.c.ultima_fecha <= hace_un_anio,
            )
        )
    data_query = _apply_q_filter(data_query, q)
    order_col = PacienteModel.expediente if (expediente_desde or expediente_hasta) else desc(PacienteModel.id)
    rows = data_query.order_by(order_col).offset(skip).limit(limit).all()

    pacientes = []
    for paciente, ultima_fecha in rows:
        paciente.ultima_consulta = ultima_fecha
        pacientes.append(paciente)

    return PacienteListResponse(total=total, pacientes=pacientes)


def buscar_pacientes_con_consultas_recientes(
    db: Session,
    q: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    expediente_desde: Optional[str] = None,
    expediente_hasta: Optional[str] = None,
):
    ultima_consulta = _build_ultima_consulta_subquery(db)
    return _exec_expedientes_query(db, ultima_consulta, "inner", "reciente", q, skip, limit, expediente_desde, expediente_hasta)


def buscar_pacientes_sin_consultas_recientes(
    db: Session,
    q: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    expediente_desde: Optional[str] = None,
    expediente_hasta: Optional[str] = None,
):
    ultima_consulta = _build_ultima_consulta_subquery(db)
    return _exec_expedientes_query(db, ultima_consulta, "outer", "no_reciente", q, skip, limit, expediente_desde, expediente_hasta)
