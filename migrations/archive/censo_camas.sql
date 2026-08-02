-- Migration: Crear tabla censo_camas
-- Censo diario de camas por servicio y sexo

CREATE TABLE IF NOT EXISTS censo_camas (
    id SERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    servicio_id INTEGER NOT NULL REFERENCES encamamiento(id) ON DELETE CASCADE,
    sexo SMALLINT NOT NULL DEFAULT 0,
    ocupados SMALLINT NOT NULL DEFAULT 0,
    camas_ocupadas SMALLINT NOT NULL DEFAULT 0,
    egresos_totales SMALLINT NOT NULL DEFAULT 0,
    egresos SMALLINT NOT NULL DEFAULT 0,
    fallecidos SMALLINT NOT NULL DEFAULT 0,
    referido SMALLINT NOT NULL DEFAULT 0,
    traslado SMALLINT NOT NULL DEFAULT 0,
    contraindicados SMALLINT NOT NULL DEFAULT 0,
    otro_ingresos SMALLINT NOT NULL DEFAULT 0,
    ingresos SMALLINT NOT NULL DEFAULT 0,
    huespedes SMALLINT NOT NULL DEFAULT 0,
    emergencia SMALLINT NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(fecha, servicio_id, sexo)
);

CREATE INDEX IF NOT EXISTS ix_censo_camas_fecha ON censo_camas(fecha);
CREATE INDEX IF NOT EXISTS ix_censo_camas_servicio ON censo_camas(servicio_id);

-- Trigger para actualizar updated_at
CREATE OR REPLACE FUNCTION update_censo_camas_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_censo_camas_updated_at ON censo_camas;
CREATE TRIGGER trg_censo_camas_updated_at
    BEFORE UPDATE ON censo_camas
    FOR EACH ROW
    EXECUTE FUNCTION update_censo_camas_updated_at();
