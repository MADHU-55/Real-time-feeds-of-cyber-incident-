# stats_service.py
from datetime import datetime, date
from sqlalchemy.orm import Session

from .models import Incident, TrendDaily, ModelMetrics


def get_dashboard_summary(db: Session):
    today = date.today()
    start = datetime.combine(today, datetime.min.time())
    end = datetime.combine(today, datetime.max.time())

    total_today = (
        db.query(Incident)
        .filter(Incident.timestamp >= start, Incident.timestamp <= end)
        .count()
    )
    critical_incidents = (
        db.query(Incident)
        .filter(Incident.priority.in_(["CRITICAL", "HIGH"]))
        .count()
    )
    affected_sectors = db.query(Incident.sector).filter(Incident.sector.isnot(None)).distinct().count()
    threats_mitigated = db.query(Incident).filter(Incident.is_mitigated.is_(True)).count()

    return {
        "total_threats_today": total_today,
        "critical_incidents": critical_incidents,
        "affected_sectors": affected_sectors,
        "threats_mitigated": threats_mitigated,
    }


def get_threat_distribution(db: Session):
    rows = (
        db.query(Incident.category, func.count(Incident.id))
        .group_by(Incident.category)
        .all()
    )
    return [{"category": c or "unknown", "count": int(n)} for c, n in rows]


from sqlalchemy import func  # needed for trends

def get_trends(db: Session, limit_days: int = 7):
    # if TrendDaily table is empty, compute from incidents on the fly
    rows = (
        db.query(TrendDaily)
        .order_by(TrendDaily.day.asc())
        .all()
    )
    if not rows:
        # build from incidents (simpler version)
        res = (
            db.query(
                func.strftime("%Y-%m-%d", Incident.timestamp),
                func.count(Incident.id),
                func.sum(func.case((Incident.is_mitigated, 1), else_=0)),
            )
            .group_by(func.strftime("%Y-%m-%d", Incident.timestamp))
            .all()
        )
        return [
            {"day": d, "detected": int(det or 0), "mitigated": int(mit or 0)}
            for d, det, mit in res
        ]
    return [
        {"day": r.day, "detected": r.detected, "mitigated": r.mitigated}
        for r in rows[-limit_days:]
    ]


def get_latest_drift_status(db: Session):
    row = (
        db.query(ModelMetrics)
        .order_by(ModelMetrics.timestamp.desc())
        .first()
    )
    if not row:
        return None
    return {
        "model_version": row.model_version,
        "drift_detected": row.drift_detected,
        "drift_score": row.drift_score,
        "last_updated": row.timestamp,
    }
