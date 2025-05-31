from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.db import SessionLocal
from app.utils.expediente import generar_expediente, generar_emergencia

router = APIRouter(tags=["Correlativos"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/generar/expediente")
def nuevo_expediente(db: Session = Depends(get_db)):
    expediente = generar_expediente(db)
    return {"correlativo de expediente": expediente}

@router.post("/generar/emergencia")
def nuevo_expediente(db: Session = Depends(get_db)):
    hoja = generar_emergencia(db)
    return {"correlativo de emergencia": hoja}