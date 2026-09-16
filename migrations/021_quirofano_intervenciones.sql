-- 021_quirofano_intervenciones.sql
-- Registro de intervenciones quirúrgicas (Quirófano).

CREATE TABLE IF NOT EXISTS intervenciones_quirurgicas (
    intervencion_id           BIGSERIAL PRIMARY KEY,
    paciente_id               INTEGER NOT NULL REFERENCES pacientes(id) ON DELETE SET NULL,
    expediente                VARCHAR(20),
    tipo_procedimiento_id     INTEGER REFERENCES tipo_procedimiento(tipo_procedimiento_id) ON DELETE SET NULL,
    estado_cirugia_id         INTEGER REFERENCES estado_cirugia(estado_cirugia_id) ON DELETE SET NULL,
    formato_procedimiento_id  INTEGER REFERENCES formato_procedimiento(formato_procedimiento_id) ON DELETE SET NULL,
    procedencia_procedimiento_id INTEGER REFERENCES procedencia_procedimiento(procedencia_procedimiento_id) ON DELETE SET NULL,
    rango_especialista_id     INTEGER REFERENCES rango_especialista(rango_especialista_id) ON DELETE SET NULL,
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
CREATE INDEX IF NOT EXISTS ix_intervenciones_quirurgicas_tipo_procedimiento_id ON intervenciones_quirurgicas (tipo_procedimiento_id);
CREATE INDEX IF NOT EXISTS ix_intervenciones_quirurgicas_estado_cirugia_id ON intervenciones_quirurgicas (estado_cirugia_id);
CREATE INDEX IF NOT EXISTS ix_intervenciones_quirurgicas_medico_id   ON intervenciones_quirurgicas (medico_id);
CREATE INDEX IF NOT EXISTS ix_intervenciones_quirurgicas_fecha       ON intervenciones_quirurgicas (fecha);