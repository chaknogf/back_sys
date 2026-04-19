CREATE TABLE ciclos_consulta (
    id SERIAL PRIMARY KEY,
    consulta_id INT NOT NULL REFERENCES consultas (id) ON DELETE RESTRICT ON UPDATE CASCADE,
    numero INT NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT true,
    registro TIMESTAMP NOT NULL DEFAULT NOW(),
    usuario TEXT NOT NULL,
    especialidad TEXT,
    servicio TEXT,
    contenido TEXT,
    datos_medicos JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT unique_ciclo_por_consulta UNIQUE (consulta_id, numero),
    CONSTRAINT check_numero_positivo CHECK (numero > 0)
);

CREATE TABLE laboratorios (
    id SERIAL PRIMARY KEY,
    cod_lab TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    registro TIMESTAMP NULL,
    usuario TEXT,
    activo BOOLEAN NOT NULL DEFAULT true,
    ciclo_consulta_id INT NULL REFERENCES ciclos_consulta (id) ON DELETE SET NULL ON UPDATE CASCADE,
    consulta_id INT NOT NULL REFERENCES consultas (id) ON DELETE RESTRICT ON UPDATE CASCADE,
    resultados JSONB,
    metadatos JSONB
);

CREATE TABLE rayos_x (
    id SERIAL PRIMARY KEY,
    cod_rx TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    registro TIMESTAMP NULL,
    usuario TEXT,
    activo BOOLEAN NOT NULL DEFAULT true,
    ciclo_consulta_id INT NULL REFERENCES ciclos_consulta (id) ON DELETE SET NULL ON UPDATE CASCADE,
    consulta_id INT NOT NULL REFERENCES consultas (id) ON DELETE RESTRICT ON UPDATE CASCADE,
    resultados JSONB,
    metadatos JSONB
);

CREATE INDEX idx_ciclos_activo ON ciclos_consulta (activo);

CREATE INDEX idx_lab_activo ON laboratorios (activo);

CREATE INDEX idx_rx_activo ON rayos_x (activo);

CREATE INDEX idx_ciclos_consulta_id ON ciclos_consulta (consulta_id);

CREATE INDEX idx_ciclos_registro ON ciclos_consulta (registro);

CREATE INDEX idx_ciclos_activo ON ciclos_consulta (activo);

CREATE INDEX idx_lab_consulta ON laboratorios (consulta_id);

CREATE INDEX idx_lab_ciclo ON laboratorios (ciclo_consulta_id);

CREATE INDEX idx_lab_registro ON laboratorios (registro);

CREATE INDEX idx_lab_activo ON laboratorios (activo);

CREATE INDEX idx_rx_consulta ON rayos_x (consulta_id);

CREATE INDEX idx_rx_ciclo ON rayos_x (ciclo_consulta_id);

CREATE INDEX idx_rx_registro ON rayos_x (registro);

CREATE INDEX idx_rx_activo ON rayos_x (activo);

CREATE INDEX idx_ciclos_datos_medicos ON ciclos_consulta USING GIN (datos_medicos);

CREATE INDEX idx_lab_resultados ON laboratorios USING GIN (resultados);

CREATE INDEX idx_rx_resultados ON rayos_x USING GIN (resultados);

CREATE INDEX idx_ciclos_timeline ON ciclos_consulta (consulta_id, registro DESC);

CREATE INDEX idx_lab_timeline ON laboratorios (consulta_id, created_at DESC);

CREATE INDEX idx_rx_timeline ON rayos_x (consulta_id, created_at DESC);