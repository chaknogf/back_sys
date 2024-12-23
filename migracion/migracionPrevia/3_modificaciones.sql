UPDATE union_old SET edad = ROUND(edad);

CREATE INDEX idx_nombre_completo_edad ON union_old (nombre_completo, edad);

UPDATE union_old u
JOIN (
    SELECT
        nombre_completo,
        edad,
        MAX(nacimiento) AS max_nacimiento
    FROM union_old
    GROUP BY
        nombre_completo,
        edad
) subquery ON u.nombre_completo = subquery.nombre_completo
AND u.edad = subquery.edad
SET
    u.nacimiento = subquery.max_nacimiento;

CREATE INDEX idx_hoja_emergencia ON union_old (hoja_emergencia);

CREATE INDEX idx_expediente_id_ou ON union_old (expediente_id);

CREATE INDEX idx_nombre_completo_uo ON union_old (nombre_completo);

CREATE INDEX idx_nombre_completo_lp ON listado_pacientes (nombre_completo);

-- Índice compuesto en nombre_completo y nacimiento
CREATE INDEX idx_nombre_nacimiento ON listado_pacientes (nombre_completo, nacimiento);

-- Índice en dpi para acelerar búsquedas
CREATE INDEX idx_dpi ON listado_pacientes (dpi);

UPDATE union_old uo
JOIN old_pacientes op ON uo.nombre_completo = op.nombre_completo
SET
    uo.nacimiento = op.nacimiento
WHERE
    uo.nacimiento IS NULL;

UPDATE union_old uo
JOIN old_consultas oc ON uo.nombre_completo = oc.nombre_completo
SET
    uo.nacimiento = oc.nacimiento
WHERE
    uo.nacimiento IS NULL;

INSERT INTO
    listado_pacientes (
        nombre,
        apellido,
        nombre_completo,
        dpi,
        pasaporte,
        sexo,
        nacimiento,
        defuncion,
        hora_defuncion,
        nacionalidad,
        lugar_nacimiento,
        estado_civil,
        educacion,
        pueblo,
        idioma,
        ocupacion,
        estado,
        gemelo,
        padre,
        madre,
        direccion,
        municipio,
        telefono,
        tel_contacto,
        conyugue,
        user_created,
        created_at,
        updated_at,
        exp_madre,
        exp_ref,
        expediente
    )
SELECT
    MIN(nombre) AS nombre,
    MIN(apellido) AS apellido,
    MIN(nombre_completo) AS nombre_completo,
    CASE
        WHEN MIN(dpi) != '' THEN CAST(MIN(dpi) AS UNSIGNED)
        ELSE NULL
    END AS dpi,
    MIN(pasaporte) AS pasaporte,
    MIN(sexo) AS sexo,
    MIN(nacimiento) AS nacimiento,
    MIN(defuncion) AS defuncion,
    NULL AS hora_defuncion,
    NULL AS nacionalidad,
    MIN(lugar_nacimiento) AS lugar_nacimiento,
    MIN(estado_civil) AS estado_civil,
    MIN(educacion) AS educacion,
    MIN(pueblo) AS pueblo,
    MIN(idioma) AS idioma,
    MIN(ocupacion) AS ocupacion,
    MIN(estado) AS estado,
    NULL AS gemelo,
    MIN(padre) AS padre,
    MIN(madre) AS madre,
    MIN(direccion) AS direccion,
    NULL AS municipio,
    MIN(telefono) AS telefono,
    MIN(telefono_responsable) AS tel_contacto,
    MIN(conyugue) AS conyugue,
    MIN(created_by) AS user_created,
    MIN(created_at) AS created_at,
    MAX(updated_at) AS updated_at,
    MIN(exp_madre) AS exp_madre,
    MIN(exp_ref) AS exp_ref,
    MAX(expediente) AS expediente
FROM union_old u
WHERE (gemelo IS NULL)
GROUP BY
    nombre_completo,
    YEAR(nacimiento)
HAVING
    NOT EXISTS (
        SELECT 1
        FROM listado_pacientes lp
        WHERE
            lp.nombre_completo = MIN(u.nombre_completo) -- Comparamos nombres
            AND YEAR(lp.nacimiento) BETWEEN YEAR(MIN(u.nacimiento)) - 2 AND YEAR(MIN(u.nacimiento))  + 2 -- Rango de ±2 años
    );

DELETE FROM listado_pacientes
WHERE
    nacimiento IS NULL
    AND nombre_completo IN (
        SELECT nombre_completo
        FROM (
                SELECT nombre_completo
                FROM listado_pacientes
                WHERE
                    nacimiento IS NOT NULL
            ) AS subquery
    );

CREATE INDEX idx_nombre_completo ON listado_pacientes (nombre_completo);

CREATE INDEX idx_nacimiento ON listado_pacientes (nacimiento);

CREATE INDEX idx_dpi ON listado_pacientes (dpi);
-- Crear índice en la columna expediente de la tabla listado_pacientes
CREATE INDEX idx_lp_expediente ON listado_pacientes (expediente);

CREATE INDEX idx_op_expediente ON old_pacientes (expediente);

UPDATE listado_pacientes lp
JOIN old_pacientes op ON lp.expediente = op.expediente
SET
    lp.nombre = op.nombre,
    lp.apellido = op.apellido,
    lp.exp_madre = op.exp_madre,
    lp.exp_ref = op.exp_ref,
    lp.dpi = op.dpi,
    lp.nombre_completo = CONCAT(op.nombre, ' ', op.apellido);

-- SELECT
--     nombre_completo,
--     nacimiento,
--     COUNT(*) AS duplicados
-- FROM listado_pacientes
-- GROUP BY
--     nombre_completo,
--     nacimiento
-- HAVING
--     COUNT(*) > 1;

-- DELETE FROM listado_pacientes where nacimiento IS NULL;

INSERT INTO
    consultas_pacientes (
        paciente_id,
        expediente_id,
        nombre_completo,
        nacimiento,
        fecha_consulta,
        historia_clinica,
        hora,
        fecha_recepcion,
        fecha_egreso,
        tipo_consulta,
        especialidad,
        servicio,
        diagnostico,
        folios,
        medico,
        nota,
        estatus,
        lactancia,
        prenatal,
        created_at,
        updated_at,
        created_by
    )
SELECT
    NULL AS paciente_id,
    expediente_id,
    nombre_completo,
    nacimiento,
    fecha_consulta,
    COALESCE(expediente, hoja_emergencia) AS historia_clinica,
    hora,
    recepcion AS fecha_recepcion,
    egreso AS fecha_egreso,
    tipo_consulta,
    especialidad,
    servicio,
    diagnostico,
    folios,
    medico,
    nota,
    status AS estatus,
    lactancia,
    prenatal,
    created_at,
    updated_at,
    created_by
FROM union_old
WHERE
    tipo_consulta IS NOT NULL;

-- INSERT INTO
--     consultas_pacientes (
--         paciente_id,
--         expediente_id,
--         nombre_completo,
--         nacimiento,
--         fecha_consulta,
--         historia_clinica,
--         hora,
--         fecha_recepcion,
--         fecha_egreso,
--         tipo_consulta,
--         tipo_lesion,
--         estancia,
--         especialidad,
--         servicio,
--         fallecido,
--         referido,
--         contraindicado,
--         diagnostico,
--         folios,
--         medico,
--         nota,
--         estatus,
--         lactancia,
--         prenatal,
--         created_by,
--         created_at,
--         updated_at,
--         grupo_edad
--     )
-- SELECT
--     lp.id AS paciente_id,
--     u.expediente_id,
--     u.nombre_completo,
--     u.nacimiento,
--     u.fecha_consulta,
--     COALESCE(
--         u.hoja_emergencia,
--         u.expediente
--     ) AS historia_clinica,
--     u.hora,
--     u.recepcion AS fecha_recepcion,
--     u.egreso AS fecha_egreso,
--     u.tipo_consulta,
--     NULL AS tipo_lesion,
--     NULL AS estancia,
--     u.especialidad,
--     u.servicio,
--     NULL AS fallecido,
--     NULL AS referido,
--     NULL AS contraindicado,
--     u.diagnostico,
--     u.folios,
--     u.medico,
--     u.nota,
--     u.status AS estatus,
--     u.lactancia,
--     u.prenatal,
--     u.created_by,
--     u.created_at,
--     u.updated_at,
--     NULL AS grupo_edad
-- FROM
--     union_old u
--     LEFT JOIN listado_pacientes lp ON u.nombre_completo = lp.nombre_completo
--     AND (
--         u.nacimiento = lp.nacimiento
--         OR (
--             u.nacimiento IS NULL
--             AND lp.nacimiento IS NULL
--         )
--     );

-- SELECT cp.id AS consulta_id, cp.paciente_id, lp.nombre_completo, lp.nacimiento, cp.fecha_consulta, cp.tipo_consulta, cp.historia_clinica,
-- FROM
--     consultas_pacientes cp
--     JOIN listado_pacientes lp ON cp.paciente_id = lp.id
-- ORDER BY lp.nombre_completo, cp.fecha_consulta DESC;

CREATE INDEX idx_consultas_nombre_nacimiento ON consultas_pacientes (nombre_completo, nacimiento);

CREATE INDEX idx_listado_nombre_nacimiento ON listado_pacientes (nombre_completo, nacimiento);

CREATE INDEX idx_union_nombre_nacimiento ON union_old (nombre_completo, nacimiento);

UPDATE consultas_pacientes cp
JOIN listado_pacientes lp ON cp.nombre_completo = lp.nombre_completo
AND (
    cp.nacimiento = lp.nacimiento
    OR (
        cp.nacimiento IS NULL
        AND lp.nacimiento IS NULL
    )
)
SET
    cp.paciente_id = lp.id;

UPDATE consultas_pacientes cp
JOIN listado_pacientes lp ON cp.nombre_completo = lp.nombre_completo
SET
    cp.paciente_id = lp.id
WHERE
    cp.paciente_id IS NULL;

-- SELECT nombre_completo, COUNT(*) AS duplicados
-- FROM listado_pacientes
-- GROUP BY
--     nombre_completo
-- HAVING
--     COUNT(*) > 1;

CREATE TABLE noemergencia AS
SELECT
    NULL AS hoja_emergencia,
    expediente,
    NULL AS paciente_id,
    exp_madre,
    created_at,
    exp_ref,
    nombre_completo
FROM old_pacientes;

ALTER TABLE noemergencia ENGINE = InnoDB, DEFAULT CHARSET = utf8mb4;

CREATE TABLE siemergencia AS
SELECT
    NULL AS expediente,
    hoja_emergencia,
    NULL AS paciente_id,
    exp_madre,
    created_at,
    expediente AS exp_ref,
    nombre_completo
FROM old_consultas
WHERE
    tipo_consulta = 3;

ALTER TABLE siemergencia ENGINE = InnoDB, DEFAULT CHARSET = utf8mb4;

INSERT INTO
    expedientes (
        expediente,
        hoja_emergencia,
        paciente_id,
        exp_madre,
        created_at,
        exp_ref,
        nombre_completo
    )
SELECT
    expediente,
    hoja_emergencia,
    NULL AS paciente_id,
    exp_madre,
    created_at,
    exp_ref,
    nombre_completo
FROM noemergencia;

INSERT INTO
    expedientes (
        expediente,
        hoja_emergencia,
        paciente_id,
        exp_madre,
        created_at,
        exp_ref,
        nombre_completo
    )
SELECT
    expediente,
    hoja_emergencia,
    NULL AS paciente_id,
    exp_madre,
    created_at,
    exp_ref,
    nombre_completo
FROM siemergencia;

UPDATE expedientes SET paciente_id = NULL;

UPDATE expedientes SET consulta_id = NULL;

CREATE INDEX idx_expediente ON expedientes (expediente);

CREATE INDEX idx_hoja_emergencia_e ON expedientes (hoja_emergencia);

CREATE INDEX idx_id_in_expedientes ON expedientes (id);

CREATE INDEX idx_nombre_completo_exp ON expedientes (nombre_completo);

CREATE INDEX idx_id_in_consultas_pacientes ON consultas_pacientes (id);

CREATE INDEX idx_historia_clinica ON consultas_pacientes (historia_clinica);

UPDATE expedientes e
JOIN listado_pacientes lp ON e.nombre_completo = lp.nombre_completo
AND e.expediente = lp.expediente
SET
    e.paciente_id = lp.id;

UPDATE expedientes e
JOIN consultas_pacientes cp ON e.nombre_completo = cp.nombre_completo
AND (
    e.expediente = cp.historia_clinica
    OR e.hoja_emergencia = cp.historia_clinica
)
SET
    e.paciente_id = cp.paciente_id,
    e.consulta_id = cp.id;

CREATE INDEX idx_listado_pacientes_exp_ref ON listado_pacientes (exp_ref);

CREATE INDEX idx_expedientes_exp_ref ON expedientes (exp_ref);

CREATE INDEX idx_listado_pacientes_exp_madre ON listado_pacientes (exp_madre);

CREATE INDEX idx_expedientes_exp_madre ON expedientes (exp_madre);

UPDATE expedientes e
JOIN pacientes p ON e.expediente = p.expediente
SET
    e.exp_madre = p.exp_madre;

UPDATE expedientes e
JOIN listado_pacientes lp ON e.exp_ref = lp.exp_ref
SET
    e.paciente_id = lp.id
WHERE
    e.paciente_id IS NULL;

UPDATE expedientes e
JOIN listado_pacientes lp ON e.exp_madre = lp.exp_madre
SET
    e.paciente_id = lp.id
WHERE
    e.paciente_id IS NULL;

UPDATE expedientes e
JOIN listado_pacientes lp ON e.nombre_completo = lp.nombre_completo
SET
    e.paciente_id = lp.id
WHERE
    e.paciente_id IS NULL;

UPDATE expedientes e
JOIN listado_pacientes lp ON e.nombre_completo LIKE CONCAT('%', lp.nombre_completo, '%')
SET
    e.paciente_id = lp.id
WHERE
    e.paciente_id IS NULL;

CREATE INDEX idx_consultas_paciente_id ON consultas_pacientes (paciente_id);

CREATE INDEX idx_expedientes_paciente_id ON expedientes (paciente_id);

UPDATE consultas_pacientes cp
JOIN expedientes e ON cp.paciente_id = e.paciente_id
SET
    cp.expediente_id = e.id;

UPDATE consultas_pacientes cp
JOIN expedientes e ON cp.historia_clinica = e.expediente
OR (
    cp.historia_clinica = e.hoja_emergencia
    AND e.hoja_emergencia IS NOT NULL
)
SET
    cp.expediente_id = e.id;