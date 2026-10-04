-- ============================================================
-- 052_procedimientos_biopsia_generica_fusionar.sql
-- Fusiona los nombres genéricos de biopsia (sin especificidad
-- anatómica) en un único registro: "Biopsia" (BIOP).
--
-- Mantiene como registros independientes los procedimientos
-- anatómicamente específicos, porque son procedimientos
-- diferentes con indicaciones distintas:
--   - Biopsia Cervical (BIOCER)
--   - Biopsia Endometrial (BE)
--   - Biopsia de Mama (BIOMAMA)
--   - Biopsia de Vulva (BIOVU)
--   - Biopsia de Trucut (BIOTRU)
--
-- Solo se absorbe "TOMA DE BIOPSIA" (TOBIO), que es el término
-- genérico duplicado.
-- ============================================================

BEGIN;

-- ─── Tabla legacy `procedimientos` ────────────────────────

DO $$
DECLARE
    ganador CONSTANT INT := 22;   -- BIOP "Biopsia"
    perdedor CONSTANT INT := 274; -- TOBIO "TOMA DE BIOPSIA"
    cnt INT;
BEGIN
    UPDATE proce_medicos
    SET id_procedimiento = ganador
    WHERE id_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'TOBIO absorbido por BIOP: % referencias migradas', cnt;
    DELETE FROM procedimientos WHERE id = perdedor;
END $$;

UPDATE procedimientos
SET descripcion = 'Toma de muestra de tejido para análisis histopatológico.'
WHERE id = 22;

-- ─── Tabla maestra `catalogo_procedimientos` ─────────────

DO $$
DECLARE
    ganador CONSTANT INT := 21;   -- BIOP "Biopsia" (catálogo)
    perdedor CONSTANT INT := 236; -- TOBIO (catálogo)
    cnt INT;
BEGIN
    UPDATE proce_medicos
    SET id_catalogo_procedimiento = ganador
    WHERE id_catalogo_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'catálogo: TOBIO absorbido por BIOP: % referencias migradas', cnt;
    DELETE FROM catalogo_procedimientos WHERE id = perdedor;
END $$;

UPDATE catalogo_procedimientos
SET descripcion = 'Toma de muestra de tejido para análisis histopatológico.'
WHERE id = 21;

COMMIT;