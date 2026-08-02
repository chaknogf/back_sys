-- Migration: Índices faltantes para constancia_nacimiento
-- 2026-07-15: Foreign keys usadas en JOINs y WHERE sin índice

CREATE INDEX IF NOT EXISTS idx_constancia_nacimiento_paciente_id ON constancia_nacimiento(paciente_id);
CREATE INDEX IF NOT EXISTS idx_constancia_nacimiento_madre_id ON constancia_nacimiento(madre_id);
CREATE INDEX IF NOT EXISTS idx_constancia_nacimiento_medico_id ON constancia_nacimiento(medico_id);
CREATE INDEX IF NOT EXISTS idx_constancia_nacimiento_registrador_id ON constancia_nacimiento(registrador_id);
