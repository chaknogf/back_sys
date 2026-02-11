CREATE TABLE medicos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    colegiado VARCHAR(20),
    dpi BIGINT,
    sexo CHAR(1),
    especialidad VARCHAR(100),
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_medicos_nombre ON medicos (nombre);

CREATE INDEX idx_medicos_colegiado ON medicos (colegiado);

CREATE INDEX idx_medicos_dpi ON medicos (dpi);

CREATE INDEX idx_medicos_especialidad ON medicos (especialidad);

CREATE INDEX idx_medicos_activo ON medicos (activo);

