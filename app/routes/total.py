from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy.exc import SQLAlchemyError
from app.database.db import SessionLocal
from app.schemas.totales import TotalesResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import text

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        

@router.get("/totales/", response_model=list[TotalesResponse], tags=["totales"])
def obtener_totales(
    db: SQLAlchemySession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    try:
        query = text("SELECT entidad, total FROM vista_totales;")
        result = db.execute(query).fetchall()
        return [{"entidad": row[0], "total": row[1]} for row in result]
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    