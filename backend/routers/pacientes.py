from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.exc import SQLAlchemyError
from fastapi.responses import JSONResponse
from sqlalchemy import func, select, desc
from fastapi.encoders import jsonable_encoder
from database.database import SessionLocal, get_db
from models.pacientes_models import Paciente, VistaPacientes
from models.consultas_models import Expediente, VistaConsultas
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, time
import enum
from sqlalchemy.orm import Session


db = SessionLocal()
# Crear el router de FastAPI
router = APIRouter()

# Enum para Sexo
class SexoEnum(str, enum.Enum):
    M = "M"
    F = "F"

# Enum para Estado
class EstadoEnum(str, enum.Enum):
    V = "V"  # Vivo
    M = "M"  # Muerto

# Modelo Pydantic para paciente
class PacienteModel(BaseModel):
    nombre: str
    apellido: str
    dpi: Optional[int] = None
    pasaporte: Optional[str] = None
    sexo: SexoEnum = SexoEnum.M
    nacimiento: Optional[date] = None
    defuncion: Optional[date] = None
    tiempo_defuncion: Optional[time] = None
    nacionalidad_iso: Optional[str] = None
    lugar_nacimiento: Optional[str] = None
    estado_civil: Optional[int] = None
    educacion: Optional[int] = None
    pueblo: Optional[int] = None
    idioma: Optional[int] = None
    ocupacion: Optional[str] = None
    estado: EstadoEnum = EstadoEnum.V
    padre: Optional[str] = None
    madre: Optional[str] = None
    conyugue: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        orm_mode = True



# Modelo Pydantic para referencia de contacto
class ReferenciaContactoModel(BaseModel):
    paciente_id: Optional[int] = None
    nombre_contacto: Optional[str] = None
    telefono_contacto: Optional[str] = None
    parentesco_id: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        orm_mode = True

class VistaPaciente(BaseModel):
    paciente_id: Optional[int] = None
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    dpi: Optional[int] = None
    pasaporte: Optional[str] = None
    sexo: Optional[str] = None
    nacimiento: Optional[date] = None
    nacionalidad: Optional[str] = None
    lugar_nacimiento: Optional[str] = None
    defuncion: Optional[date] = None
    estado: Optional[str] = None
    gemelo: Optional[int] = None
    direccion: Optional[str] = None
    municipio: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    expediente: Optional[str] = None
    referencia_anterior: Optional[str] = None
    expediente_madre: Optional[str] = None
    consulta_id: Optional[int] = None
    exp_id: Optional[int] = None
    historia_clinica: Optional[str] = None
    fecha_consulta: Optional[date] = None
    hora: Optional[time] = None
    fecha_recepcion: Optional[str] = None
    fecha_egreso: Optional[str] = None
    tipo_consulta: Optional[int] = None
    estatus: Optional[int] = None
    created_at: Optional[str] = None
   
    class Config:
        orm_mode = True
        



# Ruta para obtener todos los pacientes
@router.get("/pacientes/", tags=["Pacientes"])
def get_pacientes(db: Session = Depends(get_db)):
    try:
        result = (
            db.query(VistaPacientes)
            .order_by(desc(VistaPacientes.created_at)) 
            .limit(300)
            .all()
        )
        return JSONResponse(status_code=200, content=jsonable_encoder(result))
    except SQLAlchemyError as error:
        raise HTTPException(status_code=500, detail=f"Error al consultar: {error}")

@router.get("/paciente_id/", tags=["Pacientes"])
async def get_paciente(db: Session = Depends(get_db),
                 id: int = Query(None, description="Id"),
    expediente: str = Query(None, description="Número de Expediente"),
    hoja: str = Query(None, description="Hoja de emergencia"),
    nombre: str = Query(None, description="Nombres"),
    apellido: str = Query(None, description="Apellidos"),
    dpi: str = Query(None, description="DPI"),
    nacimiento: str = Query(None, description="Fecha de nacimiento")):
    try:
        query = db.query(Paciente).order_by(desc(Paciente.paciente_id))

        if id is not None:
            query = query.filter(Paciente.paciente_id == id)
            
        if expediente is not None:
            query = query.filter(Paciente.expediente == expediente)
            
        if hoja is not None:
            query = query.filter(Paciente.hoja_emergencia.ilike(f"{hoja}%"))

        if nombre:
            query = query.filter(Paciente.nombre.ilike(f"%{nombre}%"))

        if apellido:
            query = query.filter(Paciente.apellido.ilike(f"%{apellido}%"))

        if dpi:
            query = query.filter(Paciente.dpi.ilike(f"%{dpi}%"))

        result = query.limit(800).all()
        return JSONResponse(status_code=200, content=jsonable_encoder({"results": result}))
    except SQLAlchemyError as e:
        # Manejar errores específicos de SQLAlchemy, si es necesario
        return {"error": str(e)}
    except Exception as e:
        # Manejar otros errores inesperados
        return {"error": str(e)}
    
@router.post("/registrarPaciente", tags=["Pacientes"])
def crear_paciente(paciente: PacienteModel, db: Session = Depends(get_db)):
    try:
        nuevo_paciente = Paciente(**paciente.dict())
        db.add(nuevo_paciente)
        db.commit()
        db.refresh(nuevo_paciente)
        return JSONResponse(status_code=201, content={"message": "Se ha registrado el paciente", "paciente_id": nuevo_paciente.id})
    except SQLAlchemyError as error:
        db.rollback()  # Revertir cualquier cambio en caso de error
        return JSONResponse(status_code=500, content={"message": f"Error al crear paciente: {str(error)}"})
    
