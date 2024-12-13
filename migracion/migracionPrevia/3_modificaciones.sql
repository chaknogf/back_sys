CREATE TABLE noemergencia AS
SELECT
    NULL AS hoja_emergencia,
    expediente,
    paciente_id,
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
    paciente_id,
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
    paciente_id,
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
    paciente_id,
    exp_madre,
    created_at,
    exp_ref,
    nombre_completo
FROM siemergencia;

UPDATE expedientes SET paciente_id = NULL;

UPDATE expedientes SET consulta_id = NULL;

CREATE INDEX idx_expediente ON union_old (expediente);

CREATE INDEX idx_hoja_emergencia ON union_old (hoja_emergencia);

CREATE INDEX idx_expediente_e ON expedientes (expediente);

CREATE INDEX idx_hoja_emergencia_e ON expedientes (hoja_emergencia);

CREATE INDEX idx_expediente_id_ou ON union_old (expediente_id);

CREATE INDEX idx_id_in_expedientes ON expedientes (id);

CREATE INDEX idx_nombre_completo_uo ON union_old (nombre_completo);

CREATE INDEX idx_nombre_completo_exp ON expedientes (nombre_completo);

CREATE INDEX idx_nombre_completo_e ON expedientes (nombre_completo);

UPDATE union_old uo
JOIN expedientes e ON e.expediente = uo.expediente
SET
    uo.expediente_id = e.id;

UPDATE union_old uo
JOIN expedientes e ON e.hoja_emergencia = uo.hoja_emergencia
SET
    uo.expediente_id = e.id;

UPDATE union_old uo
JOIN expedientes e ON e.nombre_completo = uo.nombre_completo
SET
    uo.expediente_id = e.id;

INSERT INTO
    consultas_pacientes (
        expediente_id,
        fecha_consulta,
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
    expediente_id,
    fecha_consulta,
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

CREATE TABLE listado_pacientes AS
SELECT
    ROW_NUMBER() OVER () AS id,
    MAX(expediente) AS expediente,
    COALESCE(
        MAX(NULLIF(TRIM(nombre), '')),
        MIN(nombre)
    ) AS nombre,
    COALESCE(
        MAX(NULLIF(TRIM(apellido), '')),
        MIN(apellido)
    ) AS apellido,
    CASE
        WHEN MAX(
            NULLIF(TRIM(nombre_completo), '')
        ) IS NOT NULL THEN MAX(
            NULLIF(TRIM(nombre_completo), '')
        )
        WHEN MAX(nombre) LIKE 'Hijo de%'
        OR MAX(nombre) LIKE 'Hija de%' THEN MAX(nombre)
        ELSE NULL
    END AS nombre_completo,
    COALESCE(MAX(sexo), MIN(sexo)) AS sexo,
    COALESCE(MAX(dpi), MIN(dpi)) AS dpi,
    COALESCE(
        MAX(nacimiento),
        MIN(nacimiento)
    ) AS nacimiento,
    COALESCE(
        MAX(NULLIF(TRIM(direccion), '')),
        MIN(NULLIF(TRIM(direccion), ''))
    ) AS direccion,
    COALESCE(MAX(telefono), MIN(telefono)) AS telefono,
    COALESCE(
        MAX(responsable),
        MIN(responsable)
    ) AS responsable,
    COALESCE(
        MAX(parentesco),
        MIN(parentesco)
    ) AS parentesco,
    COALESCE(
        MAX(paciente_id),
        MIN(paciente_id)
    ) AS paciente_id,
    COALESCE(
        MAX(pasaporte),
        MIN(pasaporte)
    ) AS pasaporte,
    COALESCE(
        MAX(nacionalidad),
        MIN(nacionalidad)
    ) AS nacionalidad,
    COALESCE(
        MAX(lugar_nacimiento),
        MIN(lugar_nacimiento)
    ) AS lugar_nacimiento,
    COALESCE(
        MAX(estado_civil),
        MIN(estado_civil)
    ) AS estado_civil,
    COALESCE(
        MAX(educacion),
        MIN(educacion)
    ) AS educacion,
    COALESCE(MAX(pueblo), MIN(pueblo)) AS pueblo,
    COALESCE(MAX(idioma), MIN(idioma)) AS idioma,
    COALESCE(
        MAX(ocupacion),
        MIN(ocupacion)
    ) AS ocupacion,
    COALESCE(MAX(email), MIN(email)) AS email,
    COALESCE(MAX(padre), MIN(padre)) AS padre,
    COALESCE(MAX(madre), MIN(madre)) AS madre,
    COALESCE(
        MAX(dpi_responsable),
        MIN(dpi_responsable)
    ) AS dpi_responsable,
    COALESCE(
        MAX(telefono_responsable),
        MIN(telefono_responsable)
    ) AS telefono_responsable,
    COALESCE(MAX(estado), MIN(estado)) AS estado,
    COALESCE(
        MAX(exp_madre),
        MIN(exp_madre)
    ) AS exp_madre,
    COALESCE(MAX(gemelo), MIN(gemelo)) AS gemelo,
    COALESCE(MAX(conyugue), MIN(conyugue)) AS conyugue,
    COALESCE(
        MAX(defuncion),
        MIN(defuncion)
    ) AS defuncion,
    MIN(expediente) AS exp_ref -- Siempre tomar el expediente más pequeño como referencia
FROM union_old
GROUP BY
    nombre_completo,
    nacimiento,
    gemelo;

CREATE INDEX idx_expediente_pacientes ON listado_pacientes (expediente);

CREATE INDEX idx_nombre_completo_lp ON listado_pacientes (nombre_completo);

UPDATE expedientes e
JOIN listado_pacientes lp ON e.expediente = lp.expediente
SET
    e.paciente_id = lp.id;

UPDATE expedientes e
JOIN listado_pacientes lp ON e.exp_ref = lp.expediente
SET
    e.paciente_id = lp.id;

UPDATE expedientes e
JOIN listado_pacientes lp ON e.nombre_completo = lp.nombre_completo
SET
    e.paciente_id = lp.id;