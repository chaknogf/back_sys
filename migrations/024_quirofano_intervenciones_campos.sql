-- 024_quirofano_intervenciones_campos.sql
-- Evolución de intervenciones_quirurgicas:
--  - Se reemplaza la referencia tipo_procedimiento_id por procedimiento_1..5 (texto,
--    "Especialidad - Procedimiento") + área del cuerpo intervenida.
--  - Se elimina la columna genérica `hora` y se agregan 4 horas específicas.

ALTER TABLE intervenciones_quirurgicas
    ADD COLUMN IF NOT EXISTS procedimiento_principal                  VARCHAR(200),
    ADD COLUMN IF NOT EXISTS procedimiento_2                          VARCHAR(200),
    ADD COLUMN IF NOT EXISTS procedimiento_3                          VARCHAR(200),
    ADD COLUMN IF NOT EXISTS procedimiento_4                          VARCHAR(200),
    ADD COLUMN IF NOT EXISTS procedimiento_5                          VARCHAR(200),
    ADD COLUMN IF NOT EXISTS area_cuerpo_intervenida                  VARCHAR(100),
    ADD COLUMN IF NOT EXISTS hora_inicio_anestesia                    TIME,
    ADD COLUMN IF NOT EXISTS hora_inicio_intervencion                 TIME,
    ADD COLUMN IF NOT EXISTS hora_finaliza_intervencion               TIME,
    ADD COLUMN IF NOT EXISTS hora_finaliza_limpieza_prepara_quirofano TIME;

ALTER TABLE intervenciones_quirurgicas
    DROP COLUMN IF EXISTS tipo_procedimiento_id,
    DROP COLUMN IF EXISTS hora;

-- Índice del FK eliminado
DROP INDEX IF EXISTS ix_intervenciones_quirurgicas_tipo_procedimiento_id;

-- Nota: la semilla del catálogo de procedimientos se aplica con
-- scripts/seed_quirofano_procedimientos.py (catálogo auditorio: 022 categorías / 301 tipos).
-- Las intervenciones guardan los procedimientos como texto, por lo que
-- truncar/vaciar el catálogo (DELETE /quirofano/tipos/truncar) no afecta los registros existentes.