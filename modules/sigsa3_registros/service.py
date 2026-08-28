from datetime import date
from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session
from typing import Optional

from modules.sigsa3.models import Sigsa3RegistroModel
from modules.pacientes.models import PacienteModel
from modules.consultas.models import ConsultaModel
from modules.medicos.models import MedicoModel
from modules.personal_salud.models import PersonalSaludModel
from modules.cie10.models import Cie10Model
from modules.especialidades.models import EspecialidadModel
from modules.sigsa3_registros.models import TipoConsultaSigsa3Model
from modules.sigsa3_registros.schemas import Sigsa3RegistroCreate, Sigsa3RegistroUpdate


def _base_query(db: Session):
    """Consulta con JOIN a catálogos para enriquecer la respuesta."""
    return (
        db.query(
            Sigsa3RegistroModel,
            PacienteModel.nombre_completo,
            PacienteModel.expediente,
            PacienteModel.sexo,
            MedicoModel.nombre,
            PersonalSaludModel.nombre,
            TipoConsultaSigsa3Model.nombre,
            Cie10Model.codigo,
            Cie10Model.descripcion,
            EspecialidadModel.nombre,
        )
        .outerjoin(PacienteModel, Sigsa3RegistroModel.paciente_id == PacienteModel.id)
        .outerjoin(MedicoModel, Sigsa3RegistroModel.medico_id == MedicoModel.id)
        .outerjoin(PersonalSaludModel, Sigsa3RegistroModel.personal_salud_id == PersonalSaludModel.id)
        .outerjoin(TipoConsultaSigsa3Model, Sigsa3RegistroModel.tipo_consulta_id == TipoConsultaSigsa3Model.id)
        .outerjoin(Cie10Model, Sigsa3RegistroModel.codigo_cie_10_id == Cie10Model.id)
        .outerjoin(EspecialidadModel, Sigsa3RegistroModel.especialidad_id == EspecialidadModel.id)
    )


def _filtros(
    paciente_id: Optional[int] = None,
    medico_id: Optional[int] = None,
    personal_salud_id: Optional[int] = None,
    consulta_id: Optional[int] = None,
    tipo_consulta_id: Optional[int] = None,
    especialidad_id: Optional[int] = None,
    fecha_consulta: Optional[date] = None,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    nombre_paciente: Optional[str] = None,
    no_historia_clinica: Optional[str] = None,
    q: Optional[str] = None,
):
    conds = []
    if paciente_id is not None:
        conds.append(Sigsa3RegistroModel.paciente_id == paciente_id)
    if medico_id is not None:
        conds.append(Sigsa3RegistroModel.medico_id == medico_id)
    if personal_salud_id is not None:
        conds.append(Sigsa3RegistroModel.personal_salud_id == personal_salud_id)
    if consulta_id is not None:
        conds.append(Sigsa3RegistroModel.consulta_id == consulta_id)
    if tipo_consulta_id is not None:
        conds.append(Sigsa3RegistroModel.tipo_consulta_id == tipo_consulta_id)
    if especialidad_id is not None:
        conds.append(Sigsa3RegistroModel.especialidad_id == especialidad_id)
    if fecha_consulta is not None:
        conds.append(Sigsa3RegistroModel.fecha_consulta == fecha_consulta)
    if fecha_desde is not None:
        conds.append(Sigsa3RegistroModel.fecha_consulta >= fecha_desde)
    if fecha_hasta is not None:
        conds.append(Sigsa3RegistroModel.fecha_consulta <= fecha_hasta)
    if nombre_paciente:
        conds.append(PacienteModel.nombre_completo.ilike(f"%{nombre_paciente}%"))
    if no_historia_clinica:
        conds.append(PacienteModel.expediente.ilike(f"%{no_historia_clinica}%"))
    if q:
        term = f"%{q}%"
        conds.append(
            or_(
                PacienteModel.nombre_completo.ilike(term),
                PacienteModel.expediente.ilike(term),
                MedicoModel.nombre.ilike(term),
                PersonalSaludModel.nombre.ilike(term),
                TipoConsultaSigsa3Model.nombre.ilike(term),
                Cie10Model.codigo.ilike(term),
                EspecialidadModel.nombre.ilike(term),
            )
        )
    return conds


def _serializar(row) -> dict:
    reg, pac_nombre, pac_expediente, pac_sexo, med_nombre, ps_nombre, tc_nombre, cie10, cie10_desc, esp_nombre = row
    cie10_completo = f"{cie10} {cie10_desc}".strip() if cie10 else None
    return {
        "id": reg.id,
        "paciente_id": reg.paciente_id,
        "medico_id": reg.medico_id,
        "personal_salud_id": reg.personal_salud_id,
        "consulta_id": reg.consulta_id,
        "fecha_consulta": reg.fecha_consulta,
        "tipo_consulta_id": reg.tipo_consulta_id,
        "control": reg.control,
        "semana_gestacional": reg.semana_gestacional,
        "codigo_cie_10_id": reg.codigo_cie_10_id,
        "especialidad_id": reg.especialidad_id,
        "normalized_at": reg.normalized_at,
        "paciente_nombre": pac_nombre,
        "paciente_expediente": pac_expediente,
        "sexo": pac_sexo,
        "medico_nombre": med_nombre,
        "personal_salud_nombre": ps_nombre,
        "tipo_consulta_nombre": tc_nombre,
        "codigo_cie_10": cie10,
        "codigo_cie_10_descripcion": cie10_desc,
        "codigo_cie_10_completo": cie10_completo,
        "especialidad_nombre": esp_nombre,
    }


def _validar_fk_existe(db: Session, model, fk_id, nombre_campo: str, tabla: str):
    """Valida que el FK exista en su tabla de catálogo. 404 si no."""
    if fk_id is None:
        return
    if not db.get(model, fk_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{nombre_campo} con id {fk_id} no existe en {tabla}",
        )


def _validar_fks(db: Session, data) -> None:
    """Valida existencia de todas las FKs de un registro normalizado
    contra sus tablas de catálogo (coincidencias garantizadas)."""
    _validar_fk_existe(db, PacienteModel, data.paciente_id, "paciente_id", "pacientes")
    if data.medico_id is not None:
        _validar_fk_existe(db, MedicoModel, data.medico_id, "medico_id", "medicos")
    _validar_fk_existe(db, PersonalSaludModel, data.personal_salud_id, "personal_salud_id", "personal_salud")
    _validar_fk_existe(db, ConsultaModel, data.consulta_id, "consulta_id", "consultas")
    _validar_fk_existe(db, TipoConsultaSigsa3Model, data.tipo_consulta_id, "tipo_consulta_id", "tipos_consulta_sigsa3")
    _validar_fk_existe(db, Cie10Model, data.codigo_cie_10_id, "codigo_cie_10_id", "cie10_catalogo")
    _validar_fk_existe(db, EspecialidadModel, data.especialidad_id, "especialidad_id", "especialidades")


def _validar_coherencia_consulta(db: Session, paciente_id, consulta_id) -> None:
    """Si llega consulta_id, valida que pertenezca al mismo paciente.
    409 si hay conflicto de coherencia cruzada."""
    if consulta_id is None:
        return
    consulta = db.get(ConsultaModel, consulta_id)
    if not consulta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"consulta_id {consulta_id} no existe en consultas",
        )
    if paciente_id is not None and consulta.paciente_id != paciente_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"consulta_id {consulta_id} pertenece al paciente "
                f"{consulta.paciente_id}, no al paciente {paciente_id}"
            ),
        )


def _resolver_especialidad_desde_medico(db: Session, medico_id, especialidad_id) -> int | None:
    """La especialidad gana el médico: si hay medico_id, usa medicos.especialidad_id
    salvo que el usuario envíe una explícita y el médico no tenga una."""
    if especialidad_id is not None:
        return especialidad_id
    if medico_id is not None:
        medico = db.get(MedicoModel, medico_id)
        if medico and medico.especialidad_id is not None:
            return medico.especialidad_id
    return None


def listar_registros(
    db: Session,
    paciente_id: Optional[int] = None,
    medico_id: Optional[int] = None,
    personal_salud_id: Optional[int] = None,
    consulta_id: Optional[int] = None,
    tipo_consulta_id: Optional[int] = None,
    especialidad_id: Optional[int] = None,
    fecha_consulta: Optional[date] = None,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    nombre_paciente: Optional[str] = None,
    no_historia_clinica: Optional[str] = None,
    q: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
):
    conds = _filtros(
        paciente_id=paciente_id,
        medico_id=medico_id,
        personal_salud_id=personal_salud_id,
        consulta_id=consulta_id,
        tipo_consulta_id=tipo_consulta_id,
        especialidad_id=especialidad_id,
        fecha_consulta=fecha_consulta,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        nombre_paciente=nombre_paciente,
        no_historia_clinica=no_historia_clinica,
        q=q,
    )
    query = _base_query(db).filter(*conds)
    total = query.count()
    rows = (
        query.order_by(
            Sigsa3RegistroModel.fecha_consulta.desc(),
            Sigsa3RegistroModel.id.desc(),
        )
        .offset(skip)
        .limit(min(limit, 500))
        .all()
    )
    return [_serializar(r) for r in rows], total


def obtener_registro(registro_id: int, db: Session) -> dict:
    row = _base_query(db).filter(Sigsa3RegistroModel.id == registro_id).first()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registro SIGSA-3 normalizado no encontrado",
        )
    return _serializar(row)


def crear_registro(data: Sigsa3RegistroCreate, db: Session) -> dict:
    _validar_fks(db, data)
    _validar_coherencia_consulta(db, data.paciente_id, data.consulta_id)
    if not data.fecha_consulta:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="fecha_consulta es obligatoria",
        )
    datos = data.model_dump()
    datos["especialidad_id"] = _resolver_especialidad_desde_medico(
        db, datos.get("medico_id"), datos.get("especialidad_id")
    )
    registro = Sigsa3RegistroModel(**datos)
    db.add(registro)
    db.commit()
    db.refresh(registro)
    return obtener_registro(registro.id, db)


def actualizar_registro(registro_id: int, data: Sigsa3RegistroUpdate, db: Session) -> dict:
    registro = db.get(Sigsa3RegistroModel, registro_id)
    if not registro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registro SIGSA-3 normalizado no encontrado",
        )
    update_data = data.model_dump(exclude_unset=True)
    # Validar FKs contra catálogos con los valores finales
    campos = ("paciente_id", "medico_id", "personal_salud_id", "consulta_id",
              "tipo_consulta_id", "codigo_cie_10_id", "especialidad_id")
    finales = {k: update_data.get(k, getattr(registro, k)) for k in campos}
    _validar_fk_existe(db, PacienteModel, finales["paciente_id"], "paciente_id", "pacientes")
    if finales["medico_id"] is not None:
        _validar_fk_existe(db, MedicoModel, finales["medico_id"], "medico_id", "medicos")
    _validar_fk_existe(db, PersonalSaludModel, finales["personal_salud_id"], "personal_salud_id", "personal_salud")
    _validar_fk_existe(db, ConsultaModel, finales["consulta_id"], "consulta_id", "consultas")
    _validar_fk_existe(db, TipoConsultaSigsa3Model, finales["tipo_consulta_id"], "tipo_consulta_id", "tipos_consulta_sigsa3")
    _validar_fk_existe(db, Cie10Model, finales["codigo_cie_10_id"], "codigo_cie_10_id", "cie10_catalogo")
    _validar_fk_existe(db, EspecialidadModel, finales["especialidad_id"], "especialidad_id", "especialidades")
    _validar_coherencia_consulta(
        db,
        finales.get("paciente_id"),
        finales.get("consulta_id"),
    )
    for key, value in update_data.items():
        setattr(registro, key, value)
    # Especialidad: gana el médico si no viene explícita
    if "especialidad_id" not in update_data and "medico_id" in update_data:
        derivada = _resolver_especialidad_desde_medico(
            db, update_data["medico_id"], None
        )
        if derivada is not None:
            registro.especialidad_id = derivada
    db.commit()
    db.refresh(registro)
    return obtener_registro(registro.id, db)


def eliminar_registro(registro_id: int, db: Session) -> None:
    registro = db.get(Sigsa3RegistroModel, registro_id)
    if not registro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registro SIGSA-3 normalizado no encontrado",
        )
    db.delete(registro)
    db.commit()
