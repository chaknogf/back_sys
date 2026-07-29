-- Migration 008: consultas_historial (extraer ciclo JSONB → tabla)
-- Propósito: normalizar el historial de estados de consultas
-- Ahorro: ~46 MB (218k filas × ~219 bytes/fila)

BEGIN;

CREATE TABLE IF NOT EXISTS consultas_historial (
    id SERIAL PRIMARY KEY,
    consulta_id INTEGER NOT NULL REFERENCES consultas(id) ON DELETE CASCADE,
    estado VARCHAR(50) NOT NULL,
    registro TEXT NOT NULL DEFAULT (NOW()::TEXT),
    usuario VARCHAR(100),
    usuario_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    especialidad VARCHAR(100),
    servicio VARCHAR(50),
    comentario TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_historial_consulta_id ON consultas_historial(consulta_id);
CREATE INDEX IF NOT EXISTS idx_historial_registro ON consultas_historial(registro);

-- Migrar datos existentes desde ciclo JSONB
INSERT INTO consultas_historial (consulta_id, estado, registro, usuario, especialidad, servicio, comentario)
SELECT
    c.id,
    h->>'estado',
    COALESCE(
        h->>'registro',
        NOW()::TEXT
    ),
    h->>'usuario',
    h->>'especialidad',
    h->>'servicio',
    h->>'comentario'
FROM consultas c,
LATERAL jsonb_array_elements(c.ciclo) AS h
WHERE jsonb_typeof(c.ciclo) = 'array';

COMMIT;
