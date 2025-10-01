DROP TABLE IF EXISTS pacientes CASCADE;

CREATE TABLE IF NOT EXISTS pacientes (
    id SERIAL PRIMARY KEY,
    unidad INT,
    cui BIGINT UNIQUE,
    expediente VARCHAR UNIQUE DEFAULT NULL,
    pasaporte VARCHAR UNIQUE,
    otro_id VARCHAR UNIQUE,
    nombre JSONB NOT NULL,
    sexo VARCHAR(2),
    fecha_nacimiento DATE,
    contacto JSONB,
    referencias JSONB,
    datos_extra JSONB,
    estado VARCHAR(2) DEFAULT 'V',
    metadatos JSONB,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    nombre_completo TEXT
);

CREATE INDEX idx_referencias_gin ON pacientes USING GIN (referencias);

CREATE INDEX idx_datos_extra_gin ON pacientes USING GIN (datos_extra);

CREATE INDEX idx_nombre_primer ON pacientes ((nombre ->> 'primer'));

CREATE INDEX idx_nombre_apellido1 ON pacientes (
    (nombre ->> 'apellido_primero')
);

CREATE INDEX idx_contacto_telefono ON pacientes ((contacto ->> 'telefono'));

CREATE INDEX idx_estado ON pacientes (estado);

CREATE INDEX idx_fecha_nacimiento ON pacientes (fecha_nacimiento);

CREATE INDEX idx_creado_en ON pacientes (creado_en);

CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE INDEX idx_nombre_completo_trgm ON pacientes USING GIN (nombre_completo gin_trgm_ops);

CREATE OR REPLACE FUNCTION actualizar_nombre_completo()
RETURNS TRIGGER AS $$
BEGIN
  NEW.nombre_completo := TRIM(
    COALESCE(NEW.nombre->>'primer', '') || ' ' ||
    COALESCE(NEW.nombre->>'segundo', '') || ' ' ||
    COALESCE(NEW.nombre->>'otro', '') || ' ' ||
    COALESCE(NEW.nombre->>'apellido_primero', '') || ' ' ||
    COALESCE(NEW.nombre->>'apellido_segundo', '') || ' ' ||
    COALESCE(NEW.nombre->>'casada', '')
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_set_nombre_completo
BEFORE INSERT OR UPDATE ON pacientes
FOR EACH ROW
EXECUTE FUNCTION actualizar_nombre_completo();

UPDATE pacientes
SET
    nombre_completo = TRIM(
        COALESCE(nombre ->> 'primer', '') || ' ' || COALESCE(nombre ->> 'segundo', '') || ' ' || COALESCE(nombre ->> 'otro', '') || ' ' || COALESCE(
            nombre ->> 'apellido_primero',
            ''
        ) || ' ' || COALESCE(
            nombre ->> 'apellido_segundo',
            ''
        ) || ' ' || COALESCE(nombre ->> 'casada', '')
    );