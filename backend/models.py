from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, UniqueConstraint
from datetime import datetime
from .database import Base

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True)
    source = Column(String, nullable=False)
    external_id = Column(String, nullable=False)

    title = Column(String, nullable=False)
    summary = Column(String)
    description = Column(String)
    url = Column(String)

    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    ingested_at = Column(DateTime, default=datetime.utcnow)

    priority = Column(String, default="LOW")
    category = Column(String)
    sector = Column(String)
    geo_scope = Column(String)

    is_mitigated = Column(Boolean, default=False)
    anomaly_score = Column(Float)
    threat_score = Column(Float)

    __table_args__ = (
        UniqueConstraint("source", "external_id", name="uq_incident_source_ext"),
    )
