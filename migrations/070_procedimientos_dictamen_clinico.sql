-- ============================================================
-- 070_procedimientos_dictamen_clinico.sql
-- Aplica el dictamen clínico del equipo médico:
--
--   1. MPC (id 86) — renombrar a 'Manejo de Paciente Crítico (Estancia UCI)'
--      para diferenciarlo como servicio/estancia, NO como
--      procedimiento quirúrgico aislado. Mantener activo (722 usos).
--   2. ART (id 104) — Mantener independiente (Artrosentesis).
--   3. BK (id 157) — Renombrar a 'Resección de Quiste Poplíteo (Baker)'
--      porque "Quiste de Baker" es diagnóstico, no procedimiento.
--   4. GRE (id 227) — Renombrar a 'Resección Quirúrgica de Granuloma'
--      porque "Granuloma" es lesión, no la operación.
--   5. ATR (id 139) — ELIMINAR. No es procedimiento, es diagnóstico.
-- ============================================================

BEGIN;

-- 1. MPC renombrado (mantener activo pero como servicio/estancia)
UPDATE catalogo_procedimientos
SET nombre = 'Manejo de Paciente Crítico (Estancia UCI)',
    descripcion = 'Atención clínica integral en Unidad de Cuidados Intensivos (UCI) o Shock. Servicio de estancia/hora, no procedimiento quirúrgico aislado.'
WHERE id = 86;

-- 2. ART: Artrosentesis — descripción más completa
UPDATE catalogo_procedimientos
SET descripcion = 'Punción y aspiración de líquido articular (rodilla, hombro, etc.) con fines diagnósticos o terapéuticos. Procedimiento menor ambulatorio o de urgencias.'
WHERE id = 104;

-- 3. BK renombrado (Baker como diagnóstico → acción quirúrgica)
UPDATE catalogo_procedimientos
SET nombre = 'Resección de Quiste Poplíteo (Baker)',
    abreviatura = 'BK',
    descripcion = 'Exéresis o resección quirúrgica del quiste poplíteo (de Baker) detrás de la rodilla.'
WHERE id = 157;

-- 4. GRE renombrado (Granuloma como lesión → acción quirúrgica)
UPDATE catalogo_procedimientos
SET nombre = 'Resección Quirúrgica de Granuloma',
    abreviatura = 'GRE',
    descripcion = 'Exéresis, resección o cauterización quirúrgica de granuloma.'
WHERE id = 227;

-- 5. ATR eliminado (Acidosis Tubular Renal es diagnóstico, no procedimiento)
DO $$
DECLARE
    perdedor CONSTANT INT := 139;
    cnt INT;
BEGIN
    UPDATE proce_medicos SET id_catalogo_procedimiento = NULL
    WHERE id_catalogo_procedimiento = perdedor;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE 'ATR (% refs) desvinculado. Procedimiento eliminado por ser diagnóstico, no acción quirúrgica.', cnt;
    DELETE FROM catalogo_procedimientos WHERE id = perdedor;
END $$;

COMMIT;