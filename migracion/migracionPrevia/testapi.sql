-- CREATE INDEX idx_paciente_id_expediente ON expedientes (paciente_id, expediente);

-- UPDATE union_old uo
-- JOIN expedientes e ON uo.expediente = e.expediente
-- OR uo.hoja_emergencia = e.hoja_emergencia
-- SET
--     uo.expediente_id = e.id;

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
        estado,
        nacionalidad,
        lugar_nacimiento,
        estado_civil,
        educacion,
        pueblo,
        idioma,
        ocupacion,
        padre,
        madre,
        conyugue,
        gemelo,
        direccion,
        telefono,
        responsable,
        parentesco,
        created_at,
        updated_at,
        id,
        expediente_id
    )
SELECT
    MAX(nombre) AS nombre,
    MAX(apellido) AS apellido,
    MAX(nombre_completo) AS nombre_completo,
    MAX(dpi) AS dpi,
    MAX(pasaporte) AS pasaporte,
    CASE MAX(sexo)
        WHEN 'M' THEN 'M'
        WHEN 'F' THEN 'F'
        ELSE 'M'
    END AS sexo,
    MAX(nacimiento) AS nacimiento,
    MAX(
        STR_TO_DATE(defuncion, '%Y-%m-%d')
    ) AS defuncion,
    CASE MAX(estado)
        WHEN 'V' THEN 'V'
        WHEN 'M' THEN 'M'
        ELSE 'V'
    END AS estado,
    MAX(nacionalidad) AS nacionalidad,
    MAX(lugar_nacimiento) AS lugar_nacimiento,
    MAX(estado_civil) AS estado_civil,
    MAX(educacion) AS educacion,
    MAX(pueblo) AS pueblo,
    MAX(idioma) AS idioma,
    MAX(ocupacion) AS ocupacion,
    MAX(padre) AS padre,
    MAX(madre) AS madre,
    MAX(conyugue) AS conyugue,
    MAX(gemelo) AS gemelo,
    MAX(direccion) AS direccion,
    MAX(telefono) AS telefono,
    MAX(responsable) AS responsable,
    MAX(parentesco) AS parentesco,
    NOW() AS created_at,
    NOW() AS updated_at,
    id AS uo_id,
    expediente_id
FROM union_old
GROUP BY
    nombre_completo,
    gemelo;

-- INSERT INTO
--     consultas_pacientes (
--         exp_id,
--         fecha_consulta,
--         hora,
--         fecha_recepcion,
--         fecha_egreso,
--         tipo_consulta,
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
--         create_user,
--         update_user,
--         created_at,
--         updated_at,
--         grupo_edad
--     )
-- SELECT
--     e.id AS exp_id,
--     uo.fecha_consulta,
--     uo.hora,
--     uo.recepcion AS fecha_recepcion,
--     uo.egreso AS fecha_egreso,
--     uo.tipo_consulta,
--     uo.especialidad,
--     uo.servicio,
--     NULL AS fallecido,
--     NULL AS referido,
--     NULL AS contraindicado,
--     uo.diagnostico,
--     uo.folios,
--     uo.medico,
--     uo.nota,
--     uo.status AS estatus,
--     uo.lactancia,
--     uo.prenatal,
--     uo.created_by AS create_user,
--     NULL AS update_user,
--     NOW() AS created_at,
--     NOW() AS updated_at,
--     NULL AS grupo_edad
-- FROM union_old uo
--     JOIN expedientes e ON uo.expediente = e.expediente;

UPDATE union_old SET paciente_id = NULL;

CREATE INDEX idx_nombre_completo_nuevapaciente ON listado_pacientes (nombre_completo);

CREATE INDEX idx_nombre_completo_union_old ON union_old (nombre_completo);

CREATE INDEX idx_nombre_completo_old_pacientes ON old_pacientes (nombre_completo);

CREATE INDEX idx_nombre_completo_old_consultas ON old_consultas (nombre_completo);

ALTER TABLE old_pacientes MODIFY paciente_id BIGINT;

ALTER TABLE old_consultas MODIFY paciente_id BIGINT;

UPDATE union_old uo
JOIN lista_pacientes np ON uo.nombre_completo = np.nombre_completo
SET
    uo.paciente_id = np.id;

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

CREATE INDEX idx_nombre_completo_u ON old_consultas (nombre_completo);

-- CREATE INDEX idx_paciente_id ON old_consultas (paciente_id);
-- -- Índices en la tabla nuevaconsulta
-- CREATE INDEX idx_expediente_nuevaconsulta ON old_consultas (expediente);

-- CREATE INDEX idx_hoja_emergencia_nuevaconsulta ON old_consultas (hoja_emergencia);

-- -- Índices en la tabla nuevaexpediente
-- CREATE INDEX idx_expediente_nuevaexpediente ON nuevaexpediente (expediente);

-- CREATE INDEX idx_hoja_emergencia_nuevaexpediente ON old_consultas (hoja_emergencia);

-- UPDATE nuevaexpediente ne
-- JOIN temp_union_old tuo ON ne.id = tuo.paciente_id
-- SET
--     ne.expediente = tuo.expediente,
--     ne.exp_madre = tuo.exp_madre,
--     ne.exp_ref = tuo.exp_ref
-- WHERE
--     ne.expediente IS NULL;