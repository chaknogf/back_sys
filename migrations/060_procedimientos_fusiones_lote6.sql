-- ============================================================
-- 060_procedimientos_fusiones_lote6.sql
-- Lote 6: fusiones de accesos vasculares y traumatología.
--
-- Grupo 1: Catéteres venosos centrales
--   CCCS (88) absorbe a CDCO, CDCV, CDCYU
--   → "Colocación de Catéter Venoso Central" (CCCS)
--
-- Grupo 2: Traumatología e inmovilizaciones
--   CI absorbe a TCIP → "Colocación de Injerto" (genérico)
--   YESO absorbe a CCP → "Colocación de Yeso o Férula"
--   CV absorbe a CVU  → "Colocación de Vendajes Especializados"
-- ============================================================

BEGIN;

-- ──────────── Grupo 1: Catéteres ────────────
DO $$
DECLARE
    ganador CONSTANT INT := 88;   -- CCCS
    perdedor INT;
    cnt INT;
BEGIN
    FOR perdedor IN SELECT unnest(ARRAY[135, 202, 206]) LOOP
        UPDATE proce_medicos SET id_catalogo_procedimiento = ganador
        WHERE id_catalogo_procedimiento = perdedor;
        GET DIAGNOSTICS cnt = ROW_COUNT;
        RAISE NOTICE 'Catéter: % absorbido por CCCS (% refs)', perdedor, cnt;
        DELETE FROM catalogo_procedimientos WHERE id = perdedor;
    END LOOP;
END $$;
UPDATE catalogo_procedimientos
SET nombre = 'Colocación de Catéter Venoso Central',
    abreviatura = 'CCCS',
    descripcion = 'Inserción de catéter venoso central. Incluye accesos subclavios, yugulares y marcas comerciales.'
WHERE id = 88;

-- ──────────── Grupo 2a: Injerto ────────────
DO $$
DECLARE
    ganador CONSTANT INT := 205;  -- CI
    perdedor CONSTANT INT := 201; -- TCIP
    cnt INT;
BEGIN
    UPDATE proce_medicos SET id_catalogo_procedimiento = ganador
    WHERE id_catalogo_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'TCIP absorbido por CI (% refs)', cnt;
    DELETE FROM catalogo_procedimientos WHERE id = perdedor;
END $$;
UPDATE catalogo_procedimientos
SET nombre = 'Colocación de Injerto',
    abreviatura = 'CI',
    descripcion = 'Colocación de injerto (cutáneo, óseo u otro) en zona receptora.'
WHERE id = 205;

-- ──────────── Grupo 2b: Yeso + Canal Posterior ────────────
DO $$
DECLARE
    ganador CONSTANT INT := 79;   -- YESO
    perdedor CONSTANT INT := 215; -- CCP
    cnt INT;
BEGIN
    UPDATE proce_medicos SET id_catalogo_procedimiento = ganador
    WHERE id_catalogo_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'CCP absorbido por YESO (% refs)', cnt;
    DELETE FROM catalogo_procedimientos WHERE id = perdedor;
END $$;
UPDATE catalogo_procedimientos
SET nombre = 'Colocación de Yeso o Férula',
    abreviatura = 'YESO',
    descripcion = 'Inmovilización externa con yeso, férula posterior o canal abierto.'
WHERE id = 79;

-- ──────────── Grupo 2c: Vendajes + Velpeau ────────────
DO $$
DECLARE
    ganador CONSTANT INT := 218;  -- CV
    perdedor CONSTANT INT := 163; -- CVU
    cnt INT;
BEGIN
    UPDATE proce_medicos SET id_catalogo_procedimiento = ganador
    WHERE id_catalogo_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'CVU absorbido por CV (% refs)', cnt;
    DELETE FROM catalogo_procedimientos WHERE id = perdedor;
END $$;
UPDATE catalogo_procedimientos
SET nombre = 'Colocación de Vendajes Especializados',
    abreviatura = 'CV',
    descripcion = 'Vendaje especializado tipo Velpeau u otros vendajes de hombro y brazo.'
WHERE id = 218;

COMMIT;