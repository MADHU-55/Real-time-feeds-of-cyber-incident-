from sqlalchemy import text
from backend.database import engine


def migrate():
    with engine.connect() as conn:
        res = conn.execute(text("PRAGMA table_info(incidents)"))
        columns = [r[1] for r in res.fetchall()]

        if "threat_score" not in columns:
            print("➕ Adding threat_score column")
            conn.execute(
                text("ALTER TABLE incidents ADD COLUMN threat_score FLOAT DEFAULT 0.0")
            )
            conn.commit()
        else:
            print("✅ threat_score already exists")

if __name__ == "__main__":
    migrate()
