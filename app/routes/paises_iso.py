from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy.exc import SQLAlchemyError
from app.database.db import SessionLocal
from app.models.paises_iso import PaisIsoModel
from app.schemas.paises_iso import PaisOut
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/paises_iso/", response_model=list[PaisOut], tags=["paises_iso"])
async def get_paises_iso(
    db: SQLAlchemySession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    try:
        return db.query(PaisIsoModel).all()
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))