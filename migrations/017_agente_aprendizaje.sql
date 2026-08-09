-- 017_agente_aprendizaje.sql
-- Tablas de aprendizaje del Agente Estadístico: sinónimos aprendidos y feedback.

CREATE TABLE IF NOT EXISTS agente_reglas (
    id            BIGSERIAL PRIMARY KEY,
    tipo          VARCHAR(40)  NOT NULL,             -- sinonimo_entidad|sinonimo_agrupacion|sinonimo_medida
    clave         VARCHAR(200) NOT NULL,
    valor         VARCHAR(200) NOT NULL,
    veces_usado   BIGINT       NOT NULL DEFAULT 0,
    veces_exito   BIGINT       NOT NULL DEFAULT 0,
    veces_fracaso BIGINT       NOT NULL DEFAULT 0,
    origen        VARCHAR(20)  NOT NULL DEFAULT 'manual',  -- manual|feedback
    usuario       VARCHAR(60),
    creado_en     TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_agente_reglas_tipo      ON agente_reglas (tipo);
CREATE INDEX IF NOT EXISTS ix_agente_reglas_clave     ON agente_reglas (clave);
CREATE UNIQUE INDEX IF NOT EXISTS uq_agente_regla      ON agente_reglas (tipo, clave, valor);

CREATE TABLE IF NOT EXISTS agente_feedback (
    id            BIGSERIAL PRIMARY KEY,
    pregunta      TEXT         NOT NULL,
    respuesta     TEXT         NOT NULL,
    sql_generado  TEXT,
    correcto      BOOLEAN,
    correccion    TEXT,
    username      VARCHAR(60)  NOT NULL,
    creado_en     TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_agente_feedback_username  ON agente_feedback (username);
CREATE INDEX IF NOT EXISTS ix_agente_feedback_correcto  ON agente_feedback (correcto);