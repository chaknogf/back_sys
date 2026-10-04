-- ============================================================
-- 069_procedimientos_fusiones_lote7.sql
-- Fusiona:
--   1. Suturas B-Lynch: BLYN (id 53), COLB-LY (id 105)
--      → unificado en BLYN con descripción clínica.
--   2. Vías Centrales: CVC absorbe a CCCS (id 88).
--      → unificado en CVC como código maestro universal.
--
-- Mantener separados:
--   - CCUV / CCUA (catéteres umbilicales neonatales)
--   - BAKRI (balón hemostático uterino)
--   - OTB (oclusión tubárica)
--   - OTMIA (osteotomía)
--   - CBDB (barra Denis Browne)
--   - CEM (desglose de endoscopia — pendiente de decisión)
-- ============================================================

BEGIN;

-- ──────────── Grupo 1: B-Lynch ────────────
DO $$
DECLARE
    ganador CONSTANT INT := 53;   -- BLYN
    perdedor CONSTANT INT := 105; -- COLB-LY
    cnt INT;
BEGIN
    UPDATE proce_medicos SET id_catalogo_procedimiento = ganador
    WHERE id_catalogo_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'COLB-LY absorbido por BLYN (% refs)', cnt;
    DELETE FROM catalogo_procedimientos WHERE id = perdedor;
END $$;

UPDATE catalogo_procedimientos
SET nombre = 'Sutura Compresiva de B-Lynch',
    abreviatura = 'BLYN',
    descripcion = 'Técnica de sutura quirúrgica mayor que abraza mecánicamente el útero con hilos pesados para detener hemorragia masiva postparto (atonía uterina). Salva la vida de la madre evitando histerectomía de urgencia.'
WHERE id = 53;

-- ──────────── Grupo 2: Vías Centrales ────────────
-- Renombrar CVC (id 3) al nombre canónico universal
UPDATE catalogo_procedimientos
SET nombre = 'Colocación de Catéter Venoso Central',
    abreviatura = 'CVC',
    descripcion = 'Introducción de catéter largo en vena de gran calibre (subclavia, yugular, femoral) para medicamentos, nutrición parenteral o monitoreo hemodinámico en pacientes graves.'
WHERE id = 3;

-- CCCS (id 88) absorbe a CVC
DO $$
DECLARE
    ganador CONSTANT INT := 3;   -- CVC (recién renombrado)
    perdedor CONSTANT INT := 88;  -- CCCS
    cnt INT;
BEGIN
    UPDATE proce_medicos SET id_catalogo_procedimiento = ganador
    WHERE id_catalogo_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'CCCS absorbido por CVC (% refs)', cnt;
    DELETE FROM catalogo_procedimientos WHERE id = perdedor;
END $$;

COMMIT;