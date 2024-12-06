DROP TABLE IF EXISTS union_old,
noemergencia,
siemergencia,
nuevaexpediente,
nuevaconsulta,
nuevapaciente,
xxx,
old_consultas,
old_pacientes,
temp_duplicados,
nuevacitas,
nuevamedicos,
nuevausuario,
nuevarn,
temp_union_old,
sin_rn,
filtro_rn;

-- Eliminar espacios al principio, al final y reducir múltiples espacios intermedios a uno en `pacientes`
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

-- Eliminar espacios al principio, al final y reducir múltiples espacios intermedios a uno en `consultas`
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