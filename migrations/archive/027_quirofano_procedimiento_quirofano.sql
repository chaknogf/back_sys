-- 027_quirofano_procedimiento_quirofano.sql
-- Renombra el catálogo de tipos de procedimiento de quirófano:
--   tipo_procedimiento             -> procedimiento_quirofano
--   tipo_procedimiento_id          -> procedimiento_quirofano_id
--   secuencia, PK, UNIQUE(codigo), FK e índice se renombran en consecuencia.
-- Además blinda la unicidad funcional por especialidad:
--   UNIQUE (especialidad_id, lower(nombre))
--
-- No hay objetos dependientes (intervenciones_quirurgicas guarda el
-- procedimiento como texto libre), por lo que el rename es seguro.

ALTER TABLE tipo_procedimiento RENAME TO procedimiento_quirofano;

ALTER TABLE procedimiento_quirofano
    RENAME COLUMN tipo_procedimiento_id TO procedimiento_quirofano_id;

ALTER SEQUENCE tipo_procedimiento_tipo_procedimiento_id_seq
    RENAME TO procedimiento_quirofano_procedimiento_quirofano_id_seq;

ALTER TABLE procedimiento_quirofano
    RENAME CONSTRAINT tipo_procedimiento_pkey TO procedimiento_quirofano_pkey;

ALTER TABLE procedimiento_quirofano
    RENAME CONSTRAINT tipo_procedimiento_codigo_key TO procedimiento_quirofano_codigo_key;

ALTER TABLE procedimiento_quirofano
    RENAME CONSTRAINT tipo_procedimiento_especialidad_id_fkey TO procedimiento_quirofano_especialidad_id_fkey;

ALTER INDEX idx_tipo_procedimiento_especialidad
    RENAME TO idx_procedimiento_quirofano_especialidad;

CREATE UNIQUE INDEX IF NOT EXISTS uq_procedimiento_quirofano_esp_nombre
    ON procedimiento_quirofano (especialidad_id, lower(nombre));
