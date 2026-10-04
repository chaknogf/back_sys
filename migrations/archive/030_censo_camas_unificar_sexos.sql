BEGIN;

LOCK TABLE censo_camas IN ACCESS EXCLUSIVE MODE;

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM censo_camas WHERE sexo NOT IN (0, 1)) THEN
        RAISE EXCEPTION 'censo_camas contains sexo values other than 0 (masculino) or 1 (femenino)';
    END IF;
END;
$$;

ALTER TABLE censo_camas
    ADD COLUMN ocupados_masculino SMALLINT NOT NULL DEFAULT 0,
    ADD COLUMN egresos_masculino SMALLINT NOT NULL DEFAULT 0,
    ADD COLUMN fallecidos_masculino SMALLINT NOT NULL DEFAULT 0,
    ADD COLUMN referido_masculino SMALLINT NOT NULL DEFAULT 0,
    ADD COLUMN traslado_masculino SMALLINT NOT NULL DEFAULT 0,
    ADD COLUMN contraindicados_masculino SMALLINT NOT NULL DEFAULT 0,
    ADD COLUMN otro_ingresos_masculino SMALLINT NOT NULL DEFAULT 0,
    ADD COLUMN ingresos_masculino SMALLINT NOT NULL DEFAULT 0,
    ADD COLUMN huespedes_masculino SMALLINT NOT NULL DEFAULT 0,
    ADD COLUMN emergencia_masculino SMALLINT NOT NULL DEFAULT 0,
    ADD COLUMN ocupados_femenino SMALLINT NOT NULL DEFAULT 0,
    ADD COLUMN egresos_femenino SMALLINT NOT NULL DEFAULT 0,
    ADD COLUMN fallecidos_femenino SMALLINT NOT NULL DEFAULT 0,
    ADD COLUMN referido_femenino SMALLINT NOT NULL DEFAULT 0,
    ADD COLUMN traslado_femenino SMALLINT NOT NULL DEFAULT 0,
    ADD COLUMN contraindicados_femenino SMALLINT NOT NULL DEFAULT 0,
    ADD COLUMN otro_ingresos_femenino SMALLINT NOT NULL DEFAULT 0,
    ADD COLUMN ingresos_femenino SMALLINT NOT NULL DEFAULT 0,
    ADD COLUMN huespedes_femenino SMALLINT NOT NULL DEFAULT 0,
    ADD COLUMN emergencia_femenino SMALLINT NOT NULL DEFAULT 0;

WITH agrupados AS (
    SELECT fecha,
           servicio_id,
           MIN(id) AS id_conservado,
           COALESCE(MAX(ocupados) FILTER (WHERE sexo = 0), 0) AS ocupados_masculino,
           COALESCE(MAX(egresos) FILTER (WHERE sexo = 0), 0) AS egresos_masculino,
           COALESCE(MAX(fallecidos) FILTER (WHERE sexo = 0), 0) AS fallecidos_masculino,
           COALESCE(MAX(referido) FILTER (WHERE sexo = 0), 0) AS referido_masculino,
           COALESCE(MAX(traslado) FILTER (WHERE sexo = 0), 0) AS traslado_masculino,
           COALESCE(MAX(contraindicados) FILTER (WHERE sexo = 0), 0) AS contraindicados_masculino,
           COALESCE(MAX(otro_ingresos) FILTER (WHERE sexo = 0), 0) AS otro_ingresos_masculino,
           COALESCE(MAX(ingresos) FILTER (WHERE sexo = 0), 0) AS ingresos_masculino,
           COALESCE(MAX(huespedes) FILTER (WHERE sexo = 0), 0) AS huespedes_masculino,
           COALESCE(MAX(emergencia) FILTER (WHERE sexo = 0), 0) AS emergencia_masculino,
           COALESCE(MAX(ocupados) FILTER (WHERE sexo = 1), 0) AS ocupados_femenino,
           COALESCE(MAX(egresos) FILTER (WHERE sexo = 1), 0) AS egresos_femenino,
           COALESCE(MAX(fallecidos) FILTER (WHERE sexo = 1), 0) AS fallecidos_femenino,
           COALESCE(MAX(referido) FILTER (WHERE sexo = 1), 0) AS referido_femenino,
           COALESCE(MAX(traslado) FILTER (WHERE sexo = 1), 0) AS traslado_femenino,
           COALESCE(MAX(contraindicados) FILTER (WHERE sexo = 1), 0) AS contraindicados_femenino,
           COALESCE(MAX(otro_ingresos) FILTER (WHERE sexo = 1), 0) AS otro_ingresos_femenino,
           COALESCE(MAX(ingresos) FILTER (WHERE sexo = 1), 0) AS ingresos_femenino,
           COALESCE(MAX(huespedes) FILTER (WHERE sexo = 1), 0) AS huespedes_femenino,
           COALESCE(MAX(emergencia) FILTER (WHERE sexo = 1), 0) AS emergencia_femenino
    FROM censo_camas
    GROUP BY fecha, servicio_id
)
UPDATE censo_camas AS cc
SET ocupados = a.ocupados_masculino + a.ocupados_femenino,
    egresos = a.egresos_masculino + a.egresos_femenino,
    fallecidos = a.fallecidos_masculino + a.fallecidos_femenino,
    referido = a.referido_masculino + a.referido_femenino,
    traslado = a.traslado_masculino + a.traslado_femenino,
    contraindicados = a.contraindicados_masculino + a.contraindicados_femenino,
    otro_ingresos = a.otro_ingresos_masculino + a.otro_ingresos_femenino,
    ingresos = a.ingresos_masculino + a.ingresos_femenino,
    huespedes = a.huespedes_masculino + a.huespedes_femenino,
    emergencia = a.emergencia_masculino + a.emergencia_femenino,
    egresos_totales =
        (a.egresos_masculino + a.fallecidos_masculino + a.referido_masculino + a.traslado_masculino + a.contraindicados_masculino)
        + (a.egresos_femenino + a.fallecidos_femenino + a.referido_femenino + a.traslado_femenino + a.contraindicados_femenino),
    camas_ocupadas =
        (a.ocupados_masculino + a.otro_ingresos_masculino + a.ingresos_masculino + a.huespedes_masculino + a.emergencia_masculino)
        - (a.egresos_masculino + a.fallecidos_masculino + a.referido_masculino + a.traslado_masculino + a.contraindicados_masculino)
        + (a.ocupados_femenino + a.otro_ingresos_femenino + a.ingresos_femenino + a.huespedes_femenino + a.emergencia_femenino)
        - (a.egresos_femenino + a.fallecidos_femenino + a.referido_femenino + a.traslado_femenino + a.contraindicados_femenino),
    ocupados_masculino = a.ocupados_masculino,
    egresos_masculino = a.egresos_masculino,
    fallecidos_masculino = a.fallecidos_masculino,
    referido_masculino = a.referido_masculino,
    traslado_masculino = a.traslado_masculino,
    contraindicados_masculino = a.contraindicados_masculino,
    otro_ingresos_masculino = a.otro_ingresos_masculino,
    ingresos_masculino = a.ingresos_masculino,
    huespedes_masculino = a.huespedes_masculino,
    emergencia_masculino = a.emergencia_masculino,
    ocupados_femenino = a.ocupados_femenino,
    egresos_femenino = a.egresos_femenino,
    fallecidos_femenino = a.fallecidos_femenino,
    referido_femenino = a.referido_femenino,
    traslado_femenino = a.traslado_femenino,
    contraindicados_femenino = a.contraindicados_femenino,
    otro_ingresos_femenino = a.otro_ingresos_femenino,
    ingresos_femenino = a.ingresos_femenino,
    huespedes_femenino = a.huespedes_femenino,
    emergencia_femenino = a.emergencia_femenino
FROM agrupados AS a
WHERE cc.id = a.id_conservado;

DELETE FROM censo_camas AS cc
USING censo_camas AS conservado
WHERE cc.fecha = conservado.fecha
  AND cc.servicio_id = conservado.servicio_id
  AND cc.id > conservado.id;

DO $$
DECLARE
    restriccion RECORD;
BEGIN
    FOR restriccion IN
        SELECT pc.conname
        FROM pg_constraint AS pc
        WHERE pc.conrelid = 'censo_camas'::regclass
          AND pc.contype = 'u'
          AND ARRAY(
              SELECT a.attname
              FROM unnest(pc.conkey) AS key(attnum)
              JOIN pg_attribute AS a
                ON a.attrelid = pc.conrelid AND a.attnum = key.attnum
              ORDER BY a.attname
          ) IN (ARRAY['fecha', 'servicio_id', 'sexo']::name[], ARRAY['fecha', 'servicio_id']::name[])
    LOOP
        EXECUTE format('ALTER TABLE censo_camas DROP CONSTRAINT %I', restriccion.conname);
    END LOOP;
END;
$$;

ALTER TABLE censo_camas
    DROP COLUMN sexo;

ALTER TABLE censo_camas
    ADD CONSTRAINT uq_censo_camas_fecha_servicio UNIQUE (fecha, servicio_id);

COMMIT;
