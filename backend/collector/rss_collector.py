"""
RSS Collector with:
- Govt + trusted sources
- Deduplication
- Optional ML-based priority prediction
- Retention policy (1 month / 2 months for HIGH/CRITICAL)
"""

import feedparser
import html
import time
import os
from datetime import datetime, timedelta

from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, or_

from backend.database import init_db, SessionLocal
from backend.models import Incident

import joblib

# ================== FEEDS ==================
FEEDS = [
    "https://www.cert-in.org.in/rss.xml",
    "https://pib.gov.in/AllReleaseRSS.aspx?Language=0",
    "https://www.ncsc.gov.uk/rss/news",
    "https://www.bleepingcomputer.com/feed/",
    "https://threatpost.com/feed/",
]

# ================== ML ARTIFACTS (OPTIONAL) ==================
BASE_DIR = os.path.dirname(__file__)
MODEL_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "ml"))

MODEL_PATH = os.path.join(MODEL_DIR, "model.joblib")
VECT_PATH = os.path.join(MODEL_DIR, "vectorizer.joblib")

clf = vec = None

try:
    if os.path.exists(MODEL_PATH):
        clf = joblib.load(MODEL_PATH)
    if os.path.exists(VECT_PATH):
        vec = joblib.load(VECT_PATH)
except Exception:
    clf = vec = None

# ================== HELPERS ==================
def clean_text(s):
    if not s:
        return ""
    return html.unescape(s).strip()

# ================== RETENTION ==================
def cleanup_old_incidents(db):
    now = datetime.utcnow()
    one_month = now - timedelta(days=30)
    two_months = now - timedelta(days=60)

    deleted = (
        db.query(Incident)
        .filter(
            or_(
                Incident.timestamp < two_months,
                and_(
                    Incident.timestamp < one_month,
                    Incident.priority.notin_(["HIGH", "CRITICAL"])
                )
            )
        )
        .delete(synchronize_session=False)
    )

    if deleted:
        print(f"🧹 Retention cleanup removed {deleted} old incidents")

# ================== MAIN ==================
def run_once():
    init_db()
    db = SessionLocal()

    try:
        cleanup_old_incidents(db)

        for feed_url in FEEDS:
            try:
                feed = feedparser.parse(feed_url)
            except Exception as e:
                print("Feed error:", feed_url, e)
                continue

            for entry in feed.entries[:25]:
                title = clean_text(entry.get("title"))
                summary = clean_text(entry.get("summary") or entry.get("description"))
                link = entry.get("link")
                ext_id = entry.get("id") or link

                if not ext_id:
                    continue

                # Deduplication
                exists = (
                    db.query(Incident)
                    .filter(Incident.external_id == ext_id)
                    .first()
                )
                if exists:
                    continue

                # Timestamp
                ts = datetime.utcnow()
                try:
                    if entry.get("published_parsed"):
                        ts = datetime(*entry.published_parsed[:6])
                except Exception:
                    pass

                # Optional ML-based priority prediction
                priority = None
                try:
                    if clf and vec:
                        X = vec.transform([summary or title])
                        priority = clf.predict(X)[0]
                except Exception:
                    pass

                inc = Incident(
                    source=feed_url,
                    external_id=ext_id,
                    title=title,
                    summary=summary,
                    description=summary,
                    url=link,
                    timestamp=ts,
                    priority=priority,
                    category=None,
                    sector=None,
                    geo_scope="Global",
                    is_mitigated=False,
                )

                try:
                    db.add(inc)
                    db.commit()
                except IntegrityError:
                    db.rollback()
                except Exception as e:
                    db.rollback()
                    print("Insert failed:", e)

                time.sleep(0.05)

        print("Collector run completed.")

    finally:
        db.close()
