-- 021_quirofano_intervenciones.sql
-- Registro de intervenciones quirúrgicas (Quirófano).
--
-- ORDEN: las FK a los catálogos de quirófano (estado_cirugia,
-- formato_procedimiento, procedencia_procedimiento, rango_especialista y
-- tipo_procedimiento) se agregan al final de 022_quirofano_catalogos.sql,
-- porque es 022 quien crea esas tablas.

CREATE TABLE IF NOT EXISTS intervenciones_quirurgicas (
    intervencion_id           BIGSERIAL PRIMARY KEY,
    paciente_id               INTEGER NOT NULL REFERENCES pacientes(id) ON DELETE SET NULL,
    expediente                VARCHAR(20),
    medico_id                 INTEGER REFERENCES medicos(id) ON DELETE SET NULL,
    fecha                     DATE NOT NULL,
    hora                      TIME,
    observaciones             TEXT,
    activo                    BOOLEAN NOT NULL DEFAULT TRUE,
    created_at                TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at                TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_intervenciones_quirurgicas_paciente_id ON intervenciones_quirurgicas (paciente_id);
CREATE INDEX IF NOT EXISTS ix_intervenciones_quirurgicas_expediente  ON intervenciones_quirurgicas (expediente);
CREATE INDEX IF NOT EXISTS ix_intervenciones_quirurgicas_medico_id   ON intervenciones_quirurgicas (medico_id);
CREATE INDEX IF NOT EXISTS ix_intervenciones_quirurgicas_fecha       ON intervenciones_quirurgicas (fecha);
