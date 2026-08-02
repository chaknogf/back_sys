-- ============================================================================
-- Migration 012: Remove legacy especialidad string columns
-- ============================================================================
-- Las columnas especialidad (VARCHAR) son redundantes desde que existe
-- especialidad_id (FK → especialidades.id) en cada tabla.
--
-- Ejecutar:
--   psql -U postgres -d hospital -f 012_remove_especialidad_string.sql
-- ============================================================================

BEGIN;

-- 1. medicos — también elimina trigger y función asociados
DROP TRIGGER IF EXISTS trg_medicos_normalize_especialidad ON medicos;
ALTER TABLE medicos DROP COLUMN IF EXISTS especialidad;

-- 2. personal_salud
ALTER TABLE personal_salud DROP COLUMN IF EXISTS especialidad;

-- 3. sigsa3
DROP TRIGGER IF EXISTS trg_sigsa3_normalize_especialidad ON sigsa3;
ALTER TABLE sigsa3 DROP COLUMN IF EXISTS especialidad;

-- 4. Eliminar índices que ya no tienen columna
DROP INDEX IF EXISTS idx_medicos_especialidad;
DROP INDEX IF EXISTS idx_consultas_especialidad;

COMMIT;
