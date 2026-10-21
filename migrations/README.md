# Migraciones - `back_sys`

Mapeo de las modificaciones SQL del proyecto y comandos para aplicarlas.

- **Motor**: PostgreSQL, base `hospital` en `localhost`.
- **Conexión usada**: `psql -h localhost -U admin -d hospital` (password `secreto123`).
- **Estado actual**: `002` → `030` aplicadas, más `032_procedimientos_unificado.sql`, `074_quirofano_intervencion_especialidad.sql`, `075_quirofano_intervencion_consulta.sql`, `078_quirofano_config_periodo.sql`, `080_catalogo_procedimientos_nuevos.sql`, `081_ciclos_consulta_quirofano.sql`, `082_ciclos_consulta_indice_ultima_nota.sql`, `083_catalogo_procedimientos_especialidades.sql`, `084_almacen_insumos.sql` y `085_proce_medicos_no_especificado.sql`.
  El rango `031` → `073` (parches one-off con IDs hardcodeados del dump de
  producción) fue **consolidado y eliminado**; no existe `001` (el esquema base de
  `medicos`, `pacientes`, `personal_salud`, etc. se crea aparte:
  `variables/database_schema.sql` / `migrations/archive/`).

## Cómo aplicar

Una migración:

```bash
PGPASSWORD=secreto123 psql -h localhost -U admin -d hospital \
  -v ON_ERROR_STOP=1 -f migrations/030_censo_camas_unificar_sexos.sql
```

Todas (en orden, deteniéndose al primer error):

```bash
./migrations/apply.sh
```

> `apply.sh` recorre `migrations/[0-9]*.sql` en orden numérico. Es idempotente
> solo cuando cada archivo lo es (`IF NOT EXISTS`, `ON CONFLICT`, `IF EXISTS`);
> no lleva registro de migraciones ya aplicadas.

## Mapeo

| # | Archivo | Qué modifica (objetos / sentencias clave) |
|---|---------|-------------------------------------------|
| 002 | `002_medicos_colegiado_str_pasaporte.sql` | `medicos.colegiado` → `varchar(20)` + `UNIQUE`; agrega `pasaporte` e índice `idx_medicos_pasaporte`. |
| 003 | `003_especialidades.sql` | Crea catálogo `especialidades` y reemplaza el string libre `especialidad` por FK en 7 tablas. |
| 004 | `004_tipos_consulta_correlativos.sql` | Crea catálogo `tipos_consulta` y unifica correlativos. |
| 005 | `005_sigsa3_fks.sql` | Agrega `sigsa3.personal_salud_id` + índice. |
| 006 | `006_normalizacion_completa.sql` | Normalización de producción (pacientes/consultas/sigsa3). |
| 007 | `007_sigsa3_normalizado.sql` | Crea `sigsa3_registros`; migra y purga `sigsa3` (staging). |
| 008 | `008_consultas_historial.sql` | Extrae `consultas.historial` (JSONB) → tabla `consultas_historial`. |
| 009 | `009_pacientes_socioeconomicos.sql` | Extrae `pacientes.datos_extra.socioeconomicos` → columnas. |
| 010 | `010_especialidad_codigo_fk.sql` | Agrega `especialidades.codigo`, puebla FK y estandariza. |
| 011 | `011_normalize_datos_extra.sql` | Extrae campos JSONB `datos_extra` a columnas + triggers de normalización. |
| 012 | `012_remove_especialidad_string.sql` | Elimina columnas legacy `especialidad` (varchar) ya reemplazadas por FK. |
| 013 | `013_sigsa3_id_origen.sql` | Agrega `sigsa3_registros.sigsa3_id` (origen del staging). |
| 014 | `014_tipos_consulta_sigsa3.sql` | Crea catálogo `tipos_consulta_sigsa3` y repunta FKs de `sigsa3`/`sigsa3_registros`. |
| 015 | `015_sigsa3_medico_obligatorio.sql` | Sanea y hace `NOT NULL` `sigsa3_registros.medico_id`. |
| 016 | `016_sigsa3_asociacion_masiva_indexes.sql` | Índices para la asociación masiva de pacientes. |
| 017 | `017_agente_aprendizaje.sql` | Crea `agente_reglas` (aprendizaje del agente estadístico). |
| 018 | `018_audit_log_metadata.sql` | Agrega a `audit_log`: `ip_address`, `user_agent`, `os`, `device_name`. |
| 019 | `019_recrear_unaccent.sql` | Recrea extensiones `unaccent`/`pg_trgm` y `f_unaccent()` tras `pg_restore`. |
| 020 | `020_sigsa3_medico_nullable.sql` | Hace `medico_id` nullable en `sigsa3_registros`. |
| 021 | `021_quirofano_intervenciones.sql` | Crea `intervenciones_quirurgicas` (+ índices). |
| 022 | `022_quirofano_catalogos.sql` | Catálogos quirófano: `estado_cirugia`, `formato_procedimiento`, `rango_especialista`, `procedencia_procedimiento`, `categoria_procedimiento`, `tipo_procedimiento` + seeds. |
| 023 | `023_quirofano_numero.sql` | Crea `quirofano_numero` + FK `intervenciones_quirurgicas.quirofano_numero_id`. |
| 024 | `024_quirofano_intervenciones_campos.sql` | En `intervenciones_quirurgicas`: elimina `tipo_procedimiento_id`/`hora`; agrega `procedimiento_principal..5`, `area_cuerpo_intervenida` y 4 horas. |
| 025 | `025_quirofano_tipo_procedimiento_especialidad.sql` | `tipo_procedimiento.especialidad_id` → FK `especialidades.id`; elimina `categoria_procedimiento`. |
| 026 | `026_especialidades_estado_sop.sql` | Agrega a `especialidades`: `estado` y `sop` (+ índices). |
| 027 | `027_quirofano_procedimiento_quirofano.sql` | Renombra `tipo_procedimiento` → `procedimiento_quirofano` (columna/secuencia/PK/constraints/índice) + `UNIQUE(especialidad_id, lower(nombre))`. |
| 028 | `028_procedimiento_quirofano_mixta.sql` | `procedimiento_quirofano.especialidad_id` → nullable (NULL = "Todas (mixta)"); reconstruye el único con `NULLS NOT DISTINCT`. |
| 029 | `029_personal_atencion_citas.sql` | Renombra `medicos` → `personal_atencion` + columnas FK `medico_id` → `personal_atencion_id` (personal_salud, defunciones, intervenciones_quirurgicas, sigsa3, sigsa3_registros, constancia_nacimiento); crea `citas_dias_inhabiles`; agrega `citas.personal_atencion_id`. |
| 030 | `030_censo_camas_unificar_sexos.sql` | Migra `censo_camas` a una fila por fecha/servicio; conserva movimientos por sexo, recalcula las columnas agregadas y reemplaza la unicidad por `(fecha, servicio_id)`. |
| 032 | `032_procedimientos_unificado.sql` | **Consolida** el antiguo rango `031`→`073` en un único archivo idempotente y *name-based* (sin IDs hardcodeados). Ver detalle abajo. |
| 074 | `074_quirofano_intervencion_especialidad.sql` | Agrega `intervenciones_quirurgicas.especialidad_id` (FK `especialidades.id`, `ON DELETE SET NULL`) + índice. El form de Quirófano exigía la especialidad pero no se persistía. Aditiva e idempotente. |
| 075 | `075_quirofano_intervencion_consulta.sql` | Agrega `intervenciones_quirurgicas.consulta_id` (FK `consultas.id`, `ON DELETE SET NULL`) + índice. Liga cada intervención a la consulta de hospitalización que la originó (indicador del listado de quirófano). Aditiva e idempotente. |
| 078 | `078_quirofano_config_periodo.sql` | Crea `quirofano_config_periodo` (jornada por quirófano: `hora_apertura`, `hora_cierre`, `dias_habiles`, `activo`; `UNIQUE`/FK a `quirofano_numero` `ON DELETE CASCADE`) + seeds 07:00–16:00 por quirófano. Es el *fallback* del reporte/Excel cuando el período no aporta horarios. Aditiva e idempotente. |
| 080 | `080_catalogo_procedimientos_nuevos.sql` | Agrega 15 procedimientos faltantes a `catalogo_procedimientos` (`especialidad_ref`/`abreviatura` NULL). Idempotente: `ON CONFLICT DO NOTHING` sobre los UNIQUE de `nombre`/`abreviatura`. |
| 081 | `081_ciclos_consulta_quirofano.sql` | Agrega `ciclos_consulta.quirofano` (JSONB). Al registrar una intervención quirúrgica con consulta ligada se crea automáticamente la nota médica (ciclo) de la intervención en este JSONB (mismo patrón que `uisau`). Aditiva e idempotente. |
| 082 | `082_ciclos_consulta_indice_ultima_nota.sql` | Índice parcial `idx_ciclos_consulta_registro (consulta_id, registro DESC, id DESC) WHERE activo` para resolver la última nota de una consulta con un *index scan* (endpoint `GET /ciclos/consulta/{id}/ultimo`). Aditiva e idempotente. |
| 084 | `084_almacen_insumos.sql` | Módulo de almacén de insumos (**13 tablas**, 36 FKs), catálogo espejo del CSV de importación: `insumos` (1 fila por CÓDIGO DE INSUMO: `renglon VARCHAR(3)` con ceros a la izquierda, `codigo_insumo` UNIQUE, `nombre`, `caracteristicas` **crudas** en formato CSV; parseo a JSONB pendiente tras revisar datos) + `presentaciones` (1 fila por CÓDIGO DE PRESENTACIÓN: `insumo_id` FK, `nombre`, `cantidad_unidad` **crudo** ej. "250 Mililitro", `codigo_presentacion` UNIQUE; **sin** tabla `renglones` — inmutables, y sin `estado`/`grado`/`uso` parseados). Además: `almacenes` (bodega/farmacia/productos_afines/servicio), `lotes` (stock por lote y almacén — el stock NO vive en el catálogo), `kardex_movimientos` (entrada/salida/traslado/consumo/ajuste con `referencia_tipo`+`referencia_id`), `requisiciones`+detalles (pendiente→aprobada→despachada), `despachos`+detalles (tipo servicio/paciente/traslado con `chk_despachos_destino`), `atenciones`+`atenciones_insumos` (origen despacho/directo) y `unidosis`+detalles (preparación por paciente desde farmacia). Seeds: 3 almacenes, insumos 173975/125557 (`renglon='261'`), presentaciones 203578/146481/146482. Aditiva e idempotente. |
| 085 | `085_proce_medicos_no_especificado.sql` | Hace explícita la categoría **"No especificado"** en `proce_medicos`: asegura `sin_edad_m`/`sin_edad_f` (`NOT NULL DEFAULT 0`), sus `CHECK >= 0`, `proce_medicos_cantidad_check (cantidad >= 1)` y el índice parcial `idx_proce_medicos_sin_edad`. La captura (frontend) y `ProceMedicoCreate` (backend) ahora aceptan un registro cuya única cantidad sea `sin_edad_*`. Idempotente y no-op sobre la base actual (las columnas/index ya venían de `032`). |

> El rango `031` → `073` ya **no existe** como archivos separados: era un conjunto
> de parches one-off atados a los IDs de un dump de producción. Toda su lógica
> neta quedó reescrita en `032_procedimientos_unificado.sql`.

## `032_procedimientos_unificado.sql`

Reescritura idempotente (se puede re-ejecutar sin efectos) que:
- Crea `area_cuerpo_intervenida` (54 zonas) y siembra el catálogo maestro
  `catalogo_procedimientos` (476 procedimientos) vía `VALUES` + `ON CONFLICT DO
  NOTHING` (sin target, para cubrir tanto `nombre` como `abreviatura` UNIQUE).
- Repunta `proce_medicos` a `catalogo_procedimientos` y a `area_cuerpo_intervenida`
  por **nombre normalizado** (`unaccent(lower(btrim(nombre)))`).
- Crea el puente `catalogo_procedimiento_area` (32 pares zona↔procedimiento).
- Reemplaza `grupo_edad_detalle` (JSONB) por columnas desagregadas
  `nino_m/nino_f/adulto_m/adulto_f/sin_edad_m/sin_edad_f`. Corte 18 años: niño =
  `NEO+LAC+PRI+SEG+ADO`, adulto = `ADU+ADM`; los históricos sin edad ni grupo se
  respaldan desde `sexo` hacia `sin_edad_m`/`sin_edad_f` (sumando `cantidad`).
- Elimina `procedimientos` y `procedimientos_area_cuerpo` (legacy) y `sexo`,
  `id_procedimiento`, `grupo_edad_detalle`, `edad`, `unidad_edad`, `grupo_edad`.
- Agrega FKs de procedimiento/zona a `intervenciones_quirurgicas` (aditivo).
- Crea las vistas `v_catalogo_procedimientos` y `v_areas_cuerpo`.

> **Se conserva** `procedimiento_quirofano` (catálogo vivo del módulo Quirófano).
> `cantidad` se mantiene como columna normal (la app la recalcula).
> Verificado idempotente (2 corridas) sobre clon de `hospital` y sobre una BD
> sintética pre-`032`.

## Cadena de cambios del catálogo Quirófano

La evolución del catálogo de procedimientos pasó por varias migraciones; el
estado vigente es el resultado de `022 → 024 → 025 → 027 → 028`:

1. `022`: crea `categoria_procedimiento` + `tipo_procedimiento` (con FK obligatoria a categoría).
2. `024`: `intervenciones_quirurgicas` deja de referenciar el catálogo (guarda texto).
3. `025`: `tipo_procedimiento` pasa a depender de `especialidades` (se elimina `categoria_procedimiento`).
4. `027`: renombra todo a `procedimiento_quirofano`.
5. `028`: permite `especialidad_id NULL` ("Todas (mixta)").

## Comandos manuales que NO están en migraciones

- Reparación de secuencia tras `TRUNCATE` en tests: el catálogo usa
  `TRUNCATE ... RESTART IDENTITY`; si un test restaura con `setval` debe hacer
  `flush` antes (los `SessionLocal` del proyecto usan `autoflush=False`).
- No hay otros `ALTER`/`CREATE`/`DROP` aplicados a mano fuera de estos archivos.
