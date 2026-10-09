"""Security overview dashboard statistics schemas."""

from typing import Any, Dict, List
from pydantic import BaseModel


class DashboardStatsOut(BaseModel):
    total_hosts: int
    online_hosts: int
    offline_hosts: int
    degraded_hosts: int
    total_events: int
    total_alerts: int
    new_alerts: int
    investigating_alerts: int
    resolved_alerts: int
    alerts_by_severity: Dict[str, int]
    total_incidents: int
    open_incidents: int
    investigating_incidents: int
    demo_mode: bool
    events_timeline: List[Dict[str, Any]]
    alerts_timeline: List[Dict[str, Any]]
