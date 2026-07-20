from datetime import date, datetime
from typing import Optional
from modules.pacientes.models import PacienteModel
from modules.expediente.service import generar_constancia_nacimiento as generar_cn
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import inspect, desc, func, or_
from sqlalchemy.orm import Session, joinedload, attributes
from decimal import Decimal
from core.database import get_db
from core.security import get_current_user
from modules.users.models import UserModel
from modules.constancias_nacimiento.models import ConstanciaNacimientoModel
from modules.constancias_nacimiento.models import ConstanciaNacimientoHistorialModel
from modules.constancias_nacimiento.schemas import (
    ConstanciaNacimientoCreate,
    ConstanciaNacimientoHistorialResponse,
    ConstanciaNacimientoListResponse,
    ConstanciaNacimientoUpdate,
    ConstanciaNacimientoResponse,
    EstadoInformeUpdate
)

router = APIRouter(prefix="/constancias-nacimiento", tags=["Constancias Nacimiento"])


def _serializar(v):
    if isinstance(v, (date, datetime)):
        return v.isoformat()
    if isinstance(v, Decimal):
        return float(v)
    return v


def _actualizar_partos_madre(madre_id: int, db: Session):
    """Recalcula datos_extra.partos de la madre desde constancias_nacimiento."""
    if not madre_id:
        return
    stats = db.query(
        func.coalesce(func.sum(ConstanciaNacimientoModel.vivos), 0),
        func.coalesce(func.sum(ConstanciaNacimientoModel.muertos), 0),
    ).filter(
        ConstanciaNacimientoModel.madre_id == madre_id
    ).first()
    madre = db.get(PacienteModel, madre_id)
    if not madre:
        return
    if madre.datos_extra is None:
        madre.datos_extra = {}
    madre.datos_extra.setdefault("partos", {})
    madre.datos_extra["partos"]["nacidos_vivos"] = int(stats[0]) if stats else 0
    madre.datos_extra["partos"]["nacidos_muertos"] = int(stats[1]) if stats else 0
    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(madre, "datos_extra")
    db.commit()


@router.post("/", response_model=ConstanciaNacimientoResponse)
def crear_constancia(
    data: ConstanciaNacimientoCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)):
    data_dict = data.model_dump(exclude={"registrador_id"})
    nueva = ConstanciaNacimientoModel(**data_dict)
    nueva.registrador_id = current_user.id
    nueva.metadatos = {
        "historial": [
            {
                "usuario": current_user.username,
                "fecha_hora": datetime.now().isoformat(),
                "estado_informe": "creado",
            }
        ],
        "estado_informe": "creado",
    }
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    if nueva.madre_id:
        _actualizar_partos_madre(nueva.madre_id, db)
    return nueva

@router.get("/", response_model=ConstanciaNacimientoListResponse)
def listar_constancias(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
    id_usuario:     Optional[int]  = None,
    id_constancia:  Optional[int]  = None,
    nombre_madre:   Optional[str]  = None,
    fecha:          Optional[date] = None,
    documento:      Optional[str]  = None,
    expediente:      Optional[str]  = None,
    limit:  int = 10,
    offset: int = 0,
):
    query = db.query(ConstanciaNacimientoModel).options(
        joinedload(ConstanciaNacimientoModel.paciente),
        joinedload(ConstanciaNacimientoModel.madre),
        joinedload(ConstanciaNacimientoModel.medico),
    )

    if id_usuario is not None:
        query = query.filter(ConstanciaNacimientoModel.registrador_id == id_usuario)

    if id_constancia is not None:
        query = query.filter(ConstanciaNacimientoModel.id == id_constancia)

    if nombre_madre and nombre_madre.strip():
        query = query.filter(
            ConstanciaNacimientoModel.nombre_madre.ilike(f"%{nombre_madre.strip()}%")
        )

    if fecha is not None:
        query = query.filter(ConstanciaNacimientoModel.fecha_registro == fecha)

    if documento and documento.strip():
        query = query.filter(
            ConstanciaNacimientoModel.documento == documento.strip()
        )
    if expediente and expediente.strip():
        exp = expediente.strip()
        query = query.filter(
            or_(
                ConstanciaNacimientoModel.paciente.has(
                    PacienteModel.expediente == exp
                ),
                ConstanciaNacimientoModel.madre.has(
                    PacienteModel.expediente == exp
                )
            )
    )
    total = query.count()
    constancias = (
        query
        .order_by(desc(ConstanciaNacimientoModel.id))
        .offset(offset)
        .limit(limit)
        .all()
    )

    return ConstanciaNacimientoListResponse(constancias=constancias, total=total)

@router.get("/historial/{constancia_id}",
            response_model=list[ConstanciaNacimientoHistorialResponse])
def obtener_historial_constancia(
    constancia_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    historial = db.query(ConstanciaNacimientoHistorialModel).filter_by(constancia_id=constancia_id).all()
    return historial

@router.get("/{constancia_id}", response_model=ConstanciaNacimientoResponse)
def obtener_constanciaNac(
    constancia_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    data = db.query(ConstanciaNacimientoModel).filter(
        ConstanciaNacimientoModel.id == constancia_id
    ).first()

    if not data:
        raise HTTPException(status_code=404, detail="No encontrado")

    return data


@router.get("/paciente/{paciente_id}", response_model=ConstanciaNacimientoResponse)
def obtener_constancia_por_paciente(
    paciente_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    constancia = (
        db.query(ConstanciaNacimientoModel)
        .options(
            joinedload(ConstanciaNacimientoModel.paciente),
            joinedload(ConstanciaNacimientoModel.madre),
            joinedload(ConstanciaNacimientoModel.medico),
        )
        .filter(ConstanciaNacimientoModel.paciente_id == paciente_id)
        .order_by(desc(ConstanciaNacimientoModel.id))
        .first()
    )
    if not constancia:
        raise HTTPException(status_code=404, detail="No encontrado")
    return constancia


@router.put("/{constancia_id}", response_model=ConstanciaNacimientoResponse)
def actualizar_constancia(
    constancia_id: int,
    data: ConstanciaNacimientoUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    constancia = db.get(ConstanciaNacimientoModel, constancia_id)
    if not constancia:
        raise HTTPException(status_code=404, detail="Constancia no encontrada")

    if not constancia.documento or not constancia.documento.strip():
        constancia.documento = generar_cn(db)

    state = inspect(constancia)
    historial = ConstanciaNacimientoHistorialModel(
        constancia_id=constancia.id,
        datos_anteriores={
            attr.key: _serializar(getattr(constancia, attr.key))
            for attr in state.mapper.column_attrs
        },
    usuario_id=current_user.id,
   
)
    db.add(historial)

    update_data = data.model_dump(exclude_unset=True)
   

    for key, value in update_data.items():
        setattr(constancia, key, value)

    db.commit()
    db.refresh(constancia)

    if constancia.madre_id:
        _actualizar_partos_madre(constancia.madre_id, db)

    return constancia

@router.patch("/{constancia_id}/estado-informe", response_model=ConstanciaNacimientoResponse)
def actualizar_estado_informe(
    constancia_id: int,
    data: EstadoInformeUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    constancia = db.get(ConstanciaNacimientoModel, constancia_id)
    if not constancia:
        raise HTTPException(status_code=404, detail="Constancia no encontrada")

    if constancia.metadatos is None:
        constancia.metadatos = {}
    constancia.metadatos["estado_informe"] = data.estado_informe
    if "historial" not in constancia.metadatos:
        constancia.metadatos["historial"] = []
    constancia.metadatos["historial"].append({
        "usuario": current_user.username,
        "fecha_hora": datetime.now().isoformat(),
        "estado_informe": data.estado_informe
    })
    attributes.flag_modified(constancia, "metadatos")
    constancia.updated_at = datetime.now()

    db.commit()
    db.refresh(constancia)
    return constancia


@router.delete("/{constancia_id}")
def eliminar_constancia(
    constancia_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    constancia = db.get(ConstanciaNacimientoModel, constancia_id)
    if not constancia:
        raise HTTPException(status_code=404, detail="Constancia no encontrada")

    db.query(ConstanciaNacimientoHistorialModel)\
      .filter(ConstanciaNacimientoHistorialModel.constancia_id == constancia_id)\
      .delete()

    db.delete(constancia)
    db.commit()
    return {"message": "Constancia eliminada correctamente"}
