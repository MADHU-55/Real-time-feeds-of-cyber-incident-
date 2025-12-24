# backend/ml/train.py
"""
Train classification model + isolation forest, compute drift,
and save artifacts + drift_state.json.

Run as: python -m backend.ml.train
"""

from datetime import datetime, timezone
from pathlib import Path
import json
import numpy as np
import joblib

from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import cross_val_score

from ..database import init_db, SessionLocal
from ..models import Incident

# ================== PATHS ==================
ML_DIR = Path(__file__).resolve().parent
MODEL_FILE = ML_DIR / "model.joblib"
VECT_FILE = ML_DIR / "vectorizer.joblib"
IFOREST_FILE = ML_DIR / "isolation_forest.joblib"
DRIFT_STATE = ML_DIR / "drift_state.json"

DRIFT_THRESHOLD = 0.45


# ================== DATA ==================
def _load_training_data(db):
    rows = (
        db.query(Incident)
        .filter(Incident.priority.isnot(None))
        .filter(Incident.summary.isnot(None))
        .all()
    )
    texts = [r.summary or r.title or "" for r in rows]
    labels = [r.priority for r in rows]
    return texts, labels


# ================== DRIFT ==================
def compute_drift_score(iforest, vec, recent_texts):
    if not recent_texts:
        return 0.0
    Xr = vec.transform(recent_texts)
    scores = iforest.decision_function(Xr)
    mean = float(np.mean(scores))
    return float(np.clip(1 - ((mean + 1) / 2), 0.0, 1.0))


# ================== SAVE ==================
def save_artifacts(clf, vec, iforest):
    joblib.dump(clf, MODEL_FILE)
    joblib.dump(vec, VECT_FILE)
    joblib.dump(iforest, IFOREST_FILE)


def persist_drift_state(state: dict):
    with open(DRIFT_STATE, "w", encoding="utf-8") as fh:
        json.dump(state, fh, indent=2, default=str)


# ================== TRAIN ==================
def run_train():
    init_db()
    db = SessionLocal()

    try:
        texts, labels = _load_training_data(db)
        if len(texts) < 5:
            print("Not enough labelled data to train (need >=5).")
            return False

        vec = TfidfVectorizer(max_features=10000, ngram_range=(1, 2))
        X = vec.fit_transform(texts)

        clf = RandomForestClassifier(n_estimators=200, random_state=42)
        clf.fit(X, labels)

        try:
            scores = cross_val_score(clf, X, labels, cv=3, scoring="accuracy")
            accuracy = float(np.mean(scores))
        except Exception:
            accuracy = float(clf.score(X, labels))

        iforest = IsolationForest(
            n_estimators=200, contamination=0.05, random_state=42
        )
        iforest.fit(X)

        recent_rows = (
            db.query(Incident)
            .filter(Incident.summary.isnot(None))
            .order_by(Incident.timestamp.desc().nullslast(), Incident.id.desc())
            .limit(200)
            .all()
        )
        recent_texts = [r.summary or r.title or "" for r in recent_rows]

        drift_score = compute_drift_score(iforest, vec, recent_texts)
        drift_detected = drift_score >= DRIFT_THRESHOLD

        version = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")

        save_artifacts(clf, vec, iforest)

        persist_drift_state(
            {
                "model_version": version,
                "accuracy": accuracy,
                "drift_score": drift_score,
                "drift_detected": drift_detected,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

        print(
            f"Trained model {version} | "
            f"accuracy={accuracy:.3f}, "
            f"drift_score={drift_score:.3f}, "
            f"drift_detected={drift_detected}"
        )
        return True

    except Exception as e:
        print("Training failed:", e)
        return False

    finally:
        db.close()


if __name__ == "__main__":
    run_train()
