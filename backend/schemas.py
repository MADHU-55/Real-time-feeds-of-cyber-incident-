# schemas.py
from datetime import datetime
from pydantic import BaseModel


class IncidentBase(BaseModel):
    title: str
    summary: str | None = None
    description: str | None = None
    url: str | None = None
    timestamp: datetime | None = None
    priority: str | None = None
    category: str | None = None
    sector: str | None = None
    geo_scope: str | None = None
    status: str | None = None
    is_critical: bool | None = None
    is_mitigated: bool | None = None
    apt_group: str | None = None


class IncidentCreate(IncidentBase):
    pass


class IncidentOut(IncidentBase):
    id: int
    source: str | None = None
    ingested_at: datetime | None = None
    useful_score: float | None = None
    anomaly_score: float | None = None
    model_version: str | None = None

    class Config:
        from_attributes = True


class DashboardSummary(BaseModel):
    total_threats_today: int
    critical_incidents: int
    affected_sectors: int
    threats_mitigated: int


class ThreatDistributionItem(BaseModel):
    category: str
    count: int


class TrendPoint(BaseModel):
    day: str
    detected: int
    mitigated: int


class DriftStatus(BaseModel):
    model_version: str
    drift_detected: bool
    drift_score: float | None = None
    last_updated: datetime
