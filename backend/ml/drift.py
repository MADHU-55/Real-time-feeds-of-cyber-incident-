# backend/ml/drift.py
import numpy as np
from datetime import datetime
from sqlalchemy.orm import Session
from sklearn.ensemble import IsolationForest

from backend.database import SessionLocal
from backend.models import Incident, ModelMetrics
from backend.ml.train import train_model


DRIFT_THRESHOLD = 0.35  # if anomaly ratio > 35% → retrain


def check_and_handle_drift():
    db: Session = SessionLocal()

    recent_scores = (
        db.query(Incident.useful_score)
        .filter(Incident.useful_score.isnot(None))
        .order_by(Incident.timestamp.desc())
        .limit(200)
        .all()
    )

    if not recent_scores:
        db.close()
        return False

    arr = np.array([float(x[0]) for x in recent_scores]).reshape(-1, 1)

    iso = IsolationForest(contamination=0.1)
    preds = iso.fit_predict(arr)

    drift_score = preds.tolist().count(-1) / len(preds)
    drift_detected = drift_score > DRIFT_THRESHOLD

    metric = ModelMetrics(
        timestamp=datetime.utcnow(),
        model_version="auto",
        drift_score=float(drift_score),
        drift_detected=drift_detected,
    )
    db.add(metric)
    db.commit()

    if drift_detected:
        print("⚠ Drift detected — retraining model...")
        train_model()
        db.close()
        return True

    db.close()
    return False
