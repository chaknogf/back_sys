-- Migration 011: Normalize JSONB datos_extra fields across tables
-- Extrae campos JSONB de uso frecuente a columnas propias para mejorar
-- rendimiento de consultas y permitir índices B-tree directos.
-- También añade triggers de normalización de especialidad en consultas, citas, medicos, sigsa3.
-- Ejecutar como: psql -d hospital -f migrations/011_normalize_datos_extra.sql

BEGIN;

-- ===================================================================
-- 1. citas.datos_extra → razon_consulta y notas
-- ===================================================================
ALTER TABLE citas
  ADD COLUMN IF NOT EXISTS razon_consulta VARCHAR(50),
  ADD COLUMN IF NOT EXISTS notas TEXT;

UPDATE citas
  SET razon_consulta = datos_extra->>'razon_consulta'
  WHERE datos_extra IS NOT NULL AND datos_extra ? 'razon_consulta'
    AND razon_consulta IS NULL;

UPDATE citas
  SET notas = COALESCE(datos_extra->>'notas', datos_extra->>'nota')
  WHERE datos_extra IS NOT NULL
    AND (datos_extra ? 'notas' OR datos_extra ? 'nota')
    AND notas IS NULL;

CREATE INDEX IF NOT EXISTS idx_citas_razon_consulta ON citas(razon_consulta);

-- ===================================================================
-- 2. pacientes.datos_extra->'demograficos' → columnas propias
-- ===================================================================
ALTER TABLE pacientes
  ADD COLUMN IF NOT EXISTS idioma_id INTEGER,
  ADD COLUMN IF NOT EXISTS pueblo_id INTEGER,
  ADD COLUMN IF NOT EXISTS nacionalidad VARCHAR(10),
  ADD COLUMN IF NOT EXISTS lugar_nacimiento VARCHAR(4);

UPDATE pacientes SET
  idioma_id = NULLIF(NULLIF(TRIM(datos_extra->'demograficos'->>'idioma'), ''), 'null')::INTEGER,
  pueblo_id = NULLIF(NULLIF(TRIM(datos_extra->'demograficos'->>'pueblo'), ''), 'null')::INTEGER,
  nacionalidad = NULLIF(NULLIF(TRIM(datos_extra->'demograficos'->>'nacionalidad'), ''), 'null'),
  lugar_nacimiento = NULLIF(NULLIF(TRIM(datos_extra->'demograficos'->>'lugar_nacimiento'), ''), 'null')
WHERE datos_extra IS NOT NULL AND datos_extra ? 'demograficos'
  AND idioma_id IS NULL;

CREATE INDEX IF NOT EXISTS idx_pacientes_idioma ON pacientes(idioma_id);
CREATE INDEX IF NOT EXISTS idx_pacientes_pueblo ON pacientes(pueblo_id);
CREATE INDEX IF NOT EXISTS idx_pacientes_nacionalidad ON pacientes(nacionalidad);
CREATE INDEX IF NOT EXISTS idx_pacientes_lugar_nacimiento ON pacientes(lugar_nacimiento);

-- ===================================================================
-- 3. consultas.indicadores/egreso → registro_medico, condicion_egreso, fecha_egreso
-- ===================================================================
ALTER TABLE consultas
  ADD COLUMN IF NOT EXISTS registro_medico VARCHAR(50),
  ADD COLUMN IF NOT EXISTS condicion_egreso VARCHAR(100),
  ADD COLUMN IF NOT EXISTS fecha_egreso DATE;

UPDATE consultas SET
  registro_medico = NULLIF(TRIM(egreso->>'registro'), '')
WHERE egreso IS NOT NULL AND egreso ? 'registro'
  AND registro_medico IS NULL;

UPDATE consultas SET
  condicion_egreso = NULLIF(TRIM(egreso->>'condicion'), ''),
  fecha_egreso = NULLIF(egreso->>'fecha_egreso', '')::DATE
WHERE egreso IS NOT NULL AND (egreso ? 'condicion' OR egreso ? 'fecha_egreso')
  AND condicion_egreso IS NULL;

CREATE INDEX IF NOT EXISTS idx_consultas_registro_medico ON consultas(registro_medico);
CREATE INDEX IF NOT EXISTS idx_consultas_fecha_egreso ON consultas(fecha_egreso);

-- ===================================================================
-- 4. Trigger: sync citas columns ← datos_extra
-- ===================================================================
CREATE OR REPLACE FUNCTION sync_citas_datos_extra() RETURNS TRIGGER AS $$
BEGIN
  IF NEW.datos_extra IS NOT NULL AND NEW.datos_extra != '{}'::jsonb THEN
    IF NEW.datos_extra ? 'razon_consulta' THEN
      NEW.razon_consulta := NEW.datos_extra->>'razon_consulta';
    END IF;
    IF NEW.datos_extra ? 'notas' OR NEW.datos_extra ? 'nota' THEN
      NEW.notas := COALESCE(NEW.datos_extra->>'notas', NEW.datos_extra->>'nota');
    END IF;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_sync_citas_datos_extra ON citas;
CREATE TRIGGER trg_sync_citas_datos_extra
  BEFORE INSERT OR UPDATE ON citas
  FOR EACH ROW EXECUTE FUNCTION sync_citas_datos_extra();

-- ===================================================================
-- 5. Triggers de normalización de especialidad
-- Auto-resuelven especialidad_id y convierten nombre largo → código corto
-- ===================================================================
CREATE OR REPLACE FUNCTION trg_normalize_especialidad()
RETURNS TRIGGER AS $$
DECLARE
  eid INTEGER;
  ecod VARCHAR;
BEGIN
  IF NEW.especialidad IS NOT NULL AND NEW.especialidad != '' THEN
    SELECT id, codigo INTO eid, ecod
    FROM especialidades
    WHERE id = especialidad_id_from_text(NEW.especialidad);
    IF eid IS NOT NULL THEN
      NEW.especialidad_id := eid;
      IF ecod IS NOT NULL AND NEW.especialidad != ecod THEN
        NEW.especialidad := ecod;
      END IF;
    END IF;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_consultas_normalize_especialidad ON consultas;
CREATE TRIGGER trg_consultas_normalize_especialidad
  BEFORE INSERT OR UPDATE OF especialidad ON consultas
  FOR EACH ROW
  WHEN (NEW.especialidad IS NOT NULL AND NEW.especialidad != '')
  EXECUTE FUNCTION trg_normalize_especialidad();

DROP TRIGGER IF EXISTS trg_citas_normalize_especialidad ON citas;
CREATE TRIGGER trg_citas_normalize_especialidad
  BEFORE INSERT OR UPDATE OF especialidad ON citas
  FOR EACH ROW
  WHEN (NEW.especialidad IS NOT NULL AND NEW.especialidad != '')
  EXECUTE FUNCTION trg_normalize_especialidad();

DROP TRIGGER IF EXISTS trg_medicos_normalize_especialidad ON medicos;
CREATE TRIGGER trg_medicos_normalize_especialidad
  BEFORE INSERT OR UPDATE OF especialidad ON medicos
  FOR EACH ROW
  WHEN (NEW.especialidad IS NOT NULL AND NEW.especialidad != '')
  EXECUTE FUNCTION trg_normalize_especialidad();

DROP TRIGGER IF EXISTS trg_sigsa3_normalize_especialidad ON sigsa3;
CREATE TRIGGER trg_sigsa3_normalize_especialidad
  BEFORE INSERT OR UPDATE OF especialidad ON sigsa3
  FOR EACH ROW
  WHEN (NEW.especialidad IS NOT NULL AND NEW.especialidad != '')
  EXECUTE FUNCTION trg_normalize_especialidad();

COMMIT;
