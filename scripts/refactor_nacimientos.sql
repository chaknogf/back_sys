-- ============================================================
-- refactor_nacimientos.sql
-- Refactoriza tabla nacimientos:
-- 1. Agrega columnas calculadas: peso_gramos, clasificacion, trabajo_parto
-- 2. Backfill neonatales data faltante en pacientes.datos_extra
-- 3. Computa las nuevas columnas
-- 4. Elimina columnas redundantes
-- Uso: psql -f refactor_nacimientos.sql
-- ============================================================

BEGIN;

-- ============================================================
-- Helper: convertir peso_nacimiento (lb onz o decimal) a gramos
-- ============================================================
CREATE OR REPLACE FUNCTION _peso_a_gramos(peso TEXT) RETURNS DECIMAL AS $$
DECLARE
  lb DECIMAL := 0;
  onz DECIMAL := 0;
  peso_clean TEXT;
BEGIN
  IF peso IS NULL OR peso = '' THEN RETURN NULL; END IF;

  peso_clean := UPPER(TRIM(peso));

  -- Formato: "N LIBRAS N ONZAS" o "N lb N onz"
  IF peso_clean ~ '^\d+\s*(LIBRAS|LB)\s+\d+\s*(ONZAS|ONZ)' THEN
    lb := CAST(REGEXP_REPLACE(peso_clean, '^(\d+).*$', '\1') AS DECIMAL);
    onz := CAST(REGEXP_REPLACE(peso_clean, '^\d+\s*(LIBRAS|LB)\s+(\d+).*$', '\2') AS DECIMAL);
  -- Formato: "N lb" o "N LIBRAS"
  ELSIF peso_clean ~ '^\d+\s*(LIBRAS|LB)$' THEN
    lb := CAST(REGEXP_REPLACE(peso_clean, '^(\d+).*$', '\1') AS DECIMAL);
  -- Formato decimal "NN.NN" interpretado como lb.onz
  ELSIF peso_clean ~ '^\d{1,3}\.\d{1,2}$' THEN
    lb := CAST(SPLIT_PART(peso_clean, '.', 1) AS DECIMAL);
    onz := CAST(SPLIT_PART(peso_clean, '.', 2) AS DECIMAL);
  END IF;

  -- 1 lb = 453.592g, 1 onz = 28.3495g
  RETURN ROUND((lb * 453.592) + (onz * 28.3495));
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- ============================================================
-- Helper: clasificacion desde gramos
-- ============================================================
CREATE OR REPLACE FUNCTION _clasificacion_nacimiento(pg DECIMAL) RETURNS VARCHAR AS $$
BEGIN
  IF pg IS NULL THEN RETURN NULL; END IF;
  IF pg < 1000 THEN RETURN 'EBP';    -- Extremadamente bajo peso
  ELSIF pg < 1500 THEN RETURN 'MBP'; -- Muy bajo peso
  ELSIF pg < 2500 THEN RETURN 'BP';  -- Bajo peso
  ELSE RETURN 'PN';                   -- Peso normal
  END IF;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- ============================================================
-- Helper: trabajo_parto desde edad_gestacional (semanas)
-- ============================================================
CREATE OR REPLACE FUNCTION _trabajo_parto(eg TEXT) RETURNS VARCHAR AS $$
DECLARE
  semanas DECIMAL;
BEGIN
  IF eg IS NULL OR eg = '' THEN RETURN NULL; END IF;
  BEGIN
    semanas := CAST(TRIM(eg) AS DECIMAL);
  EXCEPTION WHEN OTHERS THEN
    RETURN 'no especificado';
  END;
  IF semanas > 41 THEN RETURN 'Prolongado';
  ELSIF semanas < 37 THEN RETURN 'Prematuro';
  ELSE RETURN 'a Termino';
  END IF;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- ============================================================
-- 1. Agregar nuevas columnas
-- ============================================================
ALTER TABLE nacimientos ADD COLUMN IF NOT EXISTS peso_gramos DECIMAL;
ALTER TABLE nacimientos ADD COLUMN IF NOT EXISTS clasificacion_nacimiento VARCHAR(50);
ALTER TABLE nacimientos ADD COLUMN IF NOT EXISTS trabajo_parto VARCHAR(50);

-- ============================================================
-- 2. Backfill: copiar neonatales a pacientes.datos_extra si falta
--    Solo para registros donde nacimientos tiene datos pero
--    paciente no tiene neonatales
-- ============================================================
UPDATE pacientes p
SET datos_extra = COALESCE(p.datos_extra, '{}'::jsonb) || jsonb_build_object(
  'neonatales', COALESCE(p.datos_extra->'neonatales', '{}'::jsonb) || jsonb_build_object(
    'peso_nacimiento', n.peso_nacimiento,
    'edad_gestacional', n.edad_gestacional,
    'tipo_parto', n.tipo_parto,
    'clase_parto', n.clase_parto,
    'gemelo', n.gemelo,
    'hora_nacimiento', n.hora_nacimiento,
    'extrahositalario', n.extrahospitalario
  )
)
FROM nacimientos n
WHERE n.paciente_id = p.id
  AND (n.peso_nacimiento IS NOT NULL OR n.edad_gestacional IS NOT NULL)
  AND (p.datos_extra IS NULL OR p.datos_extra = '{}'::jsonb OR NOT (p.datos_extra ? 'neonatales'));

-- ============================================================
-- 3. Computar peso_gramos, clasificacion, trabajo_parto
-- ============================================================
UPDATE nacimientos
SET
  peso_gramos = _peso_a_gramos(peso_nacimiento),
  clasificacion_nacimiento = _clasificacion_nacimiento(_peso_a_gramos(peso_nacimiento)),
  trabajo_parto = _trabajo_parto(edad_gestacional)
WHERE peso_nacimiento IS NOT NULL OR edad_gestacional IS NOT NULL;

-- ============================================================
-- 4. Eliminar columnas redundantes
-- ============================================================
ALTER TABLE nacimientos
  DROP COLUMN IF EXISTS expediente,
  DROP COLUMN IF EXISTS nombre_completo,
  DROP COLUMN IF EXISTS sexo,
  DROP COLUMN IF EXISTS fecha_nacimiento,
  DROP COLUMN IF EXISTS peso_nacimiento,
  DROP COLUMN IF EXISTS edad_gestacional,
  DROP COLUMN IF EXISTS tipo_parto,
  DROP COLUMN IF EXISTS clase_parto,
  DROP COLUMN IF EXISTS gemelo,
  DROP COLUMN IF EXISTS hora_nacimiento,
  DROP COLUMN IF EXISTS extrahospitalario,
  DROP COLUMN IF EXISTS datos_extra;

-- ============================================================
-- 5. Limpiar funciones helper
-- ============================================================
DROP FUNCTION IF EXISTS _peso_a_gramos(TEXT);
DROP FUNCTION IF EXISTS _clasificacion_nacimiento(DECIMAL);
DROP FUNCTION IF EXISTS _trabajo_parto(TEXT);

COMMIT;
