"""
Siembra el catálogo de tipos de procedimiento quirúrgico del Quirófano.

Cada línea tiene el formato "Especialidad - Procedimiento". Se crean:
  - categoria_procedimiento: la especialidad (p. ej. "Cirugía General")
  - tipo_procedimiento: el nombre completo "Especialidad - Procedimiento"
    vinculado a su categoría.

Idempotente: los códigos se derivan del hash del nombre, por lo que volver a
ejecutarlo no duplica registros.
"""

from core.database import SessionLocal
import main  # noqa: F401  # registra todos los modelos y configura los mappers
from modules.quirofano.models import CategoriaProcedimientoModel, TipoProcedimientoModel

LINEAS = """Cirugía Cardiovascular - Angioplastia coronaria
Cirugía Cardiovascular - Bypass coronario
Cirugía Cardiovascular - Cirugía de aorta torácica
Cirugía Cardiovascular - Cirugía vascular periférica
Cirugía Cardiovascular - Endarterectomía carotídea
Cirugía Cardiovascular - Implantación de marcapasos
Cirugía Cardiovascular - Pericardiocentesis quirúrgica
Cirugía Cardiovascular - Reemplazo valvular
Cirugía Cardiovascular - Reparación de aneurismas
Cirugía Cardiovascular - Reparación valvular
Cirugía Cardiovascular - Trasplante cardíaco
Cirugía de Emergencia - Amputación de urgencia
Cirugía de Emergencia - Cesárea de emergencia
Cirugía de Emergencia - Control de daños
Cirugía de Emergencia - Control de hemorragias
Cirugía de Emergencia - Craniectomía descompresiva
Cirugía de Emergencia - Desbridamiento de tejidos infectados
Cirugía de Emergencia - Drenaje de abscesos profundos
Cirugía de Emergencia - Fasciotomía urgente
Cirugía de Emergencia - Laparotomía de urgencia
Cirugía de Emergencia - Toracotomía de emergencia
Cirugía General - (VAC) Cambio de terapia de presión negativa
Cirugía General - (VAC) Colocación de terapia de presión negativa
Cirugía General - (VAC) Retiro de terapia de presión negativa
Cirugía General - Adhesiolisis
Cirugía General - Amputación
Cirugía General - Anastomosis intestinal
Cirugía General - Apendicectomía
Cirugía General - Biopsia excisional
Cirugía General - Biopsia quirúrgica
Cirugía General - Bypass gástrico
Cirugía General - Cierre de herida
Cirugía General - Cierre de ostomías
Cirugía General - Cirugía de diverticulitis
Cirugía General - Cirugía de quistes hepáticos
Cirugía General - Cirugía de quistes sebáceos
Cirugía General - Cirugía de tiroides
Cirugía General - Colecistectomía
Cirugía General - Colectomía
Cirugía General - Colostomía
Cirugía General - Debridamiento quirúrgico
Cirugía General - Dedo en gatillo
Cirugía General - Drenaje biliar
Cirugía General - Enterectomía
Cirugía General - Esplenectomía
Cirugía General - Eventrorrafia
Cirugía General - Fistulectomía
Cirugía General - Fisurotomía
Cirugía General - Funduplicatura
Cirugía General - Gastrectomía subtotal
Cirugía General - Gastrectomía total
Cirugía General - Gastrostomía
Cirugía General - Hemicolectomía derecha
Cirugía General - Hemicolectomía izquierda
Cirugía General - Hemorroidectomía
Cirugía General - Hepatectomía
Cirugía General - Hernioplastía incisional
Cirugía General - Hernioplastía inguinal
Cirugía General - Hernioplastía umbilical
Cirugía General - Herniorrafia
Cirugía General - Ileostomía
Cirugía General - Laparoscopía diagnóstica
Cirugía General - Laparotomía exploradora
Cirugía General - Manejo quirúrgico de trauma abdominal
Cirugía General - Manga gástrica
Cirugía General - Pancreatectomía
Cirugía General - Paratiroidectomía
Cirugía General - Piloroplastía
Cirugía General - Reexploración abdominal y cierre por planos
Cirugía General - Remodelación de Colostomía
Cirugía General - Reparación de hernias
Cirugía General - Reparación de perforaciones gastrointestinales
Cirugía General - Resección de lipomas
Cirugía General - Resección de tejido
Cirugía General - Resección de tumores de piel y tejidos blandos
Cirugía General - Resección intestinal
Cirugía General - Sigmoidectomía
Cirugía General - Tiroidectomía parcial
Cirugía General - Tiroidectomía total
Cirugía General - Tratamiento quirúrgico del sangrado digestivo
Cirugía General - Vagotomía
Cirugía General - Yeyunostomía
Cirugía Maxilofacial - Cirugía ortognática
Cirugía Maxilofacial - Extracción de terceros molares
Cirugía Maxilofacial - Osteotomía mandibular
Cirugía Maxilofacial - Reconstrucción maxilar
Cirugía Maxilofacial - Reducción de fractura facial
Cirugía Maxilofacial - Reparación de fractura facial
Cirugía Maxilofacial - Resección de tumores maxilares
Cirugía Oncológica - Cirugía de sarcomas
Cirugía Oncológica - Cirugía hepatobiliar
Cirugía Oncológica - Cirugía paliativa oncológica
Cirugía Oncológica - Cirugía pancreática
Cirugía Oncológica - Colectomía oncológica
Cirugía Oncológica - Cuadrantectomía
Cirugía Oncológica - Debulking tumoral
Cirugía Oncológica - Disección axilar
Cirugía Oncológica - Disección cervical
Cirugía Oncológica - Gastrectomía oncológica
Cirugía Oncológica - Linfadenectomía
Cirugía Oncológica - Mastectomía
Cirugía Oncológica - Pancreatectomía oncológica
Cirugía Oncológica - Resección de tumores
Cirugía Oncológica - Resección hepática
Cirugía Oncológica - Tiroidectomía oncológica
Cirugía Oncológica - Tumorectomía
Cirugía Oral y Maxilofacial - Colocación de arco de Erich
Cirugía Pediátrica - Apendicectomía pediátrica
Cirugía Pediátrica - Atresias intestinales
Cirugía Pediátrica - Circuncisión
Cirugía Pediátrica - Corrección de atresia intestinal
Cirugía Pediátrica - Corrección de labio y paladar hendido
Cirugía Pediátrica - Estenosis pilórica
Cirugía Pediátrica - Gastrostomía pediátrica
Cirugía Pediátrica - Herniorrafia inguinal pediátrica
Cirugía Pediátrica - Invaginación intestinal
Cirugía Pediátrica - Malformaciones anorrectales
Cirugía Pediátrica - Malformaciones congénitas
Cirugía Pediátrica - Orquidopexia
Cirugía Pediátrica - Piloromiotomía
Cirugía Plástica y Reconstructiva - Abdominoplastia
Cirugía Plástica y Reconstructiva - Blefaroplastia
Cirugía Plástica y Reconstructiva - Colgajo cutáneo
Cirugía Plástica y Reconstructiva - Injerto de piel
Cirugía Plástica y Reconstructiva - Lavado y desbridamiento por quemadura
Cirugía Plástica y Reconstructiva - Mamoplastia reductora
Cirugía Plástica y Reconstructiva - Manejo de quemaduras
Cirugía Plástica y Reconstructiva - Otoplastia
Cirugía Plástica y Reconstructiva - Reconstrucción facial
Cirugía Plástica y Reconstructiva - Reconstrucción mamaria
Cirugía Plástica y Reconstructiva - Reparación de lesiones complejas
Cirugía Torácica - Decorticación pleural
Cirugía Torácica - Decorticación pulmonar
Cirugía Torácica - Drenaje torácico
Cirugía Torácica - Lobectomía pulmonar
Cirugía Torácica - Mediastinoscopia
Cirugía Torácica - Neumonectomía
Cirugía Torácica - Pleurodesis
Cirugía Torácica - Resección de tumores mediastinales
Cirugía Torácica - Toracotomía
Cirugía Vascular - Bypass femoropoplíteo
Cirugía Vascular - Embolectomía
Cirugía Vascular - Fístula arteriovenosa
Cirugía Vascular - Reparación vascular
Cirugía Vascular - Trombectomía
Cirugía Vascular - Varicectomía
Gastroenterología - Gastroscopía
Ginecología y Obstetricia - Aspiración manual endouterina
Ginecología y Obstetricia - Biopsia cervical
Ginecología y Obstetricia - Cerclaje cervical
Ginecología y Obstetricia - Cesárea
Ginecología y Obstetricia - Cirugía por prolapso genital
Ginecología y Obstetricia - Colporrafia anterior
Ginecología y Obstetricia - Colporrafia posterior
Ginecología y Obstetricia - Conización cervical
Ginecología y Obstetricia - Embarazo ectópico
Ginecología y Obstetricia - Histerectomía abdominal
Ginecología y Obstetricia - Histerectomía laparoscópica
Ginecología y Obstetricia - Histerectomía quirúrgica
Ginecología y Obstetricia - Histerectomía vaginal
Ginecología y Obstetricia - Laparoscopía ginecológica
Ginecología y Obstetricia - Legrado uterino
Ginecología y Obstetricia - Ligadura de trompas
Ginecología y Obstetricia - Ligadura tubárica
Ginecología y Obstetricia - Marsupialización de quiste de Bartolino
Ginecología y Obstetricia - Miomectomía
Ginecología y Obstetricia - Ooforectomía
Ginecología y Obstetricia - Quistectomía ovárica
Ginecología y Obstetricia - Reparación de desgarros obstétricos
Ginecología y Obstetricia - Reparación de prolapso uterino
Ginecología y Obstetricia - Salpingectomía
Ginecología y Obstetricia - Salpingooforectomía
Ginecología y Obstetricia - Tratamiento quirúrgico de endometriosis
Nefrología - Trasplante renal
Nefrología - Biopsia renal percutánea
Nefrología - Biopsia renal abierta
Nefrología - Nefrectomía simple
Nefrología - Nefrectomía radical
Nefrología - Nefrectomía parcial
Nefrología - Nefroureterectomía
Nefrología - Reimplante de uréter
Nefrología - Nefrolitotomía percutánea
Nefrología - Nefrostomía percutánea
Nefrología - Colocación de catéter para hemodiálisis (temporal)
Nefrología - Colocación de catéter tunelizado para hemodiálisis
Nefrología - Retiro de catéter para hermodiálisis
Nefrología - Creación de fístula arteriovenosa (radiocefálica)
Nefrología - Creación de fístula arteriovenosa (braquiocefálica)
Nefrología - Transposición de vena basílica
Nefrología - Colocación de injerto arteriovenoso para diálisis
Nefrología - Reparación de fístula arteriovenosa
Nefrología - Trombectomía de fístula arteriovenosa
Nefrología - Angioplastía de acceso vascular para hemodiálisis
Nefrología - Revisión quirúrgica de acceso vascular
Nefrología - Colocación de catéter para diálisis peritoneal
Nefrología - Retiro de catéter para diálisis peritoneal
Nefrología - Revisión o recambio de catéter peritoneal
Nefrología - Decortificación de riñón
Nefrología - Drenaje de absceso renal
Nefrología - Marsupialización de quiste renal
Nefrología - Fenestración laparoscópica de quiste renal
Neurocirugía - Cirugía de aneurisma cerebral
Neurocirugía - Cirugía de columna vertebral
Neurocirugía - Cirugía de tumores cerebrales
Neurocirugía - Craneotomía
Neurocirugía - Craniectomía
Neurocirugía - Derivación ventriculoperitoneal
Neurocirugía - Discectomía
Neurocirugía - Drenaje de hematoma
Neurocirugía - Drenaje epidural
Neurocirugía - Estimulación cerebral profunda
Neurocirugía - Evacuación de hematomas
Neurocirugía - Fusión vertebral
Neurocirugía - Laminectomía
Neurocirugía - Levantamiento óseo frontal
Neurocirugía - Reparación de fracturas craneales
Neurocirugía - Resección de tumor cerebral
Oftalmología - Cirugía de catarata
Oftalmología - LASIK
Oftalmología - Queratoplastia
Oftalmología - Reparación de desprendimiento de retina
Oftalmología - Trabeculectomía
Oftalmología - Vitrectomía
Otorrinolaringología - Adenoamigdalectomía
Otorrinolaringología - Adenoidectomía
Otorrinolaringología - Amigdalectomía
Otorrinolaringología - Cirugía endoscópica nasal
Otorrinolaringología - Laringectomía
Otorrinolaringología - Mastoidectomía
Otorrinolaringología - Microlaringoscopía
Otorrinolaringología - Polipectomía nasal
Otorrinolaringología - Rinoplastia
Otorrinolaringología - Septoplastia
Otorrinolaringología - Timpanoplastia
Otorrinolaringología - Traqueostomía
Procedimientos Endoscópicos - Broncoscopia
Procedimientos Endoscópicos - Cateterismo cardíaco
Procedimientos Endoscópicos - Colonoscopia
Procedimientos Endoscópicos - CPRE
Procedimientos Endoscópicos - Endoscopía + dilatación
Procedimientos Endoscópicos - Endoscopia digestiva alta
Procedimientos Endoscópicos - Endoscopía y toma de biopsia
Procedimientos Endoscópicos - Polipectomía endoscópica
Procedimientos Generales - Banding
Procedimientos Generales - Lavado y desbridamiento
Procedimientos Menores - Biopsia excisional
Procedimientos Menores - Biopsia incisional
Procedimientos Menores - Cauterización
Procedimientos Menores - Drenaje de absceso
Procedimientos Menores - Extracción de cuerpos extraños
Procedimientos Menores - Sutura de heridas
Trasplantes - Trasplante de médula ósea
Trasplantes - Trasplante hepático
Trasplantes - Trasplante pancreático
Trasplantes - Trasplante pulmonar
Trasplantes - Trasplante renal
Traumatología y Ortopedia - Amputación
Traumatología y Ortopedia - Artroplastia
Traumatología y Ortopedia - Artroscopía
Traumatología y Ortopedia - Cirugía de columna
Traumatología y Ortopedia - Cirugía de mano
Traumatología y Ortopedia - Cirugía de pie
Traumatología y Ortopedia - Corrección de deformidades
Traumatología y Ortopedia - Corrección de escoliosis
Traumatología y Ortopedia - Fijación externa
Traumatología y Ortopedia - Fijación percutánea
Traumatología y Ortopedia - Fijador externo
Traumatología y Ortopedia - Infección en sitio quirúrgico
Traumatología y Ortopedia - Liberación del túnel carpiano
Traumatología y Ortopedia - Manejo conservador
Traumatología y Ortopedia - Meniscectomía
Traumatología y Ortopedia - Osteosíntesis
Traumatología y Ortopedia - Osteostomía
Traumatología y Ortopedia - Reducción abierta y fijación interna (RAFI)
Traumatología y Ortopedia - Reducción cerrada de fractura
Traumatología y Ortopedia - Reemplazo de cadera
Traumatología y Ortopedia - Reemplazo de rodilla
Traumatología y Ortopedia - Reparación de ligamentos
Traumatología y Ortopedia - Reparación de tendones
Traumatología y Ortopedia - Síndrome compartimental (fasciotomía)
Traumatología y Ortopedia - Tenorrafia
Traumatología y Ortopedia - Tratamiento quirúrgico de fractura expuesta
Urología - Circuncisión
Urología - Cirugía de hidrocele
Urología - Cirugía de varicocele
Urología - Cistolitotomía
Urología - Cistoscopia
Urología - Colocación de catéter doble J
Urología - Hidrocelectomía
Urología - Infección del tracto urinario (UTI)
Urología - Litotricia
Urología - Nefrectomía
Urología - Nefrostomía
Urología - Orquiectomía
Urología - Pieloplastía
Urología - Prostatectomía
Urología - Resección transuretral de próstata
Urología - Ureterolitotomía
Urología - Ureteroscopia
Urología - Varicocelectomía
Urología - Vasectomía"""


def _normalizar(s: str) -> str:
    return " ".join(s.split())


def main():
    db = SessionLocal()
    try:
        pares = []
        for linea in LINEAS.strip().splitlines():
            linea = linea.strip()
            if not linea:
                continue
            if " - " not in linea:
                raise ValueError(f"Línea sin ' - ': {linea!r}")
            especialidad, procedimiento = linea.split(" - ", 1)
            pares.append((_normalizar(especialidad), _normalizar(linea)))

        categorias = {}
        cont_cat = 0
        cont_tipo = 0
        creadas = 0
        creados = 0

        for especialidad, nombre_completo in pares:
            if especialidad not in categorias:
                # código derivado y estable
                cod_cat = f"CAT{abs(hash(especialidad)) % 1000000:06d}"
                cat = db.query(CategoriaProcedimientoModel).filter(
                    CategoriaProcedimientoModel.nombre == especialidad
                ).first()
                if not cat:
                    cat = CategoriaProcedimientoModel(
                        codigo=cod_cat, nombre=especialidad, activo=True
                    )
                    db.add(cat)
                    db.flush()
                    creadas += 1
                categorias[especialidad] = cat

            existe = db.query(TipoProcedimientoModel).filter(
                TipoProcedimientoModel.nombre == nombre_completo
            ).first()
            if not existe:
                cod_tipo = f"TP{abs(hash(nombre_completo)) % 1000000:06d}"
                db.add(TipoProcedimientoModel(
                    codigo=cod_tipo,
                    nombre=nombre_completo,
                    categoria_procedimiento_id=categorias[especialidad].categoria_procedimiento_id,
                    activo=True,
                ))
                creados += 1
        db.commit()
        print(f"Especialidades creadas: {creadas}")
        print(f"Tipos de procedimiento creados: {creados}")
        print(f"Total especialidades: {len(categorias)}")
        print(f"Total líneas: {len(pares)}")
    finally:
        db.close()


if __name__ == "__main__":
    main()