from core.database import SessionLocal
from sqlalchemy import text
db = SessionLocal()
db.execute(text("SELECT pg_advisory_unlock_all()"))
db.commit()
# Kill lingering sessions
pids = db.execute(text("SELECT pid FROM pg_stat_activity WHERE state = 'idle in transaction' AND query_start < now() - interval '5 minutes'")).fetchall()
for row in pids:
    db.execute(text(f"SELECT pg_terminate_backend({row[0]})"))
db.commit()
locks = db.execute(text("SELECT count(*) FROM pg_locks WHERE locktype = 'advisory'")).scalar()
print(f"Advisory locks: {locks}")
db.close()
