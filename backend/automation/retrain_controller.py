# backend/automation/retrain_controller.py
from datetime import datetime, timedelta
import subprocess
import json
from pathlib import Path
from backend.database import init_db, SessionLocal
from ..models import ModelMetrics

ML_DIR = Path(__file__).resolve().parent.parent / "ml"
DRIFT_STATE = ML_DIR / "drift_state.json"
RETRAIN_DAYS = 7


def latest_metrics():
    init_db()
    db = SessionLocal()
    try:
        return db.query(ModelMetrics).order_by(ModelMetrics.timestamp.desc()).first()
    finally:
        db.close()


def should_retrain():
    m = latest_metrics()
    if not m:
        print("No previous model metrics; retrain required.")
        return True
    now = datetime.utcnow()
    age = now - (m.timestamp if m.timestamp else now)
    if m.drift_detected:
        print("Drift detected in DB metrics -> retrain.")
        return True
    if age > timedelta(days=RETRAIN_DAYS):
        print(f"Model older than {RETRAIN_DAYS} days -> retrain.")
        return True
    if DRIFT_STATE.exists():
        try:
            st = json.loads(DRIFT_STATE.read_text(encoding="utf-8"))
            if st.get("drift_detected"):
                print("drift_state.json indicates drift -> retrain.")
                return True
        except Exception:
            pass
    print("No retrain necessary.")
    return False


def run_training_process():
    print("Running training process...")
    r = subprocess.run(["python", "-m", "backend.ml.train"])
    return r.returncode == 0


if __name__ == "__main__":
    if should_retrain():
        ok = run_training_process()
        print("Retrain success" if ok else "Retrain failed")
    else:
        print("Skipping retrain.")
