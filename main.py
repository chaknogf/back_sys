from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from app.routes.user import router as user
from app.routes.pacientes import router as pacientes
from app.routes.consultas import router as consultas
from app.routes.eventos import router as eventos

from app.auth.login import router as login



app = FastAPI()

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
app.include_router(consultas)
app.include_router(eventos)




@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")

