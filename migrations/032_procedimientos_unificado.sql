-- ============================================================
-- 032_procedimientos_unificado.sql
-- MIGRACIÓN ÚNICA que reemplaza los archivos 032–073.
--
-- A diferencia de los 42 archivos anteriores (que eran limpiezas
-- one-off amarradas a los IDs del dump de producción), esta versión:
--   * es IDEMPOTENTE: se puede aplicar N veces sin duplicar ni fallar;
--   * NO usa IDs hardcodeados: toda asociación es por NOMBRE
--     normalizado (unaccent + lower + btrim);
--   * SIEMBRA el catálogo canónico de forma determinista (los 476
--     procedimientos resultantes de las fusiones 032–071, más las 54
--     áreas del cuerpo y el puente procedimiento↔área);
--   * migra los datos legacy (proce_medicos, intervenciones_quirurgicas)
--     y luego elimina las tablas/columnas legacy.
--
-- Estructura de datos resultante para procedimientos MENORES:
--   catalogo_procedimientos            (catálogo maestro único)
--   area_cuerpo_intervenida            (zonas anatómicas)
--   catalogo_procedimiento_area        (puente N:M procedimiento↔zona)
--   proce_medicos.(nino|adulto|sin_edad)_(m|f)  (desglose por edad y sexo)
--
-- NO se toca el módulo Quirófano: `procedimiento_quirofano` se conserva
-- como catálogo propio (decisión explícita). `intervenciones_quirurgicas`
-- sí recibe sus FK al catálogo maestro y la FK de zona (migración 041/042
-- reincorporadas aquí), de forma aditiva y no destructiva.
--
-- NOTA: los cambios de código de aplicación (models.py, schemas.py,
-- router.py, frontend) se hacen en una pasada posterior.
-- ============================================================

BEGIN;

CREATE EXTENSION IF NOT EXISTS unaccent;

-- ============================================================
-- 1) Catálogo de áreas del cuerpo intervenidas (zonas)
--    (reincorpora 033)
-- ============================================================
CREATE TABLE IF NOT EXISTS public.area_cuerpo_intervenida (
    id              SERIAL PRIMARY KEY,
    codigo          VARCHAR(20) UNIQUE NOT NULL,
    nombre          VARCHAR(100) NOT NULL,
    region          VARCHAR(50),
    descripcion     TEXT,
    activo          BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

INSERT INTO public.area_cuerpo_intervenida (codigo, nombre, region, descripcion) VALUES
    ('CABEZA',     'Cabeza',          'cabeza',     NULL),
    ('CARA',       'Cara',          'cabeza',     NULL),
    ('CUELLO',     'Cuello',        'cuello',     NULL),
    ('TORAX',      'Tórax',          'torax',      NULL),
    ('ABDOMEN',    'Abdomen',       'tronco',     NULL),
    ('PELVIS',     'Pelvis',        'tronco',     NULL),
    ('ESPALDA',    'Espalda',       'tronco',     NULL),
    ('MANO',       'Mano',          'mss',        'Incluye dedos de la mano'),
    ('DEDO_MANO',  'Dedo de la mano',  'mss',        NULL),
    ('MUNECA',     'Muñeca',        'mss',        NULL),
    ('CODO',       'Codo',          'mss',        NULL),
    ('HOMBRO',     'Hombro',        'mss',        NULL),
    ('BRAZO',      'Brazo',          'mss',        NULL),
    ('ANTEBRAZO',  'Antebrazo',     'mss',        NULL),
    ('PIE',        'Pie',          'msi',        'Incluye dedos del pie'),
    ('DEDO_PIE',   'Dedo del pie',  'msi',        NULL),
    ('TOBILLO',    'Tobillo',       'msi',        NULL),
    ('RODILLA',    'Rodilla',       'msi',        NULL),
    ('MUSLO',      'Muslo',          'msi',        NULL),
    ('PIERNA',     'Pierna',         'msi',        NULL),
    ('CADERA',     'Cadera',        'msi',        NULL),
    ('TALON',      'Talón',          'msi',        NULL),
    ('INGLE',      'Ingle',         'tronco',     NULL),
    ('AXILA',      'Axila',         'tronco',     NULL),
    ('GLUTEO',     'Glúteo',         'msi',        NULL),
    ('MAXILAR',    'Maxilar',       'cabeza',     NULL),
    ('MANDIBULA',  'Mandíbula',     'cabeza',     NULL),
    ('MENTON',     'Mentón',        'cabeza',     NULL),
    ('PARPADO',    'Párpado',       'cabeza',     NULL),
    ('OREJA',      'Oreja',         'cabeza',     NULL),
    ('NARIZ',      'Nariz',         'cabeza',     NULL),
    ('BOCA',       'Boca',          'cabeza',     NULL),
    ('LABIO',      'Labio',         'cabeza',     NULL),
    ('CRANEO',     'Cráneo',        'cabeza',     NULL),
    ('VULVA',      'Vulva',         'pelvis',     NULL),
    ('VAGINA',     'Vagina',        'pelvis',     NULL),
    ('UTERO',      'Útero',         'pelvis',     NULL),
    ('PROSTATA',   'Próstata',      'pelvis',     NULL),
    ('TESTICULO',  'Testículo',     'pelvis',     NULL),
    ('PENE',       'Pene',          'pelvis',     NULL),
    ('ESCROTO',    'Escroto',       'pelvis',     NULL),
    ('OJO',        'Ojo',           'cabeza',     NULL),
    ('MAMA',       'Mama',          'torax',      NULL),
    ('TIBIA',      'Tibia',         'msi',        NULL),
    ('FEMUR',      'Fémur',         'msi',        NULL),
    ('HUMERO',     'Húmero',        'mss',        NULL),
    ('RADIO',      'Radio',         'mss',        NULL),
    ('CUBITO',     'Cubito',        'mss',        NULL),
    ('PULGAR',     'Pulgar',        'mss',        'Dedo de la mano'),
    ('MENIQUE',    'Meñique',       'mss',        'Dedo de la mano'),
    ('INDICE',     'Índice',        'mss',        'Dedo de la mano'),
    ('ANULAR',     'Anular',        'mss',        'Dedo de la mano'),
    ('MEDIO',      'Medio',         'mss',        'Dedo de la mano'),
    ('BILATERAL',  'Bilateral',     'general',    'Aplica a ambos lados')
ON CONFLICT (codigo) DO NOTHING;

-- ============================================================
-- 2) Catálogo maestro único de procedimientos (reincorpora 039)
--    + semilla canónica determinista (resultado neto de 032–071)
-- ============================================================
CREATE TABLE IF NOT EXISTS public.catalogo_procedimientos (
    id                  SERIAL PRIMARY KEY,
    abreviatura         VARCHAR(10) UNIQUE,
    nombre              VARCHAR(200) NOT NULL UNIQUE,
    descripcion         TEXT,
    anestesia           INTEGER NOT NULL DEFAULT 0,
    especialidad_ref    INTEGER,
    activo              BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMP NOT NULL DEFAULT NOW()
);

DO $$
BEGIN
    IF to_regclass('public.especialidades') IS NOT NULL
       AND NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'catalogo_procedimientos_especialidad_ref_fkey') THEN
        ALTER TABLE public.catalogo_procedimientos
        ADD CONSTRAINT catalogo_procedimientos_especialidad_ref_fkey
        FOREIGN KEY (especialidad_ref) REFERENCES public.especialidades(id) ON DELETE SET NULL;
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_catalogo_procedimientos_especialidad
    ON public.catalogo_procedimientos(especialidad_ref);
CREATE INDEX IF NOT EXISTS idx_catalogo_procedimientos_activo
    ON public.catalogo_procedimientos(activo);

-- Mapa auxiliar abreviatura→id de especialidad (tolerante a que la
-- tabla no exista: si falta, especialidad_ref queda NULL).
CREATE TEMP TABLE _esp_abrev (id integer, abrev text) ON COMMIT DROP;
DO $$
BEGIN
    IF to_regclass('public.especialidades') IS NOT NULL THEN
        EXECUTE 'INSERT INTO _esp_abrev (id, abrev) SELECT id, abreviatura FROM public.especialidades';
    END IF;
END $$;

-- Semilla canónica: 476 procedimientos (abreviatura, nombre, descripcion,
-- anestesia, abreviatura_especialidad). ON CONFLICT DO NOTHING (sin target)
-- cubre las dos restricciones UNIQUE (nombre y abreviatura), corrigiendo
-- el fallo original de 039 (duplicate key en abreviatura).
INSERT INTO public.catalogo_procedimientos (abreviatura, nombre, descripcion, anestesia, especialidad_ref, activo)
SELECT v.abreviatura, v.nombre, v.descripcion, v.anestesia,
       (SELECT id FROM _esp_abrev WHERE abrev = v.esp_abrev), TRUE
FROM (VALUES
    ('CCUV', 'Catéter Umbilical Venoso', 'Colocación de catéter umbilical venoso', 0, NULL),
    ('CCUA', 'Catéter Umbilical Arterial', 'Colocación de catéter umbilical arterial', 0, NULL),
    ('CVC', 'Colocación de Catéter Venoso Central', 'Introducción de catéter largo en vena de gran calibre (subclavia, yugular, femoral) para medicamentos, nutrición parenteral o monitoreo hemodinámico.', 0, NULL),
    ('RVC', 'Retiro de Catéter Venoso Central', 'Remoción de catéter venoso central, incluyendo subclavio.', 0, NULL),
    ('SONDA', 'Colocación de Sonda', 'Inserción de sonda orogástrica, vesical (Foley) o nasogástrica.', 0, NULL),
    ('IOT', 'Intubación Endotraqueal', 'Colocación de tubo endotraqueal u orotraqueal para asegurar la vía aérea.', 0, NULL),
    ('SURF', 'Administración de Surfactante', 'Aplicación de surfactante pulmonar', 0, NULL),
    ('RCP', 'Reanimación Cardiopulmonar', 'Maniobras de reanimación cardiopulmonar', 0, NULL),
    ('IO', 'Acceso Intraóseo', 'Colocación de acceso intraóseo', 0, NULL),
    ('VENO', 'Venodisección', 'Acceso venoso mediante venodisección', 0, NULL),
    ('CURA', 'Curación de Heridas', 'Curación simple o compleja de heridas', 0, NULL),
    ('VAC', 'VAC', 'Colocación, cambio o retiro de sistema VAC (cierre asistido por vacío).', 0, NULL),
    ('SUT', 'Sutura de Herida', 'Sutura y cierre de heridas', 0, NULL),
    ('DREAB', 'Drenaje de Absceso', 'Drenaje de abscesos y colecciones', 0, NULL),
    ('DREH', 'Drenaje de Hematoma', 'Drenaje de hematomas', 0, NULL),
    ('DREQ', 'Drenaje de Quiste', 'Drenaje de quistes', 0, NULL),
    ('RETPT', 'Retiro de Puntos', 'Retiro de puntos de sutura', 0, NULL),
    ('RETGR', 'Retiro de Grapas Quirúrgicas', 'Remoción de grapas de cierre quirúrgico o quirúrgicas.', 0, NULL),
    ('BIOP', 'Biopsia', 'Toma de muestra de tejido para análisis histopatológico.', 0, NULL),
    ('EXCQ', 'Escisión de Quiste', 'Resección de quistes', 0, NULL),
    ('EXCM', 'Resección de Masa de Tejido', 'Escisión quirúrgica de una masa tumoral de tejido.', 0, NULL),
    ('TENO', 'Tenorrafia', 'Reparación quirúrgica de tendones', 1, NULL),
    ('TENOT', 'Tenotomía', 'Corte parcial o total del tendón para liberar tensión y permitir su regeneración.', 1, NULL),
    ('INJPI', 'Injerto de Piel', 'Toma y colocación de injerto cutáneo', 1, NULL),
    ('OST', 'Osteosíntesis', 'Fijación quirúrgica de hueso fracturado mediante clavos, placas, tornillos o fijadores externos.', 1, NULL),
    ('RETMO', 'Retiro de Material de Osteosíntesis', 'Retiro de placas, clavos, tornillos u otro material de osteosíntesis interna.', 0, NULL),
    ('FIJEX', 'Colocación de Fijador Externo', 'Colocación quirúrgica de fijador externo (pines y barras) para estabilización de fractura.', 1, NULL),
    ('RETFI', 'Retiro de Fijación Externa', 'Retiro del fijador externo colocado previamente.', 0, NULL),
    ('MANC', 'Manipulación Cerrada', 'Reducción o manipulación cerrada', 0, NULL),
    ('AMP', 'Amputación', 'Amputación de extremidad o segmento (dedo, mano, muñeca, supracondílea, infracondílea, raqueta).', 1, NULL),
    ('LTC', 'Liberación de Túnel Carpiano', 'Descompresión del Nervio Mediano. Apertura del retináculo flexor para liberar la presión sobre el nervio mediano a nivel del carpo.', 1, NULL),
    ('APEN', 'Apendicectomía', 'Resección quirúrgica del apéndice', 1, NULL),
    ('COLE', 'Colecistectomía', 'Resección de vesícula biliar', 1, NULL),
    ('LAPE', 'Laparotomía Exploratoria', 'Exploración quirúrgica abdominal', 1, NULL),
    ('HEMO', 'Hemorroidectomía', 'Resección quirúrgica de hemorroides', 1, NULL),
    ('PARA', 'Paracentesis', 'Punción evacuadora abdominal', 0, NULL),
    ('TORA', 'Toracentesis', 'Punción evacuadora pleural', 0, NULL),
    ('LEGR', 'Legrado Uterino', 'Legrado instrumental uterino', 1, NULL),
    ('HIST', 'Histerectomía', 'Extirpación quirúrgica del útero', 1, NULL),
    ('MIOM', 'Miomectomía', 'Resección de miomas uterinos', 1, NULL),
    ('OOF', 'Ooforectomía', 'Resección de ovario', 1, NULL),
    ('CISTE', 'Cistectomía', 'Resección de quiste', 1, NULL),
    ('CERC', 'Cerclaje Cervical', 'Cerclaje del cuello uterino', 1, NULL),
    ('EPIS', 'Episiotomía', 'Incisión perineal obstétrica', 0, NULL),
    ('COLPA', 'Colporrafia', 'Reparación quirúrgica de la pared vaginal (colporrafia anterior/posterior).', 1, NULL),
    ('BAKRI', 'Balón de Bakri', 'Colocación de balón hemostático uterino', 0, NULL),
    ('BLYN', 'Sutura B-lynch', 'Sutura compresiva uterina', 0, NULL),
    ('OTB', 'Oclusión Tubárica Bilateral', 'Esterilización femenina', 1, NULL),
    ('DIU', 'Colocación de DIU', 'Inserción de dispositivo intrauterino (DIU) como método anticonceptivo de larga duración.', 0, NULL),
    ('RDIU', 'Retiro de Dispositivo Intrauterino (diu)', 'Extracción del DIU (Dispositivo Intrauterino), incluyendo T de Cobre.', 0, NULL),
    ('PAP', 'Papanicolaou', 'Citología cervical', 0, NULL),
    ('COLPO', 'Colposcopía', 'Evaluación colposcópica', 0, NULL),
    ('ORQP', 'Orquidopexia', 'Corrección quirúrgica de testículo no descendido', 1, NULL),
    ('ORQ', 'Orquiectomía', 'Resección de testículo', 1, NULL),
    ('HIDR', 'Hidrocelectomía', 'Corrección de hidrocele', 1, NULL),
    ('POST', 'Postectomía', 'Circuncisión', 1, NULL),
    ('PROS', 'Prostatectomía', 'Resección de próstata', 1, NULL),
    ('USG', 'Ultrasonido', 'Estudio ultrasonográfico', 0, NULL),
    ('RX', 'Radiografía', 'Estudio radiológico convencional', 0, NULL),
    ('TAC', 'Tomografía Computarizada', 'Tomografía axial computarizada', 0, NULL),
    ('RMN', 'Resonancia Magnética', 'Resonancia magnética nuclear', 0, NULL),
    ('DOP', 'Doppler', 'Ultrasonido Doppler', 0, NULL),
    ('ANGIO', 'Angiografía', 'Estudio angiográfico', 0, NULL),
    ('ECG', 'Electrocardiograma', 'Registro de actividad eléctrica cardíaca', 0, NULL),
    ('EMG', 'Electromiografía', 'Estudio electrofisiológico muscular', 0, NULL),
    ('CENT', 'Centellograma', 'Estudio gammagráfico.', 0, NULL),
    ('GASO', 'Gasometría', 'Análisis de gases sanguíneos', 0, NULL),
    ('HEMC', 'Hemocultivo', 'Cultivo de sangre', 0, NULL),
    ('GLUC', 'Glucometría', 'Medición de glucosa capilar', 0, NULL),
    ('FOTO', 'Fototerapia', 'Tratamiento mediante fototerapia', 0, NULL),
    ('YESO', 'Colocación de Yeso o Férula', 'Inmovilización externa con yeso, férula posterior o canal abierto.', 0, NULL),
    ('INFIL', 'Infiltración', 'Aplicación terapéutica mediante infiltración', 0, NULL),
    ('AMEU', 'Aspiración Manual Endouterina', 'Aspiración Manual Endouterina', 1, NULL),
    ('FAST', 'Ecografía FAST', 'Ultrasonido FAST para trauma', 0, NULL),
    ('ANES', 'Procedimiento con Anestesia', 'Procedimiento clínico realizado bajo anestesia.', 0, NULL),
    ('MPC', 'Manejo de Paciente Crítico (Estancia UCI)', 'Atención clínica integral en Unidad de Cuidados Intensivos (UCI) o Shock. Servicio de estancia/hora, no procedimiento quirúrgico aislado.', 0, NULL),
    ('CART', 'Artrotomía / Revisión Articular', 'Cambio de apósitos o revisión de artrotomía previa.', 1, NULL),
    ('CMEMB', 'Cambio de Membranas', 'Cambio de apósitos y drenaje de herida con membrana.', 0, NULL),
    ('EXTF', 'Exanguinotranfusion', 'Exanguinotransfusión.', 0, NULL),
    ('PES', 'Parto Eutócico Simple (parto Vaginal)', 'Parto Eutócico Simple (Parto Vaginal) — procedimiento quirúrgico o clínico.', 0, NULL),
    ('CTI', 'Colocación de Tubo Intercostal', 'Pleurotomía cerrada o tubo de tórax para neumotórax, hemotórax o derrame pleural.', 0, NULL),
    ('EXTL', 'Extracción de Lipomas', 'Resección quirúrgica de uno o varios lipomas.', 0, NULL),
    ('RQ', 'Reseccin Quistes', 'Resección quirúrgica de quiste.', 0, NULL),
    ('CEXT', 'Extracción de Cuerpo Extraño', 'Remoción quirúrgica de un cuerpo extraño.', 0, NULL),
    ('EXPEL', 'Exploracion Pelvica', 'Exploración quirúrgica o manual de la pelvis.', 0, NULL),
    ('CI3INT', 'Cierre por Tercera Intencion', 'Cierre diferido de herida (por granulación).', 0, NULL),
    ('TERMO', 'Termocoagulacion', 'Coagulación de tejido con calor (electrocauterio).', 0, NULL),
    ('RDV', 'Reparacion de Desgarro Vagina', 'Sutura del desgarro perineal/vaginal postparto.', 0, NULL),
    ('CS', 'Colocación de Surfactante', 'Administración de surfactante pulmonar en neonatos prematuros (vía tubo endotraqueal).', 0, NULL),
    ('ART', 'Artrosentesis', 'Punción y aspiración de líquido articular (rodilla, hombro, etc.) con fines diagnósticos o terapéuticos. Procedimiento menor ambulatorio o de urgencias.', 0, NULL),
    ('COLB-LY', 'Colocación de Sutura de B-lynch', 'Sutura uterina compresiva de emergencia para hemorragia masiva postparto.', 0, NULL),
    ('PUNL', 'Puncion Lumbar', 'Extracción de líquido cefalorraquídeo para diagnóstico.', 0, NULL),
    ('HERM', 'Herniorrafia', 'Reparación quirúrgica de hernia mediante sutura directa de tejidos.', 0, NULL),
    ('RDC', 'Reparacion de Desgarro Cervical', 'Sutura del desgarro del cuello uterino postparto.', 0, NULL),
    ('EXTU', 'Extracción de Uña', 'Onicectomía: extracción de la uña afectada.', 0, NULL),
    ('RESPI', 'Retiro de Espica', 'Retiro De Espica — procedimiento quirúrgico o clínico.', 0, NULL),
    ('FIMBR', 'Fimbriectomia', 'Resección de fimbrias tubáricas.', 0, NULL),
    ('EV-TOMO', 'Tomografias', 'Estudio tomográfico computarizado.', 0, NULL),
    ('SQSV', 'Resección de Quiste Sinovial', 'Extirpación quirúrgica de quiste sinovial benigno.', 0, NULL),
    ('EXA', 'Exploracion Abdominal', 'Exploración quirúrgica de la cavidad abdominal.', 0, NULL),
    ('EDC', 'Exploracion de Cuello', 'Exploración quirúrgica del cuello.', 0, NULL),
    ('OTMIA', 'Osteotomia [otmia]', 'Corte óseo quirúrgico para corrección de deformidad.', 0, NULL),
    ('XPNR', 'Exploracion Radial', 'Exploración quirúrgica del antebrazo/muñeca.', 0, NULL),
    ('RTSL', 'Retiro Transindesmal', 'Retiro de tornillo/fijación transindesmal en tobillo.', 0, NULL),
    ('RCIM', 'Retiro de Clavos Im', 'Retiro De Clavos Im — procedimiento quirúrgico o clínico.', 0, NULL),
    ('RSFBA', 'Reseccion Fibroma', 'Resección quirúrgica de fibroma.', 0, NULL),
    ('HI', 'Hisopados', 'Resección de tumor de mama con biopsia.', 0, NULL),
    ('CDM', 'Colocación de Membrana', 'Aplicación de membrana amniótica o biológica en cirugía oftálmica, maxilofacial o de herida crónica.', 0, NULL),
    ('LSDHCCT', 'Lavado/sutura de Herida Cortocortante Traumatica', 'Limpieza y cierre de herida cortocortante traumática.', 0, NULL),
    ('RCD', 'Reconstruccion de Dedo', 'Reconstrucción quirúrgica de un dedo.', 0, NULL),
    ('DM', 'Drenaje de Membranas', 'Drenaje a través de membrana cerrada o abierta.', 0, NULL),
    ('OPI', 'Orquideopexia Inguinal', 'Fijación quirúrgica del testículo en el canal inguinal.', 0, NULL),
    ('LDS', 'Liberacion de Sinequias', 'Liberación quirúrgica de adherencias/sinequias.', 0, NULL),
    ('MCH', 'Manipulación Cerrada de Hombro', 'Manipulación cerrada de hombro.', 0, NULL),
    ('I', 'Intraóseo', 'Acceso intraóseo (vía ósea para medicación).', 0, NULL),
    ('COLDIU', 'DIU', 'Inserción o manipulación de dispositivo intrauterino (alias).', 0, NULL),
    ('NST', 'Cardiotocografía (non-stress Test)', 'Monitoreo fetal no estresante.', 0, NULL),
    ('OCT', 'Tomografía de Coherencia Óptica', 'Tomografía de coherencia óptica.', 0, NULL),
    ('BK', 'Resección de Quiste Poplíteo (Baker)', 'Exéresis o resección quirúrgica del quiste poplíteo (de Baker) detrás de la rodilla.', 0, NULL),
    ('REG', 'Regularización', 'Regularización quirúrgica (dedo de la mano).', 0, NULL),
    ('LDG', 'Liberación de Dedo en Gatillo', 'Incisión milimétrica en palma y corte de polea A1 para liberar el deslizamiento del tendón.', 0, NULL),
    ('ADT', 'Antrodesis de Tobillo', 'Fusión quirúrgica de la articulación del tobillo.', 0, NULL),
    ('AADAF', 'Ampliacion Angulo de Aparato Fijador', 'Ampliacion Angulo De Aparato Fijador — procedimiento quirúrgico o clínico.', 0, NULL),
    ('FRC', 'Fractura Radio y Cubito', 'Reducción quirúrgica de fractura radio-cubital.', 0, NULL),
    ('PR', 'Prolapso Rectal', 'Reducción de prolapso rectal.', 0, NULL),
    ('TCPO', 'Toma y Colocación de Puntos Óseos', 'Fijación directa en hueso con alambres o suturas pesadas (cerclaje) en traumatología.', 0, NULL),
    ('DEQ', 'Drenaje Ecoguiado Quiste', 'Drenaje de quiste guiado por ultrasonido.', 0, NULL),
    ('DR-E', 'Drenaje Ecoguiado', 'Drenaje de colección guiada por ultrasonido.', 0, NULL),
    ('MNA', 'Manipulacion Antebrazo', 'Reducción cerrada de fractura o luxación de antebrazo.', 0, NULL),
    ('ADR', 'Artroplastia de Rodilla', 'Reemplazo articular de rodilla (prótesis).', 1, NULL),
    ('EVF', 'Exploracion Vasos Femorales', 'Exploración quirúrgica de vasos femorales.', 0, NULL),
    ('ESCRO', 'Exploracion Escrotal', 'Exploracion Escrotal — procedimiento quirúrgico o clínico.', 0, NULL),
    ('RDLH', 'Reseccion de Lesion Hiperplasica', 'Resección quirúrgica de lesión hiperplásica.', 0, NULL),
    ('CTA', 'Criptorquidia', 'Corrección quirúrgica de testículo no descendido.', 0, NULL),
    ('AR', 'Artrodesis de Rodilla', 'Fusión quirúrgica de la articulación de la rodilla.', 1, NULL),
    ('TS', 'Tenoplastia', 'Reconstrucción plástica del tendón desgastado por inflamación crónica.', 0, NULL),
    ('RDPO', 'Regulacion de Pulpejo', 'Regulación quirúrgica del pulpejo (dedo).', 0, NULL),
    ('RDMC', 'Reseccion de Masa en Cuello', 'Resección quirúrgica de masa cervical.', 0, NULL),
    ('HDC', 'Hemiartroplastia de Cadera', 'Reemplazo parcial de la cadera.', 0, NULL),
    ('CFE', 'Colocacin Fijador Externo', 'Colocación quirúrgica de fijador externo (pines y barras).', 0, NULL),
    ('EN', 'Empaque Nasal', 'Taponamiento nasal hemostático.', 0, NULL),
    ('EVASC', 'Exploracion Vascular', 'Exploración quirúrgica de vasos sanguíneos.', 0, NULL),
    ('EMIS', 'Escarectomia Miembros Inferiores', 'Resección de tejido desvitalizado en miembros inferiores.', 0, NULL),
    ('RCA', 'Reseccion Condiloma', 'Resección quirúrgica de condiloma acuminado.', 0, NULL),
    ('EMP', 'Excision de Masa en Pie', 'Resección quirúrgica de masa tumoral en el pie.', 0, NULL),
    ('CBDB', 'Colocación de Barra Denis Browne', 'Dispositivo ortopédico pediátrico (barra metálica + botas) para corrección de pie equinovaro.', 0, NULL),
    ('RPO', 'Reseccion de Polipo', 'Resección quirúrgica de pólipo.', 0, NULL),
    ('MMUÑECA', 'Manipulacion de Muñeca', 'Reducción o manipulación cerrada de muñeca.', 0, NULL),
    ('QSEB', 'Quiste Sebaceo', 'Resección quirúrgica de quiste sebáceo.', 0, NULL),
    ('DREDD', 'Drenaje de Dedo', 'Drenaje quirúrgico de absceso o colección en dedo.', 0, NULL),
    ('DREQS', 'Drenaje de Quiste Sinovial', 'Drenaje quirúrgico o aspiración de quiste sinovial.', 0, NULL),
    ('ODM', 'Onicectomia Dedo Mano', 'Extracción quirúrgica de uña del dedo de la mano.', 0, NULL),
    ('ETORAX', 'Escarectomia en Torax', 'Resección de tejido desvitalizado (esfacelo) en tórax.', 0, NULL),
    ('VS', 'Visco Suplementacion', 'Infiltración intraarticular de ácido hialurónico.', 0, NULL),
    ('TO', 'Tubo Orotraqueal', 'Colocación de tubo orotraqueal.', 0, NULL),
    ('TCIP', 'Toma y Colocación de Injerto de Piel', 'Toma de injerto cutáneo del paciente o donante y colocación en zona receptora.', 0, NULL),
    ('FA', 'Ferula Anular', 'Colocación de férula en dedo anular.', 0, NULL),
    ('ESCQ', 'Escarotomias por Quemaduras', 'Incisiones de descarga para quemaduras circulares.', 0, NULL),
    ('RESDEGR', 'Resición de Grenoloma', 'Resección quirúrgica de granuloma.', 0, NULL),
    ('cstp', 'Cesárea', 'Parto por vía abdominal', 1, NULL),
    ('SG', 'Sonda Orogastrica', 'Inserción de sonda orogástrica.', 1, NULL),
    ('hat', 'Histerectomía Abdominal Total', 'Extirpación quirúrgica del útero por vía abdominal.', 0, NULL),
    ('use', 'Ultrasonido Endovaginal', 'Estudio ecográfico transvaginal.', 0, NULL),
    ('CV', 'Colocación de Vendajes Especializados', 'Vendaje especializado tipo Velpeau u otros vendajes de hombro y brazo.', 0, NULL),
    ('RY', 'Retiro de Yesos', 'Retiro de yeso aplicado al paciente.', 0, NULL),
    ('RV', 'Retiro de Vendajes', 'Retiro de vendaje aplicado al paciente.', 0, NULL),
    ('infeco', 'Infiltración Ecoguiada', 'Infiltración guiada por ultrasonido.', 0, NULL),
    ('LIGAU', 'Ligadura de Arteria Uterina', 'Ligadura hemostática de arterias uterinas en hemorragia.', 0, NULL),
    ('COLPFANT', 'Colporrafia Anterior', 'Reparación de pared vaginal anterior (cistocele).', 0, NULL),
    ('HV', 'Histerectomia Vaginal', 'Extirpación del útero por vía vaginal.', 0, NULL),
    ('GRE', 'Resección Quirúrgica de Granuloma', 'Exéresis, resección o cauterización quirúrgica de granuloma.', 0, NULL),
    ('ESP', 'Espirometría', 'Estudio de capacidad pulmonar.', 0, NULL),
    ('VAS', 'Vasectomía', 'vasectomía es un método anticonceptivo permanente y muy seguro para hombres', 1, NULL),
    ('MDM', 'Manipulacion de Miembro (inferior o Superior)', 'Manipulacion De Miembro (Inferior O Superior) — procedimiento quirúrgico o clínico.', 0, NULL),
    ('ROTACOL', 'Rotacion Colgajo', 'Rotación quirúrgica de colgajo cutáneo.', 0, NULL),
    ('LD', 'Lavados y Debridamientos', 'Lavado quirúrgico y retiro de tejido desvitalizado.', 1, NULL),
    ('HO', 'Histerectomia Obstetrica', 'Histerectomía de emergencia postparto.', 1, NULL),
    ('DRELI', 'Drenaje de Lipoma', 'Drenaje o evacuación de lipoma.', 1, NULL),
    ('MASC', 'Masa en Cuello', 'Resección o biopsia de masa cervical.', 1, NULL),
    ('MASL', 'Masa en Labio', 'Resección o biopsia de masa en labio.', 1, NULL),
    ('O/SRA', 'O/s Radio', 'Osteosíntesis de radio.', 1, NULL),
    ('REEMRO', 'Reemplazo de Rodillas', 'Reemplazo total de rodillas (prótesis).', 1, NULL),
    ('O/SCU', 'O/s Cubito', 'Osteosíntesis de cúbito.', 1, NULL),
    ('CISTOAB', 'Cistostomia Abierta', 'Apertura quirúrgica de la vejiga para drenaje.', 1, NULL),
    ('EXTPLA', 'Extraccion Manual de Placenta', 'Remoción manual de placenta retenida postparto.', 1, NULL),
    ('MCC', 'Manipulación Cerrada de Cadera', 'Manipulación cerrada de cadera.', 0, NULL),
    ('liu', 'Legrado Instrumental Uterino', 'Legrado uterino evacuador o diagnóstico con cureta.', 0, NULL),
    ('uso', 'Ultrasonido Obstétrico', 'Estudio ecográfico obstétrico.', 0, NULL),
    ('OUB', 'Ooforectomía Unilateral o Bilateral', 'Extirpación de uno o ambos ovarios.', 0, NULL),
    ('JADELLE', 'Implante Jadelle', 'Inserción o retiro de implante subdérmico anticonceptivo (Jadelle).', 0, NULL),
    ('COLJADE', 'Colocación de Jadelle', 'Inserción de implante subdérmico anticonceptivo (Jadelle).', 1, NULL),
    ('RJAD', 'Retiro de Jadelle', 'Retiro de implante subdérmico anticonceptivo (Jadelle).', 1, NULL),
    ('MC', 'Manipulación Cerrada (general)', 'Manipulación cerrada general.', 0, NULL),
    ('LDQ', 'Liberación de de Quervain', 'Apertura del primer compartimento dorsal para liberar los tendones abductor largo y extensor corto del pulgar.', 1, NULL),
    ('HERP', 'Hernioplastia', 'Reparación quirúrgica de hernia con colocación de malla protésica.', 1, NULL),
    (NULL, 'Cambio de terapia de presión negativa', NULL, 0, 'CIR'),
    (NULL, 'Colocación de terapia de presión negativa', NULL, 0, 'CIR'),
    (NULL, 'Retiro de terapia de presión negativa', NULL, 0, 'CIR'),
    (NULL, 'Abdominoplastia', NULL, 0, 'CIR'),
    (NULL, 'Adenoamigdalectomía', NULL, 0, 'CIR'),
    (NULL, 'Adenoidectomía', NULL, 0, 'CIR'),
    (NULL, 'Adhesiolisis', NULL, 0, 'CIR'),
    (NULL, 'Amigdalectomía', NULL, 0, 'CIR'),
    (NULL, 'Amputación de urgencia', NULL, 0, 'CIR'),
    (NULL, 'Anastomosis intestinal', NULL, 0, 'CIR'),
    (NULL, 'Angioplastia coronaria', NULL, 0, 'CIR'),
    (NULL, 'Angioplastía de acceso vascular para hemodiálisis', NULL, 0, 'CIR'),
    (NULL, 'Apendicectomía pediátrica', NULL, 0, 'PED'),
    (NULL, 'Atresias intestinales', NULL, 0, 'PED'),
    (NULL, 'Banding', NULL, 0, 'CIR'),
    (NULL, 'Biopsia cervical', NULL, 0, 'GIN'),
    (NULL, 'Biopsia excisional', NULL, 0, 'CIR'),
    (NULL, 'Biopsia incisional', NULL, 0, 'CIR'),
    (NULL, 'Biopsia quirúrgica', NULL, 0, 'CIR'),
    (NULL, 'Biopsia renal abierta', NULL, 0, 'CIR'),
    (NULL, 'Biopsia renal percutánea', NULL, 0, 'CIR'),
    (NULL, 'Blefaroplastia', NULL, 0, 'CIR'),
    (NULL, 'Broncoscopia', NULL, 0, 'CIR'),
    (NULL, 'Bypass coronario', NULL, 0, 'CIR'),
    (NULL, 'Bypass femoropoplíteo', NULL, 0, 'CIR'),
    (NULL, 'Bypass gástrico', NULL, 0, 'CIR'),
    (NULL, 'Cateterismo cardíaco', NULL, 0, 'CIR'),
    (NULL, 'Cauterización', NULL, 0, 'CIR'),
    (NULL, 'Cesárea de emergencia', NULL, 0, 'CIR'),
    (NULL, 'Cierre de herida', NULL, 0, 'CIR'),
    (NULL, 'Cierre de ostomías', NULL, 0, 'CIR'),
    (NULL, 'Circuncisión', NULL, 0, 'PED'),
    (NULL, 'Cirugía de aneurisma cerebral', NULL, 0, 'CIR'),
    (NULL, 'Cirugía de aorta torácica', NULL, 0, 'CIR'),
    (NULL, 'Cirugía de catarata', NULL, 0, 'CIR'),
    (NULL, 'Hemiartroplastia', NULL, 0, 'TRA'),
    (NULL, 'Cirugía de columna vertebral', NULL, 0, 'CIR'),
    (NULL, 'Cirugía de diverticulitis', NULL, 0, 'CIR'),
    (NULL, 'Cirugía de hidrocele', NULL, 0, 'CIR'),
    (NULL, 'Catéter umbilical (arterial/venoso)', NULL, 0, 'TRA'),
    (NULL, 'Artrodesis', NULL, 0, 'TRA'),
    (NULL, 'Cirugía de quistes hepáticos', NULL, 0, 'CIR'),
    (NULL, 'Cirugía de quistes sebáceos', NULL, 0, 'CIR'),
    (NULL, 'Cirugía de sarcomas', NULL, 0, 'CIR'),
    (NULL, 'Cirugía de tiroides', NULL, 0, 'CIR'),
    (NULL, 'Cirugía de tumores cerebrales', NULL, 0, 'CIR'),
    (NULL, 'Cirugía de varicocele', NULL, 0, 'CIR'),
    (NULL, 'Cirugía endoscópica nasal', NULL, 0, 'CIR'),
    (NULL, 'Cirugía hepatobiliar', NULL, 0, 'CIR'),
    (NULL, 'Cirugía ortognática', NULL, 0, 'CIR'),
    (NULL, 'Cirugía paliativa oncológica', NULL, 0, 'CIR'),
    (NULL, 'Cirugía pancreática', NULL, 0, 'CIR'),
    (NULL, 'Cirugía por prolapso genital', NULL, 0, 'GIN'),
    (NULL, 'Cirugía vascular periférica', NULL, 0, 'CIR'),
    (NULL, 'Cistolitotomía', NULL, 0, 'CIR'),
    (NULL, 'Cistoscopia', NULL, 0, 'CIR'),
    (NULL, 'Colectomía', NULL, 0, 'CIR'),
    (NULL, 'Colectomía oncológica', NULL, 0, 'CIR'),
    (NULL, 'Colgajo cutáneo', NULL, 0, 'CIR'),
    (NULL, 'Colocación de arco de Erich', NULL, 0, 'CIR'),
    (NULL, 'Colocación de catéter doble J', NULL, 0, 'CIR'),
    (NULL, 'Colocación de catéter para diálisis peritoneal', NULL, 0, 'CIR'),
    (NULL, 'Colocación de catéter para hemodiálisis (temporal)', NULL, 0, 'CIR'),
    (NULL, 'Colocación de catéter tunelizado para hemodiálisis', NULL, 0, 'CIR'),
    (NULL, 'Colocación de injerto arteriovenoso para diálisis', NULL, 0, 'CIR'),
    (NULL, 'Colonoscopia', NULL, 0, 'CIR'),
    (NULL, 'Colostomía', NULL, 0, 'CIR'),
    (NULL, 'Colporrafia posterior', NULL, 0, 'GIN'),
    (NULL, 'Conización cervical', NULL, 0, 'GIN'),
    (NULL, 'Control de daños', NULL, 0, 'CIR'),
    (NULL, 'Control de hemorragias', NULL, 0, 'CIR'),
    (NULL, 'Corrección de atresia intestinal', NULL, 0, 'PED'),
    (NULL, 'Artrocentesis', NULL, 0, 'TRA'),
    (NULL, 'Antrodesis', NULL, 0, 'TRA'),
    (NULL, 'Corrección de labio y paladar hendido', NULL, 0, 'PED'),
    (NULL, 'CPRE', NULL, 0, 'CIR'),
    (NULL, 'Craneotomía', NULL, 0, 'CIR'),
    (NULL, 'Craniectomía', NULL, 0, 'CIR'),
    (NULL, 'Craniectomía descompresiva', NULL, 0, 'CIR'),
    (NULL, 'Creación de fístula arteriovenosa (braquiocefálica)', NULL, 0, 'CIR'),
    (NULL, 'Creación de fístula arteriovenosa (radiocefálica)', NULL, 0, 'CIR'),
    (NULL, 'Cuadrantectomía', NULL, 0, 'CIR'),
    (NULL, 'Debridamiento quirúrgico', NULL, 0, 'CIR'),
    (NULL, 'Debulking tumoral', NULL, 0, 'CIR'),
    (NULL, 'Decorticación pleural', NULL, 0, 'CIR'),
    (NULL, 'Decorticación pulmonar', NULL, 0, 'CIR'),
    (NULL, 'Decortificación de riñón', NULL, 0, 'CIR'),
    (NULL, 'Dedo en gatillo', NULL, 0, 'CIR'),
    (NULL, 'Derivación ventriculoperitoneal', NULL, 0, 'CIR'),
    (NULL, 'Desbridamiento de tejidos infectados', NULL, 0, 'CIR'),
    (NULL, 'Discectomía', NULL, 0, 'CIR'),
    (NULL, 'Disección axilar', NULL, 0, 'CIR'),
    (NULL, 'Disección cervical', NULL, 0, 'CIR'),
    (NULL, 'Drenaje biliar', NULL, 0, 'CIR'),
    (NULL, 'Drenaje de absceso renal', NULL, 0, 'CIR'),
    (NULL, 'Drenaje de abscesos profundos', NULL, 0, 'CIR'),
    (NULL, 'Drenaje epidural', NULL, 0, 'CIR'),
    (NULL, 'Drenaje torácico', NULL, 0, 'CIR'),
    (NULL, 'Embarazo ectópico', NULL, 0, 'GIN'),
    (NULL, 'Embolectomía', NULL, 0, 'CIR'),
    (NULL, 'Endarterectomía carotídea', NULL, 0, 'CIR'),
    (NULL, 'Endoscopía + dilatación', NULL, 0, 'CIR'),
    (NULL, 'Endoscopia digestiva alta', NULL, 0, 'CIR'),
    (NULL, 'Endoscopía y toma de biopsia', NULL, 0, 'CIR'),
    (NULL, 'Enterectomía', NULL, 0, 'CIR'),
    (NULL, 'Esplenectomía', NULL, 0, 'CIR'),
    (NULL, 'Estenosis pilórica', NULL, 0, 'PED'),
    (NULL, 'Estimulación cerebral profunda', NULL, 0, 'CIR'),
    (NULL, 'Evacuación de hematomas', NULL, 0, 'CIR'),
    (NULL, 'Eventrorrafia', NULL, 0, 'CIR'),
    (NULL, 'Extracción de cuerpos extraños', NULL, 0, 'CIR'),
    (NULL, 'Extracción de terceros molares', NULL, 0, 'CIR'),
    (NULL, 'Fasciotomía urgente', NULL, 0, 'CIR'),
    (NULL, 'Fenestración laparoscópica de quiste renal', NULL, 0, 'CIR'),
    (NULL, 'Tratamiento quirúrgico de fractura expuesta', NULL, 0, 'TRA'),
    (NULL, 'Fístula arteriovenosa', NULL, 0, 'CIR'),
    (NULL, 'Fistulectomía', NULL, 0, 'CIR'),
    (NULL, 'Fisurotomía', NULL, 0, 'CIR'),
    (NULL, 'Funduplicatura', NULL, 0, 'CIR'),
    (NULL, 'Fusión vertebral', NULL, 0, 'CIR'),
    (NULL, 'Gastrectomía oncológica', NULL, 0, 'CIR'),
    (NULL, 'Gastrectomía subtotal', NULL, 0, 'CIR'),
    (NULL, 'Gastrectomía total', NULL, 0, 'CIR'),
    (NULL, 'Gastroscopía', NULL, 0, 'MI'),
    (NULL, 'Gastrostomía', NULL, 0, 'CIR'),
    (NULL, 'Gastrostomía pediátrica', NULL, 0, 'PED'),
    (NULL, 'Hemicolectomía derecha', NULL, 0, 'CIR'),
    (NULL, 'Hemicolectomía izquierda', NULL, 0, 'CIR'),
    (NULL, 'Hepatectomía', NULL, 0, 'CIR'),
    (NULL, 'Hernioplastía incisional', NULL, 0, 'CIR'),
    (NULL, 'Hernioplastía inguinal', NULL, 0, 'CIR'),
    (NULL, 'Hernioplastía umbilical', NULL, 0, 'CIR'),
    (NULL, 'Herniorrafia inguinal pediátrica', NULL, 0, 'PED'),
    (NULL, 'Histerectomía abdominal', NULL, 0, 'GIN'),
    (NULL, 'Histerectomía laparoscópica', NULL, 0, 'GIN'),
    (NULL, 'Histerectomía quirúrgica', NULL, 0, 'GIN'),
    (NULL, 'Ileostomía', NULL, 0, 'CIR'),
    (NULL, 'Implantación de marcapasos', NULL, 0, 'CIR'),
    (NULL, 'Infección del tracto urinario (UTI)', NULL, 0, 'CIR'),
    (NULL, 'Síndrome compartimental (fasciotomía)', NULL, 0, 'TRA'),
    (NULL, 'Invaginación intestinal', NULL, 0, 'PED'),
    (NULL, 'Laminectomía', NULL, 0, 'CIR'),
    (NULL, 'Laparoscopía diagnóstica', NULL, 0, 'CIR'),
    (NULL, 'Laparoscopía ginecológica', NULL, 0, 'GIN'),
    (NULL, 'Laparotomía de urgencia', NULL, 0, 'CIR'),
    (NULL, 'Laparotomía exploradora', NULL, 0, 'CIR'),
    (NULL, 'Laringectomía', NULL, 0, 'CIR'),
    (NULL, 'LASIK', NULL, 0, 'CIR'),
    (NULL, 'Lavado y desbridamiento', NULL, 0, 'CIR'),
    (NULL, 'Lavado y desbridamiento por quemadura', NULL, 0, 'CIR'),
    (NULL, 'Levantamiento óseo frontal', NULL, 0, 'CIR'),
    (NULL, 'Reparación de tendones', NULL, 0, 'TRA'),
    (NULL, 'Ligadura de trompas', NULL, 0, 'GIN'),
    (NULL, 'Ligadura tubárica', NULL, 0, 'GIN'),
    (NULL, 'Linfadenectomía', NULL, 0, 'CIR'),
    (NULL, 'Litotricia', NULL, 0, 'CIR'),
    (NULL, 'Lobectomía pulmonar', NULL, 0, 'CIR'),
    (NULL, 'Malformaciones anorrectales', NULL, 0, 'PED'),
    (NULL, 'Malformaciones congénitas', NULL, 0, 'PED'),
    (NULL, 'Mamoplastia reductora', NULL, 0, 'CIR'),
    (NULL, 'Reparación de ligamentos', NULL, 0, 'TRA'),
    (NULL, 'Manejo de quemaduras', NULL, 0, 'CIR'),
    (NULL, 'Manejo quirúrgico de trauma abdominal', NULL, 0, 'CIR'),
    (NULL, 'Manga gástrica', NULL, 0, 'CIR'),
    (NULL, 'Marsupialización de quiste de Bartolino', NULL, 0, 'GIN'),
    (NULL, 'Marsupialización de quiste renal', NULL, 0, 'CIR'),
    (NULL, 'Mastectomía', NULL, 0, 'CIR'),
    (NULL, 'Mastoidectomía', NULL, 0, 'CIR'),
    (NULL, 'Mediastinoscopia', NULL, 0, 'CIR'),
    (NULL, 'Reemplazo de rodilla', NULL, 0, 'TRA'),
    (NULL, 'Microlaringoscopía', NULL, 0, 'CIR'),
    (NULL, 'Nefrectomía', NULL, 0, 'CIR'),
    (NULL, 'Nefrectomía parcial', NULL, 0, 'CIR'),
    (NULL, 'Nefrectomía radical', NULL, 0, 'CIR'),
    (NULL, 'Nefrectomía simple', NULL, 0, 'CIR'),
    (NULL, 'Nefrolitotomía percutánea', NULL, 0, 'CIR'),
    (NULL, 'Nefrostomía', NULL, 0, 'CIR'),
    (NULL, 'Nefrostomía percutánea', NULL, 0, 'CIR'),
    (NULL, 'Nefroureterectomía', NULL, 0, 'CIR'),
    (NULL, 'Neumonectomía', NULL, 0, 'CIR'),
    (NULL, 'Reemplazo de cadera', NULL, 0, 'TRA'),
    (NULL, 'Reducción cerrada de fractura', NULL, 0, 'TRA'),
    (NULL, 'Osteotomía mandibular', NULL, 0, 'CIR'),
    (NULL, 'Otoplastia', NULL, 0, 'CIR'),
    (NULL, 'Pancreatectomía', NULL, 0, 'CIR'),
    (NULL, 'Pancreatectomía oncológica', NULL, 0, 'CIR'),
    (NULL, 'Paratiroidectomía', NULL, 0, 'CIR'),
    (NULL, 'Pericardiocentesis quirúrgica', NULL, 0, 'CIR'),
    (NULL, 'Pieloplastía', NULL, 0, 'CIR'),
    (NULL, 'Piloromiotomía', NULL, 0, 'PED'),
    (NULL, 'Piloroplastía', NULL, 0, 'CIR'),
    (NULL, 'Pleurodesis', NULL, 0, 'CIR'),
    (NULL, 'Polipectomía endoscópica', NULL, 0, 'CIR'),
    (NULL, 'Polipectomía nasal', NULL, 0, 'CIR'),
    (NULL, 'Queratoplastia', NULL, 0, 'CIR'),
    (NULL, 'Quistectomía ovárica', NULL, 0, 'GIN'),
    (NULL, 'Reconstrucción facial', NULL, 0, 'CIR'),
    (NULL, 'Reconstrucción mamaria', NULL, 0, 'CIR'),
    (NULL, 'Reconstrucción maxilar', NULL, 0, 'CIR'),
    (NULL, 'Reducción abierta y fijación interna (RAFI)', NULL, 0, 'TRA'),
    (NULL, 'Osteostomía', NULL, 0, 'TRA'),
    (NULL, 'Reducción de fractura facial', NULL, 0, 'CIR'),
    (NULL, 'Meniscectomía', NULL, 0, 'TRA'),
    (NULL, 'Reemplazo valvular', NULL, 0, 'CIR'),
    (NULL, 'Reexploración abdominal y cierre por planos', NULL, 0, 'CIR'),
    (NULL, 'Reimplante de uréter', NULL, 0, 'CIR'),
    (NULL, 'Remodelación de Colostomía', NULL, 0, 'CIR'),
    (NULL, 'Reparación de aneurismas', NULL, 0, 'CIR'),
    (NULL, 'Reparación de desgarros obstétricos', NULL, 0, 'GIN'),
    (NULL, 'Reparación de desprendimiento de retina', NULL, 0, 'CIR'),
    (NULL, 'Reparación de fístula arteriovenosa', NULL, 0, 'CIR'),
    (NULL, 'Reparación de fractura facial', NULL, 0, 'CIR'),
    (NULL, 'Reparación de fracturas craneales', NULL, 0, 'CIR'),
    (NULL, 'Reparación de hernias', NULL, 0, 'CIR'),
    (NULL, 'Reparación de lesiones complejas', NULL, 0, 'CIR'),
    (NULL, 'Manejo conservador', NULL, 0, 'TRA'),
    (NULL, 'Reparación de perforaciones gastrointestinales', NULL, 0, 'CIR'),
    (NULL, 'Reparación de prolapso uterino', NULL, 0, 'GIN'),
    (NULL, 'Liberación del túnel carpiano', NULL, 0, 'TRA'),
    (NULL, 'Reparación valvular', NULL, 0, 'CIR'),
    (NULL, 'Reparación vascular', NULL, 0, 'CIR'),
    (NULL, 'Resección de lipomas', NULL, 0, 'CIR'),
    (NULL, 'Resección de tejido', NULL, 0, 'CIR'),
    (NULL, 'Resección de tumor cerebral', NULL, 0, 'CIR'),
    (NULL, 'Resección de tumores', NULL, 0, 'CIR'),
    (NULL, 'Resección de tumores de piel y tejidos blandos', NULL, 0, 'CIR'),
    (NULL, 'Resección de tumores maxilares', NULL, 0, 'CIR'),
    (NULL, 'Resección de tumores mediastinales', NULL, 0, 'CIR'),
    (NULL, 'Resección hepática', NULL, 0, 'CIR'),
    (NULL, 'Resección intestinal', NULL, 0, 'CIR'),
    (NULL, 'Resección transuretral de próstata', NULL, 0, 'CIR'),
    (NULL, 'Retiro de catéter para diálisis peritoneal', NULL, 0, 'CIR'),
    (NULL, 'Retiro de catéter para hermodiálisis', NULL, 0, 'CIR'),
    (NULL, 'Revisión o recambio de catéter peritoneal', NULL, 0, 'CIR'),
    (NULL, 'Revisión quirúrgica de acceso vascular', NULL, 0, 'CIR'),
    (NULL, 'Rinoplastia', NULL, 0, 'CIR'),
    (NULL, 'Salpingectomía', NULL, 0, 'GIN'),
    (NULL, 'Salpingooforectomía', NULL, 0, 'GIN'),
    (NULL, 'Septoplastia', NULL, 0, 'CIR'),
    (NULL, 'Sigmoidectomía', NULL, 0, 'CIR'),
    (NULL, 'Infección en sitio quirúrgico', NULL, 0, 'TRA'),
    (NULL, 'Sutura de heridas', NULL, 0, 'CIR'),
    (NULL, 'Fijador externo', NULL, 0, 'TRA'),
    (NULL, 'Timpanoplastia', NULL, 0, 'CIR'),
    (NULL, 'Tiroidectomía oncológica', NULL, 0, 'CIR'),
    (NULL, 'Tiroidectomía parcial', NULL, 0, 'CIR'),
    (NULL, 'Tiroidectomía total', NULL, 0, 'CIR'),
    (NULL, 'Toracotomía', NULL, 0, 'CIR'),
    (NULL, 'Toracotomía de emergencia', NULL, 0, 'CIR'),
    (NULL, 'Trabeculectomía', NULL, 0, 'CIR'),
    (NULL, 'Transposición de vena basílica', NULL, 0, 'CIR'),
    (NULL, 'Traqueostomía', NULL, 0, 'CIR'),
    (NULL, 'Trasplante cardíaco', NULL, 0, 'CIR'),
    (NULL, 'Trasplante de médula ósea', NULL, 0, 'CIR'),
    (NULL, 'Trasplante hepático', NULL, 0, 'CIR'),
    (NULL, 'Trasplante pancreático', NULL, 0, 'CIR'),
    (NULL, 'Trasplante pulmonar', NULL, 0, 'CIR'),
    (NULL, 'Trasplante renal', NULL, 0, 'CIR'),
    (NULL, 'Tratamiento quirúrgico de endometriosis', NULL, 0, 'GIN'),
    (NULL, 'Fijación percutánea', NULL, 0, 'TRA'),
    (NULL, 'Tratamiento quirúrgico del sangrado digestivo', NULL, 0, 'CIR'),
    (NULL, 'Trombectomía', NULL, 0, 'CIR'),
    (NULL, 'Trombectomía de fístula arteriovenosa', NULL, 0, 'CIR'),
    (NULL, 'Tumorectomía', NULL, 0, 'CIR'),
    (NULL, 'Ureterolitotomía', NULL, 0, 'CIR'),
    (NULL, 'Ureteroscopia', NULL, 0, 'CIR'),
    (NULL, 'Vagotomía', NULL, 0, 'CIR'),
    (NULL, 'Varicectomía', NULL, 0, 'CIR'),
    (NULL, 'Varicocelectomía', NULL, 0, 'CIR'),
    (NULL, 'Vitrectomía', NULL, 0, 'CIR'),
    (NULL, 'Yeyunostomía', NULL, 0, 'CIR'),
    (NULL, 'Fijación externa', NULL, 0, 'TRA'),
    (NULL, 'Corrección de escoliosis', NULL, 0, 'TRA'),
    (NULL, 'Corrección de deformidades', NULL, 0, 'TRA'),
    (NULL, 'Cirugía de pie', NULL, 0, 'TRA'),
    (NULL, 'Biopsia Tru-Cut', NULL, 0, 'CIR'),
    (NULL, 'Cirugía de mano', NULL, 0, 'TRA'),
    (NULL, 'Cirugía de columna', NULL, 0, 'TRA'),
    (NULL, 'Artroscopía', NULL, 0, 'TRA'),
    (NULL, 'Reparación de desgarro cervical/vaginal', NULL, 0, 'GIN'),
    (NULL, 'Artroplastia', NULL, 0, 'TRA')
) AS v(abreviatura, nombre, descripcion, anestesia, esp_abrev)
ON CONFLICT DO NOTHING;

-- ============================================================
-- 3) proce_medicos: enlace al catálogo maestro y a la zona
--    (reincorpora 040 y 042)
-- ============================================================
DO $$
BEGIN
    IF to_regclass('public.proce_medicos') IS NULL THEN
        RAISE NOTICE 'proce_medicos no existe: se omite su normalizacion.';
        RETURN;
    END IF;

    ALTER TABLE public.proce_medicos
        ADD COLUMN IF NOT EXISTS id_catalogo_procedimiento INTEGER,
        ADD COLUMN IF NOT EXISTS id_area_cuerpo_intervenida INTEGER;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'proce_medicos_id_catalogo_procedimiento_fkey') THEN
        ALTER TABLE public.proce_medicos
        ADD CONSTRAINT proce_medicos_id_catalogo_procedimiento_fkey
        FOREIGN KEY (id_catalogo_procedimiento) REFERENCES public.catalogo_procedimientos(id) ON DELETE SET NULL;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'proce_medicos_id_area_cuerpo_intervenida_fkey') THEN
        ALTER TABLE public.proce_medicos
        ADD CONSTRAINT proce_medicos_id_area_cuerpo_intervenida_fkey
        FOREIGN KEY (id_area_cuerpo_intervenida) REFERENCES public.area_cuerpo_intervenida(id) ON DELETE SET NULL;
    END IF;

    CREATE INDEX IF NOT EXISTS idx_pm_catalogo ON public.proce_medicos(id_catalogo_procedimiento);
    CREATE INDEX IF NOT EXISTS idx_pm_area_cuerpo ON public.proce_medicos(id_area_cuerpo_intervenida);

    -- Backfill id_catalogo_procedimiento desde el catálogo legacy por nombre
    IF to_regclass('public.procedimientos') IS NOT NULL THEN
        EXECUTE $sql$
            UPDATE public.proce_medicos pm
            SET id_catalogo_procedimiento = c.id
            FROM public.procedimientos p
            JOIN public.catalogo_procedimientos c
              ON unaccent(lower(btrim(c.nombre))) = unaccent(lower(btrim(p.nombre)))
            WHERE pm.id_procedimiento = p.id
              AND pm.id_catalogo_procedimiento IS NULL
        $sql$;
    END IF;
END $$;

-- ============================================================
-- 4) Puente N:M catalogo_procedimientos <-> area_cuerpo_intervenida
--    (reemplaza procedimientos_area_cuerpo; conserva las 44 zonas
--     legacy remapeadas por NOMBRE normalizado)
-- ============================================================
CREATE TABLE IF NOT EXISTS public.catalogo_procedimiento_area (
    id                       SERIAL PRIMARY KEY,
    id_catalogo_procedimiento INT NOT NULL REFERENCES public.catalogo_procedimientos(id) ON DELETE CASCADE,
    id_area_cuerpo           INT NOT NULL REFERENCES public.area_cuerpo_intervenida(id) ON DELETE RESTRICT,
    lateralidad              VARCHAR(10) CHECK (lateralidad IN ('izq','der','bilateral','ninguna')),
    created_at               TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (id_catalogo_procedimiento, id_area_cuerpo)
);

CREATE INDEX IF NOT EXISTS idx_cpa_catalogo ON public.catalogo_procedimiento_area(id_catalogo_procedimiento);
CREATE INDEX IF NOT EXISTS idx_cpa_area ON public.catalogo_procedimiento_area(id_area_cuerpo);

INSERT INTO public.catalogo_procedimiento_area (id_catalogo_procedimiento, id_area_cuerpo, lateralidad)
SELECT c.id, a.id, v.lateralidad
FROM (VALUES
    ('Amputacion De Dedo', 'DEDO_MANO', 'ninguna'),
    ('Amputacion De Muñeca', 'MUNECA', 'ninguna'),
    ('Amputacion En Raqueta De Dedo', 'DEDO_MANO', 'ninguna'),
    ('Antrodesis De Tobillo', 'TOBILLO', 'ninguna'),
    ('Artrodesis Rodilla', 'RODILLA', 'ninguna'),
    ('Artroplastia De Rodilla', 'RODILLA', 'ninguna'),
    ('Drenaje De Dedo', 'DEDO_MANO', 'ninguna'),
    ('Escarectomia En Torax', 'TORAX', 'ninguna'),
    ('Excision De Masa En Pie', 'PIE', 'ninguna'),
    ('Exploracion De Cuello', 'CUELLO', 'ninguna'),
    ('Ferula Anular', 'ANULAR', 'ninguna'),
    ('Fractura Radio Y Cubito', 'CUBITO', 'ninguna'),
    ('Fractura Radio Y Cubito', 'RADIO', 'ninguna'),
    ('Fx Humero Fx Tobillo', 'HUMERO', 'ninguna'),
    ('Fx Humero Fx Tobillo', 'TOBILLO', 'ninguna'),
    ('Hemiartroplastia De Cadera', 'CADERA', 'ninguna'),
    ('HISTERECTOMIA VAGINAL', 'VAGINA', 'ninguna'),
    ('Injerto de Piel', 'PIE', 'ninguna'),
    ('Liberación de Dedo en Gatillo', 'DEDO_MANO', 'ninguna'),
    ('Manipulacion Antebrazo', 'ANTEBRAZO', 'ninguna'),
    ('Manipulacion Antebrazo', 'BRAZO', 'ninguna'),
    ('Manipulación cerrada de cadera', 'CADERA', 'ninguna'),
    ('Manipulación cerrada de hombro', 'HOMBRO', 'ninguna'),
    ('Manipulacion De Muñeca', 'MUNECA', 'ninguna'),
    ('MASA EN CUELLO', 'CUELLO', 'ninguna'),
    ('MASA EN LABIO', 'LABIO', 'ninguna'),
    ('O/S CUBITO', 'CUBITO', 'ninguna'),
    ('O/S RADIO', 'RADIO', 'ninguna'),
    ('Onicectomia Dedo Mano', 'DEDO_MANO', 'ninguna'),
    ('Onicectomia Dedo Mano', 'MANO', 'ninguna'),
    ('Osteosinteis Tobillo', 'TOBILLO', 'ninguna'),
    ('Osteosíntesis de codo', 'CODO', 'ninguna'),
    ('Osteosintesis De Tobillo', 'TOBILLO', 'ninguna'),
    ('Osteosintesis Dedo Anular', 'ANULAR', 'ninguna'),
    ('Osteosintesis Dedo Anular', 'DEDO_MANO', 'ninguna'),
    ('Osteosintesis Radio', 'RADIO', 'ninguna'),
    ('Radiografía', 'RADIO', 'ninguna'),
    ('Reconstruccion De Dedo', 'DEDO_MANO', 'ninguna'),
    ('REEMPLAZO DE RODILLAS', 'RODILLA', 'ninguna'),
    ('Regularización', 'DEDO_MANO', 'ninguna'),
    ('Reparacion De Desgarro Vagina', 'VAGINA', 'ninguna'),
    ('Reseccion De Masa En Cuello', 'CUELLO', 'ninguna'),
    ('Toma Y Colocacion De Injerto De Piel', 'PIE', 'ninguna'),
    ('Ultrasonido endovaginal', 'VAGINA', 'ninguna')
) AS v(nombre, codigo, lateralidad)
JOIN public.catalogo_procedimientos c
  ON unaccent(lower(btrim(c.nombre))) = unaccent(lower(btrim(v.nombre)))
JOIN public.area_cuerpo_intervenida a ON a.codigo = v.codigo
ON CONFLICT (id_catalogo_procedimiento, id_area_cuerpo) DO NOTHING;

-- 4.b Backfill de la zona del registro histórico desde el puente (primera zona).
DO $$
BEGIN
    IF to_regclass('public.proce_medicos') IS NULL THEN
        RETURN;
    END IF;
    UPDATE public.proce_medicos pm
    SET id_area_cuerpo_intervenida = sub.id_area_cuerpo
    FROM (
        SELECT DISTINCT ON (cpa.id_catalogo_procedimiento)
            cpa.id_catalogo_procedimiento, cpa.id_area_cuerpo
        FROM public.catalogo_procedimiento_area cpa
        ORDER BY cpa.id_catalogo_procedimiento, cpa.id_area_cuerpo
    ) sub
    WHERE pm.id_area_cuerpo_intervenida IS NULL
      AND pm.id_catalogo_procedimiento = sub.id_catalogo_procedimiento;
END $$;

-- ============================================================
-- 5) proce_medicos: desglose niño/adulto × sexo
--    niño = NEO+LAC+PRI+SEG+ADO (<18), adulto = ADU+ADM (>=18)
--    Históricos sin edad -> sin_edad_(m|f) según sexo.
-- ============================================================
DO $$
BEGIN
    IF to_regclass('public.proce_medicos') IS NULL THEN
        RETURN;
    END IF;

    ALTER TABLE public.proce_medicos
        ADD COLUMN IF NOT EXISTS nino_m     INTEGER NOT NULL DEFAULT 0,
        ADD COLUMN IF NOT EXISTS nino_f     INTEGER NOT NULL DEFAULT 0,
        ADD COLUMN IF NOT EXISTS adulto_m   INTEGER NOT NULL DEFAULT 0,
        ADD COLUMN IF NOT EXISTS adulto_f   INTEGER NOT NULL DEFAULT 0,
        ADD COLUMN IF NOT EXISTS sin_edad_m INTEGER NOT NULL DEFAULT 0,
        ADD COLUMN IF NOT EXISTS sin_edad_f INTEGER NOT NULL DEFAULT 0;

    -- 5.a Desde el desglose JSONB previo, si existe.
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name='proce_medicos' AND column_name='grupo_edad_detalle') THEN
        EXECUTE $sql$
            UPDATE public.proce_medicos SET
                nino_m = COALESCE((grupo_edad_detalle->'NEO'->>'m')::int,0)
                       + COALESCE((grupo_edad_detalle->'LAC'->>'m')::int,0)
                       + COALESCE((grupo_edad_detalle->'PRI'->>'m')::int,0)
                       + COALESCE((grupo_edad_detalle->'SEG'->>'m')::int,0)
                       + COALESCE((grupo_edad_detalle->'ADO'->>'m')::int,0),
                nino_f = COALESCE((grupo_edad_detalle->'NEO'->>'f')::int,0)
                       + COALESCE((grupo_edad_detalle->'LAC'->>'f')::int,0)
                       + COALESCE((grupo_edad_detalle->'PRI'->>'f')::int,0)
                       + COALESCE((grupo_edad_detalle->'SEG'->>'f')::int,0)
                       + COALESCE((grupo_edad_detalle->'ADO'->>'f')::int,0),
                adulto_m = COALESCE((grupo_edad_detalle->'ADU'->>'m')::int,0)
                         + COALESCE((grupo_edad_detalle->'ADM'->>'m')::int,0),
                adulto_f = COALESCE((grupo_edad_detalle->'ADU'->>'f')::int,0)
                         + COALESCE((grupo_edad_detalle->'ADM'->>'f')::int,0)
            WHERE grupo_edad_detalle IS NOT NULL
              AND nino_m=0 AND nino_f=0 AND adulto_m=0 AND adulto_f=0
              AND sin_edad_m=0 AND sin_edad_f=0
        $sql$;
    END IF;

    -- 5.b Históricos sin edad: bucket separado según sexo (cantidad intacta).
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name='proce_medicos' AND column_name='sexo') THEN
        EXECUTE $sql$
            UPDATE public.proce_medicos SET sin_edad_f = GREATEST(COALESCE(cantidad,0),0)
            WHERE sexo = 'F'
              AND nino_m=0 AND nino_f=0 AND adulto_m=0 AND adulto_f=0
              AND sin_edad_m=0 AND sin_edad_f=0
        $sql$;
        EXECUTE $sql$
            UPDATE public.proce_medicos SET sin_edad_m = GREATEST(COALESCE(cantidad,0),0)
            WHERE (sexo IS DISTINCT FROM 'F')
              AND nino_m=0 AND nino_f=0 AND adulto_m=0 AND adulto_f=0
              AND sin_edad_m=0 AND sin_edad_f=0
        $sql$;
    END IF;

    -- 5.c Fuera columnas legacy.
    ALTER TABLE public.proce_medicos
        DROP COLUMN IF EXISTS sexo,
        DROP COLUMN IF EXISTS grupo_edad_detalle,
        DROP COLUMN IF EXISTS grupo_edad,
        DROP COLUMN IF EXISTS edad,
        DROP COLUMN IF EXISTS unidad_edad,
        DROP COLUMN IF EXISTS id_procedimiento;
    ALTER TABLE public.proce_medicos DROP CONSTRAINT IF EXISTS proce_medicos_sexo_check;
    ALTER TABLE public.proce_medicos DROP CONSTRAINT IF EXISTS proce_medicos_grupo_edad_check;

    CREATE INDEX IF NOT EXISTS idx_proce_medicos_nino
        ON public.proce_medicos ((nino_m + nino_f)) WHERE (nino_m + nino_f) > 0;
    CREATE INDEX IF NOT EXISTS idx_proce_medicos_adulto
        ON public.proce_medicos ((adulto_m + adulto_f)) WHERE (adulto_m + adulto_f) > 0;
    CREATE INDEX IF NOT EXISTS idx_proce_medicos_sin_edad
        ON public.proce_medicos ((sin_edad_m + sin_edad_f)) WHERE (sin_edad_m + sin_edad_f) > 0;
END $$;

-- ============================================================
-- 6) intervenciones_quirurgicas: FK al catálogo y a la zona
--    (reincorpora 041 + unificación de zona; aditivo, no borra el texto)
-- ============================================================
DO $$
BEGIN
    IF to_regclass('public.intervenciones_quirurgicas') IS NULL THEN
        RETURN;
    END IF;

    ALTER TABLE public.intervenciones_quirurgicas
        ADD COLUMN IF NOT EXISTS procedimiento_principal_id INTEGER,
        ADD COLUMN IF NOT EXISTS procedimiento_2_id INTEGER,
        ADD COLUMN IF NOT EXISTS procedimiento_3_id INTEGER,
        ADD COLUMN IF NOT EXISTS procedimiento_4_id INTEGER,
        ADD COLUMN IF NOT EXISTS procedimiento_5_id INTEGER,
        ADD COLUMN IF NOT EXISTS id_area_cuerpo_intervenida INTEGER;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'iq_procedimiento_principal_id_fkey') THEN
        ALTER TABLE public.intervenciones_quirurgicas
        ADD CONSTRAINT iq_procedimiento_principal_id_fkey FOREIGN KEY (procedimiento_principal_id) REFERENCES public.catalogo_procedimientos(id) ON DELETE SET NULL;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'iq_procedimiento_2_id_fkey') THEN
        ALTER TABLE public.intervenciones_quirurgicas
        ADD CONSTRAINT iq_procedimiento_2_id_fkey FOREIGN KEY (procedimiento_2_id) REFERENCES public.catalogo_procedimientos(id) ON DELETE SET NULL;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'iq_procedimiento_3_id_fkey') THEN
        ALTER TABLE public.intervenciones_quirurgicas
        ADD CONSTRAINT iq_procedimiento_3_id_fkey FOREIGN KEY (procedimiento_3_id) REFERENCES public.catalogo_procedimientos(id) ON DELETE SET NULL;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'iq_procedimiento_4_id_fkey') THEN
        ALTER TABLE public.intervenciones_quirurgicas
        ADD CONSTRAINT iq_procedimiento_4_id_fkey FOREIGN KEY (procedimiento_4_id) REFERENCES public.catalogo_procedimientos(id) ON DELETE SET NULL;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'iq_procedimiento_5_id_fkey') THEN
        ALTER TABLE public.intervenciones_quirurgicas
        ADD CONSTRAINT iq_procedimiento_5_id_fkey FOREIGN KEY (procedimiento_5_id) REFERENCES public.catalogo_procedimientos(id) ON DELETE SET NULL;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'iq_id_area_cuerpo_intervenida_fkey') THEN
        ALTER TABLE public.intervenciones_quirurgicas
        ADD CONSTRAINT iq_id_area_cuerpo_intervenida_fkey FOREIGN KEY (id_area_cuerpo_intervenida) REFERENCES public.area_cuerpo_intervenida(id) ON DELETE SET NULL;
    END IF;

    CREATE INDEX IF NOT EXISTS idx_iq_proc_principal ON public.intervenciones_quirurgicas(procedimiento_principal_id);
    CREATE INDEX IF NOT EXISTS idx_iq_proc_2 ON public.intervenciones_quirurgicas(procedimiento_2_id);
    CREATE INDEX IF NOT EXISTS idx_iq_proc_3 ON public.intervenciones_quirurgicas(procedimiento_3_id);
    CREATE INDEX IF NOT EXISTS idx_iq_proc_4 ON public.intervenciones_quirurgicas(procedimiento_4_id);
    CREATE INDEX IF NOT EXISTS idx_iq_proc_5 ON public.intervenciones_quirurgicas(procedimiento_5_id);
    CREATE INDEX IF NOT EXISTS idx_iq_area_cuerpo ON public.intervenciones_quirurgicas(id_area_cuerpo_intervenida);

    UPDATE public.intervenciones_quirurgicas iq SET procedimiento_principal_id = c.id
    FROM public.catalogo_procedimientos c
    WHERE iq.procedimiento_principal IS NOT NULL AND iq.procedimiento_principal_id IS NULL
      AND unaccent(lower(btrim(c.nombre))) = unaccent(lower(btrim(iq.procedimiento_principal)));
    UPDATE public.intervenciones_quirurgicas iq SET procedimiento_2_id = c.id
    FROM public.catalogo_procedimientos c
    WHERE iq.procedimiento_2 IS NOT NULL AND iq.procedimiento_2_id IS NULL
      AND unaccent(lower(btrim(c.nombre))) = unaccent(lower(btrim(iq.procedimiento_2)));
    UPDATE public.intervenciones_quirurgicas iq SET procedimiento_3_id = c.id
    FROM public.catalogo_procedimientos c
    WHERE iq.procedimiento_3 IS NOT NULL AND iq.procedimiento_3_id IS NULL
      AND unaccent(lower(btrim(c.nombre))) = unaccent(lower(btrim(iq.procedimiento_3)));
    UPDATE public.intervenciones_quirurgicas iq SET procedimiento_4_id = c.id
    FROM public.catalogo_procedimientos c
    WHERE iq.procedimiento_4 IS NOT NULL AND iq.procedimiento_4_id IS NULL
      AND unaccent(lower(btrim(c.nombre))) = unaccent(lower(btrim(iq.procedimiento_4)));
    UPDATE public.intervenciones_quirurgicas iq SET procedimiento_5_id = c.id
    FROM public.catalogo_procedimientos c
    WHERE iq.procedimiento_5 IS NOT NULL AND iq.procedimiento_5_id IS NULL
      AND unaccent(lower(btrim(c.nombre))) = unaccent(lower(btrim(iq.procedimiento_5)));

    UPDATE public.intervenciones_quirurgicas iq SET id_area_cuerpo_intervenida = a.id
    FROM public.area_cuerpo_intervenida a
    WHERE iq.area_cuerpo_intervenida IS NOT NULL AND iq.id_area_cuerpo_intervenida IS NULL
      AND unaccent(lower(btrim(a.nombre))) = unaccent(lower(btrim(iq.area_cuerpo_intervenida)));
END $$;

-- ============================================================
-- 7) Eliminación de lo legacy (el catálogo maestro lo reemplaza).
--    NO se elimina procedimiento_quirofano (catálogo del módulo Quirófano).
-- ============================================================
DROP TABLE IF EXISTS public.procedimientos_area_cuerpo CASCADE;
DROP TABLE IF EXISTS public.procedimientos CASCADE;

-- ============================================================
-- 8) Vistas (reincorpora 043, adaptada al puente nuevo)
-- ============================================================
CREATE OR REPLACE VIEW public.v_catalogo_procedimientos AS
SELECT
    cp.id, cp.abreviatura, cp.nombre, cp.descripcion, cp.anestesia,
    cp.especialidad_ref, e.nombre AS especialidad_nombre,
    cp.activo, cp.created_at, cp.updated_at
FROM public.catalogo_procedimientos cp
LEFT JOIN public.especialidades e ON e.id = cp.especialidad_ref;

CREATE OR REPLACE VIEW public.v_areas_cuerpo AS
SELECT
    a.id, a.codigo, a.nombre, a.region, a.descripcion,
    a.activo, a.created_at, a.updated_at,
    (SELECT COUNT(*) FROM public.catalogo_procedimiento_area cpa
      WHERE cpa.id_area_cuerpo = a.id) AS total_procedimientos
FROM public.area_cuerpo_intervenida a;

COMMIT;

-- Verificación
SELECT
    (SELECT COUNT(*) FROM public.catalogo_procedimientos)      AS total_catalogo,
    (SELECT COUNT(*) FROM public.area_cuerpo_intervenida)      AS total_areas,
    (SELECT COUNT(*) FROM public.catalogo_procedimiento_area)  AS total_puente;
