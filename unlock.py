from core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

# Encontrar qué PID tiene el lock
pids = db.execute(text("""
    SELECT l.pid, a.usename, a.client_addr, a.state, a.query_start, a.query
    FROM pg_locks l
    JOIN pg_stat_activity a ON l.pid = a.pid
    WHERE l.objid = hashtext('sigsa3_asociar_pacientes_masivo')
      AND l.granted = true
""")).fetchall()

for p in pids:
    print(f"PID={p[0]} user={p[1]} state={p[3]} query_start={p[4]}")
    print(f"  query: {p[5][:100] if p[5] else 'None'}")
    # Terminar esta conexión
    result = db.execute(text(f"SELECT pg_terminate_backend({p[0]})")).scalar()
    print(f"  terminate result: {result}")

db.commit()

# Esperar y verificar
import time
time.sleep(2)

locks = db.execute(text("""
    SELECT count(*) FROM pg_locks
    WHERE objid = hashtext('sigsa3_asociar_pacientes_masivo')
""")).scalar()
print(f"\nLocks restantes después de terminar: {locks}")

db.close()
