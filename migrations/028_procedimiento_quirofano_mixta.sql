-- 028_procedimiento_quirofano_mixta.sql
-- Permite procedimientos que aplican a TODAS las especialidades:
--   especialidad_id NULL = "Todas (mixta)"
-- La unicidad (especialidad, nombre) se re-crea con NULLS NOT DISTINCT para
-- cubrir también la categoría mixta (NULL).

ALTER TABLE procedimiento_quirofano
    ALTER COLUMN especialidad_id DROP NOT NULL;

DROP INDEX IF EXISTS uq_procedimiento_quirofano_esp_nombre;

CREATE UNIQUE INDEX IF NOT EXISTS uq_procedimiento_quirofano_esp_nombre
    ON procedimiento_quirofano (especialidad_id, lower(nombre)) NULLS NOT DISTINCT;
