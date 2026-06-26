from core.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(
        text("SELECT especialidad, COUNT(*) FROM sigsa3 GROUP BY especialidad ORDER BY COUNT(*) DESC")
    ).fetchall()
    for row in result:
        print(f"{row[0]}: {row[1]}")
