-- ============================================================
-- 058_procedimientos_fusiones_lote5.sql
-- Lote 5: fusiones confirmadas por el equipo clínico.
--
-- Bloque fusiones (4):
--   1. RETGR (id 19)  + RGQ  (id 109) → "Retiro de Grapas Quirúrgicas"
--   2. RDIU (id 56)  + RDTC (id 203) → "Retiro de Dispositivo Intrauterino (DIU)"
--   3. RVC  (id 4)   + RCS  (id 118) → "Retiro de Catéter Venoso Central"
--   4. RETMO (id 28) + RMA  (id 123) → "Retiro de Material de Osteosíntesis"
--
-- Mantener separados (decisión clínica):
--   - RCIM  vs RETMO  : extracción con instrumental específico (quirófano)
--   - RETFI vs RETMO  : pines externos vs material interno
--   - RESPI vs RY     : yeso masivo (niños) vs yeso simple
--   - RJAD  (Jadelle) : implante subdérmico anticonceptivo
--   - RTT   (transindesmal): minicirugía traumatológica puntual
-- ============================================================

BEGIN;

-- 1. RETGR absorbe RGQ → "Retiro de Grapas Quirúrgicas"
DO $$
DECLARE
    ganador CONSTANT INT := 19;
    perdedor CONSTANT INT := 109;
    cnt INT;
BEGIN
    UPDATE proce_medicos SET id_catalogo_procedimiento = ganador
    WHERE id_catalogo_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'RGQ absorbido por RETGR (% refs)', cnt;
    DELETE FROM catalogo_procedimientos WHERE id = perdedor;
END $$;
UPDATE catalogo_procedimientos
SET nombre = 'Retiro de Grapas Quirúrgicas',
    abreviatura = 'RETGR',
    descripcion = 'Remoción de grapas de cierre quirúrgico o quirúrgicas.'
WHERE id = 19;

-- 2. RDIU absorbe RDTC → "Retiro de Dispositivo Intrauterino (DIU)"
DO $$
DECLARE
    ganador CONSTANT INT := 56;
    perdedor CONSTANT INT := 203;
    cnt INT;
BEGIN
    UPDATE proce_medicos SET id_catalogo_procedimiento = ganador
    WHERE id_catalogo_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'RDTC absorbido por RDIU (% refs)', cnt;
    DELETE FROM catalogo_procedimientos WHERE id = perdedor;
END $$;
UPDATE catalogo_procedimientos
SET nombre = 'Retiro de Dispositivo Intrauterino (DIU)',
    abreviatura = 'RDIU',
    descripcion = 'Extracción del DIU (Dispositivo Intrauterino), incluyendo T de Cobre.'
WHERE id = 56;

-- 3. RVC absorbe RCS → "Retiro de Catéter Venoso Central"
DO $$
DECLARE
    ganador CONSTANT INT := 4;
    perdedor CONSTANT INT := 118;
    cnt INT;
BEGIN
    UPDATE proce_medicos SET id_catalogo_procedimiento = ganador
    WHERE id_catalogo_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'RCS absorbido por RVC (% refs)', cnt;
    DELETE FROM catalogo_procedimientos WHERE id = perdedor;
END $$;
UPDATE catalogo_procedimientos
SET nombre = 'Retiro de Catéter Venoso Central',
    abreviatura = 'RVC',
    descripcion = 'Remoción de catéter venoso central, incluyendo subclavio.'
WHERE id = 4;

-- 4. RETMO absorbe RMA → "Retiro de Material de Osteosíntesis"
DO $$
DECLARE
    ganador CONSTANT INT := 28;
    perdedor CONSTANT INT := 123;
    cnt INT;
BEGIN
    UPDATE proce_medicos SET id_catalogo_procedimiento = ganador
    WHERE id_catalogo_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'RMA absorbido por RETMO (% refs)', cnt;
    DELETE FROM catalogo_procedimientos WHERE id = perdedor;
END $$;
UPDATE catalogo_procedimientos
SET descripcion = 'Retiro de placas, clavos, tornillos u otro material de osteosíntesis interna.'
WHERE id = 28;

COMMIT;