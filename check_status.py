from core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

# Verificar advisory lock
locks = db.execute(text("""
    SELECT l.pid, a.usename, a.state, a.query_start, a.query
    FROM pg_locks l
    JOIN pg_stat_activity a ON l.pid = a.pid
    WHERE l.objid = hashtext('sigsa3_asociar_pacientes_masivo')
""")).fetchall()
print(f"Advisory locks: {len(locks)}")
for l in locks:
    print(f"  PID={l[0]} user={l[1]} state={l[2]} since={l[3]}")
    print(f"  query: {l[4][:150] if l[4] else 'None'}")

# Ver sesiones activas de Python/uvicorn
sessions = db.execute(text("""
    SELECT pid, state, query_start, left(query, 100) as query
    FROM pg_stat_activity
    WHERE application_name = 'psycopg2'
       OR query LIKE '%sigsa3%'
       OR query LIKE '%pacientes%'
    ORDER BY query_start DESC
""")).fetchall()
print(f"\nSesiones activas: {len(sessions)}")
for s in sessions:
    print(f"  PID={s[0]} state={s[1]} since={s[2]} q={s[3]}")

# Verificar tablas SIGSA-3
for tbl in ['sigsa3', 'sigsa3_registros']:
    count = db.execute(text(f"SELECT count(*) FROM {tbl}")).scalar()
    print(f"\n{tbl}: {count} registros")

# Ver cuántos tienen paciente_id en sigsa3
pac = db.execute(text("SELECT count(*) FROM sigsa3 WHERE paciente_id IS NOT NULL")).scalar()
sin_pac = db.execute(text("SELECT count(*) FROM sigsa3 WHERE paciente_id IS NULL")).scalar()
print(f"\nsigsa3 con paciente_id: {pac}")
print(f"sigsa3 sin paciente_id: {sin_pac}")

db.close()
