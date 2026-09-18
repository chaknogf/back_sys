-- ================================================================
-- Migration 006: Normalización completa (producción)
-- ================================================================
-- Ejecutar en orden: psql -d hospital -f migrations/006_normalizacion_completa.sql
-- ================================================================

BEGIN;

-- ================================================================
-- 1. Catálogo de especialidades
-- ================================================================
CREATE TABLE IF NOT EXISTS especialidades (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    abreviatura VARCHAR(10) UNIQUE
);
CREATE INDEX IF NOT EXISTS ix_especialidades_nombre ON especialidades(nombre);

INSERT INTO especialidades (nombre, abreviatura) VALUES
    ('Medicina General', 'MG'),
    ('Medicina Interna', 'MI'),
    ('Cirugía', 'CIR'),
    ('Pediatría', 'PED'),
    ('Ginecología', 'GIN'),
    ('Traumatología', 'TRA'),
    ('Cardiología', 'CAR'),
    ('Neurología', 'NEU'),
    ('Psicología', 'PSI'),
    ('Nutrición', 'NUT'),
    ('Odontología', 'ODT'),
    ('Terapia respiratoria', 'TR'),
    ('Educadora', 'EDU'),
    ('Anestesiología', 'ANE'),
    ('Medicina Crítica', 'UCI'),
    ('Neonatología', 'NEO')
ON CONFLICT (nombre) DO NOTHING;

-- medicos
ALTER TABLE medicos ADD COLUMN IF NOT EXISTS especialidad_id INTEGER REFERENCES especialidades(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS ix_medicos_especialidad_id ON medicos(especialidad_id);

-- consultas
ALTER TABLE consultas ADD COLUMN IF NOT EXISTS especialidad_id INTEGER REFERENCES especialidades(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS ix_consultas_especialidad_id ON consultas(especialidad_id);

-- citas
ALTER TABLE citas ADD COLUMN IF NOT EXISTS especialidad_id INTEGER REFERENCES especialidades(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS ix_citas_especialidad_id ON citas(especialidad_id);

-- ciclos_consulta
ALTER TABLE ciclos_consulta ADD COLUMN IF NOT EXISTS especialidad_id INTEGER REFERENCES especialidades(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS ix_ciclos_especialidad_id ON ciclos_consulta(especialidad_id);

-- proce_medicos
ALTER TABLE proce_medicos ADD COLUMN IF NOT EXISTS especialidad_id INTEGER REFERENCES especialidades(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS ix_proce_medicos_especialidad_id ON proce_medicos(especialidad_id);

-- sigsa3
ALTER TABLE sigsa3 ADD COLUMN IF NOT EXISTS especialidad_id INTEGER REFERENCES especialidades(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS ix_sigsa3_especialidad_id ON sigsa3(especialidad_id);

-- personal_salud
ALTER TABLE personal_salud ADD COLUMN IF NOT EXISTS especialidad_id INTEGER REFERENCES especialidades(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS ix_personal_salud_especialidad_id ON personal_salud(especialidad_id);

-- ================================================================
-- 2. Catálogo tipo_consulta
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

ALTER TABLE sigsa3 ADD COLUMN IF NOT EXISTS tipo_consulta_id SMALLINT REFERENCES tipos_consulta(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS ix_sigsa3_tipo_consulta_id ON sigsa3(tipo_consulta_id);

-- ================================================================
-- 3. FK adicionales en sigsa3
-- ================================================================
ALTER TABLE sigsa3 ADD COLUMN IF NOT EXISTS personal_salud_id INTEGER REFERENCES personal_salud(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS ix_sigsa3_personal_salud_id ON sigsa3(personal_salud_id);

ALTER TABLE sigsa3 ADD COLUMN IF NOT EXISTS codigo_cie_10_id INTEGER REFERENCES cie10_catalogo(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS ix_sigsa3_codigo_cie10_id ON sigsa3(codigo_cie_10_id);

-- ================================================================
-- 4. Unificar tablas de control correlativos
-- ================================================================
CREATE TABLE IF NOT EXISTS correlativos_control (
    tipo VARCHAR(30) NOT NULL,
    anio SMALLINT NOT NULL,
    ultimo_correlativo INTEGER NOT NULL DEFAULT 0,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (tipo, anio)
);

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

COMMIT;
