from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from routers.pacientes import router as pacientes_router


app = FastAPI()

# Redirecciona la ruta principal a la documentación ("/docs")
@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")

# Incluir el router de pacientes en la aplicación FastAPI
app.include_router(pacientes_router)


