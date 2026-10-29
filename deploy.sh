#!/usr/bin/env bash
#
# Despliegue de BackSys Hospital.
#
# - Actualiza el repositorio, el gestor de paquetes (pip/setuptools/wheel) y
#   las dependencias de Python (requirements.txt).
# - Instala las dependencias de sistema que falten (python3/venv, psql, redis)
#   usando dnf/yum o apt-get. Desactivable con INSTALL_SYSTEM_DEPS=0.
# - Valida la configuración de .env y avisa de ajustes peligrosos en producción.
# - Respalda la base de datos antes de reiniciar servicios (SKIP_DB_BACKUP=1).
# - Asegura Redis, instala el unit de systemd y reinicia el servicio.
# - Verifica /health tras el reinicio.
#
# Variables sobreescribibles: PROJECT_DIR, VENV_DIR, SERVICE_NAME, WORKERS,
# DB_POOL_SIZE, INSTALL_SYSTEM_DEPS, SKIP_DB_BACKUP, HEALTH_URL.

set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-/opt/back_sys}"
VENV_DIR="${VENV_DIR:-$PROJECT_DIR/env}"
SERVICE_NAME="${SERVICE_NAME:-backsyshospital}"
HEALTH_URL="${HEALTH_URL:-http://127.0.0.1:8015/health}"
BACKUP_DIR="${BACKUP_DIR:-/home/matrix/predeploys}"

# ── Utilidades de salida ─────────────────────────────────────────
info()  { printf '\n\033[1;36m%s\033[0m\n' "$*"; }
ok()    { printf '\033[1;32m  ✓ %s\033[0m\n' "$*"; }
warn()  { printf '\033[1;33m  ! %s\033[0m\n' "$*" >&2; }
die()   { printf '\033[1;31mERROR: %s\033[0m\n' "$*" >&2; exit 1; }

# ── Sudo (o root directo) ────────────────────────────────────────
if [ "$(id -u)" -eq 0 ]; then
  SUDO=""
elif command -v sudo >/dev/null 2>&1; then
  SUDO="sudo"
else
  SUDO=""
  warn "No hay sudo y no eres root: los pasos del sistema pueden fallar."
fi

[ -d "$PROJECT_DIR" ] || die "No existe PROJECT_DIR=$PROJECT_DIR"
cd "$PROJECT_DIR"

printf '\033[1;35m=====================================\n'
printf '   BACKSYS HOSPITAL DEPLOY\n'
printf '=====================================\033[0m\n'

# ── [1/8] Cargar configuración (.env) ────────────────────────────
info "[1/8] Cargando configuración (.env)..."
if [ ! -f .env ]; then
  if [ -f .env.example ]; then
    cp .env.example .env
    die "Se creó .env desde .env.example. Edítalo con credenciales reales y vuelve a ejecutar."
  fi
  die "Falta .env y no hay .env.example para generarlo."
fi
set -a
# shellcheck disable=SC1091
source .env
set +a
: "${REDIS_URL:=redis://127.0.0.1:6379/0}"
: "${POSTGRES_HOST:=localhost}"
: "${POSTGRES_PORT:=5432}"
: "${POSTGRES_DB:=hospital}"
: "${POSTGRES_USER:=admin}"
export REDIS_URL POSTGRES_HOST POSTGRES_PORT POSTGRES_DB POSTGRES_USER
ok ".env cargado (BD=$POSTGRES_DB, host=$POSTGRES_HOST:$POSTGRES_PORT)"

# ── Validación de configuración crítica ──────────────────────────
info "[2/8] Validando configuración..."
missing=()
for v in SECRET_KEY POSTGRES_USER POSTGRES_DB POSTGRES_HOST POSTGRES_PASSWORD; do
  [ -n "${!v:-}" ] || missing+=("$v")
done
if [ ${#missing[@]} -gt 0 ]; then
  die "Variables obligatorias vacías en .env: ${missing[*]}"
fi
case "${SECRET_KEY}" in
  ""|genera_tu_clave_aqui|changeme|secret) die "SECRET_KEY no es válida (placeholder)." ;;
esac
[ ${#SECRET_KEY} -ge 32 ] || warn "SECRET_KEY tiene menos de 32 caracteres; usa 'python -c \"import secrets;print(secrets.token_hex(32))\"'."
if [ "${ENVIRONMENT:-development}" != "production" ]; then
  warn "ENVIRONMENT=${ENVIRONMENT:-development}. En producción define ENVIRONMENT=production."
fi
if [ "${ENVIRONMENT:-development}" = "production" ] && [ "${DEBUG:-false}" = "true" ]; then
  warn "DEBUG=true con ENVIRONMENT=production. Pon DEBUG=false."
fi
ok "Configuración validada"

# ── [3/8] Dependencias de sistema ────────────────────────────────
info "[3/8] Verificando dependencias de sistema..."

translate_pkg() { # $1 = nombre lógico, $2 = gestor
  case "$2:$1" in
    dnf:python3-venv|yum:python3-venv) echo "python3" ;;
    dnf:postgresql-client|yum:postgresql-client) echo "postgresql" ;;
    dnf:redis|yum:redis) echo "redis" ;;
    apt:redis) echo "redis-server" ;;
    apt:python3) echo "python3" ;;
    *) echo "$1" ;;
  esac
}

install_system_deps() {
  [ "${INSTALL_SYSTEM_DEPS:-1}" = "1" ] || { ok "Instalación de paquetes de sistema desactivada"; return 0; }

  local missing=()
  command -v python3 >/dev/null 2>&1 || missing+=("python3")
  if command -v python3 >/dev/null 2>&1 && ! python3 -c 'import venv' >/dev/null 2>&1; then
    missing+=("python3-venv")
  fi
  command -v psql >/dev/null 2>&1 || missing+=("postgresql-client")
  command -v redis-server >/dev/null 2>&1 || missing+=("redis")

  if [ ${#missing[@]} -eq 0 ]; then
    ok "Dependencias de sistema presentes"
    return 0
  fi

  warn "Faltan: ${missing[*]}"
  local pm="" list=()
  if command -v dnf >/dev/null 2>&1; then pm="dnf"
  elif command -v yum >/dev/null 2>&1; then pm="yum"
  elif command -v apt-get >/dev/null 2>&1; then pm="apt"
  else
    warn "No se detectó dnf/yum/apt-get. Instala manualmente: ${missing[*]}"
    return 0
  fi

  local p
  for p in "${missing[@]}"; do list+=("$(translate_pkg "$p" "$pm")"); done

  if [ "$pm" = "apt" ]; then
    $SUDO apt-get update -y
    $SUDO apt-get install -y "${list[@]}"
  else
    $SUDO "$pm" install -y "${list[@]}"
  fi
  ok "Paquetes de sistema instalados con $pm"
}
install_system_deps

# ── [4/8] Actualizar repositorio ─────────────────────────────────
info "[4/8] Actualizando repositorio..."
PREV_SHA="$(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
git pull --ff-only origin main
ok "Código actualizado ($PREV_SHA -> $(git rev-parse --short HEAD))"

# ── [5/8] Entorno virtual ────────────────────────────────────────
info "[5/8] Preparando entorno virtual..."
if [ ! -x "$VENV_DIR/bin/python" ]; then
  warn "No existe $VENV_DIR; creándolo con venv."
  python3 -m venv "$VENV_DIR"
fi
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
ok "Entorno activo: $(python -V)"

# ── [6/8] Actualizar gestor de paquetes e instalar dependencias ──
info "[6/8] Actualizando pip/setuptools/wheel..."
python -m pip install --upgrade pip setuptools wheel --quiet || true

info "[6/8] Instalando dependencias (requirements.txt)..."
python -m pip install -r requirements.txt
info "[6/8] Verificando consistencia de dependencias..."
if python -m pip check; then
  ok "Dependencias consistentes"
else
  warn "pip check reportó conflictos; revisa requirements."
fi

# Smoke test de imports críticos
python - <<'PY'
import importlib
for mod in ("fastapi", "sqlalchemy", "psycopg2", "joserfc", "passlib", "argon2", "redis", "gunicorn"):
    importlib.import_module(mod)
print("  ✓ imports críticos OK")
PY

# ── [7/8] Respaldo de base de datos ──────────────────────────────
info "[7/8] Respaldo de base de datos..."
if [ "${SKIP_DB_BACKUP:-0}" = "1" ]; then
  warn "Respaldo omitido (SKIP_DB_BACKUP=1)"
elif command -v pg_dump >/dev/null 2>&1; then
  mkdir -p "$BACKUP_DIR"
  BACKUP_FILE="$BACKUP_DIR/pre_deploy_$(date +%Y%m%d_%H%M%S).dump"
  if PGPASSWORD="$POSTGRES_PASSWORD" pg_dump \
      -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" \
      -d "$POSTGRES_DB" -Fc -f "$BACKUP_FILE"; then
    ok "Respaldo guardado: $BACKUP_FILE"
  else
    die "Falló pg_dump. Abortando (usa SKIP_DB_BACKUP=1 para omitir)."
  fi
else
  warn "pg_dump no disponible; se omite el respaldo."
fi

# Limpieza automática de respaldos antiguos (> 7 días) en la carpeta externa
find "$BACKUP_DIR" -name "pre_deploy_*.dump" -type f -mtime +7 -delete 2>/dev/null || true

# ── [9/8 - Redis] ────────────────────────────────────────────────
info "Verificando Redis (rate limit y caché compartidos)..."
redis_ok() { python -c "import redis; redis.Redis.from_url('$REDIS_URL', socket_connect_timeout=3, socket_timeout=3).ping()" >/dev/null 2>&1; }
if redis_ok; then
  ok "Redis responde en $REDIS_URL"
else
  warn "Redis no responde; intentando iniciarlo..."
  if command -v systemctl >/dev/null 2>&1; then
    $SUDO systemctl enable --now redis 2>/dev/null \
      || $SUDO systemctl enable --now redis-server 2>/dev/null \
      || $SUDO systemctl enable --now redis.service 2>/dev/null || true
  fi
  sleep 2
  redis_ok || die "Redis no responde en $REDIS_URL."
  ok "Redis iniciado"
fi

# ── [10/8] Permisos SELinux (si aplica) ──────────────────────────
info "Permisos SELinux..."
if command -v chcon >/dev/null 2>&1 && command -v getenforce >/dev/null 2>&1 \
   && [ "$(getenforce 2>/dev/null)" = "Enforcing" ]; then
  $SUDO chcon -R -t usr_t "$PROJECT_DIR"
  $SUDO chcon -R -t bin_t "$VENV_DIR/bin"
  ok "Contextos SELinux aplicados"
else
  ok "SELinux no enforcing; se omite"
fi

# ── [11/8] Servicio systemd ──────────────────────────────────────
info "Configurando servicio systemd ($SERVICE_NAME)..."
UNIT_SRC="$PROJECT_DIR/backsyshospital.service"
UNIT_DST="/etc/systemd/system/$SERVICE_NAME.service"
if [ -f "$UNIT_SRC" ]; then
  if command -v systemctl >/dev/null 2>&1; then
    if ! cmp -s "$UNIT_SRC" "$UNIT_DST" 2>/dev/null; then
      $SUDO cp "$UNIT_SRC" "$UNIT_DST"
      ok "Unit instalado en $UNIT_DST"
    else
      ok "Unit sin cambios"
    fi
    $SUDO systemctl daemon-reload
    $SUDO systemctl enable "$SERVICE_NAME" >/dev/null 2>&1 || true
  else
    warn "systemctl no disponible."
  fi
else
  warn "$UNIT_SRC no encontrado; se omite la instalación del servicio."
fi

# ── [12/8] Reiniciar y verificar ─────────────────────────────────
info "Reiniciando servicio..."
WORKERS="${WORKERS:-4}"
DB_POOL_SIZE="${DB_POOL_SIZE:-5}"
echo "  → Workers: $WORKERS"
echo "  → Pool de BD por worker: $DB_POOL_SIZE conexiones"

if command -v systemctl >/dev/null 2>&1; then
  $SUDO systemctl restart "$SERVICE_NAME"
else
  warn "systemctl no disponible: inicia manualmente gunicorn."
fi

# Pausa breve para dar tiempo a que Gunicorn levante los workers y abra el puerto
sleep 3

info "Verificando salud del servicio..."
healthy=0
for i in $(seq 1 20); do
  if command -v curl >/dev/null 2>&1; then
    if curl -fsS --max-time 3 "$HEALTH_URL" | grep -q '"status":"ok"'; then
      healthy=1
      break
    fi
  else
    if python - "$HEALTH_URL" <<'PY'
import sys, urllib.request
try:
    with urllib.request.urlopen(sys.argv[1], timeout=3) as r:
        sys.exit(0 if b'"status":"ok"' in r.read() else 1)
except Exception:
    sys.exit(1)
PY
    then 
      healthy=1
      break
    fi
  fi
  sleep 2
done

if [ "$healthy" != "1" ]; then
  printf '\n'
  warn "El servicio no respondió OK en $HEALTH_URL"
  warn "Revisa: journalctl -u $SERVICE_NAME -n 80 --no-pager"
  warn "Rollback: git reset --hard $PREV_SHA && $SUDO systemctl restart $SERVICE_NAME"
  die "Deploy finalizado con errores."
fi

printf '\n\033[1;35m=====================================\n'
printf ' DEPLOY COMPLETADO CORRECTAMENTE\n'
printf '=====================================\033[0m\n'
echo "  Servicio: $SERVICE_NAME"
echo "  Health:   $HEALTH_URL"
echo "  Código:   $(git rev-parse --short HEAD)"
echo "  Rollback: git reset --hard $PREV_SHA && $SUDO systemctl restart $SERVICE_NAME"