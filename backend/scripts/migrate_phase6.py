import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import text
from app.db.session import SessionLocal

def migrate():
    db = SessionLocal()
    try:
        # Check if column exists to be idempotent
        # PostgreSQL specific check or just try/except
        # Using SQLite/Postgres generic approach for this env? 
        # Actually usually 'ALTER TABLE tasks ADD COLUMN university_id INTEGER' works in both (lite/pg)
        # But references syntax varies. 
        # Let's assume standard SQL for now or try/catch.
        
        # If SQLite, simple ADD COLUMN. If Postgres, same.
        print("Attempting to add university_id to tasks...")
        db.execute(text("ALTER TABLE tasks ADD COLUMN university_id INTEGER REFERENCES universities(id)"))
        db.commit()
        print("Migration successful.")
    except Exception as e:
        print(f"Migration failed (might already exist): {e}")
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
