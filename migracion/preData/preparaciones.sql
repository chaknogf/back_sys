INSERT INTO
    union_old (
        expediente,
        nombre,
        apellido,
        nombre_completo,
        sexo,
        dpi,
        nacimiento,
        direccion,
        telefono,
        responsable,
        parentesco,
        paciente_id,
        pasaporte,
        nacionalidad,
        lugar_nacimiento,
        estado_civil,
        educacion,
        pueblo,
        idioma,
        ocupacion,
        email,
        padre,
        madre,
        dpi_responsable,
        telefono_responsable,
        estado,
        exp_madre,
        gemelo,
        conyugue,
        defuncion,
        exp_ref,
        updated_at,
        created_at,
        created_by
    )
SELECT
    expediente,
    nombre,
    apellido,
    nombre_completo,
    sexo,
    dpi,
    nacimiento,
    direccion,
    telefono,
    responsable,
    parentesco,
    paciente_id,
    pasaporte,
    nacionalidad,
    lugar_nacimiento,
    estado_civil,
    educacion,
    pueblo,
    idioma,
    ocupacion,
    email,
    padre,
    madre,
    dpi_responsable,
    telefono_responsable,
    estado,
    exp_madre,
    gemelo,
    conyugue,
    defuncion,
    exp_ref,
    updated_at,
    created_at,
    created_by
FROM old_pacientes;

INSERT INTO
    union_old (
        expediente,
        nombre,
        apellido,
        nombre_completo,
        sexo,
        dpi,
        nacimiento,
        direccion,
        telefono,
        created_at,
        updated_at,
        responsable,
        hoja_emergencia,
        fecha_consulta,
        hora,
        edad,
        nota,
        especialidad,
        servicio,
        status,
        egreso,
        recepcion,
        tipo_consulta,
        prenatal,
        lactancia,
        diagnostico,
        folios,
        medico,
        created_by,
        consulta_por,
        archivado_por
    )
SELECT
    expediente,
    nombre,
    apellido,
    nombre_completo,
    sexo,
    dpi,
    nacimiento,
    direccion,
    telefono,
    created_at,
    updated_at,
    responsable,
    hoja_emergencia,
    fecha_consulta,
    hora,
    edad,
    nota,
    especialidad,
    servicio,
    status,
    egreso,
    recepcion,
    tipo_consulta,
    prenatal,
    lactancia,
    diagnostico,
    folios,
    medico,
    created_by,
    consulta_por,
    archivado_por
FROM old_consultas;

CREATE TABLE nuevapaciente (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    expediente INT DEFAULT NULL,
    nombre VARCHAR(50) DEFAULT NULL,
    apellido VARCHAR(50) DEFAULT NULL,
    nombre_completo VARCHAR(150) DEFAULT NULL,
    sexo VARCHAR(2) DEFAULT NULL,
    dpi VARCHAR(20) DEFAULT NULL,
    nacimiento DATE DEFAULT NULL,
    direccion VARCHAR(100) DEFAULT NULL,
    telefono VARCHAR(50) DEFAULT NULL,
    responsable VARCHAR(50) DEFAULT NULL,
    parentesco VARCHAR(19) DEFAULT NULL,
    paciente_id VARCHAR(50) DEFAULT NULL,
    pasaporte VARCHAR(50) DEFAULT NULL,
    nacionalidad INT DEFAULT NULL,
    lugar_nacimiento VARCHAR(4) DEFAULT NULL,
    estado_civil INT DEFAULT NULL,
    educacion INT DEFAULT NULL,
    pueblo INT DEFAULT NULL,
    idioma INT DEFAULT NULL,
    ocupacion VARCHAR(50) DEFAULT NULL,
    email VARCHAR(100) DEFAULT NULL,
    padre VARCHAR(50) DEFAULT NULL,
    madre VARCHAR(50) DEFAULT NULL,
    dpi_responsable BIGINT DEFAULT NULL,
    telefono_responsable VARCHAR(18) DEFAULT NULL,
    estado VARCHAR(2) DEFAULT NULL,
    exp_madre VARCHAR(20) DEFAULT NULL,
    gemelo VARCHAR(2) DEFAULT NULL,
    conyugue VARCHAR(100) DEFAULT NULL,
    defuncion VARCHAR(10) DEFAULT NULL,
    exp_ref INT DEFAULT NULL,
    updated_at DATETIME DEFAULT NULL,
    created_at DATETIME DEFAULT NULL,
    created_by VARCHAR(11) DEFAULT NULL,
    consulta_id VARCHAR(15) DEFAULT NULL,
    hoja_emergencia VARCHAR(15) DEFAULT NULL,
    fecha_consulta DATE DEFAULT NULL,
    hora TIME DEFAULT NULL,
    edad VARCHAR(200) DEFAULT NULL,
    nota TEXT NULL,
    especialidad INT DEFAULT NULL,
    servicio INT DEFAULT NULL,
    status INT DEFAULT NULL,
    egreso DATETIME DEFAULT NULL,
    recepcion DATETIME DEFAULT NULL,
    tipo_consulta INT DEFAULT NULL,
    prenatal INT DEFAULT NULL,
    lactancia VARCHAR(2) DEFAULT NULL,
    diagnostico VARCHAR(100) DEFAULT NULL,
    folios VARCHAR(25) DEFAULT NULL,
    medico VARCHAR(100) DEFAULT NULL,
    consulta_por INT DEFAULT NULL,
    archivado_por VARCHAR(10) DEFAULT NULL
) ENGINE = InnoDB CHARSET = utf8mb4;

INSERT INTO
    nuevapaciente (
        nombre,
        apellido,
        nombre_completo,
        sexo,
        dpi,
        nacimiento,
        direccion,
        telefono,
        responsable,
        parentesco,
        pasaporte,
        nacionalidad,
        lugar_nacimiento,
        estado_civil,
        educacion,
        pueblo,
        idioma,
        ocupacion,
        email,
        padre,
        madre,
        dpi_responsable,
        telefono_responsable,
        estado,
        exp_madre,
        gemelo,
        conyugue,
        defuncion,
        exp_ref,
        updated_at,
        created_at,
        created_by
    )
SELECT
    MIN(nombre) AS nombre,
    MIN(apellido) AS apellido,
    nombre_completo,
    MIN(sexo) AS sexo,
    MIN(dpi) AS dpi,
    MIN(nacimiento) AS nacimiento,
    MIN(direccion) AS direccion,
    MIN(telefono) AS telefono,
    MIN(responsable) AS responsable,
    MIN(parentesco) AS parentesco,
    MIN(pasaporte) AS pasaporte,
    MIN(nacionalidad) AS nacionalidad,
    MIN(lugar_nacimiento) AS lugar_nacimiento,
    MIN(estado_civil) AS estado_civil,
    MIN(educacion) AS educacion,
    MIN(pueblo) AS pueblo,
    MIN(idioma) AS idioma,
    MIN(ocupacion) AS ocupacion,
    MIN(email) AS email,
    MIN(padre) AS padre,
    MIN(madre) AS madre,
    MIN(dpi_responsable) AS dpi_responsable,
    MIN(telefono_responsable) AS telefono_responsable,
    MIN(estado) AS estado,
    MIN(exp_madre) AS exp_madre,
    MIN(gemelo) AS gemelo,
    MIN(conyugue) AS conyugue,
    MIN(defuncion) AS defuncion,
    MIN(exp_ref) AS exp_ref,
    MIN(updated_at) AS updated_at,
    MIN(created_at) AS created_at,
    MIN(created_by) AS created_by
FROM union_old
GROUP BY
    nombre_completo;

UPDATE union_old SET paciente_id = NULL;

CREATE INDEX idx_nombre_completo_nuevapaciente ON nuevapaciente (nombre_completo);

CREATE INDEX idx_nombre_completo_union_old ON union_old (nombre_completo);

CREATE INDEX idx_nombre_completo_old_pacientes ON old_pacientes (nombre_completo);

CREATE INDEX idx_nombre_completo_old_consultas ON old_consultas (nombre_completo);

ALTER TABLE old_pacientes MODIFY paciente_id BIGINT;

ALTER TABLE old_consultas MODIFY paciente_id BIGINT;

UPDATE union_old uo
JOIN nuevapaciente np ON uo.nombre_completo = np.nombre_completo
SET
    uo.paciente_id = np.id;

UPDATE old_pacientes uo
JOIN nuevapaciente np ON uo.nombre_completo = np.nombre_completo
SET
    uo.paciente_id = np.id;

UPDATE old_consultas uo
JOIN nuevapaciente np ON uo.nombre_completo = np.nombre_completo
SET
    uo.paciente_id = np.id;

UPDATE nuevapaciente np
JOIN union_old uo ON np.id = uo.paciente_id
SET
    np.dpi = COALESCE(np.dpi, uo.dpi),
    np.nacimiento = COALESCE(np.nacimiento, uo.nacimiento);

CREATE TABLE temp_union_old AS
SELECT
    nombre_completo,
    MAX(expediente) AS expediente,
    paciente_id,
    MIN(expediente) AS exp_ref,
    MAX(exp_madre) AS exp_madre
FROM union_old
GROUP BY
    paciente_id,
    nombre_completo;

CREATE TABLE nuevaconsulta (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    expediente INT DEFAULT NULL,
    nombre VARCHAR(50) DEFAULT NULL,
    apellido VARCHAR(50) DEFAULT NULL,
    nombre_completo VARCHAR(150) DEFAULT NULL,
    sexo VARCHAR(2) DEFAULT NULL,
    dpi VARCHAR(20) DEFAULT NULL,
    nacimiento DATE DEFAULT NULL,
    direccion VARCHAR(100) DEFAULT NULL,
    telefono VARCHAR(50) DEFAULT NULL,
    responsable VARCHAR(50) DEFAULT NULL,
    parentesco VARCHAR(19) DEFAULT NULL,
    paciente_id VARCHAR(50) DEFAULT NULL,
    pasaporte VARCHAR(50) DEFAULT NULL,
    nacionalidad INT DEFAULT NULL,
    lugar_nacimiento VARCHAR(4) DEFAULT NULL,
    estado_civil INT DEFAULT NULL,
    educacion INT DEFAULT NULL,
    pueblo INT DEFAULT NULL,
    idioma INT DEFAULT NULL,
    ocupacion VARCHAR(50) DEFAULT NULL,
    email VARCHAR(100) DEFAULT NULL,
    padre VARCHAR(50) DEFAULT NULL,
    madre VARCHAR(50) DEFAULT NULL,
    dpi_responsable BIGINT DEFAULT NULL,
    telefono_responsable VARCHAR(18) DEFAULT NULL,
    estado VARCHAR(2) DEFAULT NULL,
    exp_madre VARCHAR(20) DEFAULT NULL,
    gemelo VARCHAR(2) DEFAULT NULL,
    conyugue VARCHAR(100) DEFAULT NULL,
    defuncion VARCHAR(10) DEFAULT NULL,
    exp_ref INT DEFAULT NULL,
    updated_at DATETIME DEFAULT NULL,
    created_at DATETIME DEFAULT NULL,
    created_by VARCHAR(11) DEFAULT NULL,
    consulta_id VARCHAR(15) DEFAULT NULL,
    hoja_emergencia VARCHAR(15) DEFAULT NULL,
    fecha_consulta DATE DEFAULT NULL,
    hora TIME DEFAULT NULL,
    edad VARCHAR(200) DEFAULT NULL,
    nota TEXT NULL,
    especialidad INT DEFAULT NULL,
    servicio INT DEFAULT NULL,
    status INT DEFAULT NULL,
    egreso DATETIME DEFAULT NULL,
    recepcion DATETIME DEFAULT NULL,
    tipo_consulta INT DEFAULT NULL,
    prenatal INT DEFAULT NULL,
    lactancia VARCHAR(2) DEFAULT NULL,
    diagnostico VARCHAR(100) DEFAULT NULL,
    folios VARCHAR(25) DEFAULT NULL,
    medico VARCHAR(100) DEFAULT NULL,
    consulta_por INT DEFAULT NULL,
    archivado_por VARCHAR(10) DEFAULT NULL
) ENGINE = InnoDB CHARSET = utf8mb4;

INSERT INTO
    nuevaconsulta (
        consulta_id, -- Ahora toma el valor de "id" de la tabla "union_old"
        nombre,
        apellido,
        nombre_completo,
        sexo,
        dpi,
        nacimiento,
        direccion,
        telefono,
        responsable,
        parentesco,
        pasaporte,
        nacionalidad,
        lugar_nacimiento,
        estado_civil,
        educacion,
        pueblo,
        idioma,
        ocupacion,
        email,
        padre,
        madre,
        dpi_responsable,
        telefono_responsable,
        estado,
        exp_madre,
        gemelo,
        conyugue,
        defuncion,
        exp_ref,
        updated_at,
        created_at,
        created_by,
        paciente_id,
        hoja_emergencia,
        expediente
    )
SELECT
    id AS consulta_id, -- Toma el valor directamente de "union_old.id"
    nombre,
    apellido,
    nombre_completo,
    sexo,
    dpi,
    nacimiento,
    direccion,
    telefono,
    responsable,
    parentesco,
    pasaporte,
    nacionalidad,
    lugar_nacimiento,
    estado_civil,
    educacion,
    pueblo,
    idioma,
    ocupacion,
    email,
    padre,
    madre,
    dpi_responsable,
    telefono_responsable,
    estado,
    exp_madre,
    gemelo,
    conyugue,
    defuncion,
    exp_ref,
    updated_at,
    created_at,
    created_by,
    paciente_id,
    hoja_emergencia,
    expediente
FROM union_old
WHERE
    tipo_consulta IS NOT NULL;

-- UPDATE nuevaconsulta SET consulta_id = NULL;

-- UPDATE union_old SET consulta_id = NULL;

CREATE INDEX idx_nombre_completo_u ON nuevaconsulta (nombre_completo);

CREATE TABLE nuevaexpediente (
    id INT PRIMARY KEY,
    expediente VARCHAR(15) UNIQUE DEFAULT NULL,
    hoja_emergencia VARCHAR(15) UNIQUE DEFAULT NULL,
    paciente_id INT DEFAULT NULL,
    consulta_id INT DEFAULT NULL,
    exp_madre INT DEFAULT NULL,
    created_at DATETIME DEFAULT NULL,
    exp_ref INT DEFAULT NULL,
    nombre_completo VARCHAR(125) DEFAULT NULL
) ENGINE = InnoDB CHARSET = utf8mb4;

CREATE TABLE noemergencia AS
SELECT
    NULL AS hoja_emergencia,
    expediente,
    paciente_id,
    exp_madre,
    created_at,
    exp_ref,
    id AS id,
    nombre_completo
FROM union_old
WHERE
    tipo_consulta IS NULL;

ALTER TABLE noemergencia ENGINE = InnoDB, DEFAULT CHARSET = utf8mb4;

CREATE TABLE siemergencia AS
SELECT
    NULL AS expediente,
    hoja_emergencia,
    paciente_id,
    exp_madre,
    created_at,
    expediente AS exp_ref,
    id AS id,
    nombre_completo
FROM union_old
WHERE
    tipo_consulta IS NOT NULL;

ALTER TABLE siemergencia ENGINE = InnoDB, DEFAULT CHARSET = utf8mb4;

INSERT INTO
    nuevaexpediente (
        expediente,
        hoja_emergencia,
        paciente_id,
        id,
        exp_madre,
        created_at,
        exp_ref,
        nombre_completo
    )
SELECT
    expediente,
    hoja_emergencia,
    paciente_id,
    id,
    exp_madre,
    created_at,
    exp_ref,
    nombre_completo
FROM noemergencia;

INSERT INTO
    nuevaexpediente (
        expediente,
        hoja_emergencia,
        paciente_id,
        id,
        exp_madre,
        created_at,
        exp_ref,
        nombre_completo
    )
SELECT
    expediente,
    hoja_emergencia,
    paciente_id,
    id,
    exp_madre,
    created_at,
    exp_ref,
    nombre_completo
FROM siemergencia;

CREATE INDEX idx_paciente_id_expediente ON nuevaexpediente (paciente_id, expediente);

CREATE INDEX idx_paciente_id ON nuevaconsulta (paciente_id);
-- Índices en la tabla nuevaconsulta
CREATE INDEX idx_expediente_nuevaconsulta ON nuevaconsulta (expediente);

CREATE INDEX idx_hoja_emergencia_nuevaconsulta ON nuevaconsulta (hoja_emergencia);

-- Índices en la tabla nuevaexpediente
CREATE INDEX idx_expediente_nuevaexpediente ON nuevaexpediente (expediente);

CREATE INDEX idx_hoja_emergencia_nuevaexpediente ON nuevaexpediente (hoja_emergencia);

UPDATE nuevaexpediente ne
JOIN temp_union_old tuo ON ne.id = tuo.paciente_id
SET
    ne.expediente = tuo.expediente,
    ne.exp_madre = tuo.exp_madre,
    ne.exp_ref = tuo.exp_ref
WHERE
    ne.expediente IS NULL;