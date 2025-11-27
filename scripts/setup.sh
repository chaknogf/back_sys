#!/bin/bash

echo "Activando entorno virtual..."
source .venv/bin/activate

echo "Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Listo. Puedes ejecutar la API con:"
echo "uvicorn app.main:app --reload"