#!/usr/bin/env bash
# Aplica las migraciones numeradas del directorio migrations/ (nivel superior).
# Uso: ./migrations/apply.sh
# IMPORTANTE: solo toma los [0-9]*.sql que están directamente en migrations/.
# Lo que esté en migrations/archive/ se EXCLUYE a propósito (ya está aplicado).
# Requiere: psql en el PATH y las credenciales de abajo.
set -euo pipefail

PGHOST="${PGHOST:-localhost}"
PGUSER="${PGUSER:-admin}"
PGDATABASE="${PGDATABASE:-hospital}"
export PGPASSWORD="${PGPASSWORD:-secreto123}"

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Glob NO recursivo: nunca entra a archive/ (ni a ninguna subcarpeta).
shopt -s nullglob
FILES=("$DIR"/[0-9]*.sql)
shopt -u nullglob

if [ ${#FILES[@]} -eq 0 ]; then
    echo "No hay migraciones pendientes en $DIR."
    exit 0
fi

echo "Migraciones a aplicar (${#FILES[@]}):"
for f in "${FILES[@]}"; do
    echo "  - $(basename "$f")"
done
echo

for f in "${FILES[@]}"; do
    echo "==> $(basename "$f")"
    psql -h "$PGHOST" -U "$PGUSER" -d "$PGDATABASE" -v ON_ERROR_STOP=1 -f "$f"
done

echo "Migraciones aplicadas."
