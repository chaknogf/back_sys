from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from routers.pacientes import router as pacientes_router
from routers.consultas import router as consultas_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()


allow_origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redirecciona la ruta principal a la documentación ("/docs")
@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")

# Incluir el router de pacientes en la aplicación FastAPI
app.include_router(pacientes_router)
app.include_router(consultas_router)


