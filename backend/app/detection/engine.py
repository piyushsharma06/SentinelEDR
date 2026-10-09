"""SentinelEDR Detection Engine: rule evaluation, alert generation, and deduplication."""

import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from app.config import settings
from app.detection.evaluator import evaluate_detection_block, get_field_value
from app.detection.models import DetectionBlockSchema
from app.models.alert import Alert
from app.models.event import SecurityEvent
from app.models.rule import DetectionRule

logger = logging.getLogger(__name__)


class DetectionEngine:
    """Core evaluation engine that evaluates events against rules and generates alerts."""

    def __init__(self, db: Session):
        self.db = db

    def evaluate_event(self, event: SecurityEvent, event_dict: Optional[Dict[str, Any]] = None) -> List[Alert]:
        """
        Evaluate a single security event against all enabled detection rules.
        Handles alert deduplication within the configured time window.
        Returns newly generated or updated Alert objects.
        """
        if event_dict is None:
            # Reconstruct dictionary from event attributes and raw data
            event_dict = {
                "event_uuid": event.event_uuid,
                "host_id": event.host_id,
                "event_type": event.event_type,
                "timestamp": event.timestamp.isoformat() if event.timestamp else "",
                "process_name": event.process_name,
                "process_id": event.process_id,
                "parent_process_name": event.parent_process_name,
                "parent_process_id": event.parent_process_id,
                "command_line": event.command_line,
                "username": event.username,
                "network_remote_ip": event.network_remote_ip,
                "network_remote_port": event.network_remote_port,
                "network_protocol": event.network_protocol,
                "file_path": event.file_path,
                "file_action": event.file_action,
                "data": event.data or {}
            }

        # Query enabled detection rules
        active_rules = self.db.query(DetectionRule).filter(DetectionRule.enabled == True).all()
        resulting_alerts: List[Alert] = []

        now_utc = datetime.now(timezone.utc)
        dedup_window = timedelta(minutes=settings.alert_deduplication_window_minutes)

        for rule in active_rules:
            try:
                conditions_data = rule.conditions
                if not conditions_data or not isinstance(conditions_data, dict):
                    continue

                detection_block = DetectionBlockSchema(**conditions_data)
                matched = evaluate_detection_block(detection_block, event_dict)
                if not matched:
                    continue

                # Rule matched! Extract evidence
                evidence: Dict[str, Any] = {}
                evidence_fields = rule.evidence_fields or [
                    "process_name", "process_id", "command_line", "parent_process_name",
                    "network_remote_ip", "network_remote_port", "file_path"
                ]
                for field in evidence_fields:
                    val = get_field_value(event_dict, field)
                    if val is not None:
                        evidence[field] = val

                # Check for existing alert within deduplication window
                cutoff_time = now_utc - dedup_window
                existing_alert = (
                    self.db.query(Alert)
                    .filter(
                        Alert.rule_id == rule.rule_id,
                        Alert.host_id == event.host_id,
                        Alert.status.in_(["new", "acknowledged", "investigating"]),
                        Alert.last_seen >= cutoff_time
                    )
                    .order_by(Alert.last_seen.desc())
                    .first()
                )

                if existing_alert:
                    # Deduplicate: update count, timestamps, and attach event
                    existing_alert.event_count += 1
                    existing_alert.last_seen = now_utc
                    existing_alert.evidence_summary = {**existing_alert.evidence_summary, **evidence}
                    # Prevent duplicate linkage in many-to-many table
                    event_already_linked = any(
                        (e.id is not None and e.id == event.id) or e.event_uuid == event.event_uuid
                        for e in existing_alert.events
                    )
                    if not event_already_linked:
                        existing_alert.events.append(event)
                    resulting_alerts.append(existing_alert)
                    logger.info(f"Deduplicated alert {existing_alert.alert_id} for rule {rule.rule_id} on host {event.host_id}")
                else:
                    # Create new alert
                    alert_uid = f"ALT-{uuid.uuid4().hex[:8].upper()}"
                    new_alert = Alert(
                        alert_id=alert_uid,
                        rule_id=rule.rule_id,
                        host_id=event.host_id,
                        severity=rule.severity,
                        status="new",
                        title=f"{rule.name}",
                        description=rule.description,
                        evidence_summary=evidence,
                        mitre_technique_id=rule.mitre_technique_id,
                        mitre_technique_name=rule.mitre_technique_name,
                        mitre_tactic=rule.mitre_tactic,
                        first_seen=event.timestamp or now_utc,
                        last_seen=event.timestamp or now_utc,
                        event_count=1,
                        is_synthetic=event.is_synthetic
                    )
                    new_alert.events.append(event)
                    self.db.add(new_alert)
                    resulting_alerts.append(new_alert)
                    logger.info(f"Generated new alert {new_alert.alert_id} for rule {rule.rule_id} on host {event.host_id}")

            except Exception as e:
                logger.error(f"Error evaluating rule {rule.rule_id} against event {event.event_uuid}: {e}", exc_info=False)
                # Continue processing remaining rules
                continue

        return resulting_alerts
