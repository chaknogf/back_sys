-- 079_seed_quirofano_demo.sql
-- Data de prueba (demo) para el reporte de quirófano (`/quirofano/reportes/resumen`
-- y el Excel). Inserta intervenciones repartidas en los dos quirófanos activos,
-- con estados Finalizada/Cancelada y horarios, en la ventana reciente
-- (CURRENT_DATE - 20 .. CURRENT_DATE - 1).
--
-- ADVERTENCIA: es una siembra de DATOS DE PRUEBA, no de esquema. Se ejecuta en
-- cualquier base que corra las migraciones (incluida producción), así que
-- retírela del directorio cuando ya no la necesite. Las filas quedan marcadas en
-- `observaciones` con '[DEMO]' para poder localizarlas/eliminarlas:
--     DELETE FROM intervenciones_quirurgicas WHERE observaciones LIKE '%[DEMO]%';
--
-- Idempotente: solo inserta si aún no existen filas '[DEMO]'. Los ids de
-- paciente/personal/especialidad/área referencian catálogos existentes; si la
-- base no los tiene, el INSERT fallará por llave foránea.

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM intervenciones_quirurgicas
        WHERE observaciones LIKE '%[DEMO]%'
    ) THEN
        INSERT INTO intervenciones_quirurgicas (
            paciente_id, personal_atencion_id, especialidad_id, quirofano_numero_id,
            procedimiento_principal, procedimiento_2, id_area_cuerpo_intervenida,
            estado_cirugia_id, formato_procedimiento_id, procedencia_procedimiento_id,
            rango_especialista_id, fecha,
            hora_inicio_anestesia, hora_inicio_intervencion,
            hora_finaliza_intervencion, hora_finaliza_limpieza_prepara_quirofano,
            observaciones, activo
        ) VALUES
        (133814, 164, 3, 1, 'Apendicectomía', NULL, 5, 1, 1, 1, 1, CURRENT_DATE - 20,
            '07:45', '08:00', '09:30', '10:00', 'Caso de prueba [DEMO]', TRUE),
        (21145, 165, 5, 2, 'Cesárea', NULL, 5, 1, 1, 2, 1, CURRENT_DATE - 18,
            '08:15', '08:40', '09:50', '10:20', 'Caso de prueba [DEMO]', TRUE),
        (127552, 166, 3, 1, 'Colecistectomía laparoscópica', NULL, 5, 1, 2, 2, 1, CURRENT_DATE - 15,
            '07:30', '07:55', '09:40', '10:05', 'Caso de prueba [DEMO]', TRUE),
        (133836, 167, 6, 2, 'Reducción de fractura', 'Colocación de clavo', 4, 1, 5, 1, 2, CURRENT_DATE - 12,
            '09:00', '09:20', '10:50', '11:15', 'Caso de prueba [DEMO]', TRUE),
        (120482, 10, 1, 1, 'Drenaje de absceso', NULL, 5, 1, 1, 1, 2, CURRENT_DATE - 10,
            '07:50', '08:05', '09:00', '09:20', 'Caso de prueba [DEMO]', TRUE),
        (133814, 14, 3, 2, 'Herniorrafia inguinal', NULL, 5, 1, 1, 2, 1, CURRENT_DATE - 8,
            '08:00', '08:25', '10:00', '10:30', 'Caso de prueba [DEMO]', TRUE),
        (21145, 164, 5, 1, 'Legrado uterino', NULL, 5, 1, 3, 2, 2, CURRENT_DATE - 7,
            '07:40', '08:00', '08:50', '09:10', 'Caso de prueba [DEMO]', TRUE),
        (127552, 165, 3, 2, 'Laparotomía exploradora', NULL, 5, 1, 1, 1, 1, CURRENT_DATE - 6,
            '10:00', '10:20', '12:30', '12:55', 'Caso de prueba [DEMO]', TRUE),
        (133836, 166, 4, 1, 'Circuncisión', NULL, 1, 1, 4, 2, 3, CURRENT_DATE - 5,
            '08:10', '08:25', '09:05', '09:25', 'Caso de prueba [DEMO]', TRUE),
        (120482, 167, 6, 2, 'Artroscopia de rodilla', NULL, 4, 1, 4, 2, 1, CURRENT_DATE - 4,
            '07:55', '08:15', '09:45', '10:10', 'Caso de prueba [DEMO]', TRUE),
        (133814, 10, 1, 1, 'Biopsia de piel', NULL, 1, 1, 1, 1, 2, CURRENT_DATE - 3,
            '11:00', '11:15', '11:45', '12:00', 'Caso de prueba [DEMO]', TRUE),
        (21145, 14, 3, 2, 'Apendicectomía', NULL, 5, 2, 1, 1, 1, CURRENT_DATE - 2,
            NULL, NULL, NULL, NULL, 'Caso de prueba [DEMO]', TRUE),
        (127552, 164, 5, 1, 'Cesárea', NULL, 5, 2, 1, 3, 1, CURRENT_DATE - 1,
            NULL, NULL, NULL, NULL, 'Caso de prueba [DEMO]', TRUE),
        (133836, 165, 3, 2, 'Colecistectomía laparoscópica', NULL, 5, 1, 2, 2, 1, CURRENT_DATE - 1,
            '07:35', '08:00', '09:30', '09:55', 'Caso de prueba [DEMO]', TRUE);
    END IF;
END $$;
