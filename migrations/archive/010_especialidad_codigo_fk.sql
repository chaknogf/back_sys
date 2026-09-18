-- ============================================================================
-- Migration 010: Normalize especialidad — add codigo, populate FK, standardize
-- ============================================================================
-- Ejecutar en el servidor:
--   psql -U postgres -d hospital -f 010_especialidad_codigo_fk.sql
-- ============================================================================

BEGIN;

-- 1. Add codigo column (frontend-compatible code) y limpiar test rows
ALTER TABLE especialidades ADD COLUMN IF NOT EXISTS codigo VARCHAR(10);

UPDATE especialidades SET codigo = 'GENE' WHERE id = 1;  -- Medicina General
UPDATE especialidades SET codigo = 'MEDI' WHERE id = 2;  -- Medicina Interna
UPDATE especialidades SET codigo = 'CIRU' WHERE id = 3;  -- Cirugía
UPDATE especialidades SET codigo = 'PEDI' WHERE id = 4;  -- Pediatría
UPDATE especialidades SET codigo = 'GINE' WHERE id = 5;  -- Ginecología
UPDATE especialidades SET codigo = 'TRAU' WHERE id = 6;  -- Traumatología
UPDATE especialidades SET codigo = 'CAR'  WHERE id = 7;  -- Cardiología
UPDATE especialidades SET codigo = 'NEUR' WHERE id = 8;  -- Neurología
UPDATE especialidades SET codigo = 'PSIC' WHERE id = 9;  -- Psicología
UPDATE especialidades SET codigo = 'NUTR' WHERE id = 10; -- Nutrición
UPDATE especialidades SET codigo = 'ODON' WHERE id = 11; -- Odontología
UPDATE especialidades SET codigo = 'TERR' WHERE id = 12; -- Terapia respiratoria
UPDATE especialidades SET codigo = 'EDUC' WHERE id = 13; -- Educadora
UPDATE especialidades SET codigo = 'ANES' WHERE id = 14; -- Anestesiología
UPDATE especialidades SET codigo = 'UCI'  WHERE id = 15; -- Medicina Crítica
UPDATE especialidades SET codigo = 'NEO'  WHERE id = 16; -- Neonatología

DELETE FROM especialidades WHERE id >= 17;
CREATE UNIQUE INDEX IF NOT EXISTS especialidades_codigo_idx ON especialidades(codigo);

-- 2. Helper function: mapea cualquier texto a especialidad_id
-- Soporta: codigo frontend, abreviatura, nombre exacto, unaccent, typos comunes
CREATE OR REPLACE FUNCTION especialidad_id_from_text(val TEXT)
RETURNS INTEGER AS $$
DECLARE
  eid INTEGER;
  v TEXT;
  nu TEXT;
BEGIN
  v := upper(trim(val));
  IF v IS NULL OR v = '' OR v = 'NO_ESP' OR v = '#N/D' OR v = 'EMERGENCIA' THEN
    RETURN NULL;
  END IF;
  SELECT id INTO eid FROM especialidades WHERE codigo = v;
  IF eid IS NOT NULL THEN RETURN eid; END IF;
  SELECT id INTO eid FROM especialidades WHERE abreviatura = v;
  IF eid IS NOT NULL THEN RETURN eid; END IF;
  SELECT id INTO eid FROM especialidades WHERE lower(nombre) = lower(v);
  IF eid IS NOT NULL THEN RETURN eid; END IF;
  nu := lower(unaccent(v));
  SELECT id INTO eid FROM especialidades WHERE lower(unaccent(nombre)) = nu;
  IF eid IS NOT NULL THEN RETURN eid; END IF;
  -- Fallback: typos y variantes conocidas
  IF nu IN ('ginecologia y obstetricia', 'ginecologia y obstretricia') THEN RETURN 5; END IF;
  IF nu = 'medina general' THEN RETURN 1; END IF;
  IF nu IN ('ciurgia', 'cirugia') THEN RETURN 3; END IF;
  IF nu LIKE '%trauma%' THEN RETURN 6; END IF;
  IF nu LIKE '%pediatria%' THEN RETURN 4; END IF;
  IF nu LIKE '%ginecologia%' THEN RETURN 5; END IF;
  RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- 3. Poblar especialidad_id en todas las tablas que tienen FK
UPDATE citas          SET especialidad_id = especialidad_id_from_text(especialidad) WHERE especialidad_id IS NULL AND especialidad IS NOT NULL AND especialidad != '';
UPDATE consultas      SET especialidad_id = especialidad_id_from_text(especialidad) WHERE especialidad_id IS NULL AND especialidad IS NOT NULL AND especialidad != '';
UPDATE medicos        SET especialidad_id = especialidad_id_from_text(especialidad) WHERE especialidad_id IS NULL AND especialidad IS NOT NULL AND especialidad != '';
UPDATE personal_salud SET especialidad_id = especialidad_id_from_text(especialidad) WHERE especialidad_id IS NULL AND especialidad IS NOT NULL AND especialidad != '';
UPDATE proce_medicos  SET especialidad_id = especialidad_id_from_text(especialidad) WHERE especialidad_id IS NULL AND especialidad IS NOT NULL AND especialidad != '';
UPDATE sigsa3         SET especialidad_id = especialidad_id_from_text(especialidad) WHERE especialidad_id IS NULL AND especialidad IS NOT NULL AND especialidad != '';

-- 4. Normalizar consultas.especialidad: nombres largos → codigo corto
--    (solo las filas que tenían full names como "MEDICINA GENERAL")
UPDATE consultas c SET especialidad = e.codigo
FROM especialidades e
WHERE c.especialidad_id = e.id
  AND c.especialidad IS DISTINCT FROM e.codigo
  AND c.especialidad NOT IN ('MEDI','PEDI','GINE','CIRU','TRAU','PSIC','NUTR','ODON','GENE','CAR','NEUR','NEO','ANES','UCI','TERR','EDUC');

COMMIT;
