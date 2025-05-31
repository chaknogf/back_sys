CREATE TABLE expediente_control (
    anio SMALLINT PRIMARY KEY,
    ultimo_correlativo INT NOT NULL DEFAULT 0,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE emergencia_control (
    anio SMALLINT PRIMARY KEY,
    ultimo_correlativo INT NOT NULL DEFAULT 0,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);