-- ============================================================
-- fix_swap_tipo_clase_parto.sql
-- Swaps tipo_parto ↔ clase_parto values and normalizes:
--   EUTOCICO → Pes, DISTOCICO → Cstp
-- Aplica en: pacientes.datos_extra->'neonatales' y nacimientos
-- Uso: psql -f fix_swap_tipo_clase_parto.sql
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
    'tipo_parto', sub.clase_parto,
    'clase_parto',
      CASE sub.tipo_parto
        WHEN 'EUTOCICO' THEN 'Pes'
        WHEN 'DISTOCICO' THEN 'Cstp'
        ELSE sub.tipo_parto
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
  tipo_parto = sub.clase_parto,
  clase_parto = CASE sub.tipo_parto
    WHEN 'EUTOCICO' THEN 'Pes'
    WHEN 'DISTOCICO' THEN 'Cstp'
    ELSE sub.tipo_parto
  END
FROM (
  SELECT id, tipo_parto, clase_parto
  FROM nacimientos
  WHERE tipo_parto IS NOT NULL OR clase_parto IS NOT NULL
) sub
WHERE nacimientos.id = sub.id;

COMMIT;
