import unicodedata
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, cast, String, or_, desc
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from modules.pacientes.models import PacienteModel
from modules.pacientes.schemas import PacienteCreate, PacienteUpdate, PacienteListResponse
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


nombre_completo_col = func.unaccent(func.lower(PacienteModel.nombre_completo))


def filtro_nombre_campo(campo: str, valor: str):
    columna = func.unaccent(
        func.lower(
            func.jsonb_extract_path_text(PacienteModel.nombre, campo)
        )
    )
    return columna.ilike(f"%{quitar_tildes(valor)}%")


def buscar_pacientes(db: Session, filters: dict, skip: int = 0, limit: int = 50):
    query = db.query(PacienteModel).order_by(desc(PacienteModel.id))
    query = query.filter(PacienteModel.estado != "I")

    nombre_completo_json = func.unaccent(
        func.concat_ws(
            ' ',
            func.coalesce(func.jsonb_extract_path_text(PacienteModel.nombre, 'primer_nombre'), ''),
            func.coalesce(func.jsonb_extract_path_text(PacienteModel.nombre, 'segundo_nombre'), ''),
            func.coalesce(func.jsonb_extract_path_text(PacienteModel.nombre, 'otro_nombre'), ''),
            func.coalesce(func.jsonb_extract_path_text(PacienteModel.nombre, 'primer_apellido'), ''),
            func.coalesce(func.jsonb_extract_path_text(PacienteModel.nombre, 'segundo_apellido'), ''),
            func.coalesce(func.jsonb_extract_path_text(PacienteModel.nombre, 'apellido_casada'), '')
        )
    )

    q = filters.get("q")
    if q:
        palabras = [quitar_tildes(p) for p in q.split() if p.strip()]
        filtros_nombre = [nombre_completo_col.ilike(f"%{palabra}%") for palabra in palabras]
        query = query.filter(
            or_(
                cast(PacienteModel.cui, String).ilike(f"%{q.strip()}%"),
                PacienteModel.expediente.ilike(f"%{q.strip()}%"),
                and_(*filtros_nombre)
            )
        )

    nombre = filters.get("nombre")
    if nombre:
        palabras = [quitar_tildes(p) for p in nombre.split() if p.strip()]
        filtros = [nombre_completo_col.ilike(f"%{p}%") for p in palabras]
        query = query.filter(and_(*filtros))

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

    pid = filters.get("id")
    if pid:
        query = query.filter(PacienteModel.id == pid)

    sexo = filters.get("sexo")
    if sexo:
        query = query.filter(PacienteModel.sexo == sexo.upper())

    estado = filters.get("estado")
    if estado:
        query = query.filter(PacienteModel.estado == estado.upper())

    fecha_nac = filters.get("fecha_nac")
    if fecha_nac:
        try:
            query = query.filter(PacienteModel.fecha_nacimiento == fecha_nac)
        except:
            pass

    total = query.count()
    pacientes = query.offset(skip).limit(limit).all()
    return PacienteListResponse(total=total, pacientes=pacientes)


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
