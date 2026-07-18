from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from core.database import get_db_readonly
from core.limiter import limiter
from core.security import get_current_user
from modules.users.models import UserModel
from modules.chat.schemas import (
    ChatRequest,
    ChatResponse,
    MensajeChat,
    ColumnaInfo,
    TablaInfo,
)
from modules.chat.service import consultar, TABLAS_CONOCIDAS
from core.config import CHAT_LLM_PROVIDER, CHAT_LLM_MODEL

router = APIRouter(prefix="/chat", tags=["Chat Inteligente"])


@router.post("/consulta", response_model=ChatResponse)
@limiter.limit("10/minute")
def consulta_chat(
    request: Request,
    body: ChatRequest,
    db: Session = Depends(get_db_readonly),
    current_user: UserModel = Depends(get_current_user),
):
    mensajes = [m.model_dump() for m in body.mensajes]
    try:
        resultado = consultar(
            mensajes=mensajes,
            db=db,
            max_filas=body.max_filas,
            tablas_filtro=body.tablas,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

    return ChatResponse(
        respuesta=resultado.get("respuesta", ""),
        datos=resultado.get("datos", []),
        columnas=resultado.get("columnas", []),
        sql_generado=resultado.get("sql_generado"),
        total_filas=resultado.get("total_filas", 0),
        ejecucion_ms=resultado.get("ejecucion_ms", 0),
        modelo=resultado.get("modelo", f"{CHAT_LLM_PROVIDER}:{CHAT_LLM_MODEL}"),
        error=resultado.get("error"),
        generado_en=datetime.now(timezone.utc),
    )


@router.get("/tablas", response_model=list[TablaInfo])
def listar_tablas(
    db: Session = Depends(get_db_readonly),
    current_user: UserModel = Depends(get_current_user),
):
    from sqlalchemy import text

    result = db.execute(
        text("""
            SELECT relname AS nombre, n_live_tup AS filas_aprox
            FROM pg_stat_user_tables
            WHERE schemaname = 'public'
            ORDER BY relname
        """)
    )
    stats = {r.nombre: r.filas_aprox for r in result}

    tablas = []
    for nombre, desc in sorted(TABLAS_CONOCIDAS.items()):
        tablas.append(TablaInfo(
            nombre=nombre,
            filas_aprox=stats.get(nombre, 0),
            descripcion=desc,
            columnas=[],
        ))
    return tablas
