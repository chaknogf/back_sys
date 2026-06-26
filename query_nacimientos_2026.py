from core.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(
        text("""
            SELECT
                EXTRACT(MONTH FROM created_at)::int AS mes,
                COUNT(*) AS total
            FROM nacimientos
            WHERE EXTRACT(YEAR FROM created_at) = 2026
              AND EXTRACT(MONTH FROM created_at) BETWEEN 1 AND 5
            GROUP BY EXTRACT(MONTH FROM created_at)
            ORDER BY mes
        """)
    ).fetchall()
    for row in result:
        print(f"Mes {row[0]}: {row[1]}")
