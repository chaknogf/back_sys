-- 022_quirofano_catalogos.sql
-- Catálogos del módulo Quirófano.
-- Estado de cirugía, formato de procedimiento, rango de especialista,
-- procedencia del procedimiento, categoría (especialidad) y tipo de procedimiento.

CREATE TABLE IF NOT EXISTS estado_cirugia (
    estado_cirugia_id      SERIAL PRIMARY KEY,
    codigo                 VARCHAR(5)  NOT NULL UNIQUE,
    nombre                 VARCHAR(50) NOT NULL,
    activo                 BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS formato_procedimiento (
    formato_procedimiento_id SERIAL PRIMARY KEY,
    codigo                   VARCHAR(5)   NOT NULL UNIQUE,
    nombre                   VARCHAR(100) NOT NULL,
    activo                   BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS rango_especialista (
    rango_especialista_id SERIAL PRIMARY KEY,
    codigo                VARCHAR(5)  NOT NULL UNIQUE,
    nombre                VARCHAR(50) NOT NULL,
    activo                BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS procedencia_procedimiento (
    procedencia_procedimiento_id SERIAL PRIMARY KEY,
    codigo                       VARCHAR(5)  NOT NULL UNIQUE,
    nombre                       VARCHAR(50) NOT NULL,
    activo                       BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS categoria_procedimiento (
    categoria_procedimiento_id SERIAL PRIMARY KEY,
    codigo                     VARCHAR(10)  NOT NULL UNIQUE,
    nombre                     VARCHAR(150) NOT NULL,
    activo                     BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS tipo_procedimiento (
    tipo_procedimiento_id      SERIAL PRIMARY KEY,
    codigo                     VARCHAR(10)  NOT NULL UNIQUE,
    nombre                     VARCHAR(200) NOT NULL,
    categoria_procedimiento_id INTEGER      NOT NULL REFERENCES categoria_procedimiento(categoria_procedimiento_id) ON DELETE RESTRICT,
    activo                     BOOLEAN DEFAULT TRUE
);

-- FK de intervenciones_quirurgicas a los catálogos (se agregan aquí porque
-- 021_quirofano_intervenciones.sql se ejecuta antes de que existan).
ALTER TABLE intervenciones_quirurgicas
    ADD COLUMN IF NOT EXISTS tipo_procedimiento_id     INTEGER REFERENCES tipo_procedimiento(tipo_procedimiento_id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS estado_cirugia_id         INTEGER REFERENCES estado_cirugia(estado_cirugia_id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS formato_procedimiento_id  INTEGER REFERENCES formato_procedimiento(formato_procedimiento_id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS procedencia_procedimiento_id INTEGER REFERENCES procedencia_procedimiento(procedencia_procedimiento_id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS rango_especialista_id     INTEGER REFERENCES rango_especialista(rango_especialista_id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS ix_intervenciones_quirurgicas_tipo_procedimiento_id ON intervenciones_quirurgicas (tipo_procedimiento_id);
CREATE INDEX IF NOT EXISTS ix_intervenciones_quirurgicas_estado_cirugia_id ON intervenciones_quirurgicas (estado_cirugia_id);

-- Datos base de los catálogos (idempotente)
INSERT INTO estado_cirugia (codigo, nombre) VALUES
    ('FIN', 'Finalizada'),
    ('CAN', 'Cancelada')
ON CONFLICT (codigo) DO NOTHING;

INSERT INTO formato_procedimiento (codigo, nombre) VALUES
    ('FP01', 'Abierta'),
    ('FP02', 'Videolaparoscópica'),
    ('FP03', 'Endoscópica'),
    ('FP04', 'Artroscópica'),
    ('FP05', 'Percutánea'),
    ('FP06', 'Endourológica'),
    ('FP07', 'Vaginal'),
    ('FP08', 'Mixta'),
    ('FP09', 'Otro')
ON CONFLICT (codigo) DO NOTHING;

INSERT INTO rango_especialista (codigo, nombre) VALUES
    ('ESP', 'Especialista'),
    ('MGE', 'Médico General'),
    ('R1',  'R1'),
    ('R2',  'R2'),
    ('R3',  'R3'),
    ('R4',  'R4')
ON CONFLICT (codigo) DO NOTHING;

INSERT INTO procedencia_procedimiento (codigo, nombre) VALUES
    ('EMG', 'Emergencia'),
    ('ELE', 'Electiva'),
    ('HDD', 'Hospital de día')
ON CONFLICT (codigo) DO NOTHING;

-- Nota: los procedimientos (nombre = solo el procedimiento) se siembran con el
-- script scripts/seed_quirofano_procedimientos.py a partir de
-- data/quirofano_procedimientos.csv (idempotente).
-- Migraciones posteriores: 025 reemplaza las categorías por `especialidades`,
-- 027 renombra `tipo_procedimiento` -> `procedimiento_quirofano` y 028 admite
-- `especialidad_id NULL` ("Todas (mixta)"). Ver migrations/README.md.