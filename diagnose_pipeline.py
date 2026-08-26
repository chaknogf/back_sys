import time
import pandas as pd
from sqlalchemy import text
from core.database import SessionLocal, engine

t0 = time.time()

db = SessionLocal()

print("=" * 60)
print("DIAGNÓSTICO DEL PIPELINE SIGSA-3")
print("=" * 60)

# 0. Conteo de registros
sigsa3_total = db.execute(text("SELECT count(*) FROM sigsa3")).scalar()
sigsa3_pend = db.execute(text("SELECT count(*) FROM sigsa3 WHERE paciente_id IS NULL OR consulta_id IS NULL")).scalar()
pacientes_total = db.execute(text("SELECT count(*) FROM pacientes WHERE nombre_completo IS NOT NULL")).scalar()
consultas_total = db.execute(text("SELECT count(*) FROM consultas")).scalar()

print(f"\nRegistros SIGSA-3 total: {sigsa3_total}")
print(f"SIGSA-3 pendientes: {sigsa3_pend}")
print(f"Pacientes: {pacientes_total}")
print(f"Consultas: {consultas_total}")
print(f"Tiempo carga: {time.time()-t0:.1f}s")

# 1. PASO 1 - nombre exacto + expediente
t1 = time.time()
rows = db.execute(text("""
    SELECT s.id, p.id AS pac_id
    FROM sigsa3 s
    JOIN pacientes p ON unaccent(s.nombre_paciente) = unaccent(p.nombre_completo)
      AND s.no_historia_clinica = p.expediente
    WHERE s.paciente_id IS NULL
      AND s.nombre_paciente IS NOT NULL
      AND s.no_historia_clinica IS NOT NULL
""")).fetchall()
print(f"\nPASO 1 (nombre+expediente): {len(rows)} asociados [{time.time()-t1:.1f}s]")

# 2. PASO 2
t2 = time.time()
rows2a = db.execute(text("""
    SELECT count(*) FROM sigsa3 s
    JOIN pacientes p ON s.no_historia_clinica = p.expediente
    WHERE s.paciente_id IS NULL AND s.no_historia_clinica IS NOT NULL
""")).scalar()
rows2b = db.execute(text("""
    SELECT count(*) FROM sigsa3 s
    JOIN consultas c ON s.no_historia_clinica = c.documento
      AND s.fecha_consulta = c.fecha_consulta
    WHERE s.paciente_id IS NULL AND s.no_historia_clinica IS NOT NULL
      AND s.tipo_consulta ~ '^3'
""")).scalar()
print(f"PASO 2 (expediente/doc): {rows2a} pacientes, {rows2b} consultas [{time.time()-t2:.1f}s]")

# 3. PASO 3 - Carga de datos para vectorial
t3 = time.time()
df = pd.read_sql(
    "SELECT id, nombre_paciente, no_historia_clinica, fecha_consulta, tipo_consulta, sexo, paciente_id, consulta_id FROM sigsa3 WHERE paciente_id IS NULL OR consulta_id IS NULL",
    engine, parse_dates=["fecha_consulta"]
)
df_pac = pd.read_sql(
    "SELECT id AS pac_id, nombre_completo, expediente, sexo, estado FROM pacientes WHERE nombre_completo IS NOT NULL",
    engine
)
pendientes_p3 = df[df["paciente_id"].isna() & df["nombre_paciente"].notna()]
print(f"\nPASO 3 - Datos cargados: {len(df)} pendientes, {len(pendientes_p3)} con nombre, {len(df_pac)} pacientes [{time.time()-t3:.1f}s]")

# Tokenizar
from modules.common.vector_similarity import tokenizar, pesado_por_idf, idf_por_token, similitud_compuesta
from collections import defaultdict

# Construir firma/índices
t3b = time.time()
por_sign = defaultdict(list)
corpus = []
for _, pac in df_pac.iterrows():
    nombre = pac.get("nombre_completo")
    if not isinstance(nombre, str) or not nombre.strip():
        continue
    firma = tuple(sorted(tokenizar(nombre)))
    if not firma:
        continue
    por_sign[firma].append((int(pac["pac_id"]), nombre,
        pac.get("sexo", "") or "", 
        str(pac.get("expediente", "")).strip().lower() if pac.get("expediente") else "",
        pac.get("estado", "") or ""))
    corpus.append(firma)
idf = idf_por_token(corpus)
print(f"PASO 3 - Índices construidos: {len(por_sign)} firmas únicas, {len(corpus)} total [{time.time()-t3b:.1f}s]")

# 4. Simular paso 3: contar por tipo
t3c = time.time()
exact_match = 0
multiple_match = 0
submatch_candidates = 0
for idx, (_, reg) in enumerate(pendientes_p3.iterrows()):
    nombre = reg["nombre_paciente"]
    tokens = tokenizar(nombre)
    if len(tokens) < 2:
        continue
    firma = tuple(sorted(tokens))
    ident = por_sign[firma]
    if len(ident) == 1:
        exact_match += 1
    elif len(ident) > 1:
        multiple_match += 1
    else:
        submatch_candidates += 1

print(f"PASO 3 - Distribución: {exact_match} match exacto, {multiple_match} homónimos, {submatch_candidates} submatch candidatos [{time.time()-t3c:.1f}s]")
print(f"\nTiempo total diagnóstico: {time.time()-t0:.1f}s")

# 5. Estimar tiempo del paso 3 completo
if submatch_candidates > 0:
    print(f"\n⚠️  PASO 3 submatch: ~{submatch_candidates} registros × ~{len(df_pac)} pacientes")
    print(f"    Estimado: submatch puede tardar 5-15 minutos dependiendo de la distribución de tokens")

db.close()
