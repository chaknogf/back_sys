DROP Table IF EXISTS union_old;

DROP Table IF EXISTS noemergencia;

DROP Table IF EXISTS siemergencia;

DROP TABLE IF EXISTS nuevaexpediente;

DROP TABLE IF EXISTS nuevaconsulta;

DROP TABLE IF EXISTS nuevapaciente;

DROP Table IF EXISTS xxx;

DROP TABLE IF EXISTS old_consultas;

DROP TABLE IF EXISTS old_pacientes;

DROP TABLE IF EXISTS temp_duplicados;

UPDATE pacientes
SET
    lugar_nacimiento = NULL
WHERE
    lugar_nacimiento = '0000';

UPDATE pacientes SET parentesco = NULL WHERE parentesco = 0;

UPDATE pacientes SET dpi = NULL WHERE dpi = '';

UPDATE consultas SET dpi = NULL WHERE dpi = '';

SELECT dpi
FROM pacientes
WHERE
    dpi IS NOT NULL
    AND (
        LENGTH(dpi) != 13
        OR dpi NOT REGEXP '^[0-9]+$'
    );

SELECT dpi
FROM consultas
WHERE
    dpi IS NOT NULL
    AND (
        LENGTH(dpi) != 13
        OR dpi NOT REGEXP '^[0-9]+$'
    );

UPDATE pacientes
SET
    dpi = NULL
WHERE
    dpi IS NOT NULL
    AND (
        LENGTH(dpi) != 13
        OR dpi NOT REGEXP '^[0-9]+$'
    );

UPDATE consultas
SET
    dpi = NULL
WHERE
    dpi IS NOT NULL
    AND (
        LENGTH(dpi) != 13
        OR dpi NOT REGEXP '^[0-9]+$'
    );

UPDATE pacientes
SET
    fechaDefuncion = NULL
WHERE
    fechaDefuncion = "string";

UPDATE pacientes
SET
    fechaDefuncion = NULL
WHERE
    fechaDefuncion = "string";

UPDATE pacientes SET fechaDefuncion = NULL WHERE fechaDefuncion = "";

CREATE TABLE union_old (
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

CREATE TABLE xxx (
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

CREATE TABLE old_pacientes AS
SELECT
    id,
    expediente,
    nombre,
    apellido,
    CONCAT(
        COALESCE(nombre, ''),
        ' ',
        COALESCE(apellido, '')
    ) AS nombre_completo,
    sexo,
    dpi,
    nacimiento,
    direccion,
    telefono,
    responsable,
    parentesco,
    id AS paciente_id,
    pasaporte,
    nacionalidad,
    LPAD(
        CAST(lugar_nacimiento AS CHAR),
        4,
        '0'
    ) AS lugar_nacimiento,
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
    fechaDefuncion AS defuncion,
    exp_ref,
    update_at AS updated_at,
    created_at,
    created_by,
    NULL AS consulta_id,
    NULL AS hoja_emergencia,
    NULL AS fecha_consulta,
    NULL AS hora,
    NULL AS edad,
    NULL AS nota,
    NULL AS especialidad,
    NULL AS servicio,
    NULL AS status,
    NULL AS egreso,
    NULL AS recepcion,
    NULL AS tipo_consulta,
    NULL AS prenatal,
    NULL AS lactancia,
    NULL AS diagnostico,
    NULL AS folios,
    NULL AS medico,
    NULL AS consulta_por,
    NULL AS archivado_por
FROM pacientes;

ALTER TABLE old_pacientes ENGINE = InnoDB, DEFAULT CHARSET = utf8mb4;

CREATE TABLE old_consultas AS
SELECT
    id,
    expediente,
    nombres AS nombre,
    apellidos AS apellido,
    CONCAT(
        COALESCE(nombres, ''),
        ' ',
        COALESCE(apellidos, '')
    ) AS nombre_completo,
    sexo,
    dpi,
    nacimiento,
    direccion,
    telefono,
    created_at,
    updated_at,
    acompa AS responsable,
    NULL AS parentesco,
    NULL AS paciente_id,
    NULL AS pasaporte,
    NULL AS nacionalidad,
    NULL AS lugar_nacimiento,
    NULL AS estado_civil,
    NULL AS educacion,
    NULL AS pueblo,
    NULL AS idioma,
    NULL AS ocupacion,
    NULL AS email,
    NULL AS padre,
    NULL AS madre,
    NULL AS dpi_responsable,
    NULL AS telefono_responsable,
    NULL AS estado,
    NULL AS exp_madre,
    NULL AS gemelo,
    NULL AS conyugue,
    NULL AS defuncion,
    NULL AS exp_ref,
    id AS consulta_id,
    hoja_emergencia,
    fecha_consulta,
    hora,
    edad,
    CONCAT(
        COALESCE(medico, ''),
        ' ',
        COALESCE(nota, '')
    ) AS nota,
    especialidad,
    servicio,
    status,
    fecha_egreso AS egreso,
    fecha_recepcion AS recepcion,
    tipo_consulta,
    prenatal,
    lactancia,
    dx AS diagnostico,
    folios,
    NULL AS medico,
    created_by,
    consulta_por,
    archived_by AS archivado_por
FROM consultas;

ALTER TABLE old_consultas ENGINE = InnoDB, DEFAULT CHARSET = utf8mb4;

DELETE FROM old_consultas WHERE nombre_completo = '';

UPDATE old_consultas oc
JOIN old_pacientes op ON oc.expediente = op.expediente
SET
    oc.nombre = op.nombre,
    oc.apellido = op.apellido,
    oc.nombre_completo = op.nombre_completo,
    oc.nota = 'paciente ingresado como xx xx'
WHERE
    op.expediente = 72539;

UPDATE old_consultas oc
JOIN old_pacientes op ON oc.expediente = op.expediente
SET
    oc.nombre = op.nombre,
    oc.apellido = op.apellido,
    oc.nombre_completo = op.nombre_completo,
    oc.nota = 'paciente ingresado como xx xx'
WHERE
    op.expediente = 73387;

UPDATE old_consultas oc
JOIN old_pacientes op ON oc.expediente = op.expediente
SET
    oc.nombre = op.nombre,
    oc.apellido = op.apellido,
    oc.nombre_completo = op.nombre_completo,
    oc.nota = 'paciente ingresado como xx xx'
WHERE
    op.expediente = 65660;

CREATE TEMPORARY TABLE temp_duplicados AS
SELECT id, hoja_emergencia, ROW_NUMBER() OVER (
        PARTITION BY
            hoja_emergencia
        ORDER BY nombre_completo
    ) AS row_num
FROM old_consultas
WHERE
    tipo_consulta = 3
    AND hoja_emergencia IN (
        SELECT hoja_emergencia
        FROM old_consultas
        WHERE
            tipo_consulta = 3
        GROUP BY
            hoja_emergencia
        HAVING
            COUNT(*) > 1
    );

CREATE INDEX idx_old_consultas_id ON old_consultas (id);

CREATE INDEX idx_temp_duplicados_id ON temp_duplicados (id);

UPDATE old_consultas e
JOIN temp_duplicados t ON e.id = t.id
SET
    e.hoja_emergencia = CASE
        WHEN t.row_num = 1 THEN e.hoja_emergencia
        ELSE CONCAT(
            e.hoja_emergencia,
            CHAR(64 + t.row_num)
        )
    END
WHERE
    t.row_num <= 26;

INSERT INTO
    xxx (
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
        consulta_id,
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
    consulta_id,
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
FROM old_consultas
WHERE
    nombre_completo LIKE '%xx%';

INSERT INTO
    xxx (
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
FROM old_pacientes
WHERE
    nombre_completo LIKE '%xx%';

UPDATE old_consultas
SET
    nota = CONCAT(
        COALESCE(nombre_completo, ''),
        ' ',
        COALESCE(nota, ''),
        ' ',
        COALESCE(medico, ' ')
    ),
    nombre = 'xx',
    apellido = 'xx',
    expediente = NULL,
    nombre_completo = 'xx xx'
WHERE
    nombre_completo LIKE '%xx%';

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
        consulta_id,
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
    consulta_id,
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
SELECT DISTINCT
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
FROM union_old
WHERE
    nombre_completo IS NOT NULL;

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
FROM union_old
WHERE
    consulta_id IS NOT NULL;

UPDATE nuevaconsulta SET consulta_id = NULL;

UPDATE union_old SET consulta_id = NULL;

CREATE INDEX idx_nombre_completo ON nuevapaciente (nombre_completo);

CREATE INDEX idx_nombre_completo_u ON nuevaconsulta (nombre_completo);

UPDATE nuevaconsulta u
JOIN nuevapaciente np ON u.nombre_completo = np.nombre_completo
SET
    u.paciente_id = np.id;

CREATE TABLE nuevaexpediente (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
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
    consulta_id,
    nombre_completo
FROM old_pacientes;

ALTER TABLE noemergencia ENGINE = InnoDB, DEFAULT CHARSET = utf8mb4;

UPDATE noemergencia u
JOIN nuevapaciente np ON u.nombre_completo = np.nombre_completo
SET
    u.paciente_id = np.id;

CREATE TABLE siemergencia AS
SELECT
    NULL AS expediente,
    hoja_emergencia,
    paciente_id,
    exp_madre,
    created_at,
    expediente AS exp_ref,
    consulta_id,
    nombre_completo
FROM old_consultas;

ALTER TABLE siemergencia ENGINE = InnoDB, DEFAULT CHARSET = utf8mb4;

ALTER TABLE siemergencia MODIFY paciente_id BIGINT;

UPDATE siemergencia u
JOIN nuevapaciente np ON u.nombre_completo = np.nombre_completo
SET
    u.paciente_id = np.id;

INSERT INTO
    nuevaexpediente (
        expediente,
        hoja_emergencia,
        paciente_id,
        consulta_id,
        exp_madre,
        created_at,
        exp_ref,
        nombre_completo
    )
SELECT
    expediente,
    hoja_emergencia,
    paciente_id,
    consulta_id,
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
        consulta_id,
        exp_madre,
        created_at,
        exp_ref,
        nombre_completo
    )
SELECT
    expediente,
    hoja_emergencia,
    paciente_id,
    consulta_id,
    exp_madre,
    created_at,
    exp_ref,
    nombre_completo
FROM siemergencia;

CREATE INDEX idx_paciente_id_expediente ON nuevaexpediente (paciente_id, expediente);

CREATE INDEX idx_paciente_id ON nuevaconsulta (paciente_id);

UPDATE nuevaexpediente ne
JOIN nuevapaciente np ON ne.nombre_completo = np.nombre_completo
SET
    ne.paciente_id = np.id;

UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.paciente_id = ne.paciente_id
SET
    nc.consulta_id = ne.id;