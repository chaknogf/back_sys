# Scripts de Base de Datos — back_sys

## Fix nombre_completo

Corrige el campo `nombre_completo` en la tabla `pacientes` para que:

1. Use **UPPERCASE** (mayúsculas) en todo el nombre
2. Agregue **"de "** antes de `apellido_casada` (ej: `MARIA PEREZ LOPEZ DE GARCIA`)
3. Evite duplicar el "de " si ya existe (ej: `DE LEON` no se convierte en `DE DE LEON`)

### Uso

```bash
psql -d hospital -f fix_nombre_completo_existing.sql
```

Si la base tiene otro nombre, host o usuario:

```bash
psql -h <host> -U <user> -d <db> -f fix_nombre_completo_existing.sql
```

### Qué hace

| Paso | Descripción |
|------|-------------|
| 1 | Actualiza el trigger `actualizar_nombre_completo()` para aplicar UPPERCASE y el prefijo "de " |
| 2 | Refresca registros con `apellido_casada` (corrige el "de " faltante) |
| 3 | Refresca registros sin `apellido_casada` que no estén en mayúsculas |

### Rollback manual en caso de error

Si algo sale mal, el script está envuelto en una transacción (`BEGIN/COMMIT`). Si falla, no persiste ningún cambio.

---

## Otros scripts

| Script | Descripción |
|--------|-------------|
| `setup.sh` | Configuración inicial del proyecto |
| `fix_normalize_tipo_parto.sql` | Normaliza valores de tipo/clase de parto |
| `fix_swap_tipo_clase_parto.sql` | Intercambia tipo y clase de parto |
| `refactor_nacimientos.sql` | Refactor de la tabla nacimientos |
