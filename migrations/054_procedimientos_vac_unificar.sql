-- ============================================================
-- 054_procedimientos_vac_unificar.sql
-- Fusiona todos los procedimientos relacionados con VAC
-- en un único registro: "VAC" (id 12 / cat 12).
--
-- Variantes absorbidas:
--   id 170 CDV   "Cambio De Vas"       (typo: Vas → VAC)
--   id 203 CDVAC "Colocacion De Vacc"  (typo: Vacc → VAC)
--
-- Mantiene id 91 CAM "Cambio De Artrotomia" independiente
-- (es un procedimiento ortopédico-articular, no de VAC).
-- ============================================================

BEGIN;

-- ─── Tabla legacy `procedimientos` ────────────────────────

UPDATE procedimientos
SET nombre = 'VAC',
    descripcion = 'Colocación, cambio o retiro de sistema VAC (cierre asistido por vacío).'
WHERE id = 12;

DO $$
DECLARE
    ganador CONSTANT INT := 12;
    perdedor INT;
    cnt INT;
BEGIN
    FOR perdedor IN SELECT unnest(ARRAY[170, 203]) LOOP
        UPDATE proce_medicos
        SET id_procedimiento = ganador
        WHERE id_procedimiento = perdedor;
        GET DIAGNOSTICS cnt = ROW_COUNT;
        RAISE NOTICE 'Procedimiento % absorbido por VAC (12): % referencias migradas',
            perdedor, cnt;
        DELETE FROM procedimientos WHERE id = perdedor;
    END LOOP;
END $$;

-- ─── Tabla maestra `catalogo_procedimientos` ─────────────

UPDATE catalogo_procedimientos
SET nombre = 'VAC',
    descripcion = 'Colocación, cambio o retiro de sistema VAC (cierre asistido por vacío).'
WHERE id = 12;

DO $$
DECLARE
    ganador CONSTANT INT := 12;
    perdedor INT;
    cnt INT;
BEGIN
    FOR perdedor IN SELECT unnest(ARRAY[149, 180]) LOOP
        UPDATE proce_medicos
        SET id_catalogo_procedimiento = ganador
        WHERE id_catalogo_procedimiento = perdedor;
        GET DIAGNOSTICS cnt = ROW_COUNT;
        RAISE NOTICE 'catálogo: % absorbido por VAC (12): % referencias migradas',
            perdedor, cnt;
        DELETE FROM catalogo_procedimientos WHERE id = perdedor;
    END LOOP;
END $$;

COMMIT;