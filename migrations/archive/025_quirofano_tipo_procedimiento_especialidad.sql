-- 025_quirofano_tipo_procedimiento_especialidad.sql
-- Las especialidades de Quirófano provienen de la tabla canónica `especialidades`.
--  - tipo_procedimiento.especialidad_id -> especialidades.id
--  - se elimina categoria_procedimiento (reemplazada por especialidades)

ALTER TABLE tipo_procedimiento
    ADD COLUMN IF NOT EXISTS especialidad_id INTEGER;

-- Purgar filas sin mapeo (el catálogo se re-siembra con el CSV maestro)
DELETE FROM tipo_procedimiento WHERE especialidad_id IS NULL;

ALTER TABLE tipo_procedimiento
    DROP CONSTRAINT IF EXISTS tipo_procedimiento_categoria_procedimiento_id_fkey,
    DROP COLUMN IF EXISTS categoria_procedimiento_id;

ALTER TABLE tipo_procedimiento
    ALTER COLUMN especialidad_id SET NOT NULL;

ALTER TABLE tipo_procedimiento
    DROP CONSTRAINT IF EXISTS tipo_procedimiento_especialidad_id_fkey,
    ADD CONSTRAINT tipo_procedimiento_especialidad_id_fkey
        FOREIGN KEY (especialidad_id) REFERENCES especialidades(id) ON DELETE RESTRICT;

CREATE INDEX IF NOT EXISTS idx_tipo_procedimiento_especialidad
    ON tipo_procedimiento (especialidad_id);

DROP TABLE IF EXISTS categoria_procedimiento CASCADE;

-- Nota: 027 renombra `tipo_procedimiento` -> `procedimiento_quirofano`
-- (columna `tipo_procedimiento_id` -> `procedimiento_quirofano_id`) y 028
-- permite `especialidad_id NULL` ("Todas (mixta)"). Ver migrations/README.md.
