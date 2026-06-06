# app/routes/consultas.py
"""
Router de consultas médicas - Búsqueda avanzada, creación inteligente y CRUD completo
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import String, cast, desc, func, text, or_, String, and_, case
from sqlalchemy.orm.attributes import flag_modified
from typing import Optional, List
from datetime import datetime, date, time

from app.database.db import get_db
from app.models.consultas import ConsultaModel
from app.models.pacientes import PacienteModel
from app.schemas.paciente import PacienteSimple
from app.schemas.consultas import (
    CicloConsultaUpdate, ConsultaListado, ConsultaOut,
    ConsultaUpdate, ConsultaBusqueda, RegistroConsultaCreate, RegistroConsultaOut, 
    Indicador, CicloClinico, Egreso, ConsultaHistoriaResumidaOut, ConsultaListResponse
)
from app.utils.expediente import generar_expediente, generar_emergencia
from app.database.security import get_current_user
from app.models.user import UserModel
from sqlalchemy.orm import joinedload

router = APIRouter(prefix="/consultas", tags=["Consultas Médicas"])



# =============================================================================
# Funciones
# =============================================================================
# Función helper para no repetir lógica
def _agregar_ciclo(consulta, nuevo_ciclo, current_user):
    nuevo_ciclo["registro"] = datetime.now().isoformat()
    nuevo_ciclo["usuario"] = current_user.username
    nuevo_ciclo.setdefault("estado", "actualizado")

    # ← Normalizar ciclo aunque sea dict vacío o None
    historial = consulta.ciclo
    if not historial or isinstance(historial, dict):
        historial = []
    elif not isinstance(historial, list):
        historial = []

    consulta.ciclo = historial + [nuevo_ciclo]
    consulta.ultimo_estado = nuevo_ciclo["estado"]
    flag_modified(consulta, "ciclo")                     
# =============================================================================
# BUSCAR CONSULTAS (TODAS)
# =============================================================================



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
    query = (
        db.query(ConsultaModel)
        .join(PacienteModel, ConsultaModel.paciente_id == PacienteModel.id)
    )

    query = query.filter(ConsultaModel.activo.is_(activo))

    # ======================
    # Filtro de ARCHIVO (último estado del ciclo JSONB)
    # ======================
    if not archivo:
        query = query.filter(
            or_(
                ConsultaModel.ultimo_estado.is_(None),
                ConsultaModel.ultimo_estado != "archivo"
            )
        )
    # archivo=True → no se agrega ningún filtro, lista todo
    # ======================
    # Filtros de CONSULTA
    # ======================
    if ultimo_estado is not None:
        query = query.filter(ConsultaModel.ultimo_estado == ultimo_estado)

    if paciente_id is not None:
        query = query.filter(ConsultaModel.paciente_id == paciente_id)

    if tipo_consulta is not None:
        query = query.filter(ConsultaModel.tipo_consulta == tipo_consulta)

    if documento is not None:
        query = query.filter(ConsultaModel.documento == documento)

    if especialidad:
        query = query.filter(ConsultaModel.especialidad == especialidad)

    if servicio:
        query = query.filter(ConsultaModel.servicio == servicio)

    if fecha:
        inicio = datetime.combine(fecha, time.min)
        fin = datetime.combine(fecha, time.max)
        query = query.filter(
            ConsultaModel.fecha_consulta.between(inicio, fin)
        )

    # ======================
    # Filtros mixtos CONSULTA / PACIENTE
    # ======================
    if expediente:
        query = query.filter(
            or_(
                ConsultaModel.expediente == expediente,
                PacienteModel.expediente == expediente
            )
        )

    # ======================
    # Filtros de PACIENTE
    # ======================
    if cui is not None:
        query = query.filter(PacienteModel.cui == cui)

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

    total = query.count()
    resultados = (
        query
        .distinct()
        .order_by(ConsultaModel.id.desc())
        .limit(limit).offset(skip)
        .all()
    )

    return ConsultaListResponse(
        total=total,
        consultas=resultados
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
    # ======================
    # BASE QUERY — ahora sobre PacienteModel
    # ======================
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

    # ======================
    # FILTRO POR DOCUMENTO — requiere JOIN con consultas
    # Solo se hace el JOIN si realmente se filtra por documento
    # ======================
    if documento is not None:
        query = (
            query
            .join(ConsultaModel, ConsultaModel.paciente_id == PacienteModel.id)
            .filter(ConsultaModel.documento == documento)
        )

    # ======================
    # EJECUCIÓN
    # ======================
    pacientes = (
        query
        .distinct()
        .order_by(PacienteModel.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return [PacienteSimple.from_orm(p) for p in pacientes]


# =============================================================================
# OBTENER UNA CONSULTA POR ID
# =============================================================================
@router.get("/{consulta_id}", response_model=ConsultaOut)
def obtener_consulta(
    consulta_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    consulta = db.get(ConsultaModel, consulta_id)
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta no encontrada")
    return consulta
 


# =============================================================================
# ACTUALIZAR CONSULTA (PATCH - Actualización parcial)
# =============================================================================
@router.patch("/{consulta_id}", response_model=ConsultaOut)
def actualizar_consulta(
    consulta_id: int,
    update_data: ConsultaUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
    ):
    """
    Actualiza una consulta existente.
    
    Si se proporciona 'ciclo', se AGREGA al historial (no sobrescribe).
    Cada registro del ciclo incluye automáticamente: estado, registro, usuario.
    """
    
    # ======================
    # 1. Verificar que la consulta existe
    # ======================
    consulta = db.get(ConsultaModel, consulta_id)
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta no encontrada")
    ESTADO_ARCHIVADO = "archivo"
    esta_archivado = consulta.ultimo_estado == ESTADO_ARCHIVADO
    
    # ======================
    # 2. Obtener datos a actualizar
    # ======================
    datos = update_data.model_dump(exclude_unset=True, exclude={'ciclo'})

    if esta_archivado:
        datos.pop('ultimo_estado', None)
        datos.pop('activo', None)
        
    # ======================
    # 3. Validar paciente si se está cambiando
    # ======================
    if "paciente_id" in datos:
        paciente = db.get(PacienteModel, datos["paciente_id"])
        if not paciente:
            raise HTTPException(status_code=404, detail="Paciente no encontrado")
        
        if paciente.expediente:
            datos["expediente"] = paciente.expediente
    
    # ======================
    # 4. Regenerar documento si cambia tipo de consulta
    # ======================
    if "tipo_consulta" in datos and datos["tipo_consulta"] != consulta.tipo_consulta:
        if datos["tipo_consulta"] == 3:
            datos["documento"] = generar_emergencia(db)
        else:
            paciente = db.get(PacienteModel, consulta.paciente_id)
            if paciente and paciente.expediente:
                datos["documento"] = paciente.expediente
    
    # ======================
    # 5. Manejar actualización de indicadores (merge)
    # ======================
    if "indicadores" in datos:
        if isinstance(datos["indicadores"], Indicador):
            datos["indicadores"] = datos["indicadores"].model_dump()
        
        indicadores_actuales = consulta.indicadores or {}
        indicadores_nuevos = datos["indicadores"] or {}
        datos["indicadores"] = {**indicadores_actuales, **indicadores_nuevos}
        
    # ======================
    # 5b. Manejar actualización de egreso (merge) y agregar registro automático
    # ======================
    if "egreso" in datos:
        if isinstance(datos["egreso"], Egreso):
            datos["egreso"] = datos["egreso"].model_dump(exclude_none=True)

        egreso_actual = consulta.egreso or {}
        egreso_nuevo = datos["egreso"] or {}

        # Agregar timestamp automático si no viene
        if "registro" not in egreso_nuevo:
            egreso_nuevo["registro"] = datetime.now().isoformat()

        datos["egreso"] = {**egreso_actual, **egreso_nuevo}
        
    # ======================
    # 6. AGREGAR nuevo registro al historial del ciclo
    # ======================
    if update_data.ciclo is not None:
        nuevo_ciclo = update_data.ciclo.model_dump_clean(mode='json')
        _agregar_ciclo(consulta, nuevo_ciclo, current_user)

    # ======================
    # 7. Recalcular orden si es necesario
    # ======================
    recalcular_orden = any(
        key in datos 
        for key in ["fecha_consulta", "tipo_consulta", "especialidad"]
    )
    
    if recalcular_orden:
        fecha = datos.get("fecha_consulta", consulta.fecha_consulta)
        tipo = datos.get("tipo_consulta", consulta.tipo_consulta)
        especialidad = datos.get("especialidad", consulta.especialidad)
        
        ultimo_orden = (
            db.query(func.coalesce(func.max(ConsultaModel.orden), 0))
            .filter(
                ConsultaModel.fecha_consulta == fecha,
                ConsultaModel.tipo_consulta == tipo,
                ConsultaModel.especialidad == especialidad,
                ConsultaModel.id != consulta_id
            )
            .scalar()
        ) or 0
        
        datos["orden"] = ultimo_orden + 1
    
    # ======================
    # 8. Aplicar actualizaciones
    # ======================
    for key, value in datos.items():
        setattr(consulta, key, value)

    # ======================
    # 9. Proteger ultimo_estado si está archivado (SIEMPRE al final, antes del commit)
    # ======================
    if esta_archivado:
        consulta.ultimo_estado = ESTADO_ARCHIVADO
    
    # ======================
    # 10. Guardar cambios
    # ======================
    try:
        print(">>> ciclo recibido:", update_data.ciclo)
        print(">>> historial actual:", consulta.ciclo)
        db.commit()
        db.refresh(consulta)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar la consulta: {str(e)}"
        )
    
    return consulta
 


# =============================================================================
# REGISTRO DE CONSULTA - ENDPOINT SIMPLIFICADO
# =============================================================================
@router.post("/registro", response_model=RegistroConsultaOut, status_code=201)
def registrar_consulta( 
    datos: RegistroConsultaCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
        ):
    """
    Registro rápido de consulta:
    - Tipos 1 y 2:
        * Usa expediente del paciente si existe
        * Si no existe, genera uno nuevo y lo asigna al paciente
    - Tipo 3 (Emergencia):
        * Genera documento de emergencia
        * NO modifica expediente del paciente
    """

    # ======================
    # 1. Verificar paciente
    # ======================
    paciente = db.get(PacienteModel, datos.paciente_id)
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    # ======================
    # 2. Inicializar campos de consulta
    # ======================
    expediente_consulta: str | None = None
    documento_consulta: str | None = None

    # ======================
    # 3. Tipos 1 y 2 → Consulta normal
    # ======================
    if datos.tipo_consulta in (1, 2):
        if paciente.expediente:
            expediente_consulta = paciente.expediente
        else:
            expediente_consulta = generar_expediente(db)
            paciente.expediente = expediente_consulta
            db.add(paciente)

    # ======================
    # 4. Tipo 3 → Emergencia
    # ======================
    elif datos.tipo_consulta == 3:
        documento_consulta = generar_emergencia(db)

    else:
        raise HTTPException(status_code=400, detail="Tipo de consulta inválido")

    # ======================
    # 5. Indicadores (completos)
    # ======================
    indicadores_dict = datos.indicadores.model_dump() if datos.indicadores else {}
    indicadores_completos = {
        "estudiante_publico": indicadores_dict.get("estudiante_publico", False),
        "empleado_publico": indicadores_dict.get("empleado_publico", False),
        "accidente_laboral": indicadores_dict.get("accidente_laboral", False),
        "discapacidad": indicadores_dict.get("discapacidad", False),
        "accidente_transito": indicadores_dict.get("accidente_transito", False),
        "arma_fuego": indicadores_dict.get("arma_fuego", False),
        "arma_blanca": indicadores_dict.get("arma_blanca", False),
        "ambulancia": indicadores_dict.get("ambulancia", False),
        "embarazo": indicadores_dict.get("embarazo", False),
    }

    # ======================
    # 6. Ciclo clínico inicial
    # ======================
    ciclo_inicial = CicloClinico(
        estado="admision",
        registro=datetime.now().isoformat(),
        usuario=current_user.username,
        especialidad=datos.especialidad,
        servicio=datos.servicio
    )

    ciclo_historial = [ciclo_inicial.model_dump(mode="json")]

    # ======================
    # 7. Calcular orden diario
    # ======================
    hoy = date.today()
    ultimo_orden = (
        db.query(func.coalesce(func.max(ConsultaModel.orden), 0))
        .filter(
            ConsultaModel.fecha_consulta == hoy,
            ConsultaModel.tipo_consulta == datos.tipo_consulta,
            ConsultaModel.especialidad == datos.especialidad
        )
        .scalar()
    ) or 0

    # ======================
    # 8. Crear consulta
    # ======================
    nueva_consulta = ConsultaModel(
        paciente_id=datos.paciente_id,
        expediente=expediente_consulta,
        documento=documento_consulta,
        tipo_consulta=datos.tipo_consulta,
        especialidad=datos.especialidad,
        servicio=datos.servicio,
        fecha_consulta=hoy,
        hora_consulta=datetime.now().time(),
        indicadores=indicadores_completos,
        ciclo=ciclo_historial,
        orden=ultimo_orden + 1,
        ultimo_estado="admision",  # ← copia el estado del ciclo_inicial
    )

    db.add(nueva_consulta)

    # ======================
    # 9. Commit transaccional
    # ======================
    try:
        db.commit()
        db.refresh(nueva_consulta)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al registrar consulta: {str(e)}"
        )

    # ======================
    # 10. Respuesta
    # ======================
    return RegistroConsultaOut(
        id=nueva_consulta.id,
        expediente=nueva_consulta.expediente,
        paciente_id=nueva_consulta.paciente_id,
        tipo_consulta=nueva_consulta.tipo_consulta,
        especialidad=nueva_consulta.especialidad,
        servicio=nueva_consulta.servicio,
        documento=nueva_consulta.documento,
        fecha_consulta=nueva_consulta.fecha_consulta,
        hora_consulta=nueva_consulta.hora_consulta,
        indicadores=Indicador(**nueva_consulta.indicadores),
        ciclo=[CicloClinico(**c) for c in nueva_consulta.ciclo],
        orden=nueva_consulta.orden
    )
    

# =============================================================================
# Consultas por paciente_id
# =============================================================================
@router.get("/pacienteId/{paciente_id}", response_model=List[ConsultaHistoriaResumidaOut])
def buscar_consultas_activas(
    paciente_id: int,  # ← FALTABA ESTO
    activo: bool = Query(True, description="Filtrar solo consultas activas"),
    db: Session = Depends(get_db),
    limit: int = 100,
    skip: int = 0,
    current_user: UserModel = Depends(get_current_user)
                                                                ): 
    query = (
        db.query(ConsultaModel)
        .join(PacienteModel, ConsultaModel.paciente_id == PacienteModel.id)
        .filter(ConsultaModel.paciente_id == paciente_id)  # ← FILTRO CLAVE
    )

    # Filtro por estado activo
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

# =============================================================================
# DESACTIVAR CONSULTA (Soft Delete)
# =============================================================================
@router.delete("/{consulta_id}", response_model=ConsultaOut)
def desactivar_consulta(
    consulta_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Desactiva una consulta (soft delete).
    
    - Marca la consulta como inactiva (activo=False)
    - Agrega un registro al ciclo con estado 'archivo'
    - No elimina el registro de la base de datos
    - No se puede desactivar una consulta ya archivada
    """

    # ======================
    # 1. Verificar que la consulta existe
    # ======================
    consulta = db.get(ConsultaModel, consulta_id)
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta no encontrada")

    # ======================
    # 2. Verificar que no está ya archivada
    # ======================
    if consulta.ultimo_estado == "archivo":
        raise HTTPException(
            status_code=400,
            detail="La consulta ya se encuentra borrada"
        )

    # ======================
    # 3. Agregar ciclo de archivo
    # ======================
    _agregar_ciclo(
        consulta,
        {"estado": "borrado"},
        current_user
    )

    # ======================
    # 4. Marcar como inactiva
    # ======================
    consulta.activo = False

    # ======================
    # 5. Guardar cambios
    # ======================
    try:
        db.commit()
        db.refresh(consulta)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al archivar la consulta: {str(e)}"
        )

    return consulta