-- Migration 003: Catálogo de especialidades normalizado
-- Reemplaza el string libre 'especialidad' en 7 tablas por FK

-- 1. Crear tabla catálogo
CREATE TABLE IF NOT EXISTS especialidades (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    abreviatura VARCHAR(10) UNIQUE
);

CREATE INDEX IF NOT EXISTS ix_especialidades_nombre ON especialidades(nombre);

-- 2. Poblar con datos extraídos de los valores existentes
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

-- 3. Agregar columna especialidad_id a medicos
ALTER TABLE medicos ADD COLUMN IF NOT EXISTS especialidad_id INTEGER REFERENCES especialidades(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS ix_medicos_especialidad_id ON medicos(especialidad_id);

-- 4. Agregar columna especialidad_id a consultas
ALTER TABLE consultas ADD COLUMN IF NOT EXISTS especialidad_id INTEGER REFERENCES especialidades(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS ix_consultas_especialidad_id ON consultas(especialidad_id);

-- 5. Agregar columna especialidad_id a citas
ALTER TABLE citas ADD COLUMN IF NOT EXISTS especialidad_id INTEGER REFERENCES especialidades(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS ix_citas_especialidad_id ON citas(especialidad_id);

-- 6. Agregar columna especialidad_id a ciclos_consulta
ALTER TABLE ciclos_consulta ADD COLUMN IF NOT EXISTS especialidad_id INTEGER REFERENCES especialidades(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS ix_ciclos_especialidad_id ON ciclos_consulta(especialidad_id);

-- 7. Agregar columna especialidad_id a proce_medicos
ALTER TABLE proce_medicos ADD COLUMN IF NOT EXISTS especialidad_id INTEGER REFERENCES especialidades(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS ix_proce_medicos_especialidad_id ON proce_medicos(especialidad_id);

-- 8. Agregar columna especialidad_id a sigsa3
ALTER TABLE sigsa3 ADD COLUMN IF NOT EXISTS especialidad_id INTEGER REFERENCES especialidades(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS ix_sigsa3_especialidad_id ON sigsa3(especialidad_id);

-- 9. Agregar columna especialidad_id a personal_salud
ALTER TABLE personal_salud ADD COLUMN IF NOT EXISTS especialidad_id INTEGER REFERENCES especialidades(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS ix_personal_salud_especialidad_id ON personal_salud(especialidad_id);
