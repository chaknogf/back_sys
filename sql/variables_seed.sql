-- ============================================================================
-- BASE DE DATOS NORMALIZADA - HOSPITAL GENERAL TIPO I DE TECPÁN GUATEMALA
-- Total de Variables: 655 en 60 categorías
-- ============================================================================

-- INSERTAR CATEGORÍAS
INSERT INTO vh_variable_categories (category_name, description) VALUES ('Centro Transfuncional', '1. Centro Transfuncional (9 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('Estudios de Laboratorio transmisibles y no transmisibles', '2. Estudios de Laboratorio transmisibles y no transmisibles (13 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('Estudios de Laboratorio', '3. Estudios de Laboratorio (14 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('Personas atendidas en laboratorio', '4. Personas atendidas en laboratorio (14 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('Pruebas No reclamadas', '5. Pruebas No reclamadas (8 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('Bacterología', '6. Bacterología (9 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('Reactivos', '7. Reactivos (23 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('Prueba de Laboratorio', '8. Prueba de Laboratorio (11 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('Personas atendidas Rayos X', '9. Personas atendidas Rayos X (11 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('Estudios realizados por especialidad', '10. Estudios realizados por especialidad (8 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('Estudios realizados por servicio', '11. Estudios realizados por servicio (6 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('Pacientes Atendidos Rayos X', '12. Pacientes Atendidos Rayos X (22 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('Estudios realizados Convencional', '13. Estudios realizados Convencional (22 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('Estudios realizados portatil', '14. Estudios realizados portatil (22 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('Otras Variables de Rayos X', '15. Otras Variables de Rayos X (5 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('ESTUDIOS COMPLEMENTARIOS', '16. ESTUDIOS COMPLEMENTARIOS (5 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('Anestesias', '17. Anestesias (8 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('Censo de Procedimientos en Quirofanos (fuente Enfermería SOP)', '18. Censo de Procedimientos en Quirofanos (fuente Enfermería SOP) (26 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('SIGSA 1 - Nacimientos', '19. SIGSA 1 - Nacimientos (17 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('Censo de Procedimientos por Servicios (fuente Medicos)', '20. Censo de Procedimientos por Servicios (fuente Medicos) (7 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('Procedimientos por Especialidad', '21. Procedimientos por Especialidad (7 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('Camas censables', '22. Camas censables (14 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('Porcentaje Ocupacional', '23. Porcentaje Ocupacional (13 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('Día de cama Ocupado', '24. Día de cama Ocupado (14 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('Día de cama Desocupado', '25. Día de cama Desocupado (14 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('Día de Estancia', '26. Día de Estancia (14 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('Egresos', '27. Egresos (14 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('Indice de Rotación de Camas', '28. Indice de Rotación de Camas (14 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('Ingresos', '29. Ingresos (14 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('Egresos por Genero', '30. Egresos por Genero (14 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('Variables de Insumos Despachados', '31. Variables de Insumos Despachados (10 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('Planificación familiar', '32. Planificación familiar (5 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('Producción SIGSA 3H', '33. Producción SIGSA 3H (5 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('Consultas por especialidad', '34. Consultas por especialidad (12 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('Primeras Consultas por Especialidad', '35. Primeras Consultas por Especialidad (12 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('Reconsultas por Especialidad', '36. Reconsultas por Especialidad (12 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('Emergencias por Especialidad', '37. Emergencias por Especialidad (12 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('Interconsultas por Especialidad', '38. Interconsultas por Especialidad (12 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('Promedio diario de consultas', '39. Promedio diario de consultas (10 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('Analisis Multianual de Consultas', '40. Analisis Multianual de Consultas (3 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('Otras consultas de comités', '41. Otras consultas de comités (12 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('Mortalidad General por Grupo de Edad y Sexo', '42. Mortalidad General por Grupo de Edad y Sexo (6 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('Indice de Mortalidad Neonatal y Perinatal al Corte', '43. Indice de Mortalidad Neonatal y Perinatal al Corte (10 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('Consultas Registradas', '44. Consultas Registradas (10 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('Promedio diario de consultas Especialidad', '45. Promedio diario de consultas Especialidad (9 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('Operativos', '46. Operativos (6 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('Intendencia', '47. Intendencia (8 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('Transportes', '48. Transportes (6 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('Raciones entregadas a pacientes', '49. Raciones entregadas a pacientes (13 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('Raciones', '50. Raciones (9 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('Servicios Atendidos', '51. Servicios Atendidos (14 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('Produccion de Enfermería - Emergencia y COEX', '52. Produccion de Enfermería - Emergencia y COEX (5 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('Central de Equipo', '53. Central de Equipo (4 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('Camilleros', '54. Camilleros (8 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('Trabajo Social', '55. Trabajo Social (8 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('Programa 13', '56. Programa 13 (13 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('Programa 14', '57. Programa 14 (8 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('Programa 15', '58. Programa 15 (13 variables)')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variable_categories (category_name, description) VALUES ('Programa 16', '59. Programa 16 (5 variables)')
ON CONFLICT DO NOTHING;

-- INSERTAR VARIABLES
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Centro Transfuncional'), 'Transfunciones Efectuadas', 'TransfuncionesEfectuadas', 'Transfunciones Efectuadas', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Centro Transfuncional'), 'Celulas Empacadas', 'CelulasEmpacadas', 'Celulas Empacadas', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Centro Transfuncional'), 'Plasma Fresco Congelado', 'PlasmaFrescoCongelado', 'Plasma Fresco Congelado', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Centro Transfuncional'), 'Paquete Globular', 'PaqueteGlobular', 'Paquete Globular', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Centro Transfuncional'), 'Concentrado Plaquetario', 'ConcentradoPlaquetario', 'Concentrado Plaquetario', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Centro Transfuncional'), 'Plaquetas por Aferesis', 'PlaquetasporAferesis', 'Plaquetas por Aferesis', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Centro Transfuncional'), 'Crioprecipitados', 'Crioprecipitados', 'Crioprecipitados', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Centro Transfuncional'), 'Unidades Descartadas', 'UnidadesDescartadas', 'Unidades Descartadas', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Centro Transfuncional'), 'Reacciones diversasa la transfusión', 'Reaccionesdiversasalatransfusión', 'Reacciones diversasa la transfusión', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios de Laboratorio transmisibles y no transmisibles'), 'Estudios Lab. Cirugia', 'EstudiosLabCirugia', 'Estudios Lab. Cirugia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios de Laboratorio transmisibles y no transmisibles'), 'Estudios Lab. Emergencia', 'EstudiosLabEmergencia', 'Estudios Lab. Emergencia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios de Laboratorio transmisibles y no transmisibles'), 'Estudios Lab. Maternidad', 'EstudiosLabMaternidad', 'Estudios Lab. Maternidad', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios de Laboratorio transmisibles y no transmisibles'), 'Estudios Lab. Medicina General', 'EstudiosLabMedicinaGeneral', 'Estudios Lab. Medicina General', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios de Laboratorio transmisibles y no transmisibles'), 'Estudios Lab. Medicina', 'EstudiosLabMedicina', 'Estudios Lab. Medicina', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios de Laboratorio transmisibles y no transmisibles'), 'Estudios Lab. Pediatria', 'EstudiosLabPediatria', 'Estudios Lab. Pediatria', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios de Laboratorio transmisibles y no transmisibles'), 'Estudios Lab. Traumatologia', 'EstudiosLabTraumatologia', 'Estudios Lab. Traumatologia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios de Laboratorio transmisibles y no transmisibles'), 'Estudios Lab. UCIA', 'EstudiosLabUCIA', 'Estudios Lab. UCIA', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios de Laboratorio transmisibles y no transmisibles'), 'Estudios Lab. CRN', 'EstudiosLabCRN', 'Estudios Lab. CRN', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios de Laboratorio transmisibles y no transmisibles'), 'Estudios Lab. UCIN', 'EstudiosLabUCIN', 'Estudios Lab. UCIN', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios de Laboratorio transmisibles y no transmisibles'), 'Estudios Lab. SOP', 'EstudiosLabSOP', 'Estudios Lab. SOP', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios de Laboratorio transmisibles y no transmisibles'), 'Estudios Lab. Otros', 'EstudiosLabOtros', 'Estudios Lab. Otros', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios de Laboratorio transmisibles y no transmisibles'), 'total', 'total', 'total', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios de Laboratorio'), 'Estudios Lab. Cirugia', 'EstudiosLabCirugia', 'Estudios Lab. Cirugia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios de Laboratorio'), 'Estudios Lab. Emergencia', 'EstudiosLabEmergencia', 'Estudios Lab. Emergencia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios de Laboratorio'), 'Estudios Lab. Maternidad', 'EstudiosLabMaternidad', 'Estudios Lab. Maternidad', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios de Laboratorio'), 'Estudios Lab. Medicina General', 'EstudiosLabMedicinaGeneral', 'Estudios Lab. Medicina General', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios de Laboratorio'), 'Estudios Lab. Medicina', 'EstudiosLabMedicina', 'Estudios Lab. Medicina', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios de Laboratorio'), 'Estudios Lab. Pediatria', 'EstudiosLabPediatria', 'Estudios Lab. Pediatria', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios de Laboratorio'), 'Estudios Lab. Traumatologia', 'EstudiosLabTraumatologia', 'Estudios Lab. Traumatologia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios de Laboratorio'), 'Estudios Lab. UCIA', 'EstudiosLabUCIA', 'Estudios Lab. UCIA', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios de Laboratorio'), 'Estudios Lab. CRN', 'EstudiosLabCRN', 'Estudios Lab. CRN', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios de Laboratorio'), 'Estudios Lab. UCIN', 'EstudiosLabUCIN', 'Estudios Lab. UCIN', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios de Laboratorio'), 'Estudios Lab. SOP', 'EstudiosLabSOP', 'Estudios Lab. SOP', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios de Laboratorio'), 'Otros', 'Otros', 'Otros', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios de Laboratorio'), 'Estudios Realizados', 'EstudiosRealizados', 'Estudios Realizados', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios de Laboratorio'), 'Estadisticas Multianual', 'EstadisticasMultianual', 'Estadisticas Multianual', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Personas atendidas en laboratorio'), 'Personas Lab. Cirugia', 'PersonasLabCirugia', 'Personas Lab. Cirugia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Personas atendidas en laboratorio'), 'Personas Lab. Emergencia', 'PersonasLabEmergencia', 'Personas Lab. Emergencia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Personas atendidas en laboratorio'), 'Personas Lab. Maternidad', 'PersonasLabMaternidad', 'Personas Lab. Maternidad', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Personas atendidas en laboratorio'), 'Personas Consulta Externa', 'PersonasConsultaExterna', 'Personas Consulta Externa', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Personas atendidas en laboratorio'), 'Personas Lab. Medicina', 'PersonasLabMedicina', 'Personas Lab. Medicina', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Personas atendidas en laboratorio'), 'Personas Lab. Pediatria', 'PersonasLabPediatria', 'Personas Lab. Pediatria', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Personas atendidas en laboratorio'), 'Personas Lab. Traumatologia', 'PersonasLabTraumatologia', 'Personas Lab. Traumatologia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Personas atendidas en laboratorio'), 'Personas Lab. UCIA', 'PersonasLabUCIA', 'Personas Lab. UCIA', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Personas atendidas en laboratorio'), 'Personas Lab. CRN', 'PersonasLabCRN', 'Personas Lab. CRN', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Personas atendidas en laboratorio'), 'Personas Lab. UCIN', 'PersonasLabUCIN', 'Personas Lab. UCIN', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Personas atendidas en laboratorio'), 'Personas Lab. SOP', 'PersonasLabSOP', 'Personas Lab. SOP', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Personas atendidas en laboratorio'), 'Personas Lab. Otros', 'PersonasLabOtros', 'Personas Lab. Otros', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Personas atendidas en laboratorio'), 'Personas atendidas', 'Personasatendidas', 'Personas atendidas', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Personas atendidas en laboratorio'), 'Estadisticas Multianual', 'EstadisticasMultianual', 'Estadisticas Multianual', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Pruebas No reclamadas'), 'Cirugia', 'Cirugia', 'Cirugia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Pruebas No reclamadas'), 'Emergencia', 'Emergencia', 'Emergencia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Pruebas No reclamadas'), 'Maternidad', 'Maternidad', 'Maternidad', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Pruebas No reclamadas'), 'Medicina General', 'MedicinaGeneral', 'Medicina General', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Pruebas No reclamadas'), 'Medicina Interna', 'MedicinaInterna', 'Medicina Interna', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Pruebas No reclamadas'), 'Pediatria', 'Pediatria', 'Pediatria', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Pruebas No reclamadas'), 'Traumatologia', 'Traumatologia', 'Traumatologia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Pruebas No reclamadas'), 'total', 'total', 'total', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Bacterología'), 'Urocultivo', 'Urocultivo', 'Urocultivo', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Bacterología'), 'Coprocultivo', 'Coprocultivo', 'Coprocultivo', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Bacterología'), 'Hemocultivo', 'Hemocultivo', 'Hemocultivo', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Bacterología'), 'Secreciones Varias', 'SecrecionesVarias', 'Secreciones Varias', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Bacterología'), 'Orocultivos', 'Orocultivos', 'Orocultivos', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Bacterología'), 'Secreción Vaginal', 'SecreciónVaginal', 'Secreción Vaginal', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Bacterología'), 'Otros(BK)', 'OtrosBK', 'Otros(BK)', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Bacterología'), 'KOH', 'KOH', 'KOH', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Bacterología'), 'Estudios realizados', 'Estudiosrealizados', 'Estudios realizados', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Reactivos'), 'ACIDO URICO UNIDAD', 'ACIDOURICOUNIDAD', 'ACIDO URICO UNIDAD', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Reactivos'), 'BLIRRUBINA DIRECTA', 'BLIRRUBINADIRECTA', 'BLIRRUBINA DIRECTA', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Reactivos'), 'BILIRRUBINA TOTAL', 'BILIRRUBINATOTAL', 'BILIRRUBINA TOTAL', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Reactivos'), 'COLESTEROL TOTAL UNIDAD', 'COLESTEROLTOTALUNIDAD', 'COLESTEROL TOTAL UNIDAD', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Reactivos'), 'CREATININA UNIDAD', 'CREATININAUNIDAD', 'CREATININA UNIDAD', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Reactivos'), 'GLUCOSA', 'GLUCOSA', 'GLUCOSA', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Reactivos'), 'NITROGENO DE UREA', 'NITROGENODEUREA', 'NITROGENO DE UREA', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Reactivos'), 'PROTEINA TOTAL', 'PROTEINATOTAL', 'PROTEINA TOTAL', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Reactivos'), 'TGO UNIDAD', 'TGOUNIDAD', 'TGO UNIDAD', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Reactivos'), 'TGP UNIDAD', 'TGPUNIDAD', 'TGP UNIDAD', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Reactivos'), 'HDL UNIDAD', 'HDLUNIDAD', 'HDL UNIDAD', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Reactivos'), 'TRIGLICERIDOS UNIDAD', 'TRIGLICERIDOSUNIDAD', 'TRIGLICERIDOS UNIDAD', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Reactivos'), 'FOSFATASA ALCALINA UNIDAD', 'FOSFATASAALCALINAUNIDAD', 'FOSFATASA ALCALINA UNIDAD', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Reactivos'), 'ALBUMINA UNIDAD', 'ALBUMINAUNIDAD', 'ALBUMINA UNIDAD', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Reactivos'), 'AMILASA', 'AMILASA', 'AMILASA', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Reactivos'), 'LIPASA', 'LIPASA', 'LIPASA', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Reactivos'), 'CALCIO', 'CALCIO', 'CALCIO', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Reactivos'), 'CK-MB', 'CKMB', 'CK-MB', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Reactivos'), 'CPK', 'CPK', 'CPK', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Reactivos'), 'GGT', 'GGT', 'GGT', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Reactivos'), 'COLESTEROL LDL', 'COLESTEROLLDL', 'COLESTEROL LDL', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Reactivos'), 'DESHIDROGENASA LACTICA', 'DESHIDROGENASALACTICA', 'DESHIDROGENASA LACTICA', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Reactivos'), 'TOTAL', 'TOTAL', 'TOTAL', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Prueba de Laboratorio'), 'Casos VIH', 'CasosVIH', 'Casos VIH', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Prueba de Laboratorio'), 'Casos HCV', 'CasosHCV', 'Casos HCV', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Prueba de Laboratorio'), 'Casos Sifilis', 'CasosSifilis', 'Casos Sifilis', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Prueba de Laboratorio'), 'Casos de hepatitis A', 'CasosdehepatitisA', 'Casos de hepatitis A', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Prueba de Laboratorio'), 'Casos de hepatitis B', 'CasosdehepatitisB', 'Casos de hepatitis B', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Prueba de Laboratorio'), 'Tuberculosis 1', 'Tuberculosis1', 'Tuberculosis 1', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Prueba de Laboratorio'), 'Tuberculosis 2', 'Tuberculosis2', 'Tuberculosis 2', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Prueba de Laboratorio'), 'Tuberculosis 3', 'Tuberculosis3', 'Tuberculosis 3', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Prueba de Laboratorio'), 'Examenes de sangre', 'Examenesdesangre', 'Examenes de sangre', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Prueba de Laboratorio'), 'Examenes de orina', 'Examenesdeorina', 'Examenes de orina', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Prueba de Laboratorio'), 'Examenes de heces', 'Examenesdeheces', 'Examenes de heces', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Personas atendidas Rayos X'), 'Traumatologia', 'Traumatologia', 'Traumatologia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Personas atendidas Rayos X'), 'Cirugia', 'Cirugia', 'Cirugia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Personas atendidas Rayos X'), 'Pediatria', 'Pediatria', 'Pediatria', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Personas atendidas Rayos X'), 'Medicina Interna', 'MedicinaInterna', 'Medicina Interna', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Personas atendidas Rayos X'), 'Ginecologia', 'Ginecologia', 'Ginecologia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Personas atendidas Rayos X'), 'CRN', 'CRN', 'CRN', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Personas atendidas Rayos X'), 'EMERGENCIA', 'EMERGENCIA', 'EMERGENCIA', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Personas atendidas Rayos X'), 'ENCAMAMIENTO', 'ENCAMAMIENTO', 'ENCAMAMIENTO', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Personas atendidas Rayos X'), 'COEX', 'COEX', 'COEX', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Personas atendidas Rayos X'), 'SOP', 'SOP', 'SOP', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Personas atendidas Rayos X'), 'total', 'total', 'total', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados por especialidad'), 'Traumatologia', 'Traumatologia', 'Traumatologia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados por especialidad'), 'Cirugia', 'Cirugia', 'Cirugia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados por especialidad'), 'Pediatria', 'Pediatria', 'Pediatria', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados por especialidad'), 'Medicina Interna', 'MedicinaInterna', 'Medicina Interna', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados por especialidad'), 'Ginecologia', 'Ginecologia', 'Ginecologia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados por especialidad'), 'CRN', 'CRN', 'CRN', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados por especialidad'), 'total', 'total', 'total', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados por especialidad'), 'Estadisticas Multianual', 'EstadisticasMultianual', 'Estadisticas Multianual', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados por servicio'), 'Coex', 'Coex', 'Coex', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados por servicio'), 'Emergencia', 'Emergencia', 'Emergencia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados por servicio'), 'Hospitalizacion', 'Hospitalizacion', 'Hospitalizacion', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados por servicio'), 'Sop', 'Sop', 'Sop', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados por servicio'), 'total', 'total', 'total', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados por servicio'), 'Estadisticas Multianual', 'EstadisticasMultianual', 'Estadisticas Multianual', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Pacientes Atendidos Rayos X'), 'Emergencia Traumatologia', 'EmergenciaTraumatologia', 'Emergencia Traumatologia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Pacientes Atendidos Rayos X'), 'Emergencia Cirugia', 'EmergenciaCirugia', 'Emergencia Cirugia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Pacientes Atendidos Rayos X'), 'Emergencia Pediatria', 'EmergenciaPediatria', 'Emergencia Pediatria', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Pacientes Atendidos Rayos X'), 'Emergencia Medicina Interna', 'EmergenciaMedicinaInterna', 'Emergencia Medicina Interna', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Pacientes Atendidos Rayos X'), 'coex Traumatologia', 'coexTraumatologia', 'coex Traumatologia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Pacientes Atendidos Rayos X'), 'coex Cirugia', 'coexCirugia', 'coex Cirugia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Pacientes Atendidos Rayos X'), 'coex Pediatria', 'coexPediatria', 'coex Pediatria', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Pacientes Atendidos Rayos X'), 'coex Medicina Interna', 'coexMedicinaInterna', 'coex Medicina Interna', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Pacientes Atendidos Rayos X'), 'Encamamiento Traumatologia', 'EncamamientoTraumatologia', 'Encamamiento Traumatologia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Pacientes Atendidos Rayos X'), 'Encamamiento Cirugia', 'EncamamientoCirugia', 'Encamamiento Cirugia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Pacientes Atendidos Rayos X'), 'Encamamiento Pediatria', 'EncamamientoPediatria', 'Encamamiento Pediatria', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Pacientes Atendidos Rayos X'), 'Encamamiento Medicina Interna', 'EncamamientoMedicinaInterna', 'Encamamiento Medicina Interna', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Pacientes Atendidos Rayos X'), 'SOP Traumatologia', 'SOPTraumatologia', 'SOP Traumatologia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Pacientes Atendidos Rayos X'), 'SOP Cirugia', 'SOPCirugia', 'SOP Cirugia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Pacientes Atendidos Rayos X'), 'SOP Pediatria', 'SOPPediatria', 'SOP Pediatria', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Pacientes Atendidos Rayos X'), 'SOP Medicina Interna', 'SOPMedicinaInterna', 'SOP Medicina Interna', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Pacientes Atendidos Rayos X'), 'CRN', 'CRN', 'CRN', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Pacientes Atendidos Rayos X'), 'Emergencia Ginecologia', 'EmergenciaGinecologia', 'Emergencia Ginecologia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Pacientes Atendidos Rayos X'), 'Hosp Ginecologia', 'HospGinecologia', 'Hosp Ginecologia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Pacientes Atendidos Rayos X'), 'coex ginecologia', 'coexginecologia', 'coex ginecologia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Pacientes Atendidos Rayos X'), 'Aislamiento Pediatria', 'AislamientoPediatria', 'Aislamiento Pediatria', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Pacientes Atendidos Rayos X'), 'subtotal', 'subtotal', 'subtotal', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados Convencional'), 'Emergencia Traumatologia', 'EmergenciaTraumatologia', 'Emergencia Traumatologia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados Convencional'), 'Emergencia Cirugia', 'EmergenciaCirugia', 'Emergencia Cirugia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados Convencional'), 'Emergencia Pediatria', 'EmergenciaPediatria', 'Emergencia Pediatria', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados Convencional'), 'Emergencia Medicina Interna', 'EmergenciaMedicinaInterna', 'Emergencia Medicina Interna', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados Convencional'), 'Consulta Externa Traumatologia', 'ConsultaExternaTraumatologia', 'Consulta Externa Traumatologia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados Convencional'), 'Consulta Externa Cirugia', 'ConsultaExternaCirugia', 'Consulta Externa Cirugia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados Convencional'), 'Consulta Externa Pediatria', 'ConsultaExternaPediatria', 'Consulta Externa Pediatria', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados Convencional'), 'Consulta Externa Medicina Interna', 'ConsultaExternaMedicinaInterna', 'Consulta Externa Medicina Interna', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados Convencional'), 'Encamamiento Traumatologia', 'EncamamientoTraumatologia', 'Encamamiento Traumatologia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados Convencional'), 'Encamamiento Cirugia', 'EncamamientoCirugia', 'Encamamiento Cirugia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados Convencional'), 'Encamamiento Pediatria', 'EncamamientoPediatria', 'Encamamiento Pediatria', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados Convencional'), 'Encamamiento Medicina Interna', 'EncamamientoMedicinaInterna', 'Encamamiento Medicina Interna', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados Convencional'), 'SOP Traumatologia', 'SOPTraumatologia', 'SOP Traumatologia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados Convencional'), 'SOP Cirugia', 'SOPCirugia', 'SOP Cirugia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados Convencional'), 'SOP Pediatria', 'SOPPediatria', 'SOP Pediatria', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados Convencional'), 'SOP Medicina Interna', 'SOPMedicinaInterna', 'SOP Medicina Interna', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados Convencional'), 'CRN', 'CRN', 'CRN', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados Convencional'), 'Emergencia Ginecologia', 'EmergenciaGinecologia', 'Emergencia Ginecologia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados Convencional'), 'Hosp Ginecologia', 'HospGinecologia', 'Hosp Ginecologia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados Convencional'), 'coex ginecologia', 'coexginecologia', 'coex ginecologia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados Convencional'), 'Aislamiento Pediatria', 'AislamientoPediatria', 'Aislamiento Pediatria', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados Convencional'), 'subtotal', 'subtotal', 'subtotal', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados portatil'), 'Emergencia Traumatologia', 'EmergenciaTraumatologia', 'Emergencia Traumatologia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados portatil'), 'emergencia Cirugia', 'emergenciaCirugia', 'emergencia Cirugia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados portatil'), 'Emergencia Pediatria', 'EmergenciaPediatria', 'Emergencia Pediatria', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados portatil'), 'Emergencia Medicina Interna', 'EmergenciaMedicinaInterna', 'Emergencia Medicina Interna', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados portatil'), 'Consulta Externa Traumatologia', 'ConsultaExternaTraumatologia', 'Consulta Externa Traumatologia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados portatil'), 'Consulta Externa Cirugia', 'ConsultaExternaCirugia', 'Consulta Externa Cirugia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados portatil'), 'Consulta Externa Pediatria', 'ConsultaExternaPediatria', 'Consulta Externa Pediatria', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados portatil'), 'Consulta Externa Medicina Interna', 'ConsultaExternaMedicinaInterna', 'Consulta Externa Medicina Interna', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados portatil'), 'Encamamiento Traumatologia', 'EncamamientoTraumatologia', 'Encamamiento Traumatologia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados portatil'), 'Encamamiento Cirugia', 'EncamamientoCirugia', 'Encamamiento Cirugia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados portatil'), 'Encamamiento Pediatria', 'EncamamientoPediatria', 'Encamamiento Pediatria', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados portatil'), 'Encamamiento Medicina Interna', 'EncamamientoMedicinaInterna', 'Encamamiento Medicina Interna', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados portatil'), 'SOP Traumatologia', 'SOPTraumatologia', 'SOP Traumatologia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados portatil'), 'SOP Cirugia', 'SOPCirugia', 'SOP Cirugia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados portatil'), 'SOP Pediatria', 'SOPPediatria', 'SOP Pediatria', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados portatil'), 'SOP Medicina Interna', 'SOPMedicinaInterna', 'SOP Medicina Interna', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados portatil'), 'CRN', 'CRN', 'CRN', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados portatil'), 'Emergencia Ginecologia', 'EmergenciaGinecologia', 'Emergencia Ginecologia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados portatil'), 'Encamamiento Ginecologia', 'EncamamientoGinecologia', 'Encamamiento Ginecologia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados portatil'), 'coex ginecologia', 'coexginecologia', 'coex ginecologia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados portatil'), 'Aislamiento Pediatria', 'AislamientoPediatria', 'Aislamiento Pediatria', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Estudios realizados portatil'), 'subtotal', 'subtotal', 'subtotal', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Otras Variables de Rayos X'), 'Personas atendidas', 'Personasatendidas', 'Personas atendidas', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Otras Variables de Rayos X'), 'Tipo de enfermedad', 'Tipodeenfermedad', 'Tipo de enfermedad', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Otras Variables de Rayos X'), 'Radigrafias tomadas', 'Radigrafiastomadas', 'Radigrafias tomadas', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Otras Variables de Rayos X'), 'Placas por sexo', 'Placasporsexo', 'Placas por sexo', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Otras Variables de Rayos X'), 'Peliculas usadas', 'Peliculasusadas', 'Peliculas usadas', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'ESTUDIOS COMPLEMENTARIOS'), 'ultrasonidos', 'ultrasonidos', 'ultrasonidos', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'ESTUDIOS COMPLEMENTARIOS'), 'electrocardiograma (ekg)', 'electrocardiogramaekg', 'electrocardiograma (ekg)', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'ESTUDIOS COMPLEMENTARIOS'), 'espirometrias', 'espirometrias', 'espirometrias', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'ESTUDIOS COMPLEMENTARIOS'), 'papanicolaus', 'papanicolaus', 'papanicolaus', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'ESTUDIOS COMPLEMENTARIOS'), 'colposcopias', 'colposcopias', 'colposcopias', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Anestesias'), 'General', 'General', 'General', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Anestesias'), 'Epidural', 'Epidural', 'Epidural', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Anestesias'), 'Raquideo', 'Raquideo', 'Raquideo', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Anestesias'), 'Bloqueo Anestesico (supraclavicular)', 'BloqueoAnestesicosupraclavicular', 'Bloqueo Anestesico (supraclavicular)', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Anestesias'), 'Sedación', 'Sedación', 'Sedación', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Anestesias'), 'Local', 'Local', 'Local', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Anestesias'), 'Local Odontología', 'LocalOdontología', 'Local Odontología', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Anestesias'), 'Anestesias administradas', 'Anestesiasadministradas', 'Anestesias administradas', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Censo de Procedimientos en Quirofanos (fuente Enfermería SOP)'), 'Cirugia', 'Cirugia', 'Cirugia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Censo de Procedimientos en Quirofanos (fuente Enfermería SOP)'), 'Cirugia Pediatrica', 'CirugiaPediatrica', 'Cirugia Pediatrica', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Censo de Procedimientos en Quirofanos (fuente Enfermería SOP)'), 'Traumatologia', 'Traumatologia', 'Traumatologia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Censo de Procedimientos en Quirofanos (fuente Enfermería SOP)'), 'Traumatologia Pediatrica', 'TraumatologiaPediatrica', 'Traumatologia Pediatrica', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Censo de Procedimientos en Quirofanos (fuente Enfermería SOP)'), 'Ginecología', 'Ginecología', 'Ginecología', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Censo de Procedimientos en Quirofanos (fuente Enfermería SOP)'), 'Obstetricia', 'Obstetricia', 'Obstetricia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Censo de Procedimientos en Quirofanos (fuente Enfermería SOP)'), 'G y O', 'GyO', 'G y O', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Censo de Procedimientos en Quirofanos (fuente Enfermería SOP)'), 'Procedimientos quirofano', 'Procedimientosquirofano', 'Procedimientos quirofano', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Censo de Procedimientos en Quirofanos (fuente Enfermería SOP)'), 'Estadisticas Multianual', 'EstadisticasMultianual', 'Estadisticas Multianual', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Censo de Procedimientos en Quirofanos (fuente Enfermería SOP)'), 'Rendimiento de quirofanos y sala de parto', 'Rendimientodequirofanosysaladeparto', 'Rendimiento de quirofanos y sala de parto', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Censo de Procedimientos en Quirofanos (fuente Enfermería SOP)'), 'salas de parto', 'salasdeparto', 'salas de parto', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Censo de Procedimientos en Quirofanos (fuente Enfermería SOP)'), 'quirofanos', 'quirofanos', 'quirofanos', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Censo de Procedimientos en Quirofanos (fuente Enfermería SOP)'), 'ameu', 'ameu', 'ameu', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Censo de Procedimientos en Quirofanos (fuente Enfermería SOP)'), 'liu', 'liu', 'liu', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Censo de Procedimientos en Quirofanos (fuente Enfermería SOP)'), 'oxitocina', 'oxitocina', 'oxitocina', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Censo de Procedimientos en Quirofanos (fuente Enfermería SOP)'), 'manejo 3er periodo', 'manejo3erperiodo', 'manejo 3er periodo', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Censo de Procedimientos en Quirofanos (fuente Enfermería SOP)'), 'Episiotomias', 'Episiotomias', 'Episiotomias', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Censo de Procedimientos en Quirofanos (fuente Enfermería SOP)'), 'esterilizaciones  muejeres', 'esterilizacionesmuejeres', 'esterilizaciones  muejeres', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Censo de Procedimientos en Quirofanos (fuente Enfermería SOP)'), 'esterilizaciones  hombres', 'esterilizacioneshombres', 'esterilizaciones  hombres', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Censo de Procedimientos en Quirofanos (fuente Enfermería SOP)'), 'CSTP', 'CSTP', 'CSTP', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Censo de Procedimientos en Quirofanos (fuente Enfermería SOP)'), 'PES', 'PES', 'PES', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Censo de Procedimientos en Quirofanos (fuente Enfermería SOP)'), 'indice de cesareas', 'indicedecesareas', 'indice de cesareas', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Censo de Procedimientos en Quirofanos (fuente Enfermería SOP)'), 'codigo rojo', 'codigorojo', 'codigo rojo', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Censo de Procedimientos en Quirofanos (fuente Enfermería SOP)'), 'hemorragia 1er trimestre', 'hemorragia1ertrimestre', 'hemorragia 1er trimestre', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Censo de Procedimientos en Quirofanos (fuente Enfermería SOP)'), 'hemorragia 2do trimestre', 'hemorragia2dotrimestre', 'hemorragia 2do trimestre', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Censo de Procedimientos en Quirofanos (fuente Enfermería SOP)'), 'hemorragia 3er trimestre', 'hemorragia3ertrimestre', 'hemorragia 3er trimestre', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'SIGSA 1 - Nacimientos'), 'Recien nacidos', 'Reciennacidos', 'Recien nacidos', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'SIGSA 1 - Nacimientos'), 'Tipo de partos', 'Tipodepartos', 'Tipo de partos', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'SIGSA 1 - Nacimientos'), 'Estadisticas Multianual', 'EstadisticasMultianual', 'Estadisticas Multianual', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'SIGSA 1 - Nacimientos'), 'RN por PES', 'RNporPES', 'RN por PES', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'SIGSA 1 - Nacimientos'), 'RN por CSTP', 'RNporCSTP', 'RN por CSTP', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'SIGSA 1 - Nacimientos'), 'Recien nacidos Vivos', 'ReciennacidosVivos', 'Recien nacidos Vivos', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'SIGSA 1 - Nacimientos'), 'Recien nacidos Muertos', 'ReciennacidosMuertos', 'Recien nacidos Muertos', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'SIGSA 1 - Nacimientos'), 'Clasificación de Peso Vivos', 'ClasificacióndePesoVivos', 'Clasificación de Peso Vivos', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'SIGSA 1 - Nacimientos'), 'Clasificación de Peso Muertos', 'ClasificacióndePesoMuertos', 'Clasificación de Peso Muertos', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'SIGSA 1 - Nacimientos'), 'RN Vivos por Clasificación de Parto', 'RNVivosporClasificacióndeParto', 'RN Vivos por Clasificación de Parto', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'SIGSA 1 - Nacimientos'), 'RN Muertos por Clasificación de Parto', 'RNMuertosporClasificacióndeParto', 'RN Muertos por Clasificación de Parto', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'SIGSA 1 - Nacimientos'), 'RN a Termino Vivos', 'RNaTerminoVivos', 'RN a Termino Vivos', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'SIGSA 1 - Nacimientos'), 'RN Prematuros Vivos', 'RNPrematurosVivos', 'RN Prematuros Vivos', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'SIGSA 1 - Nacimientos'), 'RN Bajo Peso Vivos', 'RNBajoPesoVivos', 'RN Bajo Peso Vivos', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'SIGSA 1 - Nacimientos'), 'ZINC DIARREA', 'ZINCDIARREA', 'ZINC DIARREA', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'SIGSA 1 - Nacimientos'), 'ZINC NEUMONIA', 'ZINCNEUMONIA', 'ZINC NEUMONIA', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'SIGSA 1 - Nacimientos'), 'Comité NPH', 'ComitéNPH', 'Comité NPH', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Censo de Procedimientos por Servicios (fuente Medicos)'), 'Procedimientos COEX', 'ProcedimientosCOEX', 'Procedimientos COEX', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Censo de Procedimientos por Servicios (fuente Medicos)'), 'Procedimientos Encamamiento', 'ProcedimientosEncamamiento', 'Procedimientos Encamamiento', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Censo de Procedimientos por Servicios (fuente Medicos)'), 'Procedimientos Emergencia', 'ProcedimientosEmergencia', 'Procedimientos Emergencia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Censo de Procedimientos por Servicios (fuente Medicos)'), 'Procedimientos SOP Emergencia', 'ProcedimientosSOPEmergencia', 'Procedimientos SOP Emergencia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Censo de Procedimientos por Servicios (fuente Medicos)'), 'Procedimientos SOP Electiva', 'ProcedimientosSOPElectiva', 'Procedimientos SOP Electiva', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Censo de Procedimientos por Servicios (fuente Medicos)'), 'Procedimientos Menores', 'ProcedimientosMenores', 'Procedimientos Menores', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Censo de Procedimientos por Servicios (fuente Medicos)'), 'Procedimientos Por Sexo', 'ProcedimientosPorSexo', 'Procedimientos Por Sexo', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Procedimientos por Especialidad'), 'Procedimientos de Cirugía', 'ProcedimientosdeCirugía', 'Procedimientos de Cirugía', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Procedimientos por Especialidad'), 'Procedimientos de Ginecología', 'ProcedimientosdeGinecología', 'Procedimientos de Ginecología', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Procedimientos por Especialidad'), 'Procedimientos Medicina Interna', 'ProcedimientosMedicinaInterna', 'Procedimientos Medicina Interna', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Procedimientos por Especialidad'), 'Procedimientos Pediatria', 'ProcedimientosPediatria', 'Procedimientos Pediatria', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Procedimientos por Especialidad'), 'Procedimientos Traumatología', 'ProcedimientosTraumatología', 'Procedimientos Traumatología', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Procedimientos por Especialidad'), 'Procedimientos por Especialidad', 'ProcedimientosporEspecialidad', 'Procedimientos por Especialidad', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Procedimientos por Especialidad'), 'Procedimientos Menores por Especialidad', 'ProcedimientosMenoresporEspecialidad', 'Procedimientos Menores por Especialidad', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Camas censables'), 'Dias por mes corte', 'Diaspormescorte', 'Dias por mes corte', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Camas censables'), 'Medicina', 'Medicina', 'Medicina', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Camas censables'), 'Cirugia', 'Cirugia', 'Cirugia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Camas censables'), 'Cirugia Pediatrica', 'CirugiaPediatrica', 'Cirugia Pediatrica', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Camas censables'), 'Traumatologia', 'Traumatologia', 'Traumatologia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Camas censables'), 'Traumatologia Pediatrica', 'TraumatologiaPediatrica', 'Traumatologia Pediatrica', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Camas censables'), 'Ginecologia', 'Ginecologia', 'Ginecologia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Camas censables'), 'Obstetricia', 'Obstetricia', 'Obstetricia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Camas censables'), 'Pediatria', 'Pediatria', 'Pediatria', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Camas censables'), 'Neonatos', 'Neonatos', 'Neonatos', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Camas censables'), 'UCIN', 'UCIN', 'UCIN', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Camas censables'), 'CRN', 'CRN', 'CRN', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Camas censables'), 'MADRE CANGURO', 'MADRECANGURO', 'MADRE CANGURO', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Camas censables'), 'UCIA', 'UCIA', 'UCIA', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Porcentaje Ocupacional'), 'Medicina', 'Medicina', 'Medicina', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Porcentaje Ocupacional'), 'Cirugia', 'Cirugia', 'Cirugia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Porcentaje Ocupacional'), 'Cirugia Pediatrica', 'CirugiaPediatrica', 'Cirugia Pediatrica', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Porcentaje Ocupacional'), 'Traumatologia', 'Traumatologia', 'Traumatologia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Porcentaje Ocupacional'), 'Traumatologia Pediatrica', 'TraumatologiaPediatrica', 'Traumatologia Pediatrica', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Porcentaje Ocupacional'), 'Ginecologia', 'Ginecologia', 'Ginecologia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Porcentaje Ocupacional'), 'Obstetricia', 'Obstetricia', 'Obstetricia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Porcentaje Ocupacional'), 'Pediatria', 'Pediatria', 'Pediatria', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Porcentaje Ocupacional'), 'Neonatos', 'Neonatos', 'Neonatos', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Porcentaje Ocupacional'), 'UCIN', 'UCIN', 'UCIN', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Porcentaje Ocupacional'), 'CRN', 'CRN', 'CRN', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Porcentaje Ocupacional'), 'MADRE CANGURO', 'MADRECANGURO', 'MADRE CANGURO', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Porcentaje Ocupacional'), 'UCIA', 'UCIA', 'UCIA', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Día de cama Ocupado'), 'Medicina', 'Medicina', 'Medicina', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Día de cama Ocupado'), 'Cirugia', 'Cirugia', 'Cirugia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Día de cama Ocupado'), 'Cirugia Pediatrica', 'CirugiaPediatrica', 'Cirugia Pediatrica', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Día de cama Ocupado'), 'Traumatologia', 'Traumatologia', 'Traumatologia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Día de cama Ocupado'), 'Traumatologia Pediatrica', 'TraumatologiaPediatrica', 'Traumatologia Pediatrica', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Día de cama Ocupado'), 'Ginecologia', 'Ginecologia', 'Ginecologia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Día de cama Ocupado'), 'Obstetricia', 'Obstetricia', 'Obstetricia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Día de cama Ocupado'), 'Pediatria', 'Pediatria', 'Pediatria', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Día de cama Ocupado'), 'Neonatos', 'Neonatos', 'Neonatos', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Día de cama Ocupado'), 'UCIN', 'UCIN', 'UCIN', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Día de cama Ocupado'), 'CRN', 'CRN', 'CRN', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Día de cama Ocupado'), 'MADRE CANGURO', 'MADRECANGURO', 'MADRE CANGURO', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Día de cama Ocupado'), 'UCIA', 'UCIA', 'UCIA', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Día de cama Ocupado'), 'subtotal', 'subtotal', 'subtotal', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Día de cama Desocupado'), 'Medicina', 'Medicina', 'Medicina', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Día de cama Desocupado'), 'Cirugia', 'Cirugia', 'Cirugia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Día de cama Desocupado'), 'Cirugia Pediatrica', 'CirugiaPediatrica', 'Cirugia Pediatrica', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Día de cama Desocupado'), 'Traumatologia', 'Traumatologia', 'Traumatologia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Día de cama Desocupado'), 'Traumatologia Pediatrica', 'TraumatologiaPediatrica', 'Traumatologia Pediatrica', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Día de cama Desocupado'), 'Ginecologia', 'Ginecologia', 'Ginecologia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Día de cama Desocupado'), 'Obstetricia', 'Obstetricia', 'Obstetricia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Día de cama Desocupado'), 'Pediatria', 'Pediatria', 'Pediatria', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Día de cama Desocupado'), 'Neonatos', 'Neonatos', 'Neonatos', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Día de cama Desocupado'), 'UCIN', 'UCIN', 'UCIN', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Día de cama Desocupado'), 'CRN', 'CRN', 'CRN', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Día de cama Desocupado'), 'MADRE CANGURO', 'MADRECANGURO', 'MADRE CANGURO', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Día de cama Desocupado'), 'UCIA', 'UCIA', 'UCIA', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Día de cama Desocupado'), 'subtotal', 'subtotal', 'subtotal', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Día de Estancia'), 'Medicina', 'Medicina', 'Medicina', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Día de Estancia'), 'Cirugia', 'Cirugia', 'Cirugia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Día de Estancia'), 'Cirugia Pediatrica', 'CirugiaPediatrica', 'Cirugia Pediatrica', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Día de Estancia'), 'Traumatologia', 'Traumatologia', 'Traumatologia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Día de Estancia'), 'Traumatologia Pediatrica', 'TraumatologiaPediatrica', 'Traumatologia Pediatrica', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Día de Estancia'), 'Ginecologia', 'Ginecologia', 'Ginecologia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Día de Estancia'), 'Obstetricia', 'Obstetricia', 'Obstetricia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Día de Estancia'), 'Pediatria', 'Pediatria', 'Pediatria', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Día de Estancia'), 'Neonatos', 'Neonatos', 'Neonatos', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Día de Estancia'), 'UCIN', 'UCIN', 'UCIN', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Día de Estancia'), 'CRN', 'CRN', 'CRN', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Día de Estancia'), 'MADRE CANGURO', 'MADRECANGURO', 'MADRE CANGURO', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Día de Estancia'), 'UCIA', 'UCIA', 'UCIA', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Día de Estancia'), 'subtotal', 'subtotal', 'subtotal', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Egresos'), 'Medicina', 'Medicina', 'Medicina', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Egresos'), 'Cirugia', 'Cirugia', 'Cirugia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Egresos'), 'Cirugia Pediatrica', 'CirugiaPediatrica', 'Cirugia Pediatrica', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Egresos'), 'Traumatologia', 'Traumatologia', 'Traumatologia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Egresos'), 'Traumatologia Pediatrica', 'TraumatologiaPediatrica', 'Traumatologia Pediatrica', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Egresos'), 'Ginecologia', 'Ginecologia', 'Ginecologia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Egresos'), 'Obstetricia', 'Obstetricia', 'Obstetricia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Egresos'), 'Pediatria', 'Pediatria', 'Pediatria', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Egresos'), 'Neonatos', 'Neonatos', 'Neonatos', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Egresos'), 'UCIN', 'UCIN', 'UCIN', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Egresos'), 'CRN', 'CRN', 'CRN', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Egresos'), 'MADRE CANGURO', 'MADRECANGURO', 'MADRE CANGURO', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Egresos'), 'UCIA', 'UCIA', 'UCIA', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Egresos'), 'subtotal', 'subtotal', 'subtotal', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Indice de Rotación de Camas'), 'Medicina', 'Medicina', 'Medicina', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Indice de Rotación de Camas'), 'Cirugia', 'Cirugia', 'Cirugia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Indice de Rotación de Camas'), 'Cirugia Pediatrica', 'CirugiaPediatrica', 'Cirugia Pediatrica', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Indice de Rotación de Camas'), 'Traumatologia', 'Traumatologia', 'Traumatologia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Indice de Rotación de Camas'), 'Traumatologia Pediatrica', 'TraumatologiaPediatrica', 'Traumatologia Pediatrica', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Indice de Rotación de Camas'), 'Ginecologia', 'Ginecologia', 'Ginecologia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Indice de Rotación de Camas'), 'Obstetricia', 'Obstetricia', 'Obstetricia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Indice de Rotación de Camas'), 'Pediatria', 'Pediatria', 'Pediatria', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Indice de Rotación de Camas'), 'Neonatos', 'Neonatos', 'Neonatos', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Indice de Rotación de Camas'), 'UCIN', 'UCIN', 'UCIN', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Indice de Rotación de Camas'), 'CRN', 'CRN', 'CRN', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Indice de Rotación de Camas'), 'MADRE CANGURO', 'MADRECANGURO', 'MADRE CANGURO', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Indice de Rotación de Camas'), 'UCIA', 'UCIA', 'UCIA', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Indice de Rotación de Camas'), 'subtotal', 'subtotal', 'subtotal', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Ingresos'), 'Medicina', 'Medicina', 'Medicina', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Ingresos'), 'Cirugia', 'Cirugia', 'Cirugia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Ingresos'), 'Cirugia Pediatrica', 'CirugiaPediatrica', 'Cirugia Pediatrica', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Ingresos'), 'Traumatologia', 'Traumatologia', 'Traumatologia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Ingresos'), 'Traumatologia Pediatrica', 'TraumatologiaPediatrica', 'Traumatologia Pediatrica', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Ingresos'), 'Ginecologia', 'Ginecologia', 'Ginecologia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Ingresos'), 'Obstetricia', 'Obstetricia', 'Obstetricia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Ingresos'), 'Pediatria', 'Pediatria', 'Pediatria', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Ingresos'), 'Neonatos', 'Neonatos', 'Neonatos', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Ingresos'), 'UCIN', 'UCIN', 'UCIN', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Ingresos'), 'CRN', 'CRN', 'CRN', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Ingresos'), 'MADRE CANGURO', 'MADRECANGURO', 'MADRE CANGURO', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Ingresos'), 'UCIA', 'UCIA', 'UCIA', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Ingresos'), 'subtotal', 'subtotal', 'subtotal', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Egresos por Genero'), 'Medicina', 'Medicina', 'Medicina', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Egresos por Genero'), 'Cirugia', 'Cirugia', 'Cirugia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Egresos por Genero'), 'Cirugia Pedia', 'CirugiaPedia', 'Cirugia Pedia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Egresos por Genero'), 'Traumatologia', 'Traumatologia', 'Traumatologia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Egresos por Genero'), 'Trauma Pedia', 'TraumaPedia', 'Trauma Pedia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Egresos por Genero'), 'Ginecologia', 'Ginecologia', 'Ginecologia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Egresos por Genero'), 'Obstetricia', 'Obstetricia', 'Obstetricia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Egresos por Genero'), 'Pediatria', 'Pediatria', 'Pediatria', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Egresos por Genero'), 'Neonatos', 'Neonatos', 'Neonatos', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Egresos por Genero'), 'UCIN', 'UCIN', 'UCIN', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Egresos por Genero'), 'CRN', 'CRN', 'CRN', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Egresos por Genero'), 'Alojamiento conjunto', 'Alojamientoconjunto', 'Alojamiento conjunto', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Egresos por Genero'), 'MADRE CANGURO', 'MADRECANGURO', 'MADRE CANGURO', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Egresos por Genero'), 'UCIA', 'UCIA', 'UCIA', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Variables de Insumos Despachados'), 'Medicamentos', 'Medicamentos', 'Medicamentos', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Variables de Insumos Despachados'), 'Requisiones Oxigeno', 'RequisionesOxigeno', 'Requisiones Oxigeno', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Variables de Insumos Despachados'), 'Requisiones de Suministros', 'RequisionesdeSuministros', 'Requisiones de Suministros', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Variables de Insumos Despachados'), 'Productos Afines', 'ProductosAfines', 'Productos Afines', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Variables de Insumos Despachados'), 'Requisiones', 'Requisiones', 'Requisiones', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Variables de Insumos Despachados'), 'Salida de Medicamentos Controlados', 'SalidadeMedicamentosControlados', 'Salida de Medicamentos Controlados', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Variables de Insumos Despachados'), 'Unidades Despachadas M.Q Renglon-295', 'UnidadesDespachadasMQRenglon295', 'Unidades Despachadas M.Q Renglon-295', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Variables de Insumos Despachados'), 'Valor Despachado M.Q Renglon-295', 'ValorDespachadoMQRenglon295', 'Valor Despachado M.Q Renglon-295', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Variables de Insumos Despachados'), 'Unidades Despachadas Medicamento Renglon-266', 'UnidadesDespachadasMedicamentoRenglon266', 'Unidades Despachadas Medicamento Renglon-266', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Variables de Insumos Despachados'), 'Valor Despachado Medicamentos Renglon-266', 'ValorDespachadoMedicamentosRenglon266', 'Valor Despachado Medicamentos Renglon-266', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Planificación familiar'), 'Metodo Inyectable', 'MetodoInyectable', 'Metodo Inyectable', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Planificación familiar'), 'Metodo DIU', 'MetodoDIU', 'Metodo DIU', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Planificación familiar'), 'Metodo Pildora', 'MetodoPildora', 'Metodo Pildora', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Planificación familiar'), 'Metodo Condon', 'MetodoCondon', 'Metodo Condon', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Planificación familiar'), 'Metodo Implante', 'MetodoImplante', 'Metodo Implante', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Producción SIGSA 3H'), 'Primeras', 'Primeras', 'Primeras', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Producción SIGSA 3H'), 'Reconsultas', 'Reconsultas', 'Reconsultas', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Producción SIGSA 3H'), 'Emergencias', 'Emergencias', 'Emergencias', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Producción SIGSA 3H'), 'Interconsultas', 'Interconsultas', 'Interconsultas', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Producción SIGSA 3H'), 'Total de consultas', 'Totaldeconsultas', 'Total de consultas', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Consultas por especialidad'), 'Cirugía', 'Cirugía', 'Cirugía', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Consultas por especialidad'), 'Medicina General', 'MedicinaGeneral', 'Medicina General', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Consultas por especialidad'), 'Ginecología', 'Ginecología', 'Ginecología', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Consultas por especialidad'), 'Medicina Interna', 'MedicinaInterna', 'Medicina Interna', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Consultas por especialidad'), 'Nutrición', 'Nutrición', 'Nutrición', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Consultas por especialidad'), 'Pediatría', 'Pediatría', 'Pediatría', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Consultas por especialidad'), 'Psicología', 'Psicología', 'Psicología', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Consultas por especialidad'), 'Terapia Respiratoria', 'TerapiaRespiratoria', 'Terapia Respiratoria', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Consultas por especialidad'), 'Traumatología', 'Traumatología', 'Traumatología', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Consultas por especialidad'), 'Consejeria de Nutrición y Lactancia Materna', 'ConsejeriadeNutriciónyLactanciaMaterna', 'Consejeria de Nutrición y Lactancia Materna', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Consultas por especialidad'), 'Odontología', 'Odontología', 'Odontología', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Consultas por especialidad'), 'por genero', 'porgenero', 'por genero', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Primeras Consultas por Especialidad'), 'Cirugía', 'Cirugía', 'Cirugía', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Primeras Consultas por Especialidad'), 'Medicina General', 'MedicinaGeneral', 'Medicina General', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Primeras Consultas por Especialidad'), 'Ginecología', 'Ginecología', 'Ginecología', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Primeras Consultas por Especialidad'), 'Medicina Interna', 'MedicinaInterna', 'Medicina Interna', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Primeras Consultas por Especialidad'), 'Nutrición', 'Nutrición', 'Nutrición', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Primeras Consultas por Especialidad'), 'Pediatría', 'Pediatría', 'Pediatría', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Primeras Consultas por Especialidad'), 'Psicología', 'Psicología', 'Psicología', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Primeras Consultas por Especialidad'), 'Terapia Respiratoria', 'TerapiaRespiratoria', 'Terapia Respiratoria', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Primeras Consultas por Especialidad'), 'Traumatología', 'Traumatología', 'Traumatología', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Primeras Consultas por Especialidad'), 'Consejeria de Nutrición y Lactancia Materna', 'ConsejeriadeNutriciónyLactanciaMaterna', 'Consejeria de Nutrición y Lactancia Materna', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Primeras Consultas por Especialidad'), 'Odontología', 'Odontología', 'Odontología', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Primeras Consultas por Especialidad'), 'por genero', 'porgenero', 'por genero', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Reconsultas por Especialidad'), 'Cirugía', 'Cirugía', 'Cirugía', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Reconsultas por Especialidad'), 'Medicina General', 'MedicinaGeneral', 'Medicina General', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Reconsultas por Especialidad'), 'Ginecología', 'Ginecología', 'Ginecología', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Reconsultas por Especialidad'), 'Medicina Interna', 'MedicinaInterna', 'Medicina Interna', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Reconsultas por Especialidad'), 'Nutrición', 'Nutrición', 'Nutrición', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Reconsultas por Especialidad'), 'Pediatría', 'Pediatría', 'Pediatría', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Reconsultas por Especialidad'), 'Psicología', 'Psicología', 'Psicología', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Reconsultas por Especialidad'), 'Terapia Respiratoria', 'TerapiaRespiratoria', 'Terapia Respiratoria', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Reconsultas por Especialidad'), 'Traumatología', 'Traumatología', 'Traumatología', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Reconsultas por Especialidad'), 'Consejeria de Nutrición y Lactancia Materna', 'ConsejeriadeNutriciónyLactanciaMaterna', 'Consejeria de Nutrición y Lactancia Materna', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Reconsultas por Especialidad'), 'Odontología', 'Odontología', 'Odontología', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Reconsultas por Especialidad'), 'por genero', 'porgenero', 'por genero', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Emergencias por Especialidad'), 'Cirugía', 'Cirugía', 'Cirugía', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Emergencias por Especialidad'), 'Medicina General', 'MedicinaGeneral', 'Medicina General', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Emergencias por Especialidad'), 'Ginecología', 'Ginecología', 'Ginecología', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Emergencias por Especialidad'), 'Medicina Interna', 'MedicinaInterna', 'Medicina Interna', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Emergencias por Especialidad'), 'Nutrición', 'Nutrición', 'Nutrición', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Emergencias por Especialidad'), 'Pediatría', 'Pediatría', 'Pediatría', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Emergencias por Especialidad'), 'Psicología', 'Psicología', 'Psicología', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Emergencias por Especialidad'), 'Terapia Respiratoria', 'TerapiaRespiratoria', 'Terapia Respiratoria', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Emergencias por Especialidad'), 'Traumatología', 'Traumatología', 'Traumatología', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Emergencias por Especialidad'), 'Consejeria de Nutrición y Lactancia Materna', 'ConsejeriadeNutriciónyLactanciaMaterna', 'Consejeria de Nutrición y Lactancia Materna', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Emergencias por Especialidad'), 'Odontología', 'Odontología', 'Odontología', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Emergencias por Especialidad'), 'por genero', 'porgenero', 'por genero', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Interconsultas por Especialidad'), 'Cirugía', 'Cirugía', 'Cirugía', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Interconsultas por Especialidad'), 'Medicina General', 'MedicinaGeneral', 'Medicina General', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Interconsultas por Especialidad'), 'Ginecología', 'Ginecología', 'Ginecología', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Interconsultas por Especialidad'), 'Medicina Interna', 'MedicinaInterna', 'Medicina Interna', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Interconsultas por Especialidad'), 'Nutrición', 'Nutrición', 'Nutrición', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Interconsultas por Especialidad'), 'Pediatría', 'Pediatría', 'Pediatría', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Interconsultas por Especialidad'), 'Psicología', 'Psicología', 'Psicología', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Interconsultas por Especialidad'), 'Terapia Respiratoria', 'TerapiaRespiratoria', 'Terapia Respiratoria', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Interconsultas por Especialidad'), 'Traumatología', 'Traumatología', 'Traumatología', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Interconsultas por Especialidad'), 'Consejeria de Nutrición y Lactancia Materna', 'ConsejeriadeNutriciónyLactanciaMaterna', 'Consejeria de Nutrición y Lactancia Materna', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Interconsultas por Especialidad'), 'Odontología', 'Odontología', 'Odontología', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Interconsultas por Especialidad'), 'por genero', 'porgenero', 'por genero', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Promedio diario de consultas'), 'Cirugía', 'Cirugía', 'Cirugía', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Promedio diario de consultas'), 'Medicina General', 'MedicinaGeneral', 'Medicina General', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Promedio diario de consultas'), 'Ginecología', 'Ginecología', 'Ginecología', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Promedio diario de consultas'), 'Medicina Interna', 'MedicinaInterna', 'Medicina Interna', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Promedio diario de consultas'), 'Nutrición', 'Nutrición', 'Nutrición', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Promedio diario de consultas'), 'Pediatría', 'Pediatría', 'Pediatría', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Promedio diario de consultas'), 'Psicología', 'Psicología', 'Psicología', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Promedio diario de consultas'), 'Terapia Respiratoria', 'TerapiaRespiratoria', 'Terapia Respiratoria', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Promedio diario de consultas'), 'Traumatología', 'Traumatología', 'Traumatología', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Promedio diario de consultas'), 'Odontología', 'Odontología', 'Odontología', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Analisis Multianual de Consultas'), 'Total Consultas', 'TotalConsultas', 'Total Consultas', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Analisis Multianual de Consultas'), 'Primeras', 'Primeras', 'Primeras', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Analisis Multianual de Consultas'), 'Emergencias', 'Emergencias', 'Emergencias', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Otras consultas de comités'), 'Primeras Consultas Adecuaciones menores de 5 años', 'PrimerasConsultasAdecuacionesmenoresde5años', 'Primeras Consultas Adecuaciones menores de 5 años', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Otras consultas de comités'), 'Emergencias Consultas Adecuaciones menores de 5 años', 'EmergenciasConsultasAdecuacionesmenoresde5años', 'Emergencias Consultas Adecuaciones menores de 5 años', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Otras consultas de comités'), 'Reconsultas Adecuaciones menores de 5 años', 'ReconsultasAdecuacionesmenoresde5años', 'Reconsultas Adecuaciones menores de 5 años', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Otras consultas de comités'), 'Interconsultas Adecuaciones menores de 5 años', 'InterconsultasAdecuacionesmenoresde5años', 'Interconsultas Adecuaciones menores de 5 años', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Otras consultas de comités'), 'Controles de lactantes sanos Z:76:2', 'ControlesdelactantessanosZ762', 'Controles de lactantes sanos Z:76:2', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Otras consultas de comités'), 'Primeros Controles Prenatales Z:34:1', 'PrimerosControlesPrenatalesZ341', 'Primeros Controles Prenatales Z:34:1', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Otras consultas de comités'), 'Segundos Controles Prenatales Z:34:2', 'SegundosControlesPrenatalesZ342', 'Segundos Controles Prenatales Z:34:2', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Otras consultas de comités'), 'Terceros Controles PrenatalesZ:34:3', 'TercerosControlesPrenatalesZ343', 'Terceros Controles PrenatalesZ:34:3', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Otras consultas de comités'), 'Cuartos Controles PrenatalesZ:34:4', 'CuartosControlesPrenatalesZ344', 'Cuartos Controles PrenatalesZ:34:4', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Otras consultas de comités'), 'Atención despues del parto Z:39:x', 'AtencióndespuesdelpartoZ39x', 'Atención despues del parto Z:39:x', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Otras consultas de comités'), 'Examen ginecologico normal Z:01:4', 'ExamenginecologiconormalZ014', 'Examen ginecologico normal Z:01:4', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Otras consultas de comités'), 'Supervicsión del embarazo normal Z:34', 'SupervicsióndelembarazonormalZ34', 'Supervicsión del embarazo normal Z:34', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Mortalidad General por Grupo de Edad y Sexo'), '0 a 28 días', '0a28días', '0 a 28 días', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Mortalidad General por Grupo de Edad y Sexo'), 'menor a 5 años', 'menora5años', 'menor a 5 años', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Mortalidad General por Grupo de Edad y Sexo'), '5 a 18 años', '5a18años', '5 a 18 años', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Mortalidad General por Grupo de Edad y Sexo'), '19 a 59 años', '19a59años', '19 a 59 años', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Mortalidad General por Grupo de Edad y Sexo'), 'mayor a 60 años', 'mayora60años', 'mayor a 60 años', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Mortalidad General por Grupo de Edad y Sexo'), 'Mortalidad general', 'Mortalidadgeneral', 'Mortalidad general', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Indice de Mortalidad Neonatal y Perinatal al Corte'), 'Mortalidad Neonatal Inmediata (24 horas)', 'MortalidadNeonatalInmediata24horas', 'Mortalidad Neonatal Inmediata (24 horas)', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Indice de Mortalidad Neonatal y Perinatal al Corte'), 'Mortalidad Neonatal Temprana (7 dias)', 'MortalidadNeonatalTemprana7dias', 'Mortalidad Neonatal Temprana (7 dias)', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Indice de Mortalidad Neonatal y Perinatal al Corte'), 'Mortalidad Neonatal Tardia (7 a 28 dias)', 'MortalidadNeonatalTardia7a28dias', 'Mortalidad Neonatal Tardia (7 a 28 dias)', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Indice de Mortalidad Neonatal y Perinatal al Corte'), 'Mortalidad Neonatal Total', 'MortalidadNeonatalTotal', 'Mortalidad Neonatal Total', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Indice de Mortalidad Neonatal y Perinatal al Corte'), 'Muertes Fetales', 'MuertesFetales', 'Muertes Fetales', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Indice de Mortalidad Neonatal y Perinatal al Corte'), 'tasa de Mortalidad Perinatal y Neonatal', 'tasadeMortalidadPerinatalyNeonatal', 'tasa de Mortalidad Perinatal y Neonatal', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Indice de Mortalidad Neonatal y Perinatal al Corte'), 'tasa de Muertes Fetales', 'tasadeMuertesFetales', 'tasa de Muertes Fetales', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Indice de Mortalidad Neonatal y Perinatal al Corte'), 'tasa de Mortalidad Neonatal Inmediata', 'tasadeMortalidadNeonatalInmediata', 'tasa de Mortalidad Neonatal Inmediata', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Indice de Mortalidad Neonatal y Perinatal al Corte'), 'tasa de mortalidad Neonatal Temprana', 'tasademortalidadNeonatalTemprana', 'tasa de mortalidad Neonatal Temprana', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Indice de Mortalidad Neonatal y Perinatal al Corte'), 'tasa de Mortalidad Neonatal Tardia', 'tasadeMortalidadNeonatalTardia', 'tasa de Mortalidad Neonatal Tardia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Consultas Registradas'), 'Promedio demendada diaria COEX', 'PromediodemendadadiariaCOEX', 'Promedio demendada diaria COEX', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Consultas Registradas'), 'Pacientes atendidos en COEX', 'PacientesatendidosenCOEX', 'Pacientes atendidos en COEX', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Consultas Registradas'), 'Pacientes atendidos en EMERGENCIA', 'PacientesatendidosenEMERGENCIA', 'Pacientes atendidos en EMERGENCIA', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Consultas Registradas'), 'Pacientes ingresados a HOSPITALIZACION', 'PacientesingresadosaHOSPITALIZACION', 'Pacientes ingresados a HOSPITALIZACION', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Consultas Registradas'), 'Pacientes Atendidos', 'PacientesAtendidos', 'Pacientes Atendidos', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Consultas Registradas'), 'Cantidad de Reingresos', 'CantidaddeReingresos', 'Cantidad de Reingresos', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Consultas Registradas'), 'Indice de Reingresos', 'IndicedeReingresos', 'Indice de Reingresos', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Consultas Registradas'), 'Estudiantes Escuela Publica', 'EstudiantesEscuelaPublica', 'Estudiantes Escuela Publica', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Consultas Registradas'), 'Personal de Salud', 'PersonaldeSalud', 'Personal de Salud', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Consultas Registradas'), 'Estadisticas Multianual Consulta Externa', 'EstadisticasMultianualConsultaExterna', 'Estadisticas Multianual Consulta Externa', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Promedio diario de consultas Especialidad'), 'Cirugía', 'Cirugía', 'Cirugía', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Promedio diario de consultas Especialidad'), 'Medicina General', 'MedicinaGeneral', 'Medicina General', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Promedio diario de consultas Especialidad'), 'Ginecología', 'Ginecología', 'Ginecología', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Promedio diario de consultas Especialidad'), 'Medicina Interna', 'MedicinaInterna', 'Medicina Interna', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Promedio diario de consultas Especialidad'), 'Nutrición', 'Nutrición', 'Nutrición', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Promedio diario de consultas Especialidad'), 'Pediatría', 'Pediatría', 'Pediatría', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Promedio diario de consultas Especialidad'), 'Psicología', 'Psicología', 'Psicología', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Promedio diario de consultas Especialidad'), 'Odontología', 'Odontología', 'Odontología', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Promedio diario de consultas Especialidad'), 'Traumatología', 'Traumatología', 'Traumatología', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Operativos'), 'Guardiania', 'Guardiania', 'Guardiania', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Operativos'), 'Jardineria', 'Jardineria', 'Jardineria', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Operativos'), 'Costurería', 'Costurería', 'Costurería', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Operativos'), 'Lavanderia', 'Lavanderia', 'Lavanderia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Operativos'), 'Insumos Utilizados', 'InsumosUtilizados', 'Insumos Utilizados', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Operativos'), 'Mantenimiento', 'Mantenimiento', 'Mantenimiento', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Intendencia'), 'Común', 'Común', 'Común', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Intendencia'), 'Inorganico', 'Inorganico', 'Inorganico', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Intendencia'), 'Punzocortante', 'Punzocortante', 'Punzocortante', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Intendencia'), 'Organo Patologico', 'OrganoPatologico', 'Organo Patologico', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Intendencia'), 'Especial', 'Especial', 'Especial', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Intendencia'), 'Desecho Farmaceutico Vencidos Solidos', 'DesechoFarmaceuticoVencidosSolidos', 'Desecho Farmaceutico Vencidos Solidos', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Intendencia'), 'áreas limpiadas intendencia', 'áreaslimpiadasintendencia', 'áreas limpiadas intendencia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Intendencia'), 'Desechos Desagregados', 'DesechosDesagregados', 'Desechos Desagregados', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Transportes'), 'Ambulancia 042BBT', 'Ambulancia042BBT', 'Ambulancia 042BBT', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Transportes'), 'Ambulancia 036BBT', 'Ambulancia036BBT', 'Ambulancia 036BBT', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Transportes'), 'Ambulancias', 'Ambulancias', 'Ambulancias', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Transportes'), 'Pick Up', 'PickUp', 'Pick Up', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Transportes'), 'Transporte', 'Transporte', 'Transporte', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Transportes'), 'Referencias', 'Referencias', 'Referencias', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Raciones entregadas a pacientes'), 'Pediatria', 'Pediatria', 'Pediatria', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Raciones entregadas a pacientes'), 'Encamamiento Mujeres', 'EncamamientoMujeres', 'Encamamiento Mujeres', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Raciones entregadas a pacientes'), 'Encamamiento Hombres', 'EncamamientoHombres', 'Encamamiento Hombres', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Raciones entregadas a pacientes'), 'Maternidad', 'Maternidad', 'Maternidad', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Raciones entregadas a pacientes'), 'Centro de Recuperación Nutricional  ( CRN )', 'CentrodeRecuperaciónNutricionalCRN', 'Centro de Recuperación Nutricional  ( CRN )', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Raciones entregadas a pacientes'), 'UNIDAD DE CUIDADOS INTENSIVOS NEONATALES ( UCIN )', 'UNIDADDECUIDADOSINTENSIVOSNEONATALESUCIN', 'UNIDAD DE CUIDADOS INTENSIVOS NEONATALES ( UCIN )', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Raciones entregadas a pacientes'), 'Emergencia', 'Emergencia', 'Emergencia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Raciones entregadas a pacientes'), 'Acompañantes Pedia', 'AcompañantesPedia', 'Acompañantes Pedia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Raciones entregadas a pacientes'), 'Acompañantes Encamamiento', 'AcompañantesEncamamiento', 'Acompañantes Encamamiento', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Raciones entregadas a pacientes'), 'ACOMPAÑANTES MENORES DE 15 AÑOS', 'ACOMPAÑANTESMENORESDE15AÑOS', 'ACOMPAÑANTES MENORES DE 15 AÑOS', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Raciones entregadas a pacientes'), 'Acompañantes CRN', 'AcompañantesCRN', 'Acompañantes CRN', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Raciones entregadas a pacientes'), 'Acompañantes UCIN', 'AcompañantesUCIN', 'Acompañantes UCIN', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Raciones entregadas a pacientes'), 'Acompañantes EMERGENCIA', 'AcompañantesEMERGENCIA', 'Acompañantes EMERGENCIA', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Raciones'), 'desyunos', 'desyunos', 'desyunos', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Raciones'), 'refaccion matutina', 'refaccionmatutina', 'refaccion matutina', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Raciones'), 'almuerzo', 'almuerzo', 'almuerzo', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Raciones'), 'refaccion despertina', 'refacciondespertina', 'refaccion despertina', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Raciones'), 'cena', 'cena', 'cena', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Raciones'), 'refaccion nocturna', 'refaccionnocturna', 'refaccion nocturna', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Raciones'), 'alimentacion enteral', 'alimentacionenteral', 'alimentacion enteral', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Raciones'), 'formulas', 'formulas', 'formulas', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Raciones'), 'subtotal', 'subtotal', 'subtotal', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Servicios Atendidos'), 'Pediatria', 'Pediatria', 'Pediatria', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Servicios Atendidos'), 'Enc. Mujeres', 'EncMujeres', 'Enc. Mujeres', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Servicios Atendidos'), 'Enc. Hombres', 'EncHombres', 'Enc. Hombres', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Servicios Atendidos'), 'Maternidad', 'Maternidad', 'Maternidad', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Servicios Atendidos'), 'CRN', 'CRN', 'CRN', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Servicios Atendidos'), 'UCIN', 'UCIN', 'UCIN', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Servicios Atendidos'), 'Emergencia', 'Emergencia', 'Emergencia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Servicios Atendidos'), 'Acomp. Pedia', 'AcompPedia', 'Acomp. Pedia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Servicios Atendidos'), 'Acomp. Encam', 'AcompEncam', 'Acomp. Encam', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Servicios Atendidos'), 'Acomp. 15 años', 'Acomp15años', 'Acomp. 15 años', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Servicios Atendidos'), 'Acomp. CRN', 'AcompCRN', 'Acomp. CRN', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Servicios Atendidos'), 'Acomp. UCIN', 'AcompUCIN', 'Acomp. UCIN', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Servicios Atendidos'), 'Acomp. Emerg', 'AcompEmerg', 'Acomp. Emerg', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Servicios Atendidos'), 'total', 'total', 'total', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Produccion de Enfermería - Emergencia y COEX'), 'Hipodermias', 'Hipodermias', 'Hipodermias', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Produccion de Enfermería - Emergencia y COEX'), 'Curaciones', 'Curaciones', 'Curaciones', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Produccion de Enfermería - Emergencia y COEX'), 'Suturas', 'Suturas', 'Suturas', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Produccion de Enfermería - Emergencia y COEX'), 'Retiro de puntos', 'Retirodepuntos', 'Retiro de puntos', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Produccion de Enfermería - Emergencia y COEX'), 'Terapia tradicionales', 'Terapiatradicionales', 'Terapia tradicionales', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Central de Equipo'), 'cantidad', 'cantidad', 'cantidad', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Central de Equipo'), 'libras', 'libras', 'libras', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Central de Equipo'), 'sop', 'sop', 'sop', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Central de Equipo'), 'emergencia', 'emergencia', 'emergencia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Camilleros'), 'Pediatria', 'Pediatria', 'Pediatria', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Camilleros'), 'Ginecología y Obstetricia', 'GinecologíayObstetricia', 'Ginecología y Obstetricia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Camilleros'), 'Area Roja', 'AreaRoja', 'Area Roja', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Camilleros'), 'Medicina Interna', 'MedicinaInterna', 'Medicina Interna', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Camilleros'), 'Cirugía', 'Cirugía', 'Cirugía', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Camilleros'), 'Traumatología', 'Traumatología', 'Traumatología', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Camilleros'), 'Aislamiento', 'Aislamiento', 'Aislamiento', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Camilleros'), 'Camillas de transporte', 'Camillasdetransporte', 'Camillas de transporte', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Trabajo Social'), 'Consejerias VIH-SIDA', 'ConsejeriasVIHSIDA', 'Consejerias VIH-SIDA', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Trabajo Social'), 'VSVS', 'VSVS', 'VSVS', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Trabajo Social'), 'Embarazo < 14', 'Embarazo14', 'Embarazo < 14', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Trabajo Social'), 'Intrafamiliar', 'Intrafamiliar', 'Intrafamiliar', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Trabajo Social'), 'Actividades Realizadas', 'ActividadesRealizadas', 'Actividades Realizadas', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Trabajo Social'), 'Seguimientos de casos', 'Seguimientosdecasos', 'Seguimientos de casos', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Trabajo Social'), 'Hojas de madre canguro', 'Hojasdemadrecanguro', 'Hojas de madre canguro', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Trabajo Social'), 'Contraindicados', 'Contraindicados', 'Contraindicados', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Programa 13'), '000-012 Servicios De Apoyo A La Recuperación De La Salud', '000012ServiciosDeApoyoALaRecuperaciónDeLaSalud', '000-012 Servicios De Apoyo A La Recuperación De La Salud', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Programa 13'), '000-012-0001 Servicios De Apoyo A La Recuperación De La Salud', '0000120001ServiciosDeApoyoALaRecuperaciónDeLaSalud', '000-012-0001 Servicios De Apoyo A La Recuperación De La Salud', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Programa 13'), '000-012-0004 Servicios De Apoyo Diagnóstico', '0000120004ServiciosDeApoyoDiagnóstico', '000-012-0004 Servicios De Apoyo Diagnóstico', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Programa 13'), '000-028 Personas Atendidas En Servicios De Recuperación De La Salud', '000028PersonasAtendidasEnServiciosDeRecuperaciónDe', '000-028 Personas Atendidas En Servicios De Recuperación De La Salud', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Programa 13'), '000-028-0001 Personas Atendidas En Consulta Externa', '0000280001PersonasAtendidasEnConsultaExterna', '000-028-0001 Personas Atendidas En Consulta Externa', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Programa 13'), '000-028-0002 Personas Atendidas En La Emergencia', '0000280002PersonasAtendidasEnLaEmergencia', '000-028-0002 Personas Atendidas En La Emergencia', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Programa 13'), '000-028-0003 Personas Atendidas En Los Servicios De Hospitalización', '0000280003PersonasAtendidasEnLosServiciosDeHospita', '000-028-0003 Personas Atendidas En Los Servicios De Hospitalización', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Programa 13'), '000-035 Niños Y Jóvenes De Escuelas Públicas Beneficiados Con Servicios De Salud', '000035NiñosYJóvenesDeEscuelasPúblicasBeneficiadosC', '000-035 Niños Y Jóvenes De Escuelas Públicas Beneficiados Con Servicios De Salud', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Programa 13'), '000-035-0001 Niños Y Jóvenes De Escuelas Públicas Beneficiados Con Servicios De Salud', '0000350001NiñosYJóvenesDeEscuelasPúblicasBeneficia', '000-035-0001 Niños Y Jóvenes De Escuelas Públicas Beneficiados Con Servicios De Salud', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Programa 13'), '000-036 Personas Atendidas Con Diagnóstico Y Tratamiento Oncológico', '000036PersonasAtendidasConDiagnósticoYTratamientoO', '000-036 Personas Atendidas Con Diagnóstico Y Tratamiento Oncológico', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Programa 13'), '000-036-0001 Personas Atendidas Con Diagnóstico Oncológico', '0000360001PersonasAtendidasConDiagnósticoOncológic', '000-036-0001 Personas Atendidas Con Diagnóstico Oncológico', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Programa 13'), 'Programa 13', 'Programa13', 'Programa 13', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Programa 13'), 'MES EJECUTADO', 'MESEJECUTADO', 'MES EJECUTADO', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Programa 14'), '001-009 Niño Y Niña Menor De 5 Años Atendido Por Infección Respiratoria Aguda', '001009NiñoYNiñaMenorDe5AñosAtendidoPorInfecciónRes', '001-009 Niño Y Niña Menor De 5 Años Atendido Por Infección Respiratoria Aguda', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Programa 14'), '001-009-0001 Niño Y Niña Menor De 5 Años Atendido Por Infección Respiratoria Aguda', '0010090001NiñoYNiñaMenorDe5AñosAtendidoPorInfecció', '001-009-0001 Niño Y Niña Menor De 5 Años Atendido Por Infección Respiratoria Aguda', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Programa 14'), '001-010 Niño Y Niña Menor De 5 Años Atendido Por Enfermedad Diarreica Aguda', '001010NiñoYNiñaMenorDe5AñosAtendidoPorEnfermedadDi', '001-010 Niño Y Niña Menor De 5 Años Atendido Por Enfermedad Diarreica Aguda', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Programa 14'), '001-010-0001 Niño Y Niña Menor De 5 Años Atendido Por Enfermedad Diarreica Aguda', '0010100001NiñoYNiñaMenorDe5AñosAtendidoPorEnfermed', '001-010-0001 Niño Y Niña Menor De 5 Años Atendido Por Enfermedad Diarreica Aguda', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Programa 14'), '001-012 Niño Y Niña Menor De 5 Años Con Diagnóstico Y Tratamiento De La Desnutrición Aguda', '001012NiñoYNiñaMenorDe5AñosConDiagnósticoYTratamie', '001-012 Niño Y Niña Menor De 5 Años Con Diagnóstico Y Tratamiento De La Desnutrición Aguda', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Programa 14'), '001-012-0001 Niño Y Niña Menor De 5 Años Con Diagnóstico Y Tratamiento De La Desnutrición Aguda Moderada', '0010120001NiñoYNiñaMenorDe5AñosConDiagnósticoYTrat', '001-012-0001 Niño Y Niña Menor De 5 Años Con Diagnóstico Y Tratamiento De La Desnutrición Aguda Moderada', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Programa 14'), '001-012-0002 Niño Y Niña Menor De 5 Años Con Diagnóstico Y Tratamiento De La Desnutrición Aguda Severa', '0010120002NiñoYNiñaMenorDe5AñosConDiagnósticoYTrat', '001-012-0002 Niño Y Niña Menor De 5 Años Con Diagnóstico Y Tratamiento De La Desnutrición Aguda Severa', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Programa 14'), 'Programa 14', 'Programa14', 'Programa 14', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Programa 15'), '002-001 Mujer Que Recibe Atención Prenatal Oportuna', '002001MujerQueRecibeAtenciónPrenatalOportuna', '002-001 Mujer Que Recibe Atención Prenatal Oportuna', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Programa 15'), '002-001-0003 Mujer Atendida Por Complicaciones Obstétricas', '0020010003MujerAtendidaPorComplicacionesObstétrica', '002-001-0003 Mujer Atendida Por Complicaciones Obstétricas', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Programa 15'), '002-002 Mujer Que Recibe Atención Del Parto Limpio Y Seguro', '002002MujerQueRecibeAtenciónDelPartoLimpioYSeguro', '002-002 Mujer Que Recibe Atención Del Parto Limpio Y Seguro', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Programa 15'), '002-002-0002 Mujer Atendida Durante El Parto Limpio Y Seguro', '0020020002MujerAtendidaDuranteElPartoLimpioYSeguro', '002-002-0002 Mujer Atendida Durante El Parto Limpio Y Seguro', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Programa 15'), '002-002-0003 Mujer Atendida Por Urgencias Obstétricas Durante El Parto', '0020020003MujerAtendidaPorUrgenciasObstétricasDura', '002-002-0003 Mujer Atendida Por Urgencias Obstétricas Durante El Parto', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Programa 15'), '002-002-0004 Mujer Atendida Durante El Puerperio', '0020020004MujerAtendidaDuranteElPuerperio', '002-002-0004 Mujer Atendida Durante El Puerperio', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Programa 15'), '002-003 Recién Nacido O Neonato Atendido', '002003ReciénNacidoONeonatoAtendido', '002-003 Recién Nacido O Neonato Atendido', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Programa 15'), '002-003-0002 Neonato Atendido En Las Primeras 24 Horas De Vida', '0020030002NeonatoAtendidoEnLasPrimeras24HorasDeVid', '002-003-0002 Neonato Atendido En Las Primeras 24 Horas De Vida', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Programa 15'), '002-003-0003 Neonato Atendido De 1 A Menor De 28 Días De Nacido', '0020030003NeonatoAtendidoDe1AMenorDe28DíasDeNacido', '002-003-0003 Neonato Atendido De 1 A Menor De 28 Días De Nacido', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Programa 15'), '002-004 Población Con Acceso A Métodos De Planificación Familiar', '002004PoblaciónConAccesoAMétodosDePlanificaciónFam', '002-004 Población Con Acceso A Métodos De Planificación Familiar', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Programa 15'), '002-004-0001 Población En Edad Reproductiva Beneficiada Con Métodos De Planificación Familiar', '0020040001PoblaciónEnEdadReproductivaBeneficiadaCo', '002-004-0001 Población En Edad Reproductiva Beneficiada Con Métodos De Planificación Familiar', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Programa 15'), '002-004-0002 Mujer Con Tamizaje Para La Detección Temprana Del Cáncer De Cérvix', '0020040002MujerConTamizajeParaLaDetecciónTempranaD', '002-004-0002 Mujer Con Tamizaje Para La Detección Temprana Del Cáncer De Cérvix', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Programa 15'), 'Programa 15', 'Programa15', 'Programa 15', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Programa 16'), '003-001 Persona Atendida Para La Prevención De Its, Vih/Sida', '003001PersonaAtendidaParaLaPrevenciónDeItsVihSida', '003-001 Persona Atendida Para La Prevención De Its, Vih/Sida', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Programa 16'), '003-001-0004 Persona Adolescente, Adulto, Adulto Mayor Y Mujer Embarazada, Que Recibe Consejería Sobre Formas De Prevención De Las Its, Vih/Sida Y El Uso Correcto Del Condón', '0030010004PersonaAdolescenteAdultoAdultoMayorYMuje', '003-001-0004 Persona Adolescente, Adulto, Adulto Mayor Y Mujer Embarazada, Que Recibe Consejería Sobre Formas De Prevención De Las Its, Vih/Sida Y El Uso Correcto Del Condón', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Programa 16'), '003-003 Víctima/Sobreviviente Atendida Por Violencia Sexual', '003003VíctimaSobrevivienteAtendidaPorViolenciaSexu', '003-003 Víctima/Sobreviviente Atendida Por Violencia Sexual', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Programa 16'), '003-003-0001 Víctima/Sobreviviente Atendida Por Violencia Sexual', '0030030001VíctimaSobrevivienteAtendidaPorViolencia', '003-003-0001 Víctima/Sobreviviente Atendida Por Violencia Sexual', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
INSERT INTO vh_variables (category_id, variable_name, variable_code, description, unit_of_measure, data_type) VALUES ((SELECT category_id FROM vh_variable_categories WHERE category_name = 'Programa 16'), 'Programa 16', 'Programa16', 'Programa 16', 'unidades', 'numeric')
ON CONFLICT DO NOTHING;
