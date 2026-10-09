"""Services package initialization."""

from app.services.audit_service import log_audit_event
from app.services.host_service import register_or_update_host, get_hosts, get_host_by_id
from app.services.event_service import ingest_events_batch, get_events, get_event_by_id
from app.services.alert_service import get_alerts, get_alert_by_id, update_alert
from app.services.incident_service import get_incidents, get_incident_by_id, create_incident, update_incident
from app.services.rule_service import get_rules, get_rule_by_id, toggle_rule

__all__ = [
    "log_audit_event",
    "register_or_update_host",
    "get_hosts",
    "get_host_by_id",
    "ingest_events_batch",
    "get_events",
    "get_event_by_id",
    "get_alerts",
    "get_alert_by_id",
    "update_alert",
    "get_incidents",
    "get_incident_by_id",
    "create_incident",
    "update_incident",
    "get_rules",
    "get_rule_by_id",
    "toggle_rule"
]
