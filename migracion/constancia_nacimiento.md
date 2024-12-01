# Ejemplo de consulta SQL para obtener todos los datos de consultas_nacimiento:

```sql
 -- Copiar código
SELECT
    cn.id,
    cn.fecha,
    cn.cor,
    cn.ao,
    cn.doc,
    cn.fecha_parto,
    CONCAT(p.nombre, ' ', p.apellido) AS madre,  -- Concatenación del nombre y apellido de la madre
    cn.dpi AS dpi_madre,
    cn.passport AS pasaporte_madre,
    cn.libro,
    cn.folio,
    cn.partida,
    cn.depto,
    cn.muni,
    cn.edad,
    cn.vecindad,
    cn.sexo_rn,
    cn.lb,
    cn.onz,
    cn.hora,
    cn.medico,
    cn.colegiado,
    cn.dpi_medico,
    cn.hijos,
    cn.vivos,
    cn.muertos,
    cn.tipo_parto,
    cn.clase_parto,
    cn.certifica,
    cn.create_by,
    cn.expediente,
    cn.nacionalidad,
    cn.pais,
    cn.created_at,
    cn.updated_at
FROM
    consultas_nacimiento cn
JOIN
    madres m ON cn.madre_id = m.id
JOIN
    pacientes p ON m.paciente_id = p.id;
     -- Unimos con la tabla pacientes para obtener el nombre completo de la madre
```

# Explicación:

## CONCAT

(p.nombre, ' ', p.apellido) AS madre: Esto obtiene el nombre completo de la madre, concatenando el nombre y apellido de la tabla pacientes.

## JOIN

madres m ON cn.madre_id = m.id: Se realiza una unión entre la tabla consultas_nacimiento y madres usando el campo madre_id de consultas_nacimiento.

## JOIN

pacientes p ON m.paciente_id = p.id: A través de la unión con pacientes, obtenemos los detalles de la madre, específicamente el nombre y apellido.
Los demás campos son seleccionados directamente de la tabla consultas_nacimiento.

## Notas:

Esta consulta devuelve todos los datos de la tabla consultas_nacimiento, pero con el nombre completo de la madre obtenido a través de la relación con las tablas madres y pacientes.
La consulta también incluye los campos de la tabla consultas_nacimiento, como fecha, doc, hijos, peso_libras, entre otros.
Si deseas realizar una consulta más específica o filtrar por algún campo (por ejemplo, por fecha o doc), puedes agregar condiciones WHERE a la consulta.
