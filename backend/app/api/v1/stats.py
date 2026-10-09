"""Dashboard statistics API router."""

from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.config import settings
from app.database.session import get_db
from app.models.analyst import AnalystUser
from app.models.host import Host
from app.models.event import SecurityEvent
from app.models.alert import Alert
from app.models.incident import Incident
from app.schemas.stats import DashboardStatsOut
from app.auth.rbac import require_any_authenticated

router = APIRouter(prefix="/stats", tags=["System"])


@router.get("", response_model=DashboardStatsOut)
def get_security_overview_stats(
    db: Session = Depends(get_db),
    current_user: AnalystUser = Depends(require_any_authenticated)
):
    """Aggregate real database-backed security overview metrics."""
    # Hosts
    total_hosts = db.query(Host).count()
    online_hosts = db.query(Host).filter(Host.status == "online").count()
    offline_hosts = db.query(Host).filter(Host.status == "offline").count()
    degraded_hosts = db.query(Host).filter(Host.status.in_(["degraded", "stale"])).count()

    # Events
    total_events = db.query(SecurityEvent).count()

    # Alerts
    total_alerts = db.query(Alert).count()
    new_alerts = db.query(Alert).filter(Alert.status == "new").count()
    investigating_alerts = db.query(Alert).filter(Alert.status == "investigating").count()
    resolved_alerts = db.query(Alert).filter(Alert.status.in_(["resolved", "false_positive"])).count()

    # Severity breakdown
    severity_counts = (
        db.query(Alert.severity, func.count(Alert.id))
        .group_by(Alert.severity)
        .all()
    )
    severity_map = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    for sev, cnt in severity_counts:
        if sev in severity_map:
            severity_map[sev] = cnt

    # Incidents
    total_incidents = db.query(Incident).count()
    open_incidents = db.query(Incident).filter(Incident.status == "open").count()
    investigating_incidents = db.query(Incident).filter(Incident.status == "investigating").count()

    # Check if any synthetic data exists to flag demo mode
    synthetic_count = db.query(Host).filter(Host.is_synthetic == True).count()
    is_demo = settings.demo_mode or (synthetic_count > 0)

    # Timeline (last 7 intervals / hours)
    now = datetime.now(timezone.utc)
    events_timeline = []
    alerts_timeline = []

    for i in range(6, -1, -1):
        window_start = now - timedelta(hours=i + 1)
        window_end = now - timedelta(hours=i)
        label = window_end.strftime("%H:%M")

        ev_cnt = (
            db.query(SecurityEvent)
            .filter(SecurityEvent.timestamp >= window_start, SecurityEvent.timestamp < window_end)
            .count()
        )
        alt_cnt = (
            db.query(Alert)
            .filter(Alert.last_seen >= window_start, Alert.last_seen < window_end)
            .count()
        )
        events_timeline.append({"time": label, "count": ev_cnt})
        alerts_timeline.append({"time": label, "count": alt_cnt})

    return DashboardStatsOut(
        total_hosts=total_hosts,
        online_hosts=online_hosts,
        offline_hosts=offline_hosts,
        degraded_hosts=degraded_hosts,
        total_events=total_events,
        total_alerts=total_alerts,
        new_alerts=new_alerts,
        investigating_alerts=investigating_alerts,
        resolved_alerts=resolved_alerts,
        alerts_by_severity=severity_map,
        total_incidents=total_incidents,
        open_incidents=open_incidents,
        investigating_incidents=investigating_incidents,
        demo_mode=is_demo,
        events_timeline=events_timeline,
        alerts_timeline=alerts_timeline
    )
