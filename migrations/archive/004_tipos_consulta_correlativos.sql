-- Migration 004: Catálogo de tipo_consulta + unificación correlativos

-- ================================================================
-- PARTE A: Catálogo tipo_consulta
-- ================================================================
CREATE TABLE IF NOT EXISTS tipos_consulta (
    id SMALLINT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    descripcion VARCHAR(200)
);

INSERT INTO tipos_consulta (id, nombre, descripcion) VALUES
    (1, 'COEX', 'Consulta Externa - Primera vez'),
    (2, 'Hospitalización', 'Hospitalización'),
    (3, 'Emergencia', 'Servicio de Emergencia')
ON CONFLICT (id) DO NOTHING;

-- FK desde consultas (tipo_consulta ya es Integer, solo agregamos FK si no existe)
-- Nota: tipo_consulta actualmente es un int sin FK, solo documentamos la relación

-- Para sigsa3: agregar tipo_consulta_id
ALTER TABLE sigsa3 ADD COLUMN IF NOT EXISTS tipo_consulta_id SMALLINT REFERENCES tipos_consulta(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS ix_sigsa3_tipo_consulta_id ON sigsa3(tipo_consulta_id);

-- ================================================================
-- PARTE B: Unificar tablas de control correlativos
-- ================================================================
CREATE TABLE IF NOT EXISTS correlativos_control (
    tipo VARCHAR(30) NOT NULL,
    anio SMALLINT NOT NULL,
    ultimo_correlativo INTEGER NOT NULL DEFAULT 0,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (tipo, anio)
);

-- Migrar datos existentes
INSERT INTO correlativos_control (tipo, anio, ultimo_correlativo, actualizado_en)
SELECT 'expediente', anio, ultimo_correlativo, actualizado_en FROM expediente_control
ON CONFLICT (tipo, anio) DO NOTHING;

INSERT INTO correlativos_control (tipo, anio, ultimo_correlativo, actualizado_en)
SELECT 'emergencia', anio, ultimo_correlativo, actualizado_en FROM emergencia_control
ON CONFLICT (tipo, anio) DO NOTHING;

INSERT INTO correlativos_control (tipo, anio, ultimo_correlativo, actualizado_en)
SELECT 'constancia_nacimiento', anio, ultimo_correlativo, actualizado_en FROM constancia_nacimiento_control
ON CONFLICT (tipo, anio) DO NOTHING;

INSERT INTO correlativos_control (tipo, anio, ultimo_correlativo, actualizado_en)
SELECT 'defuncion', anio, ultimo_correlativo, actualizado_en FROM defuncion_control
ON CONFLICT (tipo, anio) DO NOTHING;

INSERT INTO correlativos_control (tipo, anio, ultimo_correlativo, actualizado_en)
SELECT 'constancia_medica', anio, ultimo_correlativo, actualizado_en FROM constancia_medica_control
ON CONFLICT (tipo, anio) DO NOTHING;
