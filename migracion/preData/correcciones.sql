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
nuevarn;

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