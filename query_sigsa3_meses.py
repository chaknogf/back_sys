from core.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(
        text("""
            SELECT
                EXTRACT(MONTH FROM fecha_consulta)::int AS mes,
                COUNT(*) AS total
            FROM sigsa3
            WHERE especialidad = 'Terapia Respiratoria'
              AND EXTRACT(YEAR FROM fecha_consulta) = 2026
            GROUP BY mes
            ORDER BY mes
        """)
    ).fetchall()
    for row in result:
        print(f"Mes {row[0]}: {row[1]}")
