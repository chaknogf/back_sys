-- ============================================================================
-- FIX: tipo_parto ↔ clase_parto  (valores cruzados)
-- ============================================================================
-- Descripción:
--   tipo_parto debe contener valores de TIPO de parto (Pes, Cstp, EUTOCICO,
--   DISTOCICO, CESAREA, OTRO) y clase_parto valores de CLASE de parto
--   (Simple, Multiple, UNICO, GEMELAR, TRIPLE, MULTIPLE).
--
--   Se detectan como cruzados los registros donde tipo_parto tiene un valor
--   de CLASE (Simple, Multiple, UNICO, GEMELAR, TRIPLE, MULTIPLE).
--
-- Ejecutar SOLO en producción DESPUÉS de verificar en desarrollo.
-- ============================================================================

BEGIN;

-- ====================================================================
-- 1. Corregir pacientes.datos_extra -> neonatales
-- ====================================================================

-- Caso A: tipo_parto tiene valor de CLASE y clase_parto tiene valor de TIPO → swap
UPDATE pacientes
SET datos_extra = jsonb_set(
    jsonb_set(
        datos_extra,
        '{neonatales,tipo_parto}',
        datos_extra->'neonatales'->'clase_parto'
    ),
    '{neonatales,clase_parto}',
    datos_extra->'neonatales'->'tipo_parto'
)
WHERE datos_extra->'neonatales' IS NOT NULL
  AND datos_extra->'neonatales'->>'tipo_parto' IN ('Simple', 'Multiple', 'UNICO', 'GEMELAR', 'TRIPLE', 'MULTIPLE')
  AND datos_extra->'neonatales'->>'clase_parto' IN ('Pes', 'Cstp', 'EUTOCICO', 'DISTOCICO', 'CESAREA', 'OTRO');

-- Caso B: tipo_parto tiene valor de CLASE pero clase_parto es NULL → mover
UPDATE pacientes
SET datos_extra = jsonb_set(
    jsonb_set(
        datos_extra,
        '{neonatales,clase_parto}',
        datos_extra->'neonatales'->'tipo_parto'
    ),
    '{neonatales,tipo_parto}',
    'null'::jsonb
)
WHERE datos_extra->'neonatales' IS NOT NULL
  AND datos_extra->'neonatales'->>'tipo_parto' IN ('Simple', 'Multiple', 'UNICO', 'GEMELAR', 'TRIPLE', 'MULTIPLE')
  AND (datos_extra->'neonatales'->>'clase_parto' IS NULL
    OR datos_extra->'neonatales'->>'clase_parto' = '');

-- ====================================================================
-- 2. Corregir la tabla nacimientos
-- ====================================================================

-- Caso A: swap directo
UPDATE nacimientos
SET tipo_parto = tmp.clase_parto_old,
    clase_parto = tmp.tipo_parto_old
FROM (
    SELECT id,
           tipo_parto AS tipo_parto_old,
           clase_parto AS clase_parto_old
    FROM nacimientos
    WHERE tipo_parto IN ('Simple', 'Multiple', 'UNICO', 'GEMELAR', 'TRIPLE', 'MULTIPLE')
      AND clase_parto IN ('Pes', 'Cstp', 'EUTOCICO', 'DISTOCICO', 'CESAREA', 'OTRO')
) AS tmp
WHERE nacimientos.id = tmp.id;

-- Caso B: mover clase_parto ← tipo_parto, tipo_parto ← NULL
UPDATE nacimientos
SET clase_parto = tipo_parto,
    tipo_parto = NULL
WHERE tipo_parto IN ('Simple', 'Multiple', 'UNICO', 'GEMELAR', 'TRIPLE', 'MULTIPLE')
  AND (clase_parto IS NULL OR clase_parto = '');

-- ====================================================================
-- 3. Normalizar EUTOCICO → Cstp (unificar criterio de tipo de parto)
-- ====================================================================

UPDATE pacientes
SET datos_extra = jsonb_set(
    datos_extra,
    '{neonatales,tipo_parto}',
    '"Cstp"'::jsonb
)
WHERE datos_extra->'neonatales' IS NOT NULL
  AND datos_extra->'neonatales'->>'tipo_parto' = 'EUTOCICO';

UPDATE nacimientos
SET tipo_parto = 'Cstp'
WHERE tipo_parto = 'EUTOCICO';

COMMIT;

-- ============================================================================
-- VERIFICACIÓN (ejecutar después para confirmar)
-- ============================================================================
-- SELECT tipo_parto, clase_parto, COUNT(*)
-- FROM nacimientos
-- WHERE tipo_parto IS NOT NULL OR clase_parto IS NOT NULL
-- GROUP BY tipo_parto, clase_parto ORDER BY 3 DESC;
--
-- SELECT datos_extra->'neonatales'->>'tipo_parto' AS tipo_parto,
--        datos_extra->'neonatales'->>'clase_parto' AS clase_parto,
--        COUNT(*)
-- FROM pacientes
-- WHERE datos_extra->'neonatales' IS NOT NULL
-- GROUP BY 1, 2 ORDER BY 3 DESC;
