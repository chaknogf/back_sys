from core.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(
        text("""
            SELECT
                EXTRACT(YEAR FROM fecha_consulta)::int AS anio,
                EXTRACT(MONTH FROM fecha_consulta)::int AS mes,
                COUNT(*) AS total
            FROM sigsa3
            WHERE especialidad = 'Terapia Respiratoria'
            GROUP BY anio, mes
            ORDER BY anio, mes
        """)
    ).fetchall()
    for row in result:
        print(f"{row[0]}-{row[1]:02d}: {row[2]}")
