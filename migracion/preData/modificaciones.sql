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