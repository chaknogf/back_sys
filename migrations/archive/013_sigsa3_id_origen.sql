-- Migration 013: columna sigsa3_id en sigsa3_registros
-- Guarda el id del registro staging (sigsa3) de origen para poder
-- normalizar y luego borrar el staging con ese valor.
-- Sin FK (default NULL) para evitar restricciones de borrado.

BEGIN;

ALTER TABLE sigsa3_registros
    ADD COLUMN IF NOT EXISTS sigsa3_id BIGINT DEFAULT NULL;

CREATE INDEX IF NOT EXISTS ix_sigsa3_reg_sigsa3_id
    ON sigsa3_registros(sigsa3_id);

COMMIT;
