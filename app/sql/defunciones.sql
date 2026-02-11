CREATE TABLE defunciones (
    id SERIAL PRIMARY KEY,
    documento VARCHAR(20) UNIQUE NOT NULL,
    paciente_id INTEGER NOT NULL,
    medico_id INTEGER NOT NULL,
    registrador_id INTEGER NOT NULL,
    fecha_defuncion DATE NOT NULL,
    causa_muerte VARCHAR(500) NOT NULL,
    lugar_defuncion VARCHAR(200),
    observaciones TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_defuncion_paciente FOREIGN KEY (paciente_id) REFERENCES pacientes (id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_defuncion_medico FOREIGN KEY (medico_id) REFERENCES medicos (id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_defuncion_registrador FOREIGN KEY (registrador_id) REFERENCES users (id) ON UPDATE CASCADE ON DELETE RESTRICT
);