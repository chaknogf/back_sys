from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Query, status
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from core.database import get_db
from core.limiter import limiter
from core.security import get_current_user
from modules.users.models import UserModel
from modules.agente.schemas import (
    ReglaAgenteCreate,
    ReglaAgenteList,
    ReglaAgenteOut,
    FeedbackCreate,
    FeedbackOut,
    RespuestaAgente,
)
from modules.agente.service import ejecutar_consulta
from modules.agente.models import ReglaAgente, FeedbackAgente

router = APIRouter(prefix="/agente", tags=["Agente Estadístico"])


@router.post("/consulta", response_model=RespuestaAgente)
@limiter.limit("30/minute")
def consulta_agente(
    request: Request,
    pregunta: str = Query(..., min_length=2, max_length=1000),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    resultado = ejecutar_consulta(pregunta, db, username=current_user.username)
    return RespuestaAgente(
        respuesta=resultado["respuesta"],
        datos=resultado["datos"],
        columnas=resultado["columnas"],
        total_filas=resultado["total_filas"],
        ejecucion_ms=resultado["ejecucion_ms"],
        modelo="agente-rule",
        error=resultado["error"],
        generado_en=datetime.now(timezone.utc),
    )


@router.post("/feedback", response_model=FeedbackOut)
def registrar_feedback(
    body: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    feedback = FeedbackAgente(
        pregunta=body.pregunta.strip(),
        respuesta=body.respuesta.strip(),
        sql_generado=body.sql_generado,
        correcto=body.correcto,
        correccion=body.correccion,
        username=current_user.username,
    )
    db.add(feedback)

    # Aprendizaje: si el usuario marcó incorrecta y dio una corrección,
    # intentamos derivar un sinónimo de entidad.
    if not body.correcto and body.correccion:
        n = (body.correccion or "").strip().lower()
        for entidad in ("pacientes", "consultas", "citas", "medicos",
                        "nacimientos", "defunciones", "censo_camas",
                        "prestamos", "proce_medicos", "constancia_nacimiento"):
            if entidad in n and not _existe_regla(db, "sinonimo_entidad", n, entidad):
                db.add(ReglaAgente(
                    tipo="sinonimo_entidad", clave=n, valor=entidad,
                    origen="feedback", usuario=current_user.username,
                ))

    db.commit()
    db.refresh(feedback)
    return FeedbackOut(id=feedback.id, pregunta=feedback.pregunta,
                       correcto=feedback.correcto, creado_en=feedback.creado_en)


@router.get("/reglas", response_model=ReglaAgenteList)
def listar_reglas(
    tipo: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    q = select(ReglaAgente)
    if tipo:
        q = q.where(ReglaAgente.tipo == tipo)
    total = db.execute(select(func.count()).select_from(q.subquery())).scalar() or 0
    items = db.execute(
        q.order_by(ReglaAgente.veces_usado.desc(), ReglaAgente.id.desc())
        .offset(skip).limit(limit)
    ).scalars().all()
    return ReglaAgenteList(total=total, items=[r for r in items])


@router.post("/reglas", response_model=ReglaAgenteOut, status_code=status.HTTP_201_CREATED)
def crear_regla(
    body: ReglaAgenteCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    if body.tipo not in ("sinonimo_entidad", "sinonimo_agrupacion", "sinonimo_medida"):
        raise HTTPException(400, "tipo inválido")
    if _existe_regla(db, body.tipo, body.clave, body.valor):
        raise HTTPException(409, "Ya existe una regla similar")
    regla = ReglaAgente(
        tipo=body.tipo, clave=body.clave.strip().lower(),
        valor=body.valor.strip().lower(), origen="manual",
        usuario=current_user.username,
    )
    db.add(regla)
    db.commit()
    db.refresh(regla)
    return regla


@router.delete("/reglas/{regla_id}")
def eliminar_regla(
    regla_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    regla = db.get(ReglaAgente, regla_id)
    if not regla:
        raise HTTPException(404, "Regla no encontrada")
    db.delete(regla)
    db.commit()
    return {"detail": "Regla eliminada"}


def _existe_regla(db: Session, tipo: str, clave: str, valor: str) -> bool:
    existe = db.execute(
        select(ReglaAgente.id).where(
            ReglaAgente.tipo == tipo,
            ReglaAgente.clave == clave.strip().lower(),
            ReglaAgente.valor == valor.strip().lower(),
        )
    ).first()
    return existe is not None