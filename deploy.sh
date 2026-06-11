#!/usr/bin/env bash

set -e

echo "====================================="
echo "   BACKSYS HOSPITAL DEPLOY"
echo "====================================="

PROJECT_DIR="/opt/back_sys"
VENV_DIR="$PROJECT_DIR/env"

cd "$PROJECT_DIR"

echo ""
echo "[1/6] Actualizando repositorio..."
git pull origin main

echo ""
echo "[2/6] Activando entorno virtual..."
source "$VENV_DIR/bin/activate"

echo ""
echo "[3/6] Actualizando pip..."
pip install --upgrade pip

echo ""
echo "[4/6] Instalando dependencias..."
pip install -r requirements.txt

echo ""
echo "[5/6] Aplicando permisos SELinux..."
sudo chcon -R -t usr_t /opt/back_sys
sudo chcon -R -t bin_t /opt/back_sys/env/bin

echo ""
echo "[6/6] Reiniciando servicio..."
sudo systemctl restart backsyshospital

echo ""
echo "====================================="
echo " DEPLOY COMPLETADO CORRECTAMENTE"
echo "====================================="