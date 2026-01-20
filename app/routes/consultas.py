# app/routes/consultas.py
"""
Router de consultas médicas - Búsqueda avanzada, creación inteligente y CRUD completo
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, text, or_
from typing import Optional, List
from datetime import datetime, date, time

from app.database.db import get_db
from app.models.consultas import ConsultaModel
from app.models.pacientes import PacienteModel
from app.schemas.consultas import ConsultaBase, ConsultaCreate, ConsultaListResponse, ConsultaOut, ConsultaUpdate, RegistroConsultaCreate, RegistroConsultaOut, Indicador, CicloClinico
from app.utils.expediente import generar_expediente, generar_emergencia
from app.database.security import get_current_user
from app.models.user import UserModel
from sqlalchemy.orm import joinedload

router = APIRouter(prefix="/consultas", tags=["Consultas Médicas"])


@router.get("/", response_model=List[ConsultaOut])
def buscar_consultas(
    paciente_id: Optional[int] = None,
    expediente: Optional[str] = None,
    cui: Optional[int] = None,
    primer_nombre: Optional[str] = None,
    segundo_nombre: Optional[str] = None,
    primer_apellido: Optional[str] = None,
    segundo_apellido: Optional[str] = None,
    tipo_consulta: Optional[int] = None,
    especialidad: Optional[str] = None,
    fecha: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    query = (
        db.query(ConsultaModel)
        .join(PacienteModel, ConsultaModel.paciente_id == PacienteModel.id)
    )

    # ======================
    # Filtros de CONSULTA
    # ======================
    if paciente_id:
        query = query.filter(ConsultaModel.paciente_id == paciente_id)

    if tipo_consulta:
        query = query.filter(ConsultaModel.tipo_consulta == tipo_consulta)

    if especialidad:
        query = query.filter(
            ConsultaModel.especialidad.ilike(f"%{especialidad}%")
        )

    if fecha:
        query = query.filter(ConsultaModel.fecha_consulta == fecha)

    # ======================
    # Filtros de PACIENTE
    # ======================
    if expediente:
        query = query.filter(
            or_(
                ConsultaModel.expediente == expediente,
                PacienteModel.expediente == expediente
            )
        )

    if cui:
        query = query.filter(PacienteModel.cui == cui)

    if primer_nombre:
        query = query.filter(
            PacienteModel.nombre["primer_nombre"].astext.ilike(f"%{primer_nombre}%")
        )

    if segundo_nombre:
        query = query.filter(
            PacienteModel.nombre["segundo_nombre"].astext.ilike(f"%{segundo_nombre}%")
        )

    if primer_apellido:
        query = query.filter(
            PacienteModel.nombre["primer_apellido"].astext.ilike(f"%{primer_apellido}%")
        )

    if segundo_apellido:
        query = query.filter(
            PacienteModel.nombre["segundo_apellido"].astext.ilike(f"%{segundo_apellido}%")
        )

    resultados = (
        query
        .order_by(ConsultaModel.fecha_consulta.desc())
        .all()
    )

    return resultados
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
# ACTUALIZAR CONSULTA
# =============================================================================
# app/routes/consultas.py

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
    
    # ======================
    # 2. Obtener datos a actualizar
    # ======================
    datos = update_data.model_dump(exclude_unset=True, exclude={'ciclo'})
    
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
    # 6. AGREGAR nuevo registro al historial del ciclo
    # ======================
    if update_data.ciclo:
        # Obtener historial actual (o crear lista vacía)
        ciclo_historial = consulta.ciclo or []
        if not isinstance(ciclo_historial, list):
            ciclo_historial = []
        
        # Crear nuevo registro con auditoría automática
        nuevo_ciclo = update_data.ciclo.model_dump(exclude_none=True, mode='json')
        
        # SIEMPRE agregar campos de auditoría
        nuevo_ciclo["estado"] = nuevo_ciclo.get("estado", "actualizado")
        nuevo_ciclo["registro"] = datetime.now().isoformat()
        nuevo_ciclo["usuario"] = current_user.username
        
        # AGREGAR al historial (no sobrescribir)
        ciclo_historial.append(nuevo_ciclo)
        datos["ciclo"] = ciclo_historial
    
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
    # 9. Guardar cambios
    # ======================
    try:
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
# REGISTRO DE CONSULTA - ENDPOINT COMPLETO
# =============================================================================
@router.post("/registro", response_model=RegistroConsultaOut, status_code=201)
def registrar_consulta(
    datos: RegistroConsultaCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Registro rápido de consulta:
    - El frontend envía solo paciente_id, tipo_consulta, especialidad, servicio y opcionalmente indicadores.
    - Backend genera expediente, documento, fecha/hora, ciclo inicial y orden automáticamente.
    """
    
    # ======================
    # 1. Verificar paciente
    # ======================
    paciente = db.get(PacienteModel, datos.paciente_id)
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    # ======================
    # 2. Obtener o generar expediente
    # ======================
    expediente = paciente.expediente
    if not expediente:
        if datos.tipo_consulta in [1, 2]:
            expediente = generar_expediente(db)
        elif datos.tipo_consulta == 3:
            expediente = generar_emergencia(db)
        paciente.expediente = expediente
        db.add(paciente)

    # ======================
    # 3. Documento según tipo
    # ======================
    documento = expediente
    if datos.tipo_consulta == 3:  # Emergencia
        documento = generar_emergencia(db)

    # ======================
    # 4. Inicializar indicadores completos
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
    # 5. Crear ciclo clínico inicial
    # ======================
    ciclo_inicial = CicloClinico(
        estado="admision",
        registro=datetime.now().isoformat(),
        usuario=current_user.username,
        especialidad=datos.especialidad,
        servicio=datos.servicio
    )
    ciclo_historial = [ciclo_inicial.model_dump(mode='json')]

    # ======================
    # 6. Calcular orden en la cola
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
    # 7. Crear la consulta
    # ======================
    nueva_consulta = ConsultaModel(
        paciente_id=datos.paciente_id,
        expediente=expediente,
        tipo_consulta=datos.tipo_consulta,
        especialidad=datos.especialidad,
        servicio=datos.servicio,
        documento=documento,
        fecha_consulta=hoy,
        hora_consulta=datetime.now().time(),
        indicadores=indicadores_completos,
        ciclo=ciclo_historial,
        orden=ultimo_orden + 1
    )

    db.add(nueva_consulta)

    try:
        db.commit()
        db.refresh(nueva_consulta)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear la consulta: {str(e)}"
        )

    # ======================
    # 8. Retornar respuesta estructurada
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
        ciclo=[CicloClinico(**c) for c in nueva_consulta.ciclo],  # siempre lista
        orden=nueva_consulta.orden
    )