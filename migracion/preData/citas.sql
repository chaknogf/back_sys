CREATE TABLE nuevacitas (
    id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
    paciente_id INT DEFAULT NULL,
    expediente INT DEFAULT NULL,
    especialidad INT DEFAULT NULL,
    fecha DATE DEFAULT NULL,
    nota TEXT DEFAULT NULL,
    tipo INT DEFAULT NULL,
    lab INT DEFAULT NULL,
    fecha_lab DATE DEFAULT NULL,
    created_at DATETIME DEFAULT NULL,
    updated_at DATETIME DEFAULT NULL,
    created_by VARCHAR(8) DEFAULT NULL
) ENGINE = InnoDB CHARSET = utf8mb4;

INSERT INTO
    nuevacitas (
        expediente,
        especialidad,
        fecha,
        nota,
        tipo,
        created_at,
        updated_at,
        created_by,
        lab,
        fecha_lab
    )
SELECT
    expediente,
    especialidad,
    fecha,
    nota,
    tipo,
    created_at,
    updated_at,
    created_by,
    lab,
    fecha_lab
FROM citas;

DELETE FROM nuevacitas WHERE expediente IS NULL;

UPDATE nuevacitas
SET
    especialidad = CASE
        WHEN especialidad = 0 THEN NULL
        WHEN especialidad = 9 THEN 1
        ELSE especialidad
    END
WHERE
    especialidad IN (0, 9);

UPDATE nuevacitas
SET
    tipo = CASE
        WHEN tipo = 0 THEN 1
        WHEN tipo = 9 THEN 1
        WHEN tipo = 8 THEN 3
        ELSE tipo
    END
WHERE
    tipo IN (0, 9);

CREATE INDEX idx_nuevacitas_expediente ON nuevacitas (expediente);

CREATE INDEX idx_nuevaexpediente_expediente ON nuevaexpediente (expediente);

UPDATE nuevacitas nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.paciente_id = ne.paciente_id
WHERE
    nc.expediente IS NOT NULL;