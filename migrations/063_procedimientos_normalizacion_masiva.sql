-- ============================================================
-- 063_procedimientos_normalizacion_masiva.sql
-- Normaliza nombres (MAYÚSCULAS → Título con acentos) y agrega
-- descripciones clínicas a los 101 procedimientos pendientes
-- del catálogo maestro.
--
-- Criterios:
--   * Convertir TODAS LAS MAYÚSCULAS a minúsculas con Title Case
--   * Aplicar acentos correctos (Resección, Inyección, etc.)
--   * Asignar descripción clínica concisa por procedimiento
--   * Corregir typos conocidos (Reseccin → Resección, etc.)
--
-- No se fusionan procedimientos. Esto solo limpia nombres
-- y descripciones.
-- ============================================================

BEGIN;

-- Procedimientos donde ya hay descripción clínica o son válidos en mayúscula
-- Sólo normalizamos: nombre a Título, y asignamos descripción si falta.

-- ─── Ginecología / Obstetricia ───
UPDATE catalogo_procedimientos SET nombre = 'Parto Eutócico Simple', descripcion = 'Parto vaginal espontáneo sin complicaciones.' WHERE id = 92;
UPDATE catalogo_procedimientos SET nombre = 'Reparación de Desgarro Vaginal', descripcion = 'Sutura del desgarro perineal/vaginal postparto.' WHERE id = 102;
UPDATE catalogo_procedimientos SET nombre = 'Reparación de Desgarro Cervical', descripcion = 'Sutura del desgarro del cuello uterino postparto.' WHERE id = 110;
UPDATE catalogo_procedimientos SET nombre = 'Legrado Instrumental Uterino', abreviatura = 'LIU', descripcion = 'Legrado uterino evacuador o diagnóstico con cureta.' WHERE id = 250;
UPDATE catalogo_procedimientos SET nombre = 'Fimbriectomía', descripcion = 'Resección de fimbrias tubáricas.' WHERE id = 113;
UPDATE catalogo_procedimientos SET nombre = 'Histerectomía Abdominal Total', descripcion = 'Extirpación quirúrgica del útero por vía abdominal.' WHERE id = 216;
UPDATE catalogo_procedimientos SET nombre = 'Histerectomía Vaginal', descripcion = 'Extirpación del útero por vía vaginal.' WHERE id = 224;
UPDATE catalogo_procedimientos SET nombre = 'Ligadura de Arteria Uterina', descripcion = 'Ligadura hemostática de arterias uterinas en hemorragia.' WHERE id = 222;
UPDATE catalogo_procedimientos SET nombre = 'Histerectomía Obstétrica', descripcion = 'Histerectomía de emergencia postparto.' WHERE id = 234;
UPDATE catalogo_procedimientos SET nombre = 'Extracción Manual de Placenta', descripcion = 'Remoción manual de placenta retenida postparto.' WHERE id = 247;
UPDATE catalogo_procedimientos SET nombre = 'Colporrafia Anterior', descripcion = 'Reparación quirúrgica de la pared vaginal anterior (cistocele).' WHERE id = 223;
UPDATE catalogo_procedimientos SET nombre = 'Prolapso Rectal', descripcion = 'Reducción de prolapso rectal.' WHERE id = 165;
UPDATE catalogo_procedimientos SET nombre = 'Exploración Pélvica', descripcion = 'Exploración quirúrgica o manual de la pelvis.' WHERE id = 98;
UPDATE catalogo_procedimientos SET nombre = 'Drenaje de Lipoma', descripcion = 'Drenaje o evacuación de lipoma.' WHERE id = 237;

-- ─── Traumatología / Ortopedia ───
UPDATE catalogo_procedimientos SET nombre = 'Cambio de Artrotomía', abreviatura = 'CAM', descripcion = 'Cambio de apósitos o revisión de artrotomía previa.' WHERE id = 87;
UPDATE catalogo_procedimientos SET nombre = 'Cambio de Membranas', abreviatura = 'CMEMB', descripcion = 'Cambio de apósitos y drenaje de herida con membrana.' WHERE id = 90;
UPDATE catalogo_procedimientos SET nombre = 'Drenaje de Membranas', abreviatura = 'DM', descripcion = 'Drenaje a través de membrana cerrada o abierta.' WHERE id = 140;
UPDATE catalogo_procedimientos SET nombre = 'Amputación Supracondílea', descripcion = 'Amputación de fémur distal, por encima de los cóndilos.' WHERE id = 147;
UPDATE catalogo_procedimientos SET nombre = 'Amputación Infracondílea', descripcion = 'Amputación de tibia, por debajo de los cóndilos femorales.' WHERE id = 162;
UPDATE catalogo_procedimientos SET nombre = 'Amputación en Raqueta de Dedo', descripcion = 'Amputación quirúrgica de dedo con colgajo en raqueta.' WHERE id = 120;
UPDATE catalogo_procedimientos SET nombre = 'Reconstrucción de Dedo', descripcion = 'Reconstrucción quirúrgica de un dedo (lesión o amputación parcial).' WHERE id = 137;
UPDATE catalogo_procedimientos SET nombre = 'Manipulación de Antebrazo', descripcion = 'Reducción cerrada de fractura o luxación de antebrazo.' WHERE id = 169;
UPDATE catalogo_procedimientos SET nombre = 'Artroplastia de Rodilla', descripcion = 'Reemplazo articular de rodilla.' WHERE id = 170;
UPDATE catalogo_procedimientos SET nombre = 'Artrodesis de Rodilla', descripcion = 'Fusión quirúrgica de la articulación de la rodilla.' WHERE id = 175;
UPDATE catalogo_procedimientos SET nombre = 'Hemiartroplastia de Cadera', descripcion = 'Reemplazo parcial de la cadera.' WHERE id = 179;
UPDATE catalogo_procedimientos SET nombre = 'Antrodesis de Tobillo', abreviatura = 'ADT', descripcion = 'Fusión quirúrgica de la articulación del tobillo.' WHERE id = 160;
UPDATE catalogo_procedimientos SET nombre = 'Osteotomía', abreviatura = 'OTMIA', descripcion = 'Corte óseo quirúrgico para corrección de deformidad.' WHERE id = 125;
UPDATE catalogo_procedimientos SET nombre = 'Fractura Radio y Cúbito', abreviatura = 'FRC', descripcion = 'Reducción quirúrgica o tratamiento de fractura radio-cubital.' WHERE id = 164;
UPDATE catalogo_procedimientos SET nombre = 'Resección de Masa en Cuello', descripcion = 'Resección quirúrgica de masa cervical.' WHERE id = 178;
UPDATE catalogo_procedimientos SET nombre = 'Resección de Fibroma', descripcion = 'Resección quirúrgica de fibroma.' WHERE id = 129;
UPDATE catalogo_procedimientos SET nombre = 'Resección de Pólipo', descripcion = 'Resección quirúrgica de pólipo.' WHERE id = 190;
UPDATE catalogo_procedimientos SET nombre = 'Resección Condiloma', descripcion = 'Resección quirúrgica de condiloma acuminado.' WHERE id = 186;
UPDATE catalogo_procedimientos SET nombre = 'Resección Quiste', abreviatura = 'RQ', descripcion = 'Resección quirúrgica de quiste.' WHERE id = 96;
UPDATE catalogo_procedimientos SET nombre = 'Resección de Lesión Hiperplásica', descripcion = 'Resección quirúrgica de lesión hiperplásica.' WHERE id = 173;
UPDATE catalogo_procedimientos SET nombre = 'Regulación de Pulpejo', descripcion = 'Regulación quirúrgica del pulpejo (dedo).' WHERE id = 177;
UPDATE catalogo_procedimientos SET nombre = 'Liberación de Sinequias', descripcion = 'Liberación quirúrgica de adherencias/sinequias.' WHERE id = 151;
UPDATE catalogo_procedimientos SET nombre = 'Retiro Transindesmal', descripcion = 'Retiro de tornillo/fijación transindesmal en tobillo.' WHERE id = 127;
UPDATE catalogo_procedimientos SET nombre = 'Exploración Radial', descripcion = 'Exploración quirúrgica del antebrazo/muñeca.' WHERE id = 126;
UPDATE catalogo_procedimientos SET nombre = 'Exploración de Cuello', descripcion = 'Exploración quirúrgica del cuello.' WHERE id = 122;
UPDATE catalogo_procedimientos SET nombre = 'Exploración Vascular', descripcion = 'Exploración quirúrgica de vasos sanguíneos.' WHERE id = 184;
UPDATE catalogo_procedimientos SET nombre = 'Exploración Vasos Femorales', descripcion = 'Exploración quirúrgica de vasos femorales.' WHERE id = 171;
UPDATE catalogo_procedimientos SET nombre = 'Escarectomía en Tórax', descripcion = 'Resección de tejido desvitalizado (esfacelo) en tórax.' WHERE id = 197;
UPDATE catalogo_procedimientos SET nombre = 'Escarectomía Miembros Inferiores', descripcion = 'Resección de tejido desvitalizado en miembros inferiores.' WHERE id = 185;
UPDATE catalogo_procedimientos SET nombre = 'Escarotomías por Quemaduras', descripcion = 'Incisiones de descarga para quemaduras circulares.' WHERE id = 208;
UPDATE catalogo_procedimientos SET nombre = 'Rotación Colgajo', descripcion = 'Rotación quirúrgica de colgajo cutáneo.' WHERE id = 232;
UPDATE catalogo_procedimientos SET nombre = 'Manipulación de Muñeca', descripcion = 'Reducción o manipulación cerrada de muñeca.' WHERE id = 191;
UPDATE catalogo_procedimientos SET nombre = 'Lavado y Sutura de Herida Cortocortante Traumática', descripcion = 'Limpieza y cierre de herida cortocortante traumática.' WHERE id = 134;
UPDATE catalogo_procedimientos SET nombre = 'Manipulación Cerrada de Hombro', descripcion = 'Reducción cerrada de luxación o fractura de hombro.' WHERE id = 152;
UPDATE catalogo_procedimientos SET nombre = 'Manipulación Cerrada de Cadera', descripcion = 'Reducción cerrada de luxación o fractura de cadera.' WHERE id = 248;
UPDATE catalogo_procedimientos SET nombre = 'Manipulación Cerrada (General)', descripcion = 'Reducción cerrada de fractura/luxación (general).' WHERE id = 256;
UPDATE catalogo_procedimientos SET nombre = 'Onicectomía Dedo Mano', descripcion = 'Extracción quirúrgica de uña del dedo de la mano.' WHERE id = 196;
UPDATE catalogo_procedimientos SET nombre = 'Excisión de Masa en Pie', descripcion = 'Resección quirúrgica de masa tumoral en el pie.' WHERE id = 187;
UPDATE catalogo_procedimientos SET nombre = 'Drenaje de Dedo', descripcion = 'Drenaje quirúrgico de absceso o colección en dedo.' WHERE id = 194;
UPDATE catalogo_procedimientos SET nombre = 'Drenaje Ecoguiado de Quiste', descripcion = 'Drenaje de quiste guiado por ultrasonido.' WHERE id = 167;
UPDATE catalogo_procedimientos SET nombre = 'Colocación Fijador Externo', abreviatura = 'CFE', descripcion = 'Colocación quirúrgica de fijador externo (ya normalizado en 062).' WHERE id = 181;
UPDATE catalogo_procedimientos SET nombre = 'Amputación de Artejos', descripcion = 'Amputación de uno o más artejos (dedos del pie).' WHERE id = 189;
UPDATE catalogo_procedimientos SET nombre = 'LSDHCCT' WHERE id = 134;  -- ya renombrado arriba
UPDATE catalogo_procedimientos SET nombre = 'Resección de Grenoloma', descripcion = 'Resección quirúrgica de granuloma.' WHERE id = 209;
UPDATE catalogo_procedimientos SET nombre = 'Drenaje de Quiste Sinovial', descripcion = 'Drenaje quirúrgico o aspiración de quiste sinovial.' WHERE id = 195;
UPDATE catalogo_procedimientos SET nombre = 'Manejo Paciente Crítico', descripcion = 'Atención clínica especializada a paciente en estado crítico.' WHERE id = 86;

-- ─── Diagnóstico por imagen / Estudios ───
UPDATE catalogo_procedimientos SET nombre = 'Tomografías', descripcion = 'Estudio tomográfico computarizado.' WHERE id = 115;
UPDATE catalogo_procedimientos SET nombre = 'Ultrasonido Endovaginal', descripcion = 'Estudio ecográfico transvaginal.' WHERE id = 217;
UPDATE catalogo_procedimientos SET nombre = 'Ultrasonido Obstétrico', descripcion = 'Estudio ecográfico obstétrico.' WHERE id = 251;
UPDATE catalogo_procedimientos SET nombre = 'Visco Suplementación', descripcion = 'Infiltración intraarticular de ácido hialurónico.' WHERE id = 199;

-- ─── Misceláneos ───
UPDATE catalogo_procedimientos SET nombre = 'Exanguinotransfusión', descripcion = 'Reemplazo sanguíneo total o parcial.' WHERE id = 91;
UPDATE catalogo_procedimientos SET nombre = 'Termocoagulación', descripcion = 'Coagulación de tejido con calor (electrocauterio).' WHERE id = 101;
UPDATE catalogo_procedimientos SET nombre = 'Cierre por Tercera Intención', descripcion = 'Cierre diferido de herida (por granulación).' WHERE id = 99;
UPDATE catalogo_procedimientos SET nombre = 'Punción Lumbar', descripcion = 'Extracción de líquido cefalorraquídeo para diagnóstico.' WHERE id = 107;
UPDATE catalogo_procedimientos SET nombre = 'Exploración Abdominal', descripcion = 'Exploración quirúrgica de la cavidad abdominal.' WHERE id = 119;
UPDATE catalogo_procedimientos SET nombre = 'Orquideopexia Inguinal', descripcion = 'Fijación quirúrgica del testículo en el canal inguinal.' WHERE id = 150;
UPDATE catalogo_procedimientos SET nombre = 'Orquideopexia Inguinal', descripcion = 'Corrección de testículo no descendido por vía inguinal.' WHERE id = 150;
UPDATE catalogo_procedimientos SET nombre = 'Criptorquidia', descripcion = 'Corrección quirúrgica de testículo no descendido.' WHERE id = 174;
UPDATE catalogo_procedimientos SET nombre = 'Férula Anular', descripcion = 'Colocación de férula en dedo anular.' WHERE id = 207;
UPDATE catalogo_procedimientos SET nombre = 'Masa en Cuello', descripcion = 'Resección o biopsia de masa cervical.' WHERE id = 238;
UPDATE catalogo_procedimientos SET nombre = 'Masa en Labio', descripcion = 'Resección o biopsia de masa en labio.' WHERE id = 239;
UPDATE catalogo_procedimientos SET nombre = 'Empaque Nasal', descripcion = 'Taponamiento nasal hemostático.' WHERE id = 183;
UPDATE catalogo_procedimientos SET nombre = 'Tubo Orotraqueal', descripcion = 'Colocación de tubo orotraqueal (similar a IOT).' WHERE id = 204;
UPDATE catalogo_procedimientos SET nombre = 'Sonda Orográstrica', abreviatura = 'SG', descripcion = 'Inserción de sonda orogástrica.' WHERE id = 214;
UPDATE catalogo_procedimientos SET nombre = 'O/S Radio', descripcion = 'Osteosíntesis de Radio.' WHERE id = 242;
UPDATE catalogo_procedimientos SET nombre = 'O/S Cúbito', descripcion = 'Osteosíntesis de Cúbito.' WHERE id = 244;
UPDATE catalogo_procedimientos SET nombre = 'Reemplazo de Rodillas', descripcion = 'Reemplazo total de rodillas (prótesis).' WHERE id = 243;
UPDATE catalogo_procedimientos SET nombre = 'Cistostomía Abierta', descripcion = 'Apertura quirúrgica de la vejiga para drenaje.' WHERE id = 246;
UPDATE catalogo_procedimientos SET nombre = 'Infiltración Ecoguiada', abreviatura = 'INFECO', descripcion = 'Infiltración guiada por ultrasonido.' WHERE id = 221;
UPDATE catalogo_procedimientos SET nombre = 'Retiro de Yeso', abreviatura = 'RY', descripcion = 'Retiro de yeso aplicado al paciente.' WHERE id = 219;
UPDATE catalogo_procedimientos SET nombre = 'Retiro de Vendajes', abreviatura = 'RV', descripcion = 'Retiro de vendaje aplicado al paciente.' WHERE id = 220;
UPDATE catalogo_procedimientos SET nombre = 'Lavados y Debridamientos', abreviatura = 'LD', descripcion = 'Limpieza quirúrgica y retiro de tejido desvitalizado.' WHERE id = 233;
UPDATE catalogo_procedimientos SET nombre = 'Cistoscopia Basal Oculta', descripcion = 'Estudio endoscópico de vejiga urinaria.' WHERE id = 246;
UPDATE catalogo_procedimientos SET nombre = 'Granuloma', descripcion = 'Resección quirúrgica de granuloma.' WHERE id = 227;
UPDATE catalogo_procedimientos SET nombre = 'Espirometría', descripcion = 'Estudio de capacidad pulmonar.' WHERE id = 228;
UPDATE catalogo_procedimientos SET nombre = 'Cardiotocografía (Non-Stress Test)', descripcion = 'Monitoreo fetal no estresante.' WHERE id = 155;
UPDATE catalogo_procedimientos SET nombre = 'Tomografía de Coherencia Óptica', descripcion = 'Estudio oftalmológico OCT.' WHERE id = 156;
UPDATE catalogo_procedimientos SET nombre = 'Quiste de Baker (Dx)', descripcion = 'Diagnóstico/resección de quiste de Baker (rodilla).' WHERE id = 157;
UPDATE catalogo_procedimientos SET nombre = 'Regularización', abreviatura = 'REG', descripcion = 'Regularización quirúrgica (dedo de la mano).' WHERE id = 158;
UPDATE catalogo_procedimientos SET nombre = 'Intraóseo', abreviatura = 'I', descripcion = 'Acceso intraóseo (vía ósea para medicación).' WHERE id = 153;
UPDATE catalogo_procedimientos SET nombre = 'DIU', abreviatura = 'COLDIU', descripcion = 'Inserción o manipulación de dispositivo intrauterino (alias).' WHERE id = 154;
UPDATE catalogo_procedimientos SET nombre = 'Drenaje de Quiste Sinovial', descripcion = 'Aspiración o drenaje de quiste sinovial.' WHERE id = 195;
UPDATE catalogo_procedimientos SET nombre = 'Bacteriemia por Acidosis Tubular Renal', descripcion = 'Diagnóstico/tratamiento de ATR. (Revisar: es diagnóstico, no procedimiento).' WHERE id = 139;

COMMIT;