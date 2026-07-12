#!/usr/bin/env bash

set -e

echo "====================================="
echo "   BACKSYS HOSPITAL DEPLOY"
echo "====================================="

PROJECT_DIR="/opt/back_sys"
VENV_DIR="$PROJECT_DIR/env"

cd "$PROJECT_DIR"

echo ""
echo "[1/9] Actualizando repositorio..."
git pull origin main

echo ""
echo "[2/9] Activando entorno virtual..."
source "$VENV_DIR/bin/activate"

echo ""
echo "[3/9] Actualizando pip..."
pip install --upgrade pip

echo ""
echo "[4/9] Instalando dependencias..."
pip install -r requirements.txt
pip install --upgrade authlib fastapi starlette sqlalchemy idna slowapi gunicorn

echo ""
echo "[5/9] Ejecutando migraciones de seguridad..."
python -c "
from joserfc import jwt
print('✅ joserfc instalado correctamente')
"

echo ""
echo "[6.5/9] Descargando catálogo CIE-10 (primer inicio)..."
python -c "
from core.database import SessionLocal, engine
from modules.cie10.service import asegurar_catalogo
db = SessionLocal()
try:
    total = asegurar_catalogo(db)
    print(f'  → Catálogo CIE-10: {total} códigos')
finally:
    db.close()
"

echo ""
echo "[7/9] Ejecutando migraciones de índices de concurrencia..."
if command -v psql &> /dev/null; then
    psql -d "$POSTGRES_DB" -f scripts/indices_concurrencia.sql 2>/dev/null \
        || echo "  → Nota: algunos índices ya existen (ok)"
else
    echo "  → psql no disponible, ejecutar manualmente:"
    echo "     psql -d hospital -f scripts/indices_concurrencia.sql"
fi

echo ""
echo "[8/9] Aplicando permisos SELinux..."
sudo chcon -R -t usr_t /opt/back_sys
sudo chcon -R -t bin_t /opt/back_sys/env/bin

echo ""
echo "[9/9] Configurando workers de producción..."
WORKERS=${WORKERS:-4}
echo "  → Workers: $WORKERS"
echo "  → Pool de BD por worker: ${DB_POOL_SIZE:-10} conexiones"
echo "  → Total conexiones estimadas: $((WORKERS * ${DB_POOL_SIZE:-10}))"

echo ""
echo "[10/9] Reiniciando servicio..."
# Si usas systemd con gunicorn:
#   sudo cp backsyshospital.service /etc/systemd/system/
#   sudo systemctl daemon-reload
sudo systemctl restart backsyshospital

echo ""
echo "====================================="
echo "  Comando manual de inicio:"
echo "  gunicorn main:app \\"
echo "    -c gunicorn.conf.py \\"
echo "    --access-logfile /var/log/back_sys/access.log \\"
echo "    --error-logfile /var/log/back_sys/error.log"
echo "====================================="

echo ""
echo "====================================="
echo " DEPLOY COMPLETADO CORRECTAMENTE"
echo "====================================="