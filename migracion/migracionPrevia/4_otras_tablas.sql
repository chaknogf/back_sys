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

CREATE INDEX idx_nuevaexpediente_expediente ON expedientes (expediente);

UPDATE nuevacitas nc
JOIN expedientes ne ON nc.expediente = ne.expediente
SET
    nc.paciente_id = ne.paciente_id
WHERE
    nc.expediente IS NOT NULL;

UPDATE medicos SET especialidad = NULL WHERE especialidad = 0;

UPDATE usuarios SET rol = 4 WHERE rol = 0;

UPDATE usuarios SET dpi = NULL WHERE dpi = 0;

DELETE FROM medicos WHERE colegiado = 0;

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
    TRIM(madre) AS madre,
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

DELETE FROM nuevarn
WHERE
    doc IN (
        '0952-2024',
        '1163-2024',
        '1841-2024'
    );

CREATE INDEX idx_nuevarn_expediente ON nuevarn (expediente);

CREATE INDEX idx_union_old_expediente ON union_old (expediente);

CREATE INDEX idx_union_old_exp_madre ON union_old (exp_madre);

CREATE INDEX idx_nuevarn_create_by ON nuevarn (create_by);

CREATE INDEX idx_nuevausuario_username ON nuevausuario (username);

-- Índice para la tabla 'nuevarn' para las columnas madre, expediente, rn_id
CREATE INDEX idx_nuevarn_madre_expediente_rn_id ON nuevarn (madre, expediente, rn_id);

-- Índice para la tabla 'listado_pacientes' para las columnas exp_madre y nacimiento
CREATE INDEX idx_listado_pacientes_exp_madre_nacimiento ON listado_pacientes (exp_madre, nacimiento);

-- Índice para la tabla 'nuevarn' para la columna fecha_parto (si es utilizada)
CREATE INDEX idx_nuevarn_fecha_parto ON nuevarn (fecha_parto);

UPDATE expedientes e
JOIN union_old uo ON e.expediente = uo.exp_madre
SET
    e.exp_madre = uo.exp_madre
WHERE
    e.exp_madre IS NULL;

UPDATE nuevarn nr
JOIN consultas_pacientes cp ON nr.expediente = cp.historia_clinica
SET
    nr.madre_id = cp.paciente_id
WHERE
    nr.madre_id IS NULL;

UPDATE nuevarn nr
JOIN consultas_pacientes cp ON nr.madre LIKE CONCAT('%', cp.nombre_completo, '%')
SET
    nr.madre_id = cp.paciente_id
WHERE
    nr.madre_id IS NULL;

UPDATE nuevarn nr
JOIN listado_pacientes lp ON nr.madre LIKE CONCAT('%', lp.nombre_completo, '%')
SET
    nr.madre_id = lp.id
WHERE
    nr.madre_id IS NULL;

UPDATE nuevarn nr
JOIN expedientes np ON nr.expediente = np.expediente
SET
    nr.madre_id = np.paciente_id
WHERE
    nr.madre_id IS NULL;

UPDATE nuevarn nr
JOIN expedientes np ON nr.expediente = np.exp_ref
SET
    nr.madre_id = np.paciente_id
WHERE
    nr.madre_id IS NULL;

UPDATE nuevarn nr
JOIN expedientes np ON nr.expediente = np.exp_madre
SET
    nr.rn_id = np.paciente_id
WHERE
    nr.rn_id IS NULL;

UPDATE nuevarn nr
JOIN listado_pacientes lp ON nr.expediente = lp.exp_madre
SET
    nr.rn_id = lp.id
WHERE
    nr.rn_id IS NULL;

UPDATE nuevarn nr
JOIN listado_pacientes lp ON nr.expediente = lp.exp_madre
SET
    nr.rn_id = lp.id
WHERE
    nr.rn_id IS NULL;

UPDATE nuevarn nr
JOIN nuevausuario nu ON nr.create_by = nu.username
SET
    nr.usuario_id = nu.id;

CREATE TABLE sin_rn AS
SELECT madre, expediente, rn_id
FROM nuevarn
WHERE
    rn_id IS NULL;

CREATE TABLE filtro_rn AS
SELECT
    m.*,
    e.paciente_id AS paciente_id,
    e.nombre_completo AS nombre_completo
FROM sin_rn m
    JOIN expedientes e ON e.nombre_completo LIKE CONCAT('%', m.madre, '%')
WHERE
    e.nombre_completo LIKE 'hijo de%'
    OR e.nombre_completo LIKE 'hija de%';

UPDATE nuevarn nr
JOIN filtro_rn frn ON nr.expediente = frn.expediente
SET
    nr.rn_id = frn.paciente_id;

CREATE TABLE malos_cons_nac AS
SELECT
    nr.id,
    nr.madre,
    nr.expediente,
    nr.onz,
    nr.madre_id,
    nr.rn_id,
    nr.fecha_parto,
    e.id as paciente_id,
    e.nombre_completo,
    e.nacimiento,
    e.expediente
FROM
    nuevarn nr
    JOIN listado_pacientes e ON nr.expediente = e.exp_madre
WHERE
    nr.rn_id IN (
        SELECT rn_id
        FROM nuevarn
        GROUP BY
            rn_id
        HAVING
            COUNT(rn_id) > 1
    )
ORDER BY nr.rn_id;

DELETE FROM nuevarn WHERE id = 303;

UPDATE nuevarn SET rn_id = 34028 WHERE id = 201;

UPDATE nuevarn SET rn_id = 42157 WHERE id = 1220;

UPDATE nuevarn SET rn_id = 34028 WHERE id = 201;

UPDATE nuevarn SET rn_id = 42157 WHERE id = 1220;

DELETE FROM nuevarn WHERE id = 1219;

UPDATE nuevarn SET rn_id = 42365 WHERE id = 1776;

UPDATE nuevarn SET rn_id = 42365 WHERE id = 1776;

------+------------------------------------------+------------+------+----------+-------+-------------+----------------------------------------+

| id   | madre                                    | expediente | onz  | madre_id | rn_id | paciente_id | nombre_completo                        |
+------+------------------------------------------+------------+------+----------+-------+-------------+----------------------------------------+
| 1997 | Ana Maria Tep� Raxjal                   |      74636 |   14 |     4480 | 39622 |       39622 | HIJA DE ANA MARIA TEPAZ RAXJAL         |
| 1997 | Ana Maria Tep� Raxjal                   |      74636 |   14 |     4480 | 39622 |       39622 | HIJA DE ANA MARIA TEPAZ RAXJAL         |
| 1996 | Ana Maria Tep� Raxjal                   |      74636 |    6 |     4480 | 39622 |       39622 | HIJA DE ANA MARIA TEPAZ RAXJAL         |
| 1996 | Ana Maria Tep� Raxjal                   |      74636 |    6 |     4480 | 39622 |       39622 | HIJA DE ANA MARIA TEPAZ RAXJAL         |
|  393 | Sara Lucia Mux Bala                      |      22145 |    4 |    92164 | 42205 |       92164 | SARA LUCIA MUX BALA                    |
|  393 | Sara Lucia Mux Bala                      |      22145 |    4 |    92164 | 42205 |        4308 | ANA LUISA MUX                          |
|  394 | Sara Lucia Mux Bala                      |      22145 |    4 |    92164 | 42205 |       92164 | SARA LUCIA MUX BALA                    |
|  394 | Sara Lucia Mux Bala                      |      22145 |    4 |    92164 | 42205 |        4308 | ANA LUISA MUX                          |
|  321 | Haidy Esmeralda Socoy Mel�drez          |      65819 |    2 |    37807 | 43824 |       24692 | ELIAN DARIEL CALEL SOCOY               |
|  324 | Haidy Esmeralda Socoy Mel�drez          |      65819 |    2 |    37807 | 43824 |       24692 | ELIAN DARIEL CALEL SOCOY               |
| 1702 | Sebastiana P�ez Morales                 |      70352 |    2 |    92631 | 45544 |       45544 | HIJO DE SEBASTIANA PEREZ MORALES       |
| 1702 | Sebastiana P�ez Morales                 |      70352 |    2 |    92631 | 45544 |       45544 | HIJO DE SEBASTIANA PEREZ MORALES       |
| 1703 | Sebastiana P�ez Morales                 |      70352 |    5 |    92631 | 45544 |       45544 | HIJO DE SEBASTIANA PEREZ MORALES       |
| 1703 | Sebastiana P�ez Morales                 |      70352 |    5 |    92631 | 45544 |       45544 | HIJO DE SEBASTIANA PEREZ MORALES       |
| 1317 | Alida Emiliana Velasquez Jutzutz         |      37592 |    4 |     2493 | 47606 |        2493 | ALIDA EMILIANA VELASQUEZ JUTZUTZ       |
| 1317 | Alida Emiliana Velasquez Jutzutz         |      37592 |    4 |     2493 | 47606 |       47606 | IAN CAMILO ORDO�Z VELASQUEZ           |
| 1317 | Alida Emiliana Velasquez Jutzutz         |      37592 |    4 |     2493 | 47606 |       26763 | EMILI BELEN ORDO�Z VELASQUEZ          |
| 1318 | Alida Emiliana Velasquez Jutzutz         |      37592 |    3 |     2493 | 47606 |        2493 | ALIDA EMILIANA VELASQUEZ JUTZUTZ       |
| 1318 | Alida Emiliana Velasquez Jutzutz         |      37592 |    3 |     2493 | 47606 |       47606 | IAN CAMILO ORDO�Z VELASQUEZ           |
| 1318 | Alida Emiliana Velasquez Jutzutz         |      37592 |    3 |     2493 | 47606 |       26763 | EMILI BELEN ORDO�Z VELASQUEZ          |
|  719 | Juana Juliana Morales Algua              |      69025 |    1 |    58042 | 57931 |       40938 | JUANA EMILIANA VALERIA LASTOR MORALES  |
|  718 | Juana Juliana Morales Algua              |      69025 |    1 |    58042 | 57931 |       40938 | JUANA EMILIANA VALERIA LASTOR MORALES  |
| 1633 | Mariana Ang�ica Chut�Tart� De Cuxil   |      36297 |   11 |    74377 | 74377 |       74377 | MARIANA ANG�ICA CHUT TART� DE CUXIL |
| 1633 | Mariana Ang�ica Chut�Tart� De Cuxil   |      36297 |   11 |    74377 | 74377 |       44837 | JUAN ENRIQUE CUXIL CHUTA               |
| 1633 | Mariana Ang�ica Chut�Tart� De Cuxil   |      36297 |   11 |    74377 | 74377 |       44837 | JOSUE ALEJANDRO CUXIL CHUTA            |
| 1634 | Mariana Ang�ica Chut�Tart� De Cuxil   |      36297 |    7 |    74377 | 74377 |       74377 | MARIANA ANG�ICA CHUT TART� DE CUXIL |
| 1634 | Mariana Ang�ica Chut�Tart� De Cuxil   |      36297 |    7 |    74377 | 74377 |       44837 | JUAN ENRIQUE CUXIL CHUTA               |
| 1634 | Mariana Ang�ica Chut�Tart� De Cuxil   |      36297 |    7 |    74377 | 74377 |       44837 | JOSUE ALEJANDRO CUXIL CHUTA            |
| 1365 | Rosa Paola Sotz Morales                  |      39643 |    0 |    89123 | 79117 |       89123 | ROSA PAOLA SOTZ MORALES                |
| 1365 | Rosa Paola Sotz Morales                  |      39643 |    0 |    89123 | 79117 |       18828 | DARLYN GABRIELA SANIC SOTZ             |
| 1365 | Rosa Paola Sotz Morales                  |      39643 |    0 |    89123 | 79117 |       79117 | MEREDIT DAYANA SANIC SOTZ              |
| 1366 | Rosa Paola Sotz Morales                  |      39643 |    8 |    89123 | 79117 |       89123 | ROSA PAOLA SOTZ MORALES                |
| 1366 | Rosa Paola Sotz Morales                  |      39643 |    8 |    89123 | 79117 |       18828 | DARLYN GABRIELA SANIC SOTZ             |
| 1366 | Rosa Paola Sotz Morales                  |      39643 |    8 |    89123 | 79117 |       79117 | MEREDIT DAYANA SANIC SOTZ              |
| 1034 | Dina Mar� Xico Nix                      |      38934 |    8 |    21252 | 84309 |       21252 | DINA MARIA XICO NIX                    |
| 1034 | Dina Mar� Xico Nix                      |      38934 |    8 |    21252 | 84309 |       47757 | IKER LEONEL PEREZ XICO                 |
| 1034 | Dina Mar� Xico Nix                      |      38934 |    8 |    21252 | 84309 |       43246 | OLIVER ABIMAEL PEREZ XICO              |
| 1033 | Dina Mar� Xico Nix                      |      38934 |    0 |    21252 | 84309 |       21252 | DINA MARIA XICO NIX                    |
| 1033 | Dina Mar� Xico Nix                      |      38934 |    0 |    21252 | 84309 |       47757 | IKER LEONEL PEREZ XICO                 |
| 1033 | Dina Mar� Xico Nix                      |      38934 |    0 |    21252 | 84309 |       43246 | OLIVER ABIMAEL PEREZ XICO              |
|   72 | Rosalina Miculax Xico                    |      48670 |   12 |    89387 | 89387 |       89387 | ROSALINA MICULAX XICO                  |
|   72 | Rosalina Miculax Xico                    |      48670 |   12 |    89387 | 89387 |        NULL | FRANCISCO GAEL DIAZ MICULAX            |
|   72 | Rosalina Miculax Xico                    |      48670 |   12 |    89387 | 89387 |        NULL | ERIK BENJAMIN DIAZ MICULAX             |
|   73 | Rosalina Miculax Xico                    |      48670 |   11 |    89387 | 89387 |       89387 | ROSALINA MICULAX XICO                  |
|   73 | Rosalina Miculax Xico                    |      48670 |   11 |    89387 | 89387 |        NULL | FRANCISCO GAEL DIAZ MICULAX            |
|   73 | Rosalina Miculax Xico                    |      48670 |   11 |    89387 | 89387 |        NULL | ERIK BENJAMIN DIAZ MICULAX             |
+------+------------------------------------------+------------+------+----------+------