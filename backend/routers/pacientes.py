from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.exc import SQLAlchemyError
from fastapi.responses import JSONResponse
from sqlalchemy import func, select, desc
from fastapi.encoders import jsonable_encoder
from database.database import SessionLocal, get_db
from models.pacientes_models import Paciente, VistaPacientes, ConsultaRapida
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
    direccion: Optional[str] = None
    municipio: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    telefono2: Optional[str] = None
    telefono3: Optional[str] = None

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
class CosnultaRapida(BaseModel):
    consulta_id: Optional[int] = None
    paciente_id: Optional[int] = None
    exp_id: Optional[int] = None
    historia_clinica: Optional[str] = None
    fecha_consulta: Optional[date] = None
    hora: Optional[time] = None
    fecha_recepcion: Optional[str] = None
    fecha_egreso: Optional[str] = None
    tipo_consulta: Optional[int] = None
    estatus: Optional[int] = None
    
   
    class Config:
        orm_mode = True
    



# # Ruta para obtener todos los pacientes

@router.get("/pacientes/", tags=["Pacientes"])
def get_pacientes(db: Session = Depends(get_db)):
    try:
        result = (
            db.query(VistaPacientes)
            .order_by(desc(VistaPacientes.created_at)) 
            .limit(200)
            .all()
        )
        return JSONResponse(status_code=200, content=jsonable_encoder(result))
    except SQLAlchemyError as error:
        raise HTTPException(status_code=500, detail=f"Error al consultar: {error}")
    
    
@router.get("/datapaciente/{id}", tags=["Pacientes"])
def get_pacientes(id: int, db: Session = Depends(get_db)):
    try:
        result = (
            db.query(Paciente)
            .filter(Paciente.id == id)
            .first()
        )
        return JSONResponse(status_code=200, content=jsonable_encoder(result))
    except SQLAlchemyError as error:
        raise HTTPException(status_code=500, detail=f"Error al consultar: {error}")
    
@router.get("/consultarapida/", tags=["Pacientes"])
def get_consultaRapida(paciente_id: int, db: Session = Depends(get_db)):
    try:        
        result = (
            db.query(ConsultaRapida)  # Corregido el nombre del modelo
            .filter(ConsultaRapida.paciente_id == paciente_id)  
            .all()  # Ejecuta la consulta y obtiene todos los resultados
        )
        return JSONResponse(status_code=200, content=jsonable_encoder(result))
    except SQLAlchemyError as error:
        raise HTTPException(status_code=500, detail=f"Error al consultar: {error}")

@router.get("/paciente_id/", tags=["Pacientes"])
async def get_paciente(
    db: Session = Depends(get_db),
    id: Optional[int] = Query(None, description="Id del paciente"),
    expediente: Optional[str] = Query(None, description="Número de expediente"),
    madre: Optional[str] = Query(None, description="Número de expediente de la madre"),
    consulta: Optional[str] = Query(None, description="Consulta"),
    nombre: Optional[str] = Query(None, description="Nombre del paciente"),
    apellido: Optional[str] = Query(None, description="Apellido del paciente"),
    dpi: Optional[str] = Query(None, description="DPI del paciente"),
    nacimiento: Optional[str] = Query(None, description="Fecha de nacimiento en formato YYYY-MM-DD")
):
    try:
        # Construir la consulta base
        query = db.query(VistaPacientes)

        # Aplicar filtros dinámicos según los parámetros recibidos
        if id is not None:
            query = query.filter(VistaPacientes.paciente_id == id)

        if expediente is not None:
            # Si expediente tiene un valor, buscar en expediente
            query = query.filter(VistaPacientes.expediente == expediente)
        else:
            # Si expediente es None, buscar en referencia_anterior
            query = query.filter(VistaPacientes.referencia_anterior.isnot(None))

        if madre is not None:
            query = query.filter(VistaPacientes.expediente_madre == madre)
        if consulta is not None:
            query = query.filter(VistaPacientes.historia_clinica == consulta)
        if nombre is not None:
            query = query.filter(VistaPacientes.nombre.ilike(f"%{nombre}%"))
        if apellido is not None:
            query = query.filter(VistaPacientes.apellido.ilike(f"%{apellido}%"))
        if dpi is not None:
            query = query.filter(VistaPacientes.dpi.ilike(f"%{dpi}%"))
        if nacimiento is not None:
            query = query.filter(VistaPacientes.nacimiento == nacimiento)
        # Obtener resultados con un límite
        result = query.all()

        # Validar si no hay resultados
        if not result:
            raise HTTPException(status_code=404, detail="No hay coincidencias")

        # Retornar resultados en una estructura descriptiva
        return JSONResponse(
            status_code=200,
            content=jsonable_encoder(result)
        )
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar la base de datos: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")
    
    
    
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
    
@router.put("/actualizarPaciente/{id}", tags=["Pacientes"])
def actualizar_paciente(id: int, paciente: PacienteModel, db: Session = Depends(get_db)):
    try:
        paciente_actualizado = (
            db.query(Paciente)
            .filter(Paciente.id == id)
            .update(paciente.dict())
        )
        db.commit()
        return JSONResponse(status_code=200, content={"message": "Se ha actualizado el paciente"})
    except SQLAlchemyError as error:
        db.rollback()
        return JSONResponse(status_code=500, content={"message": f"Error al actualizar paciente: {str(error)}"})
    
@router.delete("/eliminarPaciente/{id}", tags=["Pacientes"])
def eliminar_paciente(id: int, db: Session = Depends(get_db)):
    try:
        paciente_eliminado = db.query(Paciente).filter(Paciente.id == id).delete()
        db.commit()
        return JSONResponse(status_code=200, content={"message": "Se ha eliminado el paciente"})
    except SQLAlchemyError as error:
        db.rollback()
        return JSONResponse(status_code=500, content={"message": f"Error al eliminar paciente: {str(error)}"})