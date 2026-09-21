# Migraciones — `back_sys`

Mapeo de las modificaciones SQL del proyecto y comandos para aplicarlas.

- **Motor**: PostgreSQL, base `hospital` en `localhost`.
- **Conexión usada**: `psql -h localhost -U admin -d hospital` (password `secreto123`).
- **Estado actual**: migraciones `002` → `028` aplicadas. No existe `001`
  (el esquema base de `medicos`, `pacientes`, `personal_salud`, etc. se crea
  aparte: `variables/database_schema.sql` / `migrations/archive/`).

## Cómo aplicar

Una migración:

```bash
PGPASSWORD=secreto123 psql -h localhost -U admin -d hospital \
  -v ON_ERROR_STOP=1 -f migrations/028_procedimiento_quirofano_mixta.sql
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
| 029 | `029_personal_atencion_citas.sql` | Renombra `medicos` → `personal_atencion` + columnas FK `medico_id` → `personal_atencion_id` (personal_salud, defunciones, intervenciones_quirurgicas, sigsa3, sigsa3_registros, constancia_nacimiento); crea `citas_dias_inhabiles`; agrega `citas.personal_atencion_id`. |
