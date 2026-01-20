#m
from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from app.routes.user import router as user
from app.routes.pacientes import router as pacientes
from app.routes.recienNacido import router as recienNacido
from app.routes.consultas import router as consultas
from app.routes.expediente import router as expediente
from app.routes.municipios import router as municipios
from app.routes.paises_iso import router as paises
from app.routes.total import router as total

from app.routes.renap import router as renap


from app.auth.login import router as login



# ====================== APLICACIÓN FASTAPI ======================
app = FastAPI(
    title="Hospital General Tipo I de Tecpán - Sistema FAH",
    version="3.0.0",
    description="""
    **Sistema de Gestión Hospitalaria**
    
    Características:
    - Integración RENAP Guatemala --nightly--
    - Expediente Único Electrónico
    - Dashboard en tiempo real
    - Autenticación JWT + Argon2
    - 100% desarrollado en Guatemala
    - Desarrollado por Ronald Chacón  www.ronchak.dev
    """,
    contact={
        "name": "Departamento de Informática - Hospital General Tipo I de Tecpán Guatemala",
        "email": "sistemas@hospitaltecpan.gob.gt",
    },
    license_info={
        "name": "Ronald Chacón",
        "url": "https://www.ronchak.dev",
       "para": "Hospital General Tipo I de Tecpán Guatemala"
        
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    root_path="/fah",  # ← IMPORTANTE para DuckDNS + proxy
   
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(login)
app.include_router(user)
app.include_router(pacientes)
app.include_router(recienNacido)
app.include_router(expediente)
app.include_router(consultas)
app.include_router(municipios)
app.include_router(paises)
app.include_router(renap)
app.include_router(total)




@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")

