# backend/collector/ml_classifier.py

import joblib
from pathlib import Path

ML_DIR = Path(__file__).resolve().parent.parent / "ml"

vectorizer = joblib.load(ML_DIR / "vectorizer.joblib")
classifier = joblib.load(ML_DIR / "model.joblib")
isolation_forest = joblib.load(ML_DIR / "isolation_forest.joblib")


def classify(text: str):
    """Returns: {priority, category, proba[], anomaly_score}"""
    X = vectorizer.transform([text])
    proba = classifier.predict_proba(X)[0]
    label = classifier.classes_[proba.argmax()]

    anomaly_score = isolation_forest.score_samples(X)[0]

    return {
        "priority": label,
        "category": label,
        "proba": {
            cls: float(p)
            for cls, p in zip(classifier.classes_, proba)
        },
        "anomaly_score": float(anomaly_score)
    }
