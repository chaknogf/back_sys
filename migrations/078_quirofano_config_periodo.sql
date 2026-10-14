-- 078_quirofano_config_periodo.sql
-- Configuración de jornada por quirófano para el reporte/Excel de quirófano.
-- Los valores aquí almacenados son el *fallback* cuando el período no tiene
-- datos: en el reporte, la hora de apertura se deduce del MIN de la hora de
-- inicio de anestesia y la de cierre del MAX de la hora de finalización de
-- limpieza; los días abiertos se cuentan como fechas distintas con actividad.
-- Aditiva e idempotente.

CREATE TABLE IF NOT EXISTS quirofano_config_periodo (
    config_periodo_id  SERIAL PRIMARY KEY,
    quirofano_numero_id INTEGER NOT NULL UNIQUE
        REFERENCES quirofano_numero(quirofano_numero_id) ON DELETE CASCADE,
    hora_apertura TIME NOT NULL DEFAULT '07:00',
    hora_cierre   TIME NOT NULL DEFAULT '16:00',
    dias_habiles  INTEGER NOT NULL DEFAULT 0 CHECK (dias_habiles >= 0),
    activo        BOOLEAN NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Semilla para cada quirófano del catálogo (jornada típica 07:00–16:00).
INSERT INTO quirofano_config_periodo
    (quirofano_numero_id, hora_apertura, hora_cierre, dias_habiles, activo)
SELECT q.quirofano_numero_id, TIME '07:00', TIME '16:00', 0, TRUE
FROM quirofano_numero q
ON CONFLICT (quirofano_numero_id) DO NOTHING;
