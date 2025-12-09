# backend/app.py
"""
Flask application serving dashboard static files and JSON endpoints.
Run with: python -m backend.app  OR python -m backend.app:create_app
"""

from datetime import datetime, timedelta, date
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from sqlalchemy import func, case
from .database import init_db, SessionLocal
from .models import Incident, ModelMetrics

import os

STATIC_FOLDER = os.path.join(os.path.dirname(__file__), "static")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_app():
    app = Flask(__name__, static_folder=STATIC_FOLDER, static_url_path="/static")
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # ensure DB/tables exist
    init_db()

    @app.route("/")
    def index():
        return send_from_directory(app.static_folder, "index.html")

    @app.route("/api/dashboard/summary")
    def dashboard_summary():
        db = next(get_db())
        today = date.today()
        start = datetime.combine(today, datetime.min.time())
        end = datetime.combine(today, datetime.max.time())

        total_today = (
            db.query(Incident)
            .filter(Incident.timestamp >= start, Incident.timestamp <= end)
            .count()
        )
        critical_incidents = db.query(Incident).filter(Incident.priority.in_(["HIGH", "CRITICAL"])).count()
        affected_sectors = db.query(Incident.sector).filter(Incident.sector.isnot(None)).distinct().count()
        mitigated = db.query(Incident).filter(Incident.is_mitigated.is_(True)).count()

        return jsonify(
            {
                "total_threats_today": total_today,
                "critical_incidents": critical_incidents,
                "affected_sectors": affected_sectors,
                "threats_mitigated": mitigated,
            }
        )

    @app.route("/api/incidents/live")
    def live_incidents():
        db = next(get_db())
        rows = (
            db.query(Incident)
            .order_by(Incident.timestamp.desc().nullslast(), Incident.id.desc())
            .limit(100)
            .all()
        )
        data = []
        for inc in rows:
            data.append(
                {
                    "id": inc.id,
                    "external_id": inc.external_id,
                    "title": inc.title,
                    "summary": inc.summary,
                    "description": inc.description,
                    "timestamp": inc.timestamp.isoformat() if inc.timestamp else None,
                    "priority": inc.priority,
                    "category": inc.category,
                    "sector": inc.sector,
                    "anomaly_score": inc.anomaly_score,
                    "useful_score": inc.useful_score,
                    "threat_score": inc.threat_score,
                    "status": inc.status,
                    "source": inc.source,
                    "url": inc.url,
                }
            )
        return jsonify(data)

    @app.route("/api/analytics/threat-distribution")
    def threat_distribution():
        db = next(get_db())
        rows = db.query(Incident.category, func.count(Incident.id)).group_by(Incident.category).all()
        data = [{"label": (c or "Unknown"), "value": int(n)} for c, n in rows]
        return jsonify(data)

    @app.route("/api/analytics/trends")
    def threat_trends():
        db = next(get_db())
        # last 14 days aggregated by date
        rows = (
            db.query(
                func.date(Incident.timestamp).label("day"),
                func.count(Incident.id).label("detected"),
                func.sum(case((Incident.is_mitigated == True, 1), else_=0)).label("mitigated"),
            )
            .group_by(func.date(Incident.timestamp))
            .order_by(func.date(Incident.timestamp))
            .limit(14)
            .all()
        )

        labels = []
        detected = []
        mitigated = []
        for day, det, mit in rows:
            # day may be string or date depending on SQLite; normalize
            if hasattr(day, "isoformat"):
                labels.append(day.isoformat())
            else:
                labels.append(str(day))
            detected.append(int(det or 0))
            mitigated.append(int(mit or 0))

        return jsonify(
            {
                "labels": labels,
                "datasets": [
                    {"label": "Detected", "values": detected},
                    {"label": "Mitigated", "values": mitigated},
                ],
            }
        )

    @app.route("/api/analytics/advanced")
    def advanced_analytics():
        db = next(get_db())
        last_metric = db.query(ModelMetrics).order_by(ModelMetrics.timestamp.desc()).first()
        ml_accuracy = float(last_metric.accuracy) if last_metric and last_metric.accuracy else 0.0

        week_ago = datetime.utcnow() - timedelta(days=7)
        anomalies = (
            db.query(Incident).filter(Incident.anomaly_score.isnot(None)).filter(Incident.timestamp >= week_ago).filter(Incident.anomaly_score > 0.5).count()
        )

        return jsonify({"ml_accuracy": ml_accuracy, "anomalies_detected": anomalies})

    @app.route("/api/ml/drift-status")
    def drift_status():
        db = next(get_db())
        last_metric = db.query(ModelMetrics).order_by(ModelMetrics.timestamp.desc()).first()
        if not last_metric:
            return jsonify({"model_version": None, "drift_detected": False})
        return jsonify(
            {
                "model_version": last_metric.model_version,
                "drift_detected": last_metric.drift_detected,
                "drift_score": last_metric.drift_score,
                "timestamp": last_metric.timestamp.isoformat() if last_metric.timestamp else None,
            }
        )

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
