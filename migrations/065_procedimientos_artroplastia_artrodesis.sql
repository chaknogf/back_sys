-- ============================================================
-- 065_procedimientos_artroplastia_artrodesis.sql
-- 1. ARTP (id 33) "Artroplastia" → absorbido por ADR (id 170)
--    "Artroplastia de Rodilla" (renombrado a genérico para
--    cubrir cadera, hombro, rodilla).
-- 2. ARTD (id 34) "Artrodesis" → absorbido por AR (id 175)
--    "Artrodesis de Rodilla" (renombrado a genérico).
-- 3. CAM (id 87) "Cambio de Artrotomía" → renombrado y abreviado
--    a CART (Artrotomía / Revisión articular). Mantener anestesia=1.
-- 4. Corrección CRÍTICA de seguridad: anestesia de ADR y AR = 1.
-- ============================================================

BEGIN;

-- 1. ARTP absorbe ARTD... espera, son conceptos distintos:
--    ARTP = Artroplastia (genérico)
--    ADR  = Artroplastia de Rodilla (específico)
--    Decisión: fusionar ARTP → ADR (rodilla absorbe el genérico).
--    Renombrar ADR a "Artroplastia de Rodilla" (manteniendo id).

DO $$
DECLARE
    ganador CONSTANT INT := 170;  -- ADR
    perdedor CONSTANT INT := 33;   -- ARTP
    cnt INT;
BEGIN
    UPDATE proce_medicos SET id_catalogo_procedimiento = ganador
    WHERE id_catalogo_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'ARTP absorbido por ADR (% refs)', cnt;
    DELETE FROM catalogo_procedimientos WHERE id = perdedor;
END $$;

UPDATE catalogo_procedimientos
SET nombre = 'Artroplastia de Rodilla',
    abreviatura = 'ADR',
    descripcion = 'Reemplazo articular total o parcial de rodilla (prótesis).',
    anestesia = 1
WHERE id = 170;

-- 2. ARTD absorbido por AR
DO $$
DECLARE
    ganador CONSTANT INT := 175;  -- AR
    perdedor CONSTANT INT := 34;   -- ARTD
    cnt INT;
BEGIN
    UPDATE proce_medicos SET id_catalogo_procedimiento = ganador
    WHERE id_catalogo_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'ARTD absorbido por AR (% refs)', cnt;
    DELETE FROM catalogo_procedimientos WHERE id = perdedor;
END $$;

UPDATE catalogo_procedimientos
SET nombre = 'Artrodesis de Rodilla',
    abreviatura = 'AR',
    descripcion = 'Fusión quirúrgica de la articulación de la rodilla.',
    anestesia = 1
WHERE id = 175;

-- 3. Renombrar CAM → CART (Artrotomía / Revisión articular)
UPDATE catalogo_procedimientos
SET nombre = 'Artrotomía / Revisión Articular',
    abreviatura = 'CART',
    descripcion = 'Apertura quirúrgica de la articulación para lavado, revisión o cambio de apósitos.',
    anestesia = 1
WHERE id = 87;

COMMIT;