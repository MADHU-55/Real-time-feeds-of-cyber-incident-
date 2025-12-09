# backend/collector/rss_collector.py
"""
Simple RSS collector:
- uses feedparser to fetch several feeds
- runs simple normalization
- stores new incidents into SQLite via SQLAlchemy (models.Incident)
- uses a simple ML model if available to classify priority/anomaly (optional)
"""

import feedparser
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from backend.database import init_db, SessionLocal
from ..models import Incident
import time
import html
import os
import joblib

# feeds list - add government and reputable sources here
FEEDS = [
    # CERT India RSS / advisories
    "https://www.cert-in.org.in/rss.xml",
    # National Cyber Security Centre (example)
    "https://www.ncsc.gov.uk/rss/news",
    # Indian government press release (example)
    "https://pib.gov.in/AllReleaseRSS.aspx?Language=0",
    # cyber security news sites
    "https://threatpost.com/feed/",
    "https://www.bleepingcomputer.com/feed/",
    # generic news (filtering later)
    "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
]

# optional model artifacts
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "ml", "model.joblib")
VECT_PATH = os.path.join(os.path.dirname(__file__), "..", "ml", "vectorizer.joblib")
IF_PATH = os.path.join(os.path.dirname(__file__), "..", "ml", "isolation_forest.joblib")

clf = None
vec = None
iforest = None
try:
    if os.path.exists(MODEL_PATH):
        clf = joblib.load(MODEL_PATH)
    if os.path.exists(VECT_PATH):
        vec = joblib.load(VECT_PATH)
    if os.path.exists(IF_PATH):
        iforest = joblib.load(IF_PATH)
except Exception:
    clf = None
    vec = None
    iforest = None


def normalize_text(s):
    if not s:
        return ""
    s = html.unescape(s)
    return s.strip()


def map_priority_from_pred(pred):
    # If classifier returns a probability or label, map to priority. Here we assume label.
    return pred


def run_once():
    init_db()
    db = SessionLocal()
    try:
        for feed_url in FEEDS:
            try:
                f = feedparser.parse(feed_url)
            except Exception as e:
                print("Feed parse failed:", feed_url, e)
                continue

            for entry in f.entries[:30]:
                title = normalize_text(entry.get("title") or entry.get("summary") or "")
                summary = normalize_text(entry.get("summary") or entry.get("description") or "")
                link = entry.get("link")
                ext_id = entry.get("id") or link
                published = entry.get("published") or entry.get("updated") or None
                ts = None
                if published:
                    try:
                        ts = datetime(*entry.published_parsed[:6])
                    except Exception:
                        try:
                            ts = datetime.strptime(published, "%Y-%m-%dT%H:%M:%S")
                        except Exception:
                            ts = datetime.utcnow()
                else:
                    ts = datetime.utcnow()

                # Basic deduplication: skip if same external id & close timestamp exists
                exists = (
                    db.query(Incident)
                    .filter(Incident.external_id == ext_id)
                    .first()
                )
                if exists:
                    continue

                priority = None
                useful_score = 0.0
                anomaly_score = 0.0
                model_version = None

                # If we have a classifier + vectorizer, predict priority and anomaly
                try:
                    if clf and vec:
                        X = vec.transform([summary or title])
                        pred = clf.predict(X)[0]
                        priority = map_priority_from_pred(pred)
                        model_version = getattr(clf, "version", None)
                    if iforest and vec:
                        X2 = vec.transform([summary or title])
                        # decision_function: higher means more normal -> invert
                        raw = float(iforest.decision_function(X2)[0])
                        # map raw [-1..1] to anomaly_score [0..1]
                        anomaly_score = max(0.0, min(1.0, (1 - ((raw + 1) / 2))))
                except Exception:
                    priority = None

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
                    is_useful=True,
                    useful_score=useful_score,
                    anomaly_score=anomaly_score,
                    model_version=model_version,
                    status="Observed",
                )
                try:
                    db.add(inc)
                    db.commit()
                except IntegrityError:
                    db.rollback()
                except Exception as e:
                    db.rollback()
                    print("Failed to store incident:", e)
                # small delay so some feeds tolerate it
                time.sleep(0.05)
    finally:
        db.close()
