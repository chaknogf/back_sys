-- Actualizar valores nulos o incorrectos en las tablas existentes
UPDATE medicos SET especialidad = NULL WHERE especialidad = 0;

UPDATE usuarios SET rol = 4 WHERE rol = 0;

-- DELETE FROM medicos WHERE colegiado = 0;

-- Crear la nueva tabla
CREATE TABLE nuevausuario (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(10) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    contraseña VARCHAR(255) NOT NULL,
    dpi BIGINT UNIQUE DEFAULT NULL,
    rol INT NOT NULL,
    created_at DATETIME,
    updated_at DATETIME
) ENGINE = InnoDB CHARSET = utf8mb4;

-- Insertar datos desde la tabla 'usuarios' en la nueva tabla
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

-- Crear la nueva tabla 'nuevamedicos'
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

-- Insertar datos desde la tabla 'medicos' en 'nuevamedicos'
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

CREATE TABLE nueva_rn (
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
    partida INT DEFAULT NULL,
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

-- Inserción en la nueva tabla
INSERT INTO
    nueva_rn (
        id,
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
    id,
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

-- Actualización de madre_id
UPDATE nueva_rn nr
JOIN nuevapaciente np ON nr.expediente = np.expediente
SET
    nr.madre_id = np.paciente_id;

-- Actualización de rn_id
UPDATE nueva_rn nr
JOIN nuevapaciente np ON nr.expediente = np.exp_madre
SET
    nr.rn_id = np.paciente_id;