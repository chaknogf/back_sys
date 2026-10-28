-- 087: asociación SIGSA-3 → paciente (asoc-v2, sin tocar pacientes).
--
-- Crea:
--   * pacientes_sigsa3: pacientes "creados" desde SIGSA-3 que NO existen en
--     pacientes (sin asociación y sin paciente parecido). Son registros de
--     trabajo, no se mezclan con pacientes.
--   * sigsa3_asociacion: una fila por registro de staging, con el estado,
--     el paciente (real o de pacientes_sigsa3), puntuación y motivo.
--   * Columnas `pacientes_sigsa3_id` en sigsa3 y sigsa3_registros, para que la
--     normalización pueda asociar paciente_id O pacientes_sigsa3_id.
--
-- Reversible: migrations/rollback/087_sigsa3_asociacion_rollback.sql
-- Idempotente (IF NOT EXISTS / IF NOT EXISTS).

CREATE TABLE IF NOT EXISTS pacientes_sigsa3 (
    id               BIGSERIAL PRIMARY KEY,
    nombre           TEXT NOT NULL,
    sexo             CHAR(1),
    expediente       VARCHAR(20),
    sigsa3_id_origen BIGINT,                 -- primer registro de staging que lo creó
    datos_extra      JSONB,
    estado           VARCHAR(2) NOT NULL DEFAULT 'A',
    creado_en        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_pacientes_sigsa3_nombre ON pacientes_sigsa3 (nombre);
CREATE INDEX IF NOT EXISTS ix_pacientes_sigsa3_expediente ON pacientes_sigsa3 (expediente) WHERE expediente IS NOT NULL;

CREATE TABLE IF NOT EXISTS sigsa3_asociacion (
    id                BIGSERIAL PRIMARY KEY,
    sigsa3_id         BIGINT NOT NULL UNIQUE,
    estado            VARCHAR(30) NOT NULL,
    paciente_id       INTEGER REFERENCES pacientes(id) ON DELETE SET NULL,
    pacientes_sigsa3_id BIGINT REFERENCES pacientes_sigsa3(id) ON DELETE SET NULL,
    metodo            VARCHAR(60),
    motivo            VARCHAR(120),
    score             NUMERIC(6,4),
    margen            NUMERIC(6,4),
    version           VARCHAR(20) NOT NULL,
    aplicado          BOOLEAN NOT NULL DEFAULT FALSE,
    usuario           VARCHAR(50),
    creado_en         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_sigsa3_asoc_paciente ON sigsa3_asociacion (paciente_id);
CREATE INDEX IF NOT EXISTS ix_sigsa3_asoc_ps ON sigsa3_asociacion (pacientes_sigsa3_id);
CREATE INDEX IF NOT EXISTS ix_sigsa3_asoc_estado ON sigsa3_asociacion (estado) WHERE NOT aplicado;

ALTER TABLE sigsa3
    ADD COLUMN IF NOT EXISTS pacientes_sigsa3_id BIGINT REFERENCES pacientes_sigsa3(id) ON DELETE SET NULL;

ALTER TABLE sigsa3_registros
    ADD COLUMN IF NOT EXISTS pacientes_sigsa3_id BIGINT REFERENCES pacientes_sigsa3(id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS ix_sigsa3_pacientes_sigsa3_id ON sigsa3 (pacientes_sigsa3_id) WHERE pacientes_sigsa3_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS ix_sigsa3_reg_pacientes_sigsa3_id ON sigsa3_registros (pacientes_sigsa3_id) WHERE pacientes_sigsa3_id IS NOT NULL;
