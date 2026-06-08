# modules/consultas/router.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import String, cast, desc, func, text, or_, String, and_, case
from typing import Optional, List
from datetime import datetime, date, time

from core.database import get_db
from core.security import get_current_user
from modules.users.models import UserModel
from modules.pacientes.models import PacienteModel
from modules.pacientes.schemas import PacienteSimple
from .schemas import (
    CicloConsultaUpdate, ConsultaListado, ConsultaOut,
    ConsultaUpdate, ConsultaBusqueda, RegistroConsultaCreate, RegistroConsultaOut,
    Indicador, CicloClinico, Egreso, ConsultaHistoriaResumidaOut, ConsultaListResponse
)
from .service import (
    _agregar_ciclo, buscar_consultas_activas as service_buscar_consultas,
    obtener_consulta as service_obtener_consulta,
    registrar_consulta as service_registrar_consulta,
    actualizar_consulta as service_actualizar_consulta,
    desactivar_consulta as service_desactivar_consulta,
    eliminar_consulta as service_eliminar_consulta,
    sincronizar_indicadores as service_sincronizar_indicadores,
)

router = APIRouter(prefix="/consultas", tags=["Consultas Médicas"])


@router.get("/", response_model=ConsultaListResponse)
def buscar_consultas_activas(
    paciente_id: Optional[int] = None,
    expediente: Optional[str] = None,
    documento: Optional[str] = None,
    cui: Optional[int] = None,
    primer_nombre: Optional[str] = None,
    segundo_nombre: Optional[str] = None,
    primer_apellido: Optional[str] = None,
    segundo_apellido: Optional[str] = None,
    tipo_consulta: Optional[int] = None,
    especialidad: Optional[str] = None,
    servicio: Optional[str] = None,
    fecha: Optional[date] = None,
    ultimo_estado: Optional[str] = None,
    activo: bool = Query(True, description="Filtrar solo consultas activas"),
    archivo: bool = Query(True, description="Excluye consultas cuyo último estado de ciclo sea 'archivo'"),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: UserModel = Depends(get_current_user)
):
    return service_buscar_consultas(
        db=db,
        paciente_id=paciente_id,
        expediente=expediente,
        documento=documento,
        cui=cui,
        primer_nombre=primer_nombre,
        segundo_nombre=segundo_nombre,
        primer_apellido=primer_apellido,
        segundo_apellido=segundo_apellido,
        tipo_consulta=tipo_consulta,
        especialidad=especialidad,
        servicio=servicio,
        fecha=fecha,
        ultimo_estado=ultimo_estado,
        activo=activo,
        archivo=archivo,
        skip=skip,
        limit=limit,
    )


@router.get("/buscarpaciente", response_model=List[PacienteSimple])
def buscar_pacientes(
    paciente_id: Optional[int] = None,
    expediente: Optional[str] = None,
    documento: Optional[str] = None,
    cui: Optional[int] = None,
    primer_nombre: Optional[str] = None,
    segundo_nombre: Optional[str] = None,
    primer_apellido: Optional[str] = None,
    segundo_apellido: Optional[str] = None,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: UserModel = Depends(get_current_user)
):
    from modules.pacientes.models import PacienteModel
    query = db.query(PacienteModel)

    if paciente_id is not None:
        query = query.filter(PacienteModel.id == paciente_id)

    if cui is not None:
        query = query.filter(PacienteModel.cui == cui)

    if expediente:
        query = query.filter(PacienteModel.expediente == expediente)

    if primer_nombre:
        query = query.filter(
            cast(PacienteModel.nombre["primer_nombre"], String)
            .ilike(f"%{primer_nombre}%")
        )
    if segundo_nombre:
        query = query.filter(
            cast(PacienteModel.nombre["segundo_nombre"], String)
            .ilike(f"%{segundo_nombre}%")
        )
    if primer_apellido:
        query = query.filter(
            cast(PacienteModel.nombre["primer_apellido"], String)
            .ilike(f"%{primer_apellido}%")
        )
    if segundo_apellido:
        query = query.filter(
            cast(PacienteModel.nombre["segundo_apellido"], String)
            .ilike(f"%{segundo_apellido}%")
        )

    if documento is not None:
        from modules.consultas.models import ConsultaModel
        query = (
            query
            .join(ConsultaModel, ConsultaModel.paciente_id == PacienteModel.id)
            .filter(ConsultaModel.documento == documento)
        )

    pacientes = (
        query
        .distinct()
        .order_by(PacienteModel.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return [PacienteSimple.from_orm(p) for p in pacientes]


@router.get("/{consulta_id}", response_model=ConsultaOut)
def obtener_consulta(
    consulta_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return service_obtener_consulta(consulta_id, db)


@router.patch("/sincronizar-indicadores")
def sincronizar_indicadores(
    desde: str = Query(..., description="Fecha inicio (YYYY-MM-DD)"),
    hasta: str = Query(..., description="Fecha fin (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    try:
        f_desde = datetime.strptime(desde, "%Y-%m-%d").date()
        f_hasta = datetime.strptime(hasta, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")
    return service_sincronizar_indicadores(db, f_desde, f_hasta, current_user)


@router.patch("/{consulta_id}", response_model=ConsultaOut)
def actualizar_consulta(
    consulta_id: int,
    update_data: ConsultaUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return service_actualizar_consulta(consulta_id, update_data, db, current_user)


@router.post("/registro", response_model=RegistroConsultaOut, status_code=201)
def registrar_consulta(
    datos: RegistroConsultaCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return service_registrar_consulta(datos, db, current_user)


@router.get("/pacienteId/{paciente_id}", response_model=List[ConsultaHistoriaResumidaOut])
def buscar_consultas_por_paciente(
    paciente_id: int,
    activo: bool = Query(True, description="Filtrar solo consultas activas"),
    db: Session = Depends(get_db),
    limit: int = 100,
    skip: int = 0,
    current_user: UserModel = Depends(get_current_user)
):
    from modules.consultas.models import ConsultaModel
    from modules.pacientes.models import PacienteModel
    query = (
        db.query(ConsultaModel)
        .join(PacienteModel, ConsultaModel.paciente_id == PacienteModel.id)
        .filter(ConsultaModel.paciente_id == paciente_id)
    )

    if activo is not None:
        query = query.filter(ConsultaModel.activo.is_(activo))

    resultados = (
        query
        .distinct()
        .order_by(ConsultaModel.fecha_consulta.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return resultados


@router.delete("/{consulta_id}", response_model=ConsultaOut)
def desactivar_consulta(
    consulta_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return service_desactivar_consulta(consulta_id, db, current_user)


@router.delete("/{consulta_id}/eliminar", response_model=dict)
def eliminar_consulta(
    consulta_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return service_eliminar_consulta(consulta_id, db)
