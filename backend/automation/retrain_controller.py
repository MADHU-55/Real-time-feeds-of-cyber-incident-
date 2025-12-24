# backend/automation/retrain_controller.py

from datetime import datetime, timedelta
import subprocess
import json
import sys
from pathlib import Path

ML_DIR = Path(__file__).resolve().parent.parent / "ml"
DRIFT_STATE = ML_DIR / "drift_state.json"

RETRAIN_DAYS = 7
LAST_TRAIN_FILE = ML_DIR / "last_trained.txt"


def last_trained_time():
    if not LAST_TRAIN_FILE.exists():
        return None
    try:
        return datetime.fromisoformat(
            LAST_TRAIN_FILE.read_text(encoding="utf-8").strip()
        )
    except Exception:
        return None


def should_retrain():
    now = datetime.utcnow()

    # 1️⃣ No previous training record
    last = last_trained_time()
    if not last:
        print("No previous training record → retrain required.")
        return True

    # 2️⃣ Time-based retraining
    if now - last > timedelta(days=RETRAIN_DAYS):
        print(f"Model older than {RETRAIN_DAYS} days → retrain.")
        return True

    # 3️⃣ Drift-based retraining (optional)
    if DRIFT_STATE.exists():
        try:
            st = json.loads(DRIFT_STATE.read_text(encoding="utf-8"))
            if st.get("drift_detected"):
                print("drift_state.json indicates drift → retrain.")
                return True
        except Exception as e:
            print("Warning: failed reading drift_state.json:", e)

    print("No retrain necessary.")
    return False


def run_training_process():
    print("Running training process...")
    try:
        subprocess.run(
            [sys.executable, "-m", "backend.ml.train"],
            check=True,
        )
        LAST_TRAIN_FILE.write_text(
            datetime.utcnow().isoformat(),
            encoding="utf-8",
        )
        return True
    except subprocess.CalledProcessError as e:
        print("Training subprocess failed:", e)
        return False

def run_retraining():
    """
    Entry point for pipeline.
    Decides whether retraining is needed and runs it if required.
    """
    if should_retrain():
        return run_training_process()
    return False


if __name__ == "__main__":
    if should_retrain():
        ok = run_training_process()
        print("Retrain success ✅" if ok else "Retrain failed ❌")
    else:
        print("Skipping retrain.")
