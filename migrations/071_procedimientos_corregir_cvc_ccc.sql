-- ============================================================
-- 071_procedimientos_corregir_cvc_ccc.sql
-- Corrige la migración 069 que falló por conflicto de nombre único.
--
-- El objetivo era:
--   - Renombrar CVC (id 3) → "Colocación de Catéter Venoso Central"
--   - Fusionar CCCS (id 88) en CVC
--
-- Pero ambos quedaron sin aplicar el renombramiento.
-- Esta migración corrige el orden:
--   1. Renombra CCCS (id 88) → "Catéter Subclavio" (temporal)
--   2. Renombra CVC (id 3) → "Colocación de Catéter Venoso Central"
--   3. Fusiona CCCS → CVC
-- ============================================================

BEGIN;

-- Paso 1: Renombrar CCCS temporalmente
UPDATE catalogo_procedimientos
SET nombre = 'Catéter Subclavio (Legacy)'
WHERE id = 88;

-- Paso 2: Renombrar CVC al nombre canónico
UPDATE catalogo_procedimientos
SET nombre = 'Colocación de Catéter Venoso Central',
    abreviatura = 'CVC',
    descripcion = 'Introducción de catéter largo en vena de gran calibre (subclavia, yugular, femoral) para medicamentos, nutrición parenteral o monitoreo hemodinámico.'
WHERE id = 3;

-- Paso 3: Absorber CCCS en CVC
DO $$
DECLARE
    ganador CONSTANT INT := 3;
    perdedor CONSTANT INT := 88;
    cnt INT;
BEGIN
    UPDATE proce_medicos SET id_catalogo_procedimiento = ganador
    WHERE id_catalogo_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'CCCS absorbido por CVC (% refs)', cnt;
    DELETE FROM catalogo_procedimientos WHERE id = perdedor;
END $$;

COMMIT;