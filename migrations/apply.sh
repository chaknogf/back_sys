#!/usr/bin/env bash
# Aplica todas las migraciones numeradas de back_sys en orden.
# Uso: ./migrations/apply.sh
# Requiere: psql en el PATH y las credenciales de abajo.
set -euo pipefail

PGHOST="${PGHOST:-localhost}"
PGUSER="${PGUSER:-admin}"
PGDATABASE="${PGDATABASE:-hospital}"
export PGPASSWORD="${PGPASSWORD:-secreto123}"

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

for f in $(ls "$DIR"/[0-9]*.sql | sort); do
    echo "==> $(basename "$f")"
    psql -h "$PGHOST" -U "$PGUSER" -d "$PGDATABASE" -v ON_ERROR_STOP=1 -f "$f"
done

echo "Migraciones aplicadas."
