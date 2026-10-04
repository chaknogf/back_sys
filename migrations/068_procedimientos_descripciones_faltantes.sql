-- ============================================================
-- 068_procedimientos_descripciones_faltantes.sql
-- Asigna descripciones clínicas a los 89 procedimientos que aún
-- tienen 'Procedimiento no catalogado' o descripción vacía.
--
-- Estrategia:
--   - Descripción concisa, max 120 caracteres
--   - Basada en el nombre canónico del procedimiento
--   - No se modifican los demás campos
-- ============================================================

BEGIN;

-- Categoría: Ginecología / Obstetricia
UPDATE catalogo_procedimientos SET descripcion = 'Reducción quirúrgica de prolapso rectal.' WHERE id = 165 AND (descripcion IS NULL OR descripcion = '' OR descripcion = 'Procedimiento no catalogado');
UPDATE catalogo_procedimientos SET descripcion = 'Sutura del desgarro perineal/vaginal postparto.' WHERE id = 102;
UPDATE catalogo_procedimientos SET descripcion = 'Sutura del desgarro del cuello uterino postparto.' WHERE id = 110;
UPDATE catalogo_procedimientos SET descripcion = 'Legrado uterino evacuador o diagnóstico con cureta.' WHERE id = 250;
UPDATE catalogo_procedimientos SET descripcion = 'Resección de fimbrias tubáricas.' WHERE id = 113;
UPDATE catalogo_procedimientos SET descripcion = 'Extirpación quirúrgica del útero por vía abdominal.' WHERE id = 216;
UPDATE catalogo_procedimientos SET descripcion = 'Extirpación del útero por vía vaginal.' WHERE id = 224;
UPDATE catalogo_procedimientos SET descripcion = 'Ligadura hemostática de arterias uterinas en hemorragia.' WHERE id = 222;
UPDATE catalogo_procedimientos SET descripcion = 'Histerectomía de emergencia postparto.' WHERE id = 234;
UPDATE catalogo_procedimientos SET descripcion = 'Remoción manual de placenta retenida postparto.' WHERE id = 247;
UPDATE catalogo_procedimientos SET descripcion = 'Reparación de pared vaginal anterior (cistocele).' WHERE id = 223;
UPDATE catalogo_procedimientos SET descripcion = 'Exploración quirúrgica o manual de la pelvis.' WHERE id = 98;
UPDATE catalogo_procedimientos SET descripcion = 'Drenaje o evacuación de lipoma.' WHERE id = 237;

-- Categoría: Traumatología / Ortopedia
UPDATE catalogo_procedimientos SET descripcion = 'Cambio de apósitos o revisión de artrotomía previa.' WHERE id = 87;
UPDATE catalogo_procedimientos SET descripcion = 'Cambio de apósitos y drenaje de herida con membrana.' WHERE id = 90;
UPDATE catalogo_procedimientos SET descripcion = 'Drenaje a través de membrana cerrada o abierta.' WHERE id = 140;
UPDATE catalogo_procedimientos SET descripcion = 'Amputación de fémur distal, por encima de los cóndilos.' WHERE id = 147;
UPDATE catalogo_procedimientos SET descripcion = 'Amputación de tibia, por debajo de los cóndilos femorales.' WHERE id = 162;
UPDATE catalogo_procedimientos SET descripcion = 'Amputación quirúrgica de dedo con colgajo en raqueta.' WHERE id = 120;
UPDATE catalogo_procedimientos SET descripcion = 'Reconstrucción quirúrgica de un dedo.' WHERE id = 137;
UPDATE catalogo_procedimientos SET descripcion = 'Reducción cerrada de fractura o luxación de antebrazo.' WHERE id = 169;
UPDATE catalogo_procedimientos SET descripcion = 'Reemplazo articular de rodilla (prótesis).' WHERE id = 170;
UPDATE catalogo_procedimientos SET descripcion = 'Fusión quirúrgica de la articulación de la rodilla.' WHERE id = 175;
UPDATE catalogo_procedimientos SET descripcion = 'Reemplazo parcial de la cadera.' WHERE id = 179;
UPDATE catalogo_procedimientos SET descripcion = 'Fusión quirúrgica de la articulación del tobillo.' WHERE id = 160;
UPDATE catalogo_procedimientos SET descripcion = 'Corte óseo quirúrgico para corrección de deformidad.' WHERE id = 125;
UPDATE catalogo_procedimientos SET descripcion = 'Reducción quirúrgica de fractura radio-cubital.' WHERE id = 164;
UPDATE catalogo_procedimientos SET descripcion = 'Resección quirúrgica de masa cervical.' WHERE id = 178;
UPDATE catalogo_procedimientos SET descripcion = 'Resección quirúrgica de fibroma.' WHERE id = 129;
UPDATE catalogo_procedimientos SET descripcion = 'Resección quirúrgica de pólipo.' WHERE id = 190;
UPDATE catalogo_procedimientos SET descripcion = 'Resección quirúrgica de condiloma.' WHERE id = 186;
UPDATE catalogo_procedimientos SET descripcion = 'Resección quirúrgica de quiste.' WHERE id = 96;
UPDATE catalogo_procedimientos SET descripcion = 'Resección quirúrgica de lesión hiperplásica.' WHERE id = 173;
UPDATE catalogo_procedimientos SET descripcion = 'Regulación quirúrgica del pulpejo (dedo).' WHERE id = 177;
UPDATE catalogo_procedimientos SET descripcion = 'Liberación quirúrgica de adherencias/sinequias.' WHERE id = 151;
UPDATE catalogo_procedimientos SET descripcion = 'Retiro de tornillo/fijación transindesmal en tobillo.' WHERE id = 127;
UPDATE catalogo_procedimientos SET descripcion = 'Exploración quirúrgica del antebrazo/muñeca.' WHERE id = 126;
UPDATE catalogo_procedimientos SET descripcion = 'Exploración quirúrgica del cuello.' WHERE id = 122;
UPDATE catalogo_procedimientos SET descripcion = 'Exploración quirúrgica de vasos sanguíneos.' WHERE id = 184;
UPDATE catalogo_procedimientos SET descripcion = 'Exploración quirúrgica de vasos femorales.' WHERE id = 171;
UPDATE catalogo_procedimientos SET descripcion = 'Resección de tejido desvitalizado (esfacelo) en tórax.' WHERE id = 197;
UPDATE catalogo_procedimientos SET descripcion = 'Resección de tejido desvitalizado en miembros inferiores.' WHERE id = 185;
UPDATE catalogo_procedimientos SET descripcion = 'Incisiones de descarga para quemaduras circulares.' WHERE id = 208;
UPDATE catalogo_procedimientos SET descripcion = 'Rotación quirúrgica de colgajo cutáneo.' WHERE id = 232;
UPDATE catalogo_procedimientos SET descripcion = 'Reducción o manipulación cerrada de muñeca.' WHERE id = 191;
UPDATE catalogo_procedimientos SET descripcion = 'Limpieza y cierre de herida cortocortante traumática.' WHERE id = 134;
UPDATE catalogo_procedimientos SET descripcion = 'Reducción cerrada de luxación o fractura de hombro.' WHERE id = 152;
UPDATE catalogo_procedimientos SET descripcion = 'Reducción cerrada de luxación o fractura de cadera.' WHERE id = 248;
UPDATE catalogo_procedimientos SET descripcion = 'Reducción cerrada de fractura/luxación (general).' WHERE id = 256;
UPDATE catalogo_procedimientos SET descripcion = 'Extracción quirúrgica de uña del dedo de la mano.' WHERE id = 196;
UPDATE catalogo_procedimientos SET descripcion = 'Resección quirúrgica de masa tumoral en el pie.' WHERE id = 187;
UPDATE catalogo_procedimientos SET descripcion = 'Drenaje quirúrgico de absceso o colección en dedo.' WHERE id = 194;
UPDATE catalogo_procedimientos SET descripcion = 'Drenaje de quiste guiado por ultrasonido.' WHERE id = 167;
UPDATE catalogo_procedimientos SET descripcion = 'Colocación quirúrgica de fijador externo (pines y barras).' WHERE id = 181;
UPDATE catalogo_procedimientos SET descripcion = 'Amputación de uno o más artejos (dedos del pie).' WHERE id = 189;
UPDATE catalogo_procedimientos SET descripcion = 'Resección quirúrgica de granuloma.' WHERE id = 209;
UPDATE catalogo_procedimientos SET descripcion = 'Drenaje quirúrgico o aspiración de quiste sinovial.' WHERE id = 195;
UPDATE catalogo_procedimientos SET descripcion = 'Resección quirúrgica de condiloma.' WHERE id = 186;
UPDATE catalogo_procedimientos SET descripcion = 'Resección quirúrgica de condiloma acuminado.' WHERE id = 186;

-- Categoría: Estudios / Diagnóstico
UPDATE catalogo_procedimientos SET descripcion = 'Estudio tomográfico computarizado.' WHERE id = 115;
UPDATE catalogo_procedimientos SET descripcion = 'Estudio ecográfico transvaginal.' WHERE id = 217;
UPDATE catalogo_procedimientos SET descripcion = 'Estudio ecográfico obstétrico.' WHERE id = 251;
UPDATE catalogo_procedimientos SET descripcion = 'Infiltración intraarticular de ácido hialurónico.' WHERE id = 199;
UPDATE catalogo_procedimientos SET descripcion = 'Taponamiento nasal hemostático.' WHERE id = 183;
UPDATE catalogo_procedimientos SET descripcion = 'Colocación de tubo orotraqueal.' WHERE id = 204;
UPDATE catalogo_procedimientos SET descripcion = 'Inserción de sonda orogástrica.' WHERE id = 214;
UPDATE catalogo_procedimientos SET descripcion = 'Estudio endoscópico de vejiga urinaria.' WHERE id = 246;
UPDATE catalogo_procedimientos SET descripcion = 'Resección quirúrgica de granuloma.' WHERE id = 227;
UPDATE catalogo_procedimientos SET descripcion = 'Estudio de capacidad pulmonar.' WHERE id = 228;
UPDATE catalogo_procedimientos SET descripcion = 'Estudio gammagráfico.' WHERE id = 73;
UPDATE catalogo_procedimientos SET descripcion = 'Reducción de prolapso rectal.' WHERE id = 165;
UPDATE catalogo_procedimientos SET descripcion = 'Corrección quirúrgica de testículo no descendido.' WHERE id = 174;
UPDATE catalogo_procedimientos SET descripcion = 'Colocación de férula en dedo anular.' WHERE id = 207;
UPDATE catalogo_procedimientos SET descripcion = 'Resección o biopsia de masa cervical.' WHERE id = 238;
UPDATE catalogo_procedimientos SET descripcion = 'Resección o biopsia de masa en labio.' WHERE id = 239;
UPDATE catalogo_procedimientos SET descripcion = 'Osteosíntesis de radio.' WHERE id = 242;
UPDATE catalogo_procedimientos SET descripcion = 'Osteosíntesis de cúbito.' WHERE id = 244;
UPDATE catalogo_procedimientos SET descripcion = 'Reemplazo total de rodillas (prótesis).' WHERE id = 243;
UPDATE catalogo_procedimientos SET descripcion = 'Apertura quirúrgica de la vejiga para drenaje.' WHERE id = 246;
UPDATE catalogo_procedimientos SET descripcion = 'Infiltración guiada por ultrasonido.' WHERE id = 221;
UPDATE catalogo_procedimientos SET descripcion = 'Estudio de capacidad pulmonar.' WHERE id = 228;
UPDATE catalogo_procedimientos SET descripcion = 'Reducción cerrada de fractura/luxación (general).' WHERE id = 256;

-- Categoría: Misceláneos / Generales
UPDATE catalogo_procedimientos SET descripcion = 'Atención clínica especializada a paciente en estado crítico.' WHERE id = 86;
UPDATE catalogo_procedimientos SET descripcion = 'Resección quirúrgica de quiste sebáceo.' WHERE id = 193;
UPDATE catalogo_procedimientos SET descripcion = 'Monitoreo fetal no estresante.' WHERE id = 155;
UPDATE catalogo_procedimientos SET descripcion = 'Estudio oftalmológico OCT.' WHERE id = 156;
UPDATE catalogo_procedimientos SET descripcion = 'Diagnóstico/resección de quiste de Baker (rodilla).' WHERE id = 157;
UPDATE catalogo_procedimientos SET descripcion = 'Regularización quirúrgica (dedo de la mano).' WHERE id = 158;
UPDATE catalogo_procedimientos SET descripcion = 'Acceso intraóseo (vía ósea para medicación).' WHERE id = 153;
UPDATE catalogo_procedimientos SET descripcion = 'Inserción o manipulación de dispositivo intrauterino (alias).' WHERE id = 154;
UPDATE catalogo_procedimientos SET descripcion = 'Exanguinotransfusión: reemplazo sanguíneo total o parcial.' WHERE id = 91;
UPDATE catalogo_procedimientos SET descripcion = 'Coagulación de tejido con calor (electrocauterio).' WHERE id = 101;
UPDATE catalogo_procedimientos SET descripcion = 'Cierre diferido de herida (por granulación).' WHERE id = 99;
UPDATE catalogo_procedimientos SET descripcion = 'Extracción de líquido cefalorraquídeo para diagnóstico.' WHERE id = 107;
UPDATE catalogo_procedimientos SET descripcion = 'Exploración quirúrgica de la cavidad abdominal.' WHERE id = 119;
UPDATE catalogo_procedimientos SET descripcion = 'Fijación quirúrgica del testículo en el canal inguinal.' WHERE id = 150;
UPDATE catalogo_procedimientos SET descripcion = 'Inserción o retiro de implante subdérmico anticonceptivo (Jadelle).' WHERE id = 253;
UPDATE catalogo_procedimientos SET descripcion = 'Inserción de implante subdérmico anticonceptivo (Jadelle).' WHERE id = 254;
UPDATE catalogo_procedimientos SET descripcion = 'Retiro de implante subdérmico anticonceptivo (Jadelle).' WHERE id = 255;
UPDATE catalogo_procedimientos SET descripcion = 'Reemplazo de uno o más artejos (dedos del pie).' WHERE id = 189;
UPDATE catalogo_procedimientos SET descripcion = 'Resección de tumor de mama con biopsia.' WHERE id = 130;
UPDATE catalogo_procedimientos SET descripcion = 'Biopsia de mama con escisión de tumor.' WHERE id = 240;
UPDATE catalogo_procedimientos SET descripcion = 'Biopsia de vulva.' WHERE id = 241;
UPDATE catalogo_procedimientos SET descripcion = 'Manipulación cerrada de hombro.' WHERE id = 152;
UPDATE catalogo_procedimientos SET descripcion = 'Manipulación cerrada de cadera.' WHERE id = 248;
UPDATE catalogo_procedimientos SET descripcion = 'Manipulación cerrada general.' WHERE id = 256;
UPDATE catalogo_procedimientos SET descripcion = 'Amputación de muñeca.' WHERE id = 138;
UPDATE catalogo_procedimientos SET descripcion = 'Tomografía de coherencia óptica.' WHERE id = 156;
UPDATE catalogo_procedimientos SET descripcion = 'Exanguinotransfusión.' WHERE id = 91;

-- Final: cualquier procedimiento aún sin descripción (catch-all)
UPDATE catalogo_procedimientos
SET descripcion = INITCAP(LOWER(nombre)) || ' — procedimiento quirúrgico o clínico.'
WHERE activo = TRUE
  AND (descripcion IS NULL OR descripcion = '' OR descripcion = 'Procedimiento no catalogado');

COMMIT;