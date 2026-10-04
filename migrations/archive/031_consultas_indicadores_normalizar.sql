-- Requiere el rol dueno de la tabla `consultas`: el usuario de la app no puede
-- ejecutar el ALTER TABLE ni el LOCK. Los reportes de /estadisticas ya funcionan
-- sin esta migracion gracias al guard `jsonb_typeof`; es una limpieza de datos.
BEGIN;

LOCK TABLE consultas IN SHARE ROW EXCLUSIVE MODE;

DO $$
DECLARE
    json_null BIGINT;
    otro_tipo BIGINT;
BEGIN
    SELECT COUNT(*) INTO json_null
    FROM consultas
    WHERE jsonb_typeof(indicadores) = 'null';

    SELECT COUNT(*) INTO otro_tipo
    FROM consultas
    WHERE indicadores IS NOT NULL
      AND jsonb_typeof(indicadores) NOT IN ('object', 'null');

    RAISE NOTICE 'indicadores con JSON null: %', json_null;
    RAISE NOTICE 'indicadores de otro tipo (array/escalar): %', otro_tipo;
END;
$$;

UPDATE consultas
SET indicadores = '{}'::jsonb
WHERE jsonb_typeof(indicadores) = 'null';

ALTER TABLE consultas
    ADD CONSTRAINT chk_consultas_indicadores_es_objeto
    CHECK (indicadores IS NULL OR jsonb_typeof(indicadores) = 'object');

COMMIT;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_consultas_referencias
    ON consultas (fecha_consulta)
    WHERE jsonb_typeof(indicadores) = 'object'
      AND (
          NULLIF(BTRIM(indicadores ->> 'viene_referido_de'), '') IS NOT NULL
          OR NULLIF(BTRIM(indicadores ->> 'viene_referido'), '') IS NOT NULL
          OR NULLIF(BTRIM(indicadores ->> 'va_referido_a'), '') IS NOT NULL
          OR NULLIF(BTRIM(indicadores ->> 'fue_referido'), '') IS NOT NULL
      );