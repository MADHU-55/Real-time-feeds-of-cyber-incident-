# backend/automation/update_scores.py
from backend.database import init_db, SessionLocal
from ..models import Incident
from sqlalchemy.orm import Session

PRIORITY_MAP = {"CRITICAL": 1.0, "HIGH": 0.8, "MEDIUM": 0.5, "MED": 0.5, "LOW": 0.1, None: 0.0}
W_PRIORITY = 0.6
W_ANOMALY = 0.25
W_USEFUL = 0.15


def normalize_anomaly(a):
    if a is None:
        return 0.0
    try:
        s = float(a)
    except Exception:
        return 0.0
    val = (1 - ((s + 1) / 2))
    return max(0.0, min(1.0, val))


def compute_threat_score(inc: Incident):
    p = PRIORITY_MAP.get((inc.priority or "").upper(), 0.0)
    a = normalize_anomaly(inc.anomaly_score)
    u = float(inc.useful_score or 0.0)
    score = W_PRIORITY * p + W_ANOMALY * a + W_USEFUL * u
    return float(round(score * 100, 2))


def run_update():
    init_db()
    db: Session = SessionLocal()
    try:
        rows = db.query(Incident).all()
        for inc in rows:
            inc.threat_score = compute_threat_score(inc)
        db.commit()
        print("Threat scores updated for", len(rows), "incidents")
    except Exception as e:
        print("update_scores error:", e)
    finally:
        db.close()


if __name__ == "__main__":
    run_update()
    print("Threat scores update completed.")