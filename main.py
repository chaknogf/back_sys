from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sqlalchemy import text

from core.database import engine
from core.exceptions import register_exception_handlers

from modules.auth.router import router as auth_router
from modules.users.router import router as users_router
from modules.pacientes.router import router as pacientes_router
from modules.pacientes.duplicados_router import router as duplicados_router
from modules.pacientes.merge_router import router as merge_router
from modules.pacientes.recien_nacido_router import router as recien_nacido_router
from modules.consultas.router import router as consultas_router
from modules.ciclos.router import router as ciclos_router
from modules.citas.router import router as citas_router
from modules.medicos.router import router as medicos_router
from modules.nacimientos_legacy.router import router as nacimientos_legacy_router
from modules.constancias_nacimiento.router import router as constancias_nacimiento_router
from modules.expediente.router import router as expediente_router
from modules.municipios.router import router as municipios_router
from modules.paises_iso.router import router as paises_router
from modules.renap.router import router as renap_router
from modules.totales.router import router as totales_router
from modules.prestamos.router import router as prestamos_router
from modules.procedimientos.router import router as procedimientos_router
from modules.eventos.router import router as eventos_router
from modules.estadisticas.router import router as estadisticas_router

app = FastAPI(
    title="Hospital General Tipo I de Tecpán - Sistema FAH",
    version="3.0.0",
    description="""
    **Sistema de Gestión Hospitalaria**

    Características:

    - Expediente Único Electrónico
    - Dashboard en tiempo real
    - Autenticación JWT + Argon2
    - 100% desarrollado en Guatemala
    - Desarrollado por Ronald Chacón  www.ronchak.dev
    """,
    contact={
        "name": "Departamento de Registros Médicos y Estadísticas - Hospital General Tipo I de Tecpán Guatemala",
        "email": "chaknogf@gmail.com",
    },
    license_info={
        "name": "Ronald Chacón",
        "url": "https://www.ronchak.dev",
        "para": "Hospital General Tipo I de Tecpán Guatemala"
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    root_path="/fah",
)

register_exception_handlers(app)


@app.get("/health")
def health():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "database": str(e)}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(pacientes_router)
app.include_router(duplicados_router)
app.include_router(merge_router)
app.include_router(recien_nacido_router)
app.include_router(consultas_router)
app.include_router(ciclos_router)
app.include_router(citas_router)
app.include_router(medicos_router)
app.include_router(nacimientos_legacy_router)
app.include_router(constancias_nacimiento_router)
app.include_router(expediente_router)
app.include_router(municipios_router)
app.include_router(paises_router)
app.include_router(renap_router)
app.include_router(totales_router)
app.include_router(prestamos_router)
app.include_router(procedimientos_router)
app.include_router(eventos_router)
app.include_router(estadisticas_router)


@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")
