-- 026_especialidades_estado_sop.sql
-- Agrega a `especialidades`:
--  - estado: si la especialidad está activa/inactiva
--  - sop:    si está disponible para el formulario de quirófano (Sala de Operaciones)

ALTER TABLE especialidades
    ADD COLUMN IF NOT EXISTS estado BOOLEAN NOT NULL DEFAULT TRUE,
    ADD COLUMN IF NOT EXISTS sop BOOLEAN NOT NULL DEFAULT TRUE;

COMMENT ON COLUMN especialidades.estado IS 'Especialidad activa (true/false)';
COMMENT ON COLUMN especialidades.sop IS 'Disponible para quirófano / Sala de Operaciones (true/false)';

CREATE INDEX IF NOT EXISTS idx_especialidades_estado ON especialidades (estado);
CREATE INDEX IF NOT EXISTS idx_especialidades_sop ON especialidades (sop);
