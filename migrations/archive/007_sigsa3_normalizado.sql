-- Migration 007: sigsa3_registros (tabla normalizada)
-- Ejecutar DESPUÉS de 006_normalizacion_completa.sql
-- Propósito: sigsa3 queda como staging; los registros con paciente+medico
-- se migran a sigsa3_registros y se purgan de sigsa3.

BEGIN;

CREATE TABLE IF NOT EXISTS sigsa3_registros (
    id BIGSERIAL PRIMARY KEY,
    paciente_id INTEGER NOT NULL REFERENCES pacientes(id) ON DELETE SET NULL,
    medico_id INTEGER REFERENCES medicos(id) ON DELETE SET NULL,
    personal_salud_id INTEGER REFERENCES personal_salud(id) ON DELETE SET NULL,
    consulta_id INTEGER REFERENCES consultas(id) ON DELETE SET NULL,
    fecha_consulta DATE NOT NULL,
    tipo_consulta_id SMALLINT REFERENCES tipos_consulta(id) ON DELETE SET NULL,
    control VARCHAR(80),
    semana_gestacional INTEGER,
    codigo_cie_10_id INTEGER REFERENCES cie10_catalogo(id) ON DELETE SET NULL,
    especialidad_id INTEGER REFERENCES especialidades(id) ON DELETE SET NULL,
    normalized_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_sigsa3_reg_paciente_fecha ON sigsa3_registros(paciente_id, fecha_consulta);
CREATE INDEX IF NOT EXISTS ix_sigsa3_reg_fecha ON sigsa3_registros(fecha_consulta);
CREATE INDEX IF NOT EXISTS ix_sigsa3_reg_medico ON sigsa3_registros(medico_id);
CREATE INDEX IF NOT EXISTS ix_sigsa3_reg_cie10 ON sigsa3_registros(codigo_cie_10_id);
CREATE INDEX IF NOT EXISTS ix_sigsa3_reg_especialidad ON sigsa3_registros(especialidad_id);

COMMIT;
