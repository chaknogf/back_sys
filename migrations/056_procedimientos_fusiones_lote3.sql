-- ============================================================
-- 056_procedimientos_fusiones_lote3.sql
-- Aplica las fusiones confirmadas por el equipo médico:
--
--   1. DR-E (id 168) + DECO (id 226)   → "Drenaje Ecoguiado"
--   2. RETFI (id 30) + RDFIJ (id 114)  → "Retiro de Fijación Externa"
--   3. SQSV (id 116) + RQDS (id 132)  → "Resección de Quiste Sinovial"
--   4. EXTU (id 111) + EUÑA (id 198)  → "Extracción de Uña"
--   5. CEXT (id 97) + RCE (id 136)    → "Extracción de Cuerpo Extraño"
--   6. YESO (id 79) + CY (id 95)      → "Colocación de Yeso"
--   7. EXCM (id 23) + RMASA (id 121)  → "Resección de Masa de Tejido"
--   8. ADD (id 146) + ANA (id 189)    → "Amputación de Dedo"
--
-- NO se fusionan (mantener separados):
--   - MCC vs MC (caderas vs general, diferente complejidad)
--   - DEQ vs DR-E (quiste vs drenaje general, distinto insumo)
--   - YESO vs CI (inmovilización externa vs cirugía de injerto)
-- ============================================================

BEGIN;

-- ──────────── Pares simples ────────────

-- 1. DR-E absorbe DECO → "Drenaje Ecoguiado"
DO $$
DECLARE
    ganador CONSTANT INT := 168;
    perdedor CONSTANT INT := 226;
    cnt INT;
BEGIN
    UPDATE proce_medicos SET id_catalogo_procedimiento = ganador
    WHERE id_catalogo_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'DECO absorbido por DR-E (% refs)', cnt;
    DELETE FROM catalogo_procedimientos WHERE id = perdedor;
END $$;
UPDATE catalogo_procedimientos
SET nombre = 'Drenaje Ecoguiado',
    abreviatura = 'DR-E',
    descripcion = 'Drenaje de colección guiada por ultrasonido.'
WHERE id = 168;

-- 2. RETFI absorbe RDFIJ → "Retiro de Fijación Externa"
DO $$
DECLARE
    ganador CONSTANT INT := 30;
    perdedor CONSTANT INT := 114;
    cnt INT;
BEGIN
    UPDATE proce_medicos SET id_catalogo_procedimiento = ganador
    WHERE id_catalogo_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'RDFIJ absorbido por RETFI (% refs)', cnt;
    DELETE FROM catalogo_procedimientos WHERE id = perdedor;
END $$;
UPDATE catalogo_procedimientos
SET nombre = 'Retiro de Fijación Externa',
    descripcion = 'Retiro del fijador externo colocado previamente.'
WHERE id = 30;

-- 3. SQSV absorbe RQDS → "Resección de Quiste Sinovial"
DO $$
DECLARE
    ganador CONSTANT INT := 116;
    perdedor CONSTANT INT := 132;
    cnt INT;
BEGIN
    UPDATE proce_medicos SET id_catalogo_procedimiento = ganador
    WHERE id_catalogo_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'RQDS absorbido por SQSV (% refs)', cnt;
    DELETE FROM catalogo_procedimientos WHERE id = perdedor;
END $$;
UPDATE catalogo_procedimientos
SET nombre = 'Resección de Quiste Sinovial',
    abreviatura = 'SQSV',
    descripcion = 'Extirpación quirúrgica de quiste sinovial benigno.'
WHERE id = 116;

-- 4. EXTU absorbe EUÑA → "Extracción de Uña"
DO $$
DECLARE
    ganador CONSTANT INT := 111;
    perdedor CONSTANT INT := 198;
    cnt INT;
BEGIN
    UPDATE proce_medicos SET id_catalogo_procedimiento = ganador
    WHERE id_catalogo_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'EUÑA absorbido por EXTU (% refs)', cnt;
    DELETE FROM catalogo_procedimientos WHERE id = perdedor;
END $$;
UPDATE catalogo_procedimientos
SET nombre = 'Extracción de Uña',
    abreviatura = 'EXTU',
    descripcion = 'Onicectomía: extracción de la uña afectada.'
WHERE id = 111;

-- 5. CEXT absorbe RCE → "Extracción de Cuerpo Extraño"
DO $$
DECLARE
    ganador CONSTANT INT := 97;
    perdedor CONSTANT INT := 136;
    cnt INT;
BEGIN
    UPDATE proce_medicos SET id_catalogo_procedimiento = ganador
    WHERE id_catalogo_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'RCE absorbido por CEXT (% refs)', cnt;
    DELETE FROM catalogo_procedimientos WHERE id = perdedor;
END $$;
UPDATE catalogo_procedimientos
SET nombre = 'Extracción de Cuerpo Extraño',
    descripcion = 'Remoción quirúrgica de un cuerpo extraño.'
WHERE id = 97;

-- 6. YESO absorbe CY → "Colocación de Yeso"
DO $$
DECLARE
    ganador CONSTANT INT := 79;
    perdedor CONSTANT INT := 95;
    cnt INT;
BEGIN
    UPDATE proce_medicos SET id_catalogo_procedimiento = ganador
    WHERE id_catalogo_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'CY absorbido por YESO (% refs)', cnt;
    DELETE FROM catalogo_procedimientos WHERE id = perdedor;
END $$;
UPDATE catalogo_procedimientos
SET nombre = 'Colocación de Yeso',
    abreviatura = 'YESO',
    descripcion = 'Inmovilización externa con vendaje de yeso.'
WHERE id = 79;

-- 7. EXCM absorbe RMASA → "Resección de Masa de Tejido"
-- (Escisión y resección son sinónimos quirúrgicos para masa)
DO $$
DECLARE
    ganador CONSTANT INT := 23;
    perdedor CONSTANT INT := 121;
    cnt INT;
BEGIN
    UPDATE proce_medicos SET id_catalogo_procedimiento = ganador
    WHERE id_catalogo_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'RMASA absorbido por EXCM (% refs)', cnt;
    DELETE FROM catalogo_procedimientos WHERE id = perdedor;
END $$;
UPDATE catalogo_procedimientos
SET nombre = 'Resección de Masa de Tejido',
    abreviatura = 'EXCM',
    descripcion = 'Escisión quirúrgica de una masa tumoral de tejido.'
WHERE id = 23;

-- 8. ADD absorbe ANA → "Amputación de Dedo"
DO $$
DECLARE
    ganador CONSTANT INT := 146;
    perdedor CONSTANT INT := 189;
    cnt INT;
BEGIN
    UPDATE proce_medicos SET id_catalogo_procedimiento = ganador
    WHERE id_catalogo_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'ANA absorbido por ADD (% refs)', cnt;
    DELETE FROM catalogo_procedimientos WHERE id = perdedor;
END $$;
UPDATE catalogo_procedimientos
SET nombre = 'Amputación de Dedo',
    abreviatura = 'ADD',
    descripcion = 'Amputación quirúrgica de un dedo (mano o pie).'
WHERE id = 146;

COMMIT;