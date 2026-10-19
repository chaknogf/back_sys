-- 081: columna JSONB `quirofano` en ciclos_consulta.
-- Al registrar una intervención quirúrgica se crea una nota médica (ciclo)
-- que guarda los datos de la intervención de forma flexible en este JSONB,
-- siguiendo el mismo patrón que `uisau`.
BEGIN;

ALTER TABLE ciclos_consulta
    ADD COLUMN IF NOT EXISTS quirofano JSONB;

COMMENT ON COLUMN ciclos_consulta.quirofano IS
    'Datos flexibles de la intervención quirúrgica asociada a la nota del ciclo';

COMMIT;
