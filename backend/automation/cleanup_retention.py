from datetime import datetime, timedelta
from backend.database import init_db, SessionLocal
from backend.models import Incident

LOW_RETENTION = 60   # days
HIGH_RETENTION = 120  # days


def cleanup_old_incidents():
    init_db()
    db = SessionLocal()
    now = datetime.utcnow()

    low_cutoff = now - timedelta(days=LOW_RETENTION)
    high_cutoff = now - timedelta(days=HIGH_RETENTION)

    # Delete LOW/MEDIUM older than 30 days
    low_deleted = (
        db.query(Incident)
        .filter(
            Incident.priority.notin_(["HIGH", "CRITICAL"]),
            Incident.timestamp < low_cutoff
        )
        .delete(synchronize_session=False)
    )

    # Delete HIGH/CRITICAL older than 60 days
    high_deleted = (
        db.query(Incident)
        .filter(
            Incident.priority.in_(["HIGH", "CRITICAL"]),
            Incident.timestamp < high_cutoff
        )
        .delete(synchronize_session=False)
    )

    db.commit()
    db.close()

    print(f"Retention cleanup: removed {low_deleted + high_deleted} incidents")


if __name__ == "__main__":
    cleanup_old_incidents()
