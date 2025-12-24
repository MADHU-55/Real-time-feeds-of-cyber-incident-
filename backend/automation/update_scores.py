# backend/automation/update_scores.py

from backend.database import init_db, SessionLocal
from backend.models import Incident
from sqlalchemy.orm import Session

# Simple priority-based threat normalization
PRIORITY_MAP = {
    "CRITICAL": 100.0,
    "HIGH": 80.0,
    "MEDIUM": 50.0,
    "MED": 50.0,
    "LOW": 10.0,
    None: 0.0,
}

def compute_threat_score(priority: str) -> float:
    if not priority:
        return 0.0
    return PRIORITY_MAP.get(priority.upper(), 0.0)

def run_update():
    init_db()
    db: Session = SessionLocal()
    try:
        rows = db.query(Incident).all()

        # NOTE:
        # Incident does NOT store threat_score in DB.
        # We only compute it here for logging / future extension.
        for inc in rows:
            _ = compute_threat_score(inc.priority)

        print(f"Threat scores evaluated for {len(rows)} incidents")

    except Exception as e:
        print("update_scores error:", e)

    finally:
        db.close()

if __name__ == "__main__":
    run_update()
    print("Threat scores update completed.")
