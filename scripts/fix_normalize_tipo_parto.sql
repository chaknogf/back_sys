-- ============================================================
-- fix_normalize_tipo_parto.sql
-- Normaliza tipo_parto: UNICO->Simple, GEMELAR->Multiple
-- Residual EUTOCICO en tipo_parto -> clase_parto como 'Pes'
-- Aplica en: pacientes.datos_extra->'neonatales' y nacimientos
-- Uso: psql -f fix_normalize_tipo_parto.sql
-- ============================================================

BEGIN;

-- ============================================================
-- 1. pacientes (JSONB datos_extra -> neonatales)
-- ============================================================
UPDATE pacientes
SET datos_extra = jsonb_set(
  datos_extra,
  '{neonatales}',
  jsonb_build_object(
    'tipo_parto',
      CASE sub.tipo_parto
        WHEN 'UNICO'    THEN 'Simple'
        WHEN 'GEMELAR'  THEN 'Multiple'
        WHEN 'EUTOCICO' THEN NULL
        ELSE sub.tipo_parto
      END,
    'clase_parto',
      CASE
        WHEN sub.tipo_parto = 'EUTOCICO' THEN 'Pes'
        WHEN sub.clase_parto = 'EUTOCICO' THEN 'Pes'
        ELSE sub.clase_parto
      END
  )
)
FROM (
  SELECT id,
    datos_extra #>> '{neonatales,tipo_parto}' AS tipo_parto,
    datos_extra #>> '{neonatales,clase_parto}' AS clase_parto
  FROM pacientes
  WHERE datos_extra ? 'neonatales'
    AND (datos_extra #>> '{neonatales,tipo_parto}' IS NOT NULL
      OR datos_extra #>> '{neonatales,clase_parto}' IS NOT NULL)
) sub
WHERE pacientes.id = sub.id;

-- ============================================================
-- 2. nacimientos
-- ============================================================
UPDATE nacimientos
SET
  tipo_parto = CASE
    WHEN tipo_parto = 'UNICO'    THEN 'Simple'
    WHEN tipo_parto = 'GEMELAR'  THEN 'Multiple'
    WHEN tipo_parto = 'EUTOCICO' THEN NULL
    ELSE tipo_parto
  END,
  clase_parto = CASE
    WHEN tipo_parto = 'EUTOCICO' THEN 'Pes'
    WHEN clase_parto = 'EUTOCICO' THEN 'Pes'
    ELSE clase_parto
  END
WHERE tipo_parto IN ('UNICO','GEMELAR','EUTOCICO')
   OR clase_parto = 'EUTOCICO';

COMMIT;
