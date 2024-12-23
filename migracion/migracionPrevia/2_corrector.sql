UPDATE pacientes
SET
    nombre = UPPER(nombre),
    apellido = UPPER(apellido);

UPDATE consultas
set
    nombres = UPPER(nombres),
    apellidos = UPPER(apellidos);

-- Eliminar espacios al principio, al final y reducir múltiples espacios intermedios

UPDATE pacientes
SET
    nombre = TRIM(
        REPLACE (
                REPLACE (
                        REPLACE (nombre, '    ', ' '),
                            '   ',
                            ' '
                    ),
                    '  ',
                    ' '
            )
    ),
    apellido = TRIM(
        REPLACE (
                REPLACE (
                        REPLACE (apellido, '    ', ' '),
                            '   ',
                            ' '
                    ),
                    '  ',
                    ' '
            )
    )
WHERE
    nombre LIKE '%  %'
    OR apellido LIKE '%  %';

UPDATE consultas
SET
    nombres = TRIM(
        REPLACE (
                REPLACE (
                        REPLACE (nombres, '    ', ' '),
                            '   ',
                            ' '
                    ),
                    '  ',
                    ' '
            )
    ),
    apellidos = TRIM(
        REPLACE (
                REPLACE (
                        REPLACE (apellidos, '    ', ' '),
                            '   ',
                            ' '
                    ),
                    '  ',
                    ' '
            )
    )
WHERE
    nombres LIKE '%  %'
    OR apellidos LIKE '%  %';

UPDATE cons_nac
SET
    madre = TRIM(
        REPLACE (
                REPLACE (
                        REPLACE (madre, '    ', ' '),
                            '   ',
                            ' '
                    ),
                    '  ',
                    ' '
            )
    )
WHERE
    madre LIKE '%  %';

UPDATE pacientes
SET
    nombre = TRIM(nombre),
    apellido = TRIM(apellido);

UPDATE consultas
SET
    nombres = TRIM(nombres),
    apellidos = TRIM(apellidos);

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
    fechaDefuncion IN ('string', '');

CREATE TABLE old_pacientes AS
SELECT
    id,
    expediente,
    nombre,
    apellido,
    CONCAT_WS(' ', nombre, apellido) AS nombre_completo,
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
    CONCAT_WS(' ', nombres, apellidos) AS nombre_completo,
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
    CONCAT_WS(' ', medico, nota) AS nota,
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

CREATE INDEX idx_old_consultas_id ON old_consultas (id);

ALTER TABLE old_consultas ENGINE = InnoDB, DEFAULT CHARSET = utf8mb4;

DELETE FROM old_consultas WHERE nombre_completo LIKE '%anula%';

DELETE FROM old_consultas WHERE nombre_completo = '';

ALTER TABLE old_pacientes MODIFY COLUMN nacionalidad VARCHAR(3);

UPDATE old_pacientes
SET
    nacionalidad = CASE
        WHEN nacionalidad = 1 THEN 'GTM'
        WHEN nacionalidad = 2 THEN 'BLZ'
        WHEN nacionalidad = 3 THEN 'SLV'
        WHEN nacionalidad = 4 THEN 'HND'
        WHEN nacionalidad = 5 THEN 'NIC'
        WHEN nacionalidad = 6 THEN 'CRI'
        WHEN nacionalidad = 7 THEN 'PAN'
        WHEN nacionalidad = 8 THEN 'MEX'
        WHEN nacionalidad = 9 THEN 'OTR'
        WHEN nacionalidad = 0 THEN NULL
        ELSE nacionalidad
    END;

UPDATE old_consultas oc
JOIN old_pacientes op ON oc.expediente = op.expediente
SET
    oc.nombre = op.nombre,
    oc.apellido = op.apellido,
    oc.nombre_completo = op.nombre_completo,
    oc.nota = 'paciente ingresado como xx xx'
WHERE
    op.expediente IN (72539, 73387, 65660);

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

DELETE FROM union_old
WHERE
    expediente IS NULL
    AND hoja_emergencia IS NULL;

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
    nota = CONCAT_WS(
        ' ',
        nombre_completo,
        nota,
        medico
    ),
    nombre = 'xx',
    apellido = 'xx',
    expediente = NULL,
    nombre_completo = 'xx xx'
WHERE
    nombre_completo LIKE '%xx%';

update union_old set gemelo = NULL where gemelo = 'no';

update union_old set gemelo = NULL where gemelo = '';

update union_old set gemelo = 1 where gemelo = 'si';

UPDATE union_old SET paciente_id = NULL;

UPDATE union_old SET consulta_id = NULL;

UPDATE union_old
SET
    nombre = TRIM(nombre),
    apellido = TRIM(apellido),
    nombre_completo = TRIM(nombre_completo);