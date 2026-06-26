from core.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(
        text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'nacimientos_legacy' ORDER BY ordinal_position")
    ).fetchall()
    if result:
        for row in result:
            print(row)
    else:
        print("Table nacimientos_legacy not found")

    result = conn.execute(
        text("SELECT table_name FROM information_schema.tables WHERE table_name LIKE '%constan%' OR table_name LIKE '%nacim%' ORDER BY table_name")
    ).fetchall()
    print("\n--- Matching tables ---")
    for row in result:
        print(row)
