# Nota: Análisis del Endpoint /estadisticas/nacimientos

**Fecha**: 2026-07-01  
**Problema reportado**: El endpoint `/estadisticas/nacimientos` devuelve valores `null` en `trabajo_parto` para la mayoría de registros.

---

## 1. Problema Original

El usuario reportó que `/estadisticas/nacimientos` devolvía:

```json
{
  "trabajo_parto": "Termino", "estado": "Vivo", "sexo": "F", "total": 3
},
{
  "trabajo_parto": null, "estado": "Vivo", "sexo": "F", "total": 36
}
```

Y en el listado de `/nacimientos/` la mayoría de registros tenían `trabajo_parto` vacío.

---

## 2. Análisis de Causa Raíz

### Cómo se calcula `trabajo_parto`

El campo `trabajo_parto` se **computa** (no almacena directamente) a partir de `pacientes.datos_extra.neonatales.edad_gestacional`:

```python
# modules/nacimientos/service.py:168
def trabajo_parto(eg: str | None) -> str | None:
    if not eg:
        return None
    semanas = Decimal(str(eg).strip())
    if semanas > 41:
        return "Prolongado"
    if semanas < 37:
        return "Prematuro"
    return "a Termino"
```

La función `_computar()` (service.py:182) calcula `peso_gramos`, `clasificacion_nacimiento` y `trabajo_parto` desde los datos neonatales del paciente.

### Flujo de lectura (`_row_to_out`)

```
1. Lee pacientes.datos_extra.neonatales
2. Si tiene datos → _computar(neonatales) → calcula valores
3. Si no tiene datos o computa null → usa valor almacenado en nacimientos.tabla
```

### El problema real

**La mayoría de pacientes no tienen `edad_gestacional`** en `datos_extra.neonatales`:

```
nacimientos: 5823 registros
├── Con edad_gestacional en paciente: ~131
├── Sin datos neonatales en paciente: ~5692
└── Con neonatales pero sin edad_gestacional: ~80
```

Cuando `edad_gestacional` es `null`, `_computar()` retorna `trabajo_parto = null`.

---

## 3. Bugs Encontrados y Corregidos

### Bug 1: `_recomputar_desde_origen` sobrescribía valores existentes con null

**Archivo**: `modules/nacimientos/service.py:191`

**Problema**: La función se ejecuta cada vez que se consulta un nacimiento (`obtener_nacimiento`). Comparaba el valor computado con el almacenado y lo sobrescribía, incluso si el computado era `null`.

```python
# ANTES (bug)
if computado["trabajo_parto"] != nacimiento.trabajo_parto:
    nacimiento.trabajo_parto = computado["trabajo_parto"]  # ← sobrescribe con null
```

**Corrección**: Solo sobrescribir si el valor computado NO es null:

```python
# DESPUÉS (corregido)
if tiene_eg and computado["trabajo_parto"] is not None and computado["trabajo_parto"] != nacimiento.trabajo_parto:
    nacimiento.trabajo_parto = computado["trabajo_parto"]
```

### Bug 2: `peso_lb_onz_a_gramos` no manejaba tipos numéricos

**Archivo**: `modules/nacimientos/service.py:131`

**Problema**: El campo `peso_nacimiento` puede ser un float/int en JSON, pero la función llamaba `.strip()` directamente.

```python
# ANTES (bug)
peso_clean = peso.strip().upper()  # ← error si peso es float
```

**Corrección**: Convertir a string primero:

```python
# DESPUÉS (corregido)
peso_clean = str(peso).strip().upper()
```

### Bug 3: Conflicto de rutas en el router

**Archivo**: `modules/nacimientos/router.py`

**Problema**: `GET /referenciar-legacy` y `POST /recomputar` estaban definidas DESPUÉS de `GET /{nacimiento_id}`, causando que FastAPI las interpretara como parámetros de ruta.

**Corrección**: Mover todas las rutas estáticas ANTES de las rutas dinámicas (`/{nacimiento_id}`).

---

## 4. Daño por el Bug #1

La primera ejecución de `recomputar_todos` (con el bug) sobrescribió valores válidos:

| ID Nacimiento | Paciente ID | Antes | Después |
|---------------|-------------|-------|---------|
| 5784 | 131564 | "Termino" | null |
| 5535 | 130109 | "Prolongado" | null |
| 5536 | 130112 | "Prolongado" | null |
| ... | ... | ... | ... |

**Registros afectados**: ~200+ nacimientos perdieron su valor de `trabajo_parto`.

**Nota**: Los nacimientos antiguos (IDs bajos, sin `paciente_id`) NO fueron afectados porque la función los saltaba.

---

## 5. Función Recomputar Corregida

Se creó `POST /nacimientos/recomputar` con la lógica correcta:

```python
# Solo actualiza si:
# 1. El paciente TIENE datos neonatales
# 2. El campo fuente (edad_gestacional/peso_nacimiento) EXISTE
# 3. El valor computado es DIFERENTE al almacenado
# 4. El valor computado NO es null
```

Resultado actual:
```json
{
  "total_analizados": 5823,
  "actualizados": 0,
  "sin_cambios": 131,
  "sin_datos_neonatales": 5692
}
```

---

## 6. Recomendaciones

### Para recuperar los datos perdidos

1. **Restaurar backup** de la BD anterior al 2026-07-01 (antes de la primera ejecución de recomputar)
2. Si no hay backup, actualizar `edad_gestacional` en los pacientes afectados y re-ejecutar `recomputar`

### Para prevenir el problema

1. **Nunca sobrescribir valores existentes con null** en funciones de recomputación
2. **Validar que los datos fuente existan** antes de computar
3. **Hacer backup** antes de ejecutar operaciones masivas de actualización

### Para completar los datos faltantes

Los ~5692 nacimientos sin `trabajo_parto` necesitan que se actualice `edad_gestacional` en sus pacientes. Opciones:

- Importar desde historiales clínicos físicos
- Calcular desde otros campos si están disponibles (fecha de último período menstrual, etc.)
- Marcar como "No especificado" en las estadísticas en lugar de null

---

## 7. Archivos Modificados

| Archivo | Cambio |
|---------|--------|
| `modules/nacimientos/service.py` | Corregido `_recomputar_desde_origen`, `peso_lb_onz_a_gramos`, nueva función `recomputar_todos` |
| `modules/nacimientos/router.py` | Reordenar rutas estáticas antes de dinámicas, agregar `POST /recomputar` |
| `modules/nacimientos/schemas.py` | Sin cambios |

---

## 8. Endpoints Relacionados

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/nacimientos/` | GET | Lista nacimientos con valores computados |
| `/nacimientos/{id}` | GET | Detalle (ejecuta `_recomputar_desde_origen`) |
| `/nacimientos/recomputar` | POST | Recomputa masivamente desde datos del paciente |
| `/estadisticas/nacimientos` | GET | Estadísticas agrupadas por trabajo_parto |
