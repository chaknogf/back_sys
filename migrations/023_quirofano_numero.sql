-- 023_quirofano_numero.sql
-- Catálogo de número de quirófano (administrable, solo rol admin) + FK en
-- intervenciones_quirurgicas.

CREATE TABLE IF NOT EXISTS quirofano_numero (
    quirofano_numero_id SERIAL PRIMARY KEY,
    numero              INTEGER      NOT NULL UNIQUE,
    nombre              VARCHAR(50)  NOT NULL,
    activo              BOOLEAN DEFAULT TRUE
);

-- Seed inicial: 2 quirófanos
INSERT INTO quirofano_numero (numero, nombre) VALUES
    (1, 'Quirófano 1'),
    (2, 'Quirófano 2')
ON CONFLICT (numero) DO NOTHING;

-- Vinculación con las intervenciones
ALTER TABLE intervenciones_quirurgicas
    ADD COLUMN IF NOT EXISTS quirofano_numero_id INTEGER
        REFERENCES quirofano_numero(quirofano_numero_id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS ix_intervenciones_quirofano_numero
    ON intervenciones_quirurgicas (quirofano_numero_id);