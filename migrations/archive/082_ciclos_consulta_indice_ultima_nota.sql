-- 082: índice compuesto para resolver la última nota (ciclo) de una consulta.
-- El endpoint GET /ciclos/consulta/{consulta_id}/ultimo ordena por
-- (registro DESC, id DESC) filtrando por consulta_id y activo; este índice
-- permite resolverlo con un index scan de la primera fila sin ordenar todo
-- el conjunto ni recorrer los ciclos uno por uno.
BEGIN;

CREATE INDEX IF NOT EXISTS idx_ciclos_consulta_registro
    ON ciclos_consulta (consulta_id, registro DESC, id DESC)
    WHERE activo;

COMMENT ON INDEX idx_ciclos_consulta_registro IS
    'Última nota por consulta: cubre el filtro por consulta y el orden por registro/id';

COMMIT;
