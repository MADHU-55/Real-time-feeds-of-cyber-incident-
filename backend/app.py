from datetime import datetime
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
from datetime import date, datetime, timedelta
from sqlalchemy import func, case
from sqlalchemy import and_
import os
import hashlib
import requests
import json
from pathlib import Path

from .database import init_db, SessionLocal
from .models import Incident

# ---------------- CONFIG ----------------
BASE_DIR = os.path.dirname(__file__)
STATIC_DIR = os.path.join(BASE_DIR, "static")
ML_DIR = Path(BASE_DIR) / "ml"
DRIFT_STATE = ML_DIR / "drift_state.json"

app = Flask(
    __name__,
    static_folder="static",
    static_url_path="/static"
)

CORS(app)
init_db()

# ---------------- DB SESSION (FIXED) ----------------
def get_db():
    return SessionLocal()

# ---------------- FRONTEND ROUTES ----------------
@app.route("/")
@app.route("/live-feed")
@app.route("/apt-groups")
@app.route("/sectors")
@app.route("/trends")
@app.route("/analytics")
@app.route("/reports")
def index():
    return send_from_directory(STATIC_DIR, "index.html")

# ---------------- DASHBOARD APIs ----------------
@app.route("/api/dashboard/summary")
def dashboard_summary():
    db = SessionLocal()

    today_start = datetime.combine(date.today(), datetime.min.time())
    today_end = datetime.combine(date.today(), datetime.max.time())

    total_today = db.query(Incident).filter(
        Incident.timestamp.between(today_start, today_end)
    ).count()

    critical_today = db.query(Incident).filter(
        Incident.timestamp.between(today_start, today_end),
        Incident.priority.in_(["HIGH", "CRITICAL"])
    ).count()

    affected_sectors = db.query(Incident.sector).filter(
        Incident.sector.isnot(None)
    ).distinct().count()

    mitigated = db.query(Incident).filter(
        Incident.is_mitigated.is_(True)
    ).count()

    db.close()

    return jsonify({
        "total_threats_today": total_today,
        "critical_incidents": critical_today,
        "affected_sectors": affected_sectors,
        "threats_mitigated": mitigated
    })
@app.route("/api/incidents/live")
def live_incidents():
    db = SessionLocal()

    rows = (
        db.query(Incident)
        .order_by(Incident.timestamp.desc())
        .limit(50)
        .all()
    )

    return jsonify([
        {
            "title": i.title,
            "summary": i.summary,
            "timestamp": i.timestamp.isoformat() if i.timestamp else None,
            "priority": i.priority or "LOW",
            "url": i.url,  # ✅ correct column
        }
        for i in rows
    ])

@app.route("/api/analytics/threat-distribution")
def threat_distribution():
    db = get_db()
    try:
        rows = (
            db.query(Incident.category, func.count(Incident.id))
            .group_by(Incident.category)
            .all()
        )

        return jsonify([
            {"label": c or "Unknown", "value": int(n)}
            for c, n in rows
        ])
    finally:
        db.close()

@app.route("/api/analytics/trends")
def threat_trends():
    db = get_db()
    try:
        rows = (
            db.query(
                func.date(Incident.timestamp),
                func.count(Incident.id),
                func.sum(case((Incident.is_mitigated == True, 1), else_=0))
            )
            .group_by(func.date(Incident.timestamp))
            .order_by(func.date(Incident.timestamp))
            .limit(14)
            .all()
        )

        labels, detected, mitigated = [], [], []
        for d, det, mit in rows:
            labels.append(str(d))
            detected.append(int(det))
            mitigated.append(int(mit or 0))

        return jsonify({
            "labels": labels,
            "datasets": [
                {"label": "Detected", "values": detected},
                {"label": "Mitigated", "values": mitigated},
            ],
        })
    finally:
        db.close()

# ---------------- ML STATUS ----------------
@app.route("/api/ml/status")
def ml_status():
    if DRIFT_STATE.exists():
        state = json.loads(DRIFT_STATE.read_text())
        return jsonify({
            "status": "Active",
            "drift_detected": state.get("drift_detected", False)
        })
    return jsonify({"status": "Not Trained", "drift_detected": False})

# ---------------- HIBP PASSWORD CHECK (FIXED) ----------------
@app.route("/api/security/password-check", methods=["POST"])
def password_check():
    data = request.get_json(silent=True)
    if not data or "password" not in data:
        return jsonify({"error": "Password required"}), 400

    password = data["password"]

    sha1 = hashlib.sha1(password.encode()).hexdigest().upper()
    prefix, suffix = sha1[:5], sha1[5:]

    r = requests.get(
        f"https://api.pwnedpasswords.com/range/{prefix}",
        headers={"User-Agent": "CyberNow"}
    )

    for line in r.text.splitlines():
        h, count = line.split(":")
        if h == suffix:
            return jsonify({"pwned": True, "count": int(count)})

    return jsonify({"pwned": False, "count": 0})

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
