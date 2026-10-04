-- ============================================================
-- 057_procedimientos_fusiones_lote4.sql
-- Lote 4: fusiones confirmadas del tercer análisis.
--
--   1. RETFI (id 30)  + RDFE (id 141)  → "Retiro de Fijación Externa"
--   2. SQSV (id 116) + RDQS (id 144)  → "Resección de Quiste Sinovial"
--   3. COLPA (id 51) + COLFPOST (id 117)→ "Colporrafia"
--   4. AUB  (id 225) + OUB  (id 252)  → "Ooforectomía Unilateral o Bilateral"
--   5. EXTL (id 94)  + RESCP (id 235) → "Resección de Lipoma"
--
-- Mantener separados (decisión clínica):
--   - MCC vs MC (caderas vs general)
--   - DEQ vs DR-E (quiste vs drenaje general)
--   - YESO vs CI (inmovilización vs injerto)
--   - SQSV vs DREQS (resección vs drenaje)
--   - CDCO "Oyster" (revisar typo)
-- ============================================================

BEGIN;

-- 1. RETFI absorbe RDFE
DO $$
DECLARE
    ganador CONSTANT INT := 30;
    perdedor CONSTANT INT := 141;
    cnt INT;
BEGIN
    UPDATE proce_medicos SET id_catalogo_procedimiento = ganador
    WHERE id_catalogo_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'RDFE absorbido por RETFI (% refs)', cnt;
    DELETE FROM catalogo_procedimientos WHERE id = perdedor;
END $$;
UPDATE catalogo_procedimientos
SET descripcion = 'Retiro del fijador externo colocado previamente.'
WHERE id = 30;

-- 2. SQSV absorbe RDQS (resección vs retiro, mismo concepto de quiste sinovial)
DO $$
DECLARE
    ganador CONSTANT INT := 116;
    perdedor CONSTANT INT := 144;
    cnt INT;
BEGIN
    UPDATE proce_medicos SET id_catalogo_procedimiento = ganador
    WHERE id_catalogo_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'RDQS absorbido por SQSV (% refs)', cnt;
    DELETE FROM catalogo_procedimientos WHERE id = perdedor;
END $$;
UPDATE catalogo_procedimientos
SET descripcion = 'Extirpación quirúrgica de quiste sinovial benigno.'
WHERE id = 116;

-- 3. COLPA absorbe COLFPOST
DO $$
DECLARE
    ganador CONSTANT INT := 51;
    perdedor CONSTANT INT := 117;
    cnt INT;
BEGIN
    UPDATE proce_medicos SET id_catalogo_procedimiento = ganador
    WHERE id_catalogo_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'COLFPOST absorbido por COLPA (% refs)', cnt;
    DELETE FROM catalogo_procedimientos WHERE id = perdedor;
END $$;
UPDATE catalogo_procedimientos
SET descripcion = 'Reparación quirúrgica de la pared vaginal (colporrafia anterior/posterior).'
WHERE id = 51;

-- 4. OUB absorbe AUB (OUB es más general, cubre ambos casos)
DO $$
DECLARE
    ganador CONSTANT INT := 252;
    perdedor CONSTANT INT := 225;
    cnt INT;
BEGIN
    UPDATE proce_medicos SET id_catalogo_procedimiento = ganador
    WHERE id_catalogo_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'AUB absorbido por OUB (% refs)', cnt;
    DELETE FROM catalogo_procedimientos WHERE id = perdedor;
END $$;
UPDATE catalogo_procedimientos
SET nombre = 'Ooforectomía Unilateral o Bilateral',
    abreviatura = 'OUB',
    descripcion = 'Extirpación de uno o ambos ovarios.'
WHERE id = 252;

-- 5. EXTL absorbe RESCP (mismo concepto: lipoma)
DO $$
DECLARE
    ganador CONSTANT INT := 94;
    perdedor CONSTANT INT := 235;
    cnt INT;
BEGIN
    UPDATE proce_medicos SET id_catalogo_procedimiento = ganador
    WHERE id_catalogo_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'RESCP absorbido por EXTL (% refs)', cnt;
    DELETE FROM catalogo_procedimientos WHERE id = perdedor;
END $$;
UPDATE catalogo_procedimientos
SET nombre = 'Extracción de Lipomas',
    abreviatura = 'EXTL',
    descripcion = 'Resección quirúrgica de uno o varios lipomas.'
WHERE id = 94;

COMMIT;