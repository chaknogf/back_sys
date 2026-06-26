from core.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(
        text("""
            SELECT
                EXTRACT(MONTH FROM creado_en)::int AS mes,
                COUNT(*) AS total
            FROM consultas
            WHERE EXTRACT(YEAR FROM creado_en) = 2026
              AND EXTRACT(MONTH FROM creado_en) BETWEEN 1 AND 5
            GROUP BY EXTRACT(MONTH FROM creado_en)
            ORDER BY mes
        """)
    ).fetchall()
    for row in result:
        print(f"Mes {row[0]}: {row[1]}")
