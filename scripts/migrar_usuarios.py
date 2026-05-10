import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5433/vinculo_db")

def migrate():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        print("🔍 Verificando columna 'nombre' en tabla 'usuarios'...")
        try:
            conn.execute(text("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS nombre VARCHAR(255);"))
            conn.commit()
            print("✅ Columna 'nombre' añadida (o ya existía).")
        except Exception as e:
            print(f"❌ Error migrando: {e}")

if __name__ == "__main__":
    migrate()
