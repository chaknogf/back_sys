from fastapi import APIRouter, Depends, Query, status, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from core.dependencies import get_db, get_current_admin_user, get_current_user
from modules.users.models import UserModel

from . import schemas as sch
from . import service as svc

router = APIRouter(
    prefix="/quirofano",
    tags=["Quirófano"],
)


# ========================
# Formato Procedimiento
# ========================
@router.get("/formatos", response_model=List[sch.FormatoProcedimientoOut])
@router.get("/formatos/", response_model=List[sch.FormatoProcedimientoOut])
def listar_formatos(
    activos: bool = Query(True, description="Solo activos"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return svc.listar_formatos(db, solo_activos=activos)


@router.get("/formatos/{formato_id}", response_model=sch.FormatoProcedimientoOut)
def obtener_formato(
    formato_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return svc.obtener_formato(formato_id, db)


@router.post("/formatos", response_model=sch.FormatoProcedimientoOut, status_code=status.HTTP_201_CREATED)
@router.post("/formatos/", response_model=sch.FormatoProcedimientoOut, status_code=status.HTTP_201_CREATED)
def crear_formato(
    data: sch.FormatoProcedimientoCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user),
):
    return svc.crear_formato(data, db)


@router.put("/formatos/{formato_id}", response_model=sch.FormatoProcedimientoOut)
def actualizar_formato(
    formato_id: int,
    data: sch.FormatoProcedimientoUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user),
):
    return svc.actualizar_formato(formato_id, data, db)


@router.delete("/formatos/{formato_id}")
def eliminar_formato(
    formato_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user),
):
    return svc.eliminar_formato(formato_id, db)


# ========================
# Estado Cirugía
# ========================
@router.get("/estados-cirugia", response_model=List[sch.EstadoCirugiaOut])
@router.get("/estados-cirugia/", response_model=List[sch.EstadoCirugiaOut])
def listar_estados_cirugia(
    activos: bool = Query(True, description="Solo activos"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return svc.listar_estados_cirugia(db, solo_activos=activos)


@router.get("/estados-cirugia/{estado_id}", response_model=sch.EstadoCirugiaOut)
def obtener_estado_cirugia(
    estado_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return svc.obtener_estado_cirugia(estado_id, db)


@router.post("/estados-cirugia", response_model=sch.EstadoCirugiaOut, status_code=status.HTTP_201_CREATED)
@router.post("/estados-cirugia/", response_model=sch.EstadoCirugiaOut, status_code=status.HTTP_201_CREATED)
def crear_estado_cirugia(
    data: sch.EstadoCirugiaCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user),
):
    return svc.crear_estado_cirugia(data, db)


@router.put("/estados-cirugia/{estado_id}", response_model=sch.EstadoCirugiaOut)
def actualizar_estado_cirugia(
    estado_id: int,
    data: sch.EstadoCirugiaUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user),
):
    return svc.actualizar_estado_cirugia(estado_id, data, db)


@router.delete("/estados-cirugia/{estado_id}")
def eliminar_estado_cirugia(
    estado_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user),
):
    return svc.eliminar_estado_cirugia(estado_id, db)


# ========================
# Rango Especialista
# ========================
@router.get("/rangos-especialista", response_model=List[sch.RangoEspecialistaOut])
@router.get("/rangos-especialista/", response_model=List[sch.RangoEspecialistaOut])
def listar_rangos_especialista(
    activos: bool = Query(True, description="Solo activos"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return svc.listar_rangos_especialista(db, solo_activos=activos)


@router.get("/rangos-especialista/{rango_id}", response_model=sch.RangoEspecialistaOut)
def obtener_rango_especialista(
    rango_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return svc.obtener_rango_especialista(rango_id, db)


@router.post("/rangos-especialista", response_model=sch.RangoEspecialistaOut, status_code=status.HTTP_201_CREATED)
@router.post("/rangos-especialista/", response_model=sch.RangoEspecialistaOut, status_code=status.HTTP_201_CREATED)
def crear_rango_especialista(
    data: sch.RangoEspecialistaCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user),
):
    return svc.crear_rango_especialista(data, db)


@router.put("/rangos-especialista/{rango_id}", response_model=sch.RangoEspecialistaOut)
def actualizar_rango_especialista(
    rango_id: int,
    data: sch.RangoEspecialistaUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user),
):
    return svc.actualizar_rango_especialista(rango_id, data, db)


@router.delete("/rangos-especialista/{rango_id}")
def eliminar_rango_especialista(
    rango_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user),
):
    return svc.eliminar_rango_especialista(rango_id, db)


# ========================
# Procedencia Procedimiento
# ========================
@router.get("/procedencias", response_model=List[sch.ProcedenciaProcedimientoOut])
@router.get("/procedencias/", response_model=List[sch.ProcedenciaProcedimientoOut])
def listar_procedencias(
    activos: bool = Query(True, description="Solo activos"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return svc.listar_procedencias(db, solo_activos=activos)


@router.get("/procedencias/{procedencia_id}", response_model=sch.ProcedenciaProcedimientoOut)
def obtener_procedencia(
    procedencia_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return svc.obtener_procedencia(procedencia_id, db)


@router.post("/procedencias", response_model=sch.ProcedenciaProcedimientoOut, status_code=status.HTTP_201_CREATED)
@router.post("/procedencias/", response_model=sch.ProcedenciaProcedimientoOut, status_code=status.HTTP_201_CREATED)
def crear_procedencia(
    data: sch.ProcedenciaProcedimientoCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user),
):
    return svc.crear_procedencia(data, db)


@router.put("/procedencias/{procedencia_id}", response_model=sch.ProcedenciaProcedimientoOut)
def actualizar_procedencia(
    procedencia_id: int,
    data: sch.ProcedenciaProcedimientoUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user),
):
    return svc.actualizar_procedencia(procedencia_id, data, db)


@router.delete("/procedencias/{procedencia_id}")
def eliminar_procedencia(
    procedencia_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user),
):
    return svc.eliminar_procedencia(procedencia_id, db)


# ========================
# Número de Quirófano
# ========================
@router.get("/quirofanos-numero", response_model=List[sch.QuirofanoNumeroOut])
@router.get("/quirofanos-numero/", response_model=List[sch.QuirofanoNumeroOut])
def listar_quirofanos_numero(
    activos: bool = Query(True, description="Solo activos"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return svc.listar_quirofanos_numero(db, solo_activos=activos)


@router.get("/quirofanos-numero/{qn_id}", response_model=sch.QuirofanoNumeroOut)
def obtener_quirofano_numero(
    qn_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return svc.obtener_quirofano_numero(qn_id, db)


@router.post("/quirofanos-numero", response_model=sch.QuirofanoNumeroOut, status_code=status.HTTP_201_CREATED)
@router.post("/quirofanos-numero/", response_model=sch.QuirofanoNumeroOut, status_code=status.HTTP_201_CREATED)
def crear_quirofano_numero(
    data: sch.QuirofanoNumeroCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user),
):
    return svc.crear_quirofano_numero(data, db)


@router.put("/quirofanos-numero/{qn_id}", response_model=sch.QuirofanoNumeroOut)
def actualizar_quirofano_numero(
    qn_id: int,
    data: sch.QuirofanoNumeroUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user),
):
    return svc.actualizar_quirofano_numero(qn_id, data, db)


@router.delete("/quirofanos-numero/{qn_id}")
def eliminar_quirofano_numero(
    qn_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user),
):
    return svc.eliminar_quirofano_numero(qn_id, db)


# ========================
# Categoría Procedimiento
# ========================
@router.get("/categorias", response_model=List[sch.CategoriaProcedimientoOut])
@router.get("/categorias/", response_model=List[sch.CategoriaProcedimientoOut])
def listar_categorias(
    activos: bool = Query(True, description="Solo activos"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return svc.listar_categorias(db, solo_activos=activos)


@router.get("/categorias/{categoria_id}", response_model=sch.CategoriaProcedimientoOut)
def obtener_categoria(
    categoria_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return svc.obtener_categoria(categoria_id, db)


@router.get("/categorias/{categoria_id}/con-tipos", response_model=sch.CategoriaProcedimientoConTiposOut)
def obtener_categoria_con_tipos(
    categoria_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    from .models import CategoriaProcedimientoModel
    reg = db.query(CategoriaProcedimientoModel).filter(
        CategoriaProcedimientoModel.categoria_procedimiento_id == categoria_id
    ).first()
    if not reg:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return reg


@router.post("/categorias", response_model=sch.CategoriaProcedimientoOut, status_code=status.HTTP_201_CREATED)
@router.post("/categorias/", response_model=sch.CategoriaProcedimientoOut, status_code=status.HTTP_201_CREATED)
def crear_categoria(
    data: sch.CategoriaProcedimientoCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user),
):
    return svc.crear_categoria(data, db)


@router.put("/categorias/{categoria_id}", response_model=sch.CategoriaProcedimientoOut)
def actualizar_categoria(
    categoria_id: int,
    data: sch.CategoriaProcedimientoUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user),
):
    return svc.actualizar_categoria(categoria_id, data, db)


@router.delete("/categorias/{categoria_id}")
def eliminar_categoria(
    categoria_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user),
):
    return svc.eliminar_categoria(categoria_id, db)


# ========================
# Tipo Procedimiento
# ========================
@router.get("/tipos", response_model=List[sch.TipoProcedimientoOut])
@router.get("/tipos/", response_model=List[sch.TipoProcedimientoOut])
def listar_tipos_procedimiento(
    activos: bool = Query(True, description="Solo activos"),
    categoria_id: Optional[int] = Query(None, description="Filtrar por categoría"),
    q: Optional[str] = Query(None, description="Buscar por nombre o código"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return svc.listar_tipos_procedimiento(db, solo_activos=activos, categoria_id=categoria_id, q=q)


@router.get("/tipos/{tipo_id}", response_model=sch.TipoProcedimientoConCategoriaOut)
def obtener_tipo_procedimiento(
    tipo_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    from .models import TipoProcedimientoModel
    reg = db.query(TipoProcedimientoModel).filter(
        TipoProcedimientoModel.tipo_procedimiento_id == tipo_id
    ).first()
    if not reg:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Tipo de procedimiento no encontrado")
    return reg


@router.post("/tipos", response_model=sch.TipoProcedimientoOut, status_code=status.HTTP_201_CREATED)
@router.post("/tipos/", response_model=sch.TipoProcedimientoOut, status_code=status.HTTP_201_CREATED)
def crear_tipo_procedimiento(
    data: sch.TipoProcedimientoCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user),
):
    return svc.crear_tipo_procedimiento(data, db)


@router.put("/tipos/{tipo_id}", response_model=sch.TipoProcedimientoOut)
def actualizar_tipo_procedimiento(
    tipo_id: int,
    data: sch.TipoProcedimientoUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user),
):
    return svc.actualizar_tipo_procedimiento(tipo_id, data, db)


@router.delete("/tipos/truncar")
def truncar_tipos(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user),
):
    return svc.truncar_tipos(db)


@router.post("/tipos/importar-csv")
async def importar_csv_tipos(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user),
):
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="El archivo debe ser un CSV (.csv)")
    contenido = (await file.read()).decode("utf-8")
    return svc.importar_csv_tipos(contenido, db)


@router.delete("/tipos/{tipo_id}")
def eliminar_tipo_procedimiento(
    tipo_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user),
):
    return svc.eliminar_tipo_procedimiento(tipo_id, db)


# ========================
# Intervención Quirúrgica
# ========================
@router.get("/intervenciones", response_model=sch.IntervencionQuirurgicaListResponse)
@router.get("/intervenciones/", response_model=sch.IntervencionQuirurgicaListResponse)
def listar_intervenciones(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    expediente: Optional[str] = Query(None),
    fecha_desde: Optional[date] = Query(None, alias="fecha_desde"),
    fecha_hasta: Optional[date] = Query(None, alias="fecha_hasta"),
    activos: Optional[bool] = Query(True),
    q: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return svc.listar_intervenciones(
        db,
        skip=skip,
        limit=limit,
        expediente=expediente,
        fecha_desde=fecha_desde.isoformat() if fecha_desde else None,
        fecha_hasta=fecha_hasta.isoformat() if fecha_hasta else None,
        activo=activos,
        q=q,
    )


@router.get("/intervenciones/{intervencion_id}", response_model=sch.IntervencionQuirurgicaOut)
def obtener_intervencion(
    intervencion_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return svc.obtener_intervencion(intervencion_id, db)


@router.post("/intervenciones", response_model=sch.IntervencionQuirurgicaOut, status_code=status.HTTP_201_CREATED)
@router.post("/intervenciones/", response_model=sch.IntervencionQuirurgicaOut, status_code=status.HTTP_201_CREATED)
def crear_intervencion(
    data: sch.IntervencionQuirurgicaCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return svc.crear_intervencion(data, db, created_by=current_user.username)


@router.put("/intervenciones/{intervencion_id}", response_model=sch.IntervencionQuirurgicaOut)
def actualizar_intervencion(
    intervencion_id: int,
    data: sch.IntervencionQuirurgicaUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return svc.actualizar_intervencion(intervencion_id, data, db)


@router.delete("/intervenciones/{intervencion_id}")
def eliminar_intervencion(
    intervencion_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return svc.eliminar_intervencion(intervencion_id, db)