# backend/models.py
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean
from sqlalchemy.sql import func
from .database import Base


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(255), unique=False, index=True, nullable=True)
    source = Column(String(255), nullable=True)
    title = Column(String(1024), nullable=True)
    summary = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    url = Column(String(2048), nullable=True)
    timestamp = Column(DateTime, nullable=True, index=True)
    ingested_at = Column(DateTime, server_default=func.now())
    priority = Column(String(50), nullable=True, index=True)
    category = Column(String(255), nullable=True)
    sector = Column(String(255), nullable=True)
    geo_scope = Column(String(255), nullable=True)
    status = Column(String(255), nullable=True)
    is_critical = Column(Boolean, default=False)
    is_mitigated = Column(Boolean, default=False)
    is_useful = Column(Boolean, default=True)
    useful_score = Column(Float, default=0.0)
    anomaly_score = Column(Float, default=0.0)
    model_version = Column(String(128), nullable=True)
    threat_score = Column(Float, default=0.0)


class ModelMetrics(Base):
    __tablename__ = "model_metrics"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    model_version = Column(String(128), nullable=True)
    accuracy = Column(Float, nullable=True)
    drift_score = Column(Float, nullable=True)
    drift_detected = Column(Boolean, default=False)
