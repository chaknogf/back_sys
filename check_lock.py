from core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
db.execute(text("SELECT pg_advisory_unlock_all()"))
db.commit()
locks = db.execute(text("SELECT count(*) FROM pg_locks WHERE locktype = 'advisory'")).scalar()
print(f"Advisory locks: {locks}")

# Verificar datos
sigsa3_pend = db.execute(text("SELECT count(*) FROM sigsa3 WHERE paciente_id IS NULL OR consulta_id IS NULL")).scalar()
print(f"SIGSA-3 pendientes: {sigsa3_pend}")
db.close()
