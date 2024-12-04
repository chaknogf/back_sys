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

UPDATE medicos SET especialidad = NULL WHERE especialidad = 0;

UPDATE usuarios SET rol = 4 WHERE rol = 0;

UPDATE usuarios SET dpi = NULL WHERE dpi = 0;

DELETE FROM medicos WHERE colegiado = 0;

CREATE TABLE nuevausuario (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(10) UNIQUE NOT NULL,
    nombre VARCHAR(100) DEFAULT NULL,
    email VARCHAR(100) DEFAULT NULL,
    contraseña VARCHAR(255) DEFAULT NULL,
    dpi BIGINT UNIQUE DEFAULT NULL,
    rol INT NOT NULL,
    created_at DATETIME,
    updated_at DATETIME
) ENGINE = InnoDB CHARSET = utf8mb4;

CREATE TABLE nuevamedicos (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, -- Hacemos que sea autoincremental
    colegiado INT NOT NULL,
    nombre VARCHAR(200) DEFAULT NULL,
    dpi BIGINT DEFAULT NULL,
    especialidad INT DEFAULT NULL,
    pasaporte VARCHAR(30) DEFAULT NULL,
    sexo ENUM('M', 'F') DEFAULT NULL,
    created_at DATETIME,
    updated_at DATETIME
) ENGINE = InnoDB CHARSET = utf8mb4;

CREATE TABLE nuevarn (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    fecha DATE DEFAULT NULL,
    cor INT DEFAULT NULL,
    ao INT DEFAULT NULL,
    doc VARCHAR(12) DEFAULT NULL UNIQUE,
    fecha_parto DATE DEFAULT NULL,
    madre VARCHAR(100) DEFAULT NULL,
    madre_id INT DEFAULT NULL,
    rn_id INT DEFAULT NULL,
    dpi BIGINT DEFAULT NULL,
    passport VARCHAR(30) DEFAULT NULL,
    libro INT DEFAULT NULL,
    folio INT DEFAULT NULL,
    partida VARCHAR(20) DEFAULT NULL,
    depto INT DEFAULT NULL,
    muni INT DEFAULT NULL,
    edad INT DEFAULT NULL,
    vecindad INT DEFAULT NULL,
    sexo_rn VARCHAR(1) DEFAULT NULL,
    lb INT DEFAULT NULL,
    onz INT DEFAULT NULL,
    hora TIME DEFAULT NULL,
    medico VARCHAR(200) DEFAULT NULL,
    colegiado INT DEFAULT NULL,
    dpi_medico BIGINT DEFAULT NULL,
    hijos INT DEFAULT NULL,
    vivos INT DEFAULT NULL,
    muertos INT DEFAULT NULL,
    tipo_parto INT DEFAULT NULL,
    clase_parto INT DEFAULT NULL,
    certifica VARCHAR(200) DEFAULT NULL,
    create_by VARCHAR(10) NULL,
    expediente INT DEFAULT NULL,
    nacionalidad VARCHAR(25) DEFAULT NULL,
    pais VARCHAR(25) DEFAULT NULL,
    created_at DATETIME,
    updated_at DATETIME
) ENGINE = InnoDB CHARSET = utf8mb4;

INSERT INTO
    nuevausuario (
        username,
        nombre,
        email,
        contraseña,
        dpi,
        rol,
        created_at,
        updated_at
    )
SELECT
    username,
    name AS nombre,
    email,
    password AS contraseña,
    dpi,
    rol,
    created_at,
    updated_at
FROM usuarios;

INSERT INTO
    nuevamedicos (
        colegiado,
        nombre,
        dpi,
        especialidad,
        pasaporte,
        sexo,
        created_at,
        updated_at
    )
SELECT
    colegiado,
    name AS nombre,
    dpi,
    especialidad,
    pasaporte,
    sexo,
    created_at,
    updated_at
FROM medicos;

INSERT INTO
    nuevarn (
        fecha,
        cor,
        ao,
        doc,
        fecha_parto,
        madre,
        dpi,
        passport,
        libro,
        folio,
        partida,
        depto,
        muni,
        edad,
        vecindad,
        sexo_rn,
        lb,
        onz,
        hora,
        medico,
        colegiado,
        dpi_medico,
        hijos,
        vivos,
        muertos,
        tipo_parto,
        clase_parto,
        certifica,
        create_by,
        expediente,
        nacionalidad,
        pais,
        created_at,
        updated_at
    )
SELECT
    fecha,
    cor,
    ao,
    doc,
    fecha_parto,
    madre,
    dpi,
    passport,
    libro,
    folio,
    partida,
    depto,
    muni,
    edad,
    vecindad,
    sexo_rn,
    lb,
    onz,
    hora,
    medico,
    colegiado,
    dpi_medico,
    hijos,
    vivos,
    muertos,
    tipo_parto,
    clase_parto,
    certifica,
    create_by,
    expediente,
    nacionalidad,
    pais,
    created_at,
    updated_at
FROM cons_nac;

CREATE INDEX idx_nuevarn_expediente ON nuevarn (expediente);

CREATE INDEX idx_union_old_expediente ON union_old (expediente);

CREATE INDEX idx_union_old_exp_madre ON union_old (exp_madre);

UPDATE nuevarn nr
JOIN union_old np ON nr.expediente = np.expediente
SET
    nr.madre_id = np.paciente_id;

UPDATE nuevarn nr
JOIN union_old np ON nr.expediente = np.exp_madre
SET
    nr.rn_id = np.paciente_id;