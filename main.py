from fastapi import FastAPI
from fastapi.responses import RedirectResponse




app = FastAPI()


@app.get("/", include_in_schema=False)
def docs():
    return RedirectResponse(url="/docs")