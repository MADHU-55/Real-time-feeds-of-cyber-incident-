# backend/ml/predict.py
from pathlib import Path
import pickle

from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import ModelMetrics
from .train import train_model, MODEL_PATH, VECT_PATH, ISO_PATH
from .drift import drift_detector


BASE_DIR = Path(__file__).resolve().parent


def _load_or_train():
    if not (MODEL_PATH.exists() and VECT_PATH.exists() and ISO_PATH.exists()):
        print("Model files not found – training initial model...")
        train_model()

    with open(MODEL_PATH, "rb") as f:
        clf = pickle.load(f)
    with open(VECT_PATH, "rb") as f:
        vect = pickle.load(f)
    with open(ISO_PATH, "rb") as f:
        iso = pickle.load(f)
    return clf, vect, iso


clf_model, vectorizer, iso_model = _load_or_train()


def classify_and_score(text: str) -> dict:
    """Return priority, probabilities, anomaly score, drift info."""
    global clf_model, vectorizer, iso_model

    X = vectorizer.transform([text])
    proba = clf_model.predict_proba(X)[0]
    labels = list(clf_model.classes_)
    max_idx = proba.argmax()
    priority = labels[max_idx]
    max_score = float(proba[max_idx])

    # anomaly: higher = more abnormal
    anomaly_raw = -iso_model.decision_function(X.toarray())[0]
    anomaly_score = float(anomaly_raw)

    drift_info = drift_detector.update(max_score)

    # If drift detected: retrain and store metrics
    if drift_info["drift_detected"]:
        print("⚠ Drift detected – retraining model...")
        train_model()
        # reload models to keep memory in sync
        clf_model, vectorizer, iso_model = _load_or_train()

        # record drift metric
        db: Session = SessionLocal()
        try:
            version = "drift-" + drift_info["last_drift"]
            m = ModelMetrics(
                model_version=version,
                accuracy=None,
                f1=None,
                drift_detected=True,
                drift_score=max_score,
            )
            db.add(m)
            db.commit()
        finally:
            db.close()

    return {
        "priority": priority,
        "proba": dict(zip(labels, map(float, proba))),
        "anomaly_score": anomaly_score,
        "drift": drift_info,
    }
