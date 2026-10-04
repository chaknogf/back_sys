-- ============================================================
-- 049_procedimientos_descompresion_ner_medio_unificar.sql
-- Unifica "Liberación de Túnel del Carpo" (id 38 / cat 37) con
-- "Liberacion De Tunel Carpiano" (id 161 / cat 143) en un único
-- procedimiento:
--   "Descompresión del Nervio Mediano" (DNMC)
--
-- Justificación clínica:
--   Ambos nombres describen el mismo procedimiento quirúrgico
--   (liberación del túnel carpiano / descompresión del nervio
--   mediano). El término institucional canónico es
--   "Descompresión del Nervio Mediano".
-- ============================================================

BEGIN;

-- ─── Tabla legacy `procedimientos` ────────────────────────

-- Renombrar el ganador (id 38) al nombre canónico + descripción
UPDATE procedimientos
SET nombre = 'Descompresión del Nervio Mediano',
    abreviatura = 'DNMC',
    descripcion = 'Apertura del retináculo flexor para liberar la presión sobre el nervio mediano a nivel del carpo.'
WHERE id = 38;

-- Absorber id 161 → 38
DO $$
DECLARE
    ganador CONSTANT INT := 38;
    perdedor CONSTANT INT := 161;
    cnt INT;
BEGIN
    UPDATE proce_medicos
    SET id_procedimiento = ganador
    WHERE id_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'LDTC absorbido por DNMC: % referencias migradas', cnt;
    DELETE FROM procedimientos WHERE id = perdedor;
END $$;

-- ─── Tabla maestra `catalogo_procedimientos` ─────────────

UPDATE catalogo_procedimientos
SET nombre = 'Descompresión del Nervio Mediano',
    abreviatura = 'DNMC',
    descripcion = 'Apertura del retináculo flexor para liberar la presión sobre el nervio mediano a nivel del carpo.'
WHERE id = 37;

DO $$
DECLARE
    ganador CONSTANT INT := 37;
    perdedor CONSTANT INT := 143;
    cnt INT;
BEGIN
    UPDATE proce_medicos
    SET id_catalogo_procedimiento = ganador
    WHERE id_catalogo_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'catálogo: LDTC absorbido por DNMC: % referencias migradas', cnt;
    DELETE FROM catalogo_procedimientos WHERE id = perdedor;
END $$;

COMMIT;