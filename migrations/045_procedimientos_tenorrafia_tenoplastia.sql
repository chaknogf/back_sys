-- ============================================================
-- 045_procedimientos_tenorrafia_tenoplastia.sql
-- 1) Fusiona "TENORRAFIAS (UNA O MAS)" (id 265) en
--    "Tenorrafia" (id 25). Nombre canónico: "Tenorrafia".
-- 2) Renombra "Tendinitis" (id 198) a "Tenoplastia" porque
--    "Tendinitis" es un diagnóstico (no un procedimiento).
-- 3) Aplica los mismos cambios en `catalogo_procedimientos`.
--
-- No se toca id 176 (Liberación Túnel del Carpo Dedo en
-- Gatillo Tendinitis Quervain): es nombre específico distinto.
-- ============================================================

BEGIN;

-- ─── Tabla legacy `procedimientos` ────────────────────────

-- 1) Fusionar TENORRAFIAS (265) → Tenorrafia (25)
DO $$
DECLARE
    ganador CONSTANT INT := 25;   -- Tenorrafia
    perdedor CONSTANT INT := 265; -- TENORRAFIAS (UNA O MAS)
    cnt INT;
BEGIN
    UPDATE proce_medicos
    SET id_procedimiento = ganador
    WHERE id_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'TENORRAFIAS (UNA O MAS) absorbido por Tenorrafia: % referencias migradas', cnt;
    DELETE FROM procedimientos WHERE id = perdedor;
END $$;

-- 2) Renombrar Tendinitis (198) → Tenoplastia
UPDATE procedimientos
SET nombre = 'Tenoplastia'
WHERE id = 198 AND nombre = 'Tendinitis';

-- ─── Tabla maestra `catalogo_procedimientos` ─────────────

-- 1) Fusionar TENORRAFIAS (cat 230) → Tenorrafia (cat 24)
DO $$
DECLARE
    ganador CONSTANT INT := 24;
    perdedor CONSTANT INT := 230;
    cnt INT;
BEGIN
    UPDATE proce_medicos
    SET id_catalogo_procedimiento = ganador
    WHERE id_catalogo_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'catálogo: TENORRAFIAS absorbido por Tenorrafia: % referencias migradas', cnt;
    DELETE FROM catalogo_procedimientos WHERE id = perdedor;
END $$;

-- 2) Renombrar Tendinitis (cat 176) → Tenoplastia
UPDATE catalogo_procedimientos
SET nombre = 'Tenoplastia'
WHERE id = 176 AND nombre = 'Tendinitis';

COMMIT;