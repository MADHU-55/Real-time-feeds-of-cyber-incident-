# backend/collector/ml_classifier.py

import joblib
from pathlib import Path

from backend.database import SessionLocal
from backend.models import Incident

# ---------------- ML ASSETS ----------------
ML_DIR = Path(__file__).resolve().parent.parent / "ml"

vectorizer = joblib.load(ML_DIR / "vectorizer.joblib")
classifier = joblib.load(ML_DIR / "model.joblib")
isolation_forest = joblib.load(ML_DIR / "isolation_forest.joblib")

CATEGORY_TO_SEVERITY = {
    # Critical
    "ransomware": "CRITICAL",
    "apt": "CRITICAL",
    "nation_state": "CRITICAL",
    "zero_day": "CRITICAL",

    # High
    "malware": "HIGH",
    "phishing": "HIGH",
    "credential_theft": "HIGH",
    "supply_chain": "HIGH",
    "botnet": "HIGH",

    # Medium
    "vulnerability": "MEDIUM",
    "exploit": "MEDIUM",
    "ddos": "MEDIUM",
    "misconfiguration": "MEDIUM",

    # Low
    "info": "LOW",
    "policy": "LOW",
    "patch": "LOW",
    "update": "LOW",
}

CATEGORY_TO_SECTOR = {
    "ransomware": "Finance",
    "banking": "Finance",
    "phishing": "Finance",
    "apt": "Government",
    "espionage": "Government",
    "malware": "Technology",
    "supply_chain": "Technology",
    "vulnerability": "Technology",
    "healthcare": "Healthcare",
    "medical": "Healthcare",
    "energy": "Energy",
    "oil": "Energy",
    "power": "Energy",
}
SEVERITY_KEYWORDS = {
    "CRITICAL": [
        "ransomware", "zero-day", "zero day", "apt", "nation-state",
        "critical infrastructure", "ics", "scada"
    ],
    "HIGH": [
        "malware", "data breach", "credential", "phishing",
        "exploit", "backdoor", "trojan", "botnet"
    ],
    "MEDIUM": [
        "vulnerability", "cve-", "ddos", "misconfiguration"
    ]
}

# ---------------- SINGLE TEXT CLASSIFIER ----------------
def classify(text: str):
    """
    Classify a single incident text.

    Returns:
    {
        priority: str,
        category: str,
        proba: dict,
        anomaly_score: float
    }
    """
    X = vectorizer.transform([text])

    proba = classifier.predict_proba(X)[0]
    category = classifier.classes_[proba.argmax()].lower()
    anomaly_score = isolation_forest.score_samples(X)[0]
    text_l = text.lower()
    priority = CATEGORY_TO_SEVERITY.get(category.lower(), "LOW")
    for sev, keywords in SEVERITY_KEYWORDS.items():
        if any(kw in text_l for kw in keywords):
            priority = sev
            break
    return {
        "priority": priority,
        "category": category,
        "proba": {
            cls: float(p)
            for cls, p in zip(classifier.classes_, proba)
        },
        "anomaly_score": float(anomaly_score),
    }


# ---------------- PIPELINE / BATCH CLASSIFIER ----------------
def classify_new_incidents():
    """
    Classifies incidents in DB that are not yet categorized.
    Used by run_pipeline.py
    """
    db = SessionLocal()
    classified_count = 0

    try:
        incidents = (
            db.query(Incident)
            .filter(
    (Incident.priority.is_(None)) |
    (Incident.priority == "LOW")
)
            .all()
        )

        for inc in incidents:
            text = f"{inc.title or ''} {inc.summary or ''}".strip()
            if not text:
                continue

            result = classify(text)

            category = result["category"]
            priority = result["priority"]

            inc.category = category
            inc.priority = priority
            inc.anomaly_score = result["anomaly_score"]

            # ✅ sector mapping (safe)
            inc.sector = CATEGORY_TO_SECTOR.get(
                category.lower() if category else "",
                "General"
            )

            # ✅ mitigation logic (unchanged intent)
            inc.is_mitigated = priority == "LOW"

            # ✅ use existing DB columns properly
            inc.is_critical = priority in ["HIGH", "CRITICAL"]
            inc.threat_score = max(result["proba"].values())

            classified_count += 1

        if classified_count > 0:
            db.commit()

        print(f"🧠 Classified {classified_count} new incidents")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()
