"""Security event ingestion and query service."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.detection.engine import DetectionEngine
from app.models.event import SecurityEvent
from app.models.host import Host
from app.schemas.event import NormalizedEvent

logger = logging.getLogger(__name__)


def ingest_events_batch(db: Session, events: List[NormalizedEvent]) -> Tuple[int, int, int, int]:
    """
    Process and ingest a batch of normalized security events.
    Returns: (accepted, rejected, duplicates, alerts_generated)
    """
    accepted = 0
    rejected = 0
    duplicates = 0
    alerts_generated = 0

    detection_engine = DetectionEngine(db)
    now_utc = datetime.now(timezone.utc)

    for ev in events:
        try:
            # Check duplicate event_uuid
            existing = db.query(SecurityEvent).filter(SecurityEvent.event_uuid == ev.event_uuid).first()
            if existing:
                duplicates += 1
                continue

            # Ensure host exists, update last_seen
            host = db.query(Host).filter(Host.host_id == ev.host_id).first()
            if not host:
                host = Host(
                    host_id=ev.host_id,
                    hostname=ev.host_id,
                    os_platform="Windows",
                    agent_version="1.0.0",
                    status="online",
                    first_seen=now_utc,
                    last_seen=now_utc,
                    is_synthetic=ev.is_synthetic
                )
                db.add(host)
            else:
                host.last_seen = now_utc
                host.status = "online"

            # Flatten specific metadata for query optimization
            data = ev.data or {}
            proc_name = data.get("process_name")
            proc_id = data.get("process_id")
            parent_proc = data.get("parent_process_name")
            parent_id = data.get("parent_process_id")
            cmd_line = data.get("command_line")
            user = data.get("username")
            remote_ip = data.get("remote_address") or data.get("network_remote_ip")
            remote_port = data.get("remote_port") or data.get("network_remote_port")
            protocol = data.get("protocol") or data.get("network_protocol")
            file_path = data.get("file_path")
            file_action = data.get("action") or data.get("file_action")

            sec_event = SecurityEvent(
                event_uuid=ev.event_uuid,
                host_id=ev.host_id,
                event_type=ev.event_type,
                timestamp=ev.timestamp,
                ingested_at=now_utc,
                schema_version=ev.schema_version,
                data=data,
                process_name=proc_name,
                process_id=proc_id,
                parent_process_name=parent_proc,
                parent_process_id=parent_id,
                command_line=cmd_line,
                username=user,
                network_remote_ip=remote_ip,
                network_remote_port=remote_port,
                network_protocol=protocol,
                file_path=file_path,
                file_action=file_action,
                is_synthetic=ev.is_synthetic
            )
            db.add(sec_event)
            db.flush()  # Generate event ID for relation

            # Run detection engine
            generated_alerts = detection_engine.evaluate_event(sec_event)
            alerts_generated += len(generated_alerts)
            accepted += 1

        except Exception as e:
            logger.error(f"Error ingesting event {ev.event_uuid}: {e}", exc_info=False)
            rejected += 1

    db.commit()
    return accepted, rejected, duplicates, alerts_generated


def get_events(
    db: Session,
    host_id: Optional[str] = None,
    event_type: Optional[str] = None,
    process_name: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    is_synthetic: Optional[bool] = None,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 50
) -> Tuple[List[SecurityEvent], int]:
    """Retrieve filtered, paginated events."""
    query = db.query(SecurityEvent)

    if host_id:
        query = query.filter(SecurityEvent.host_id == host_id)
    if event_type:
        query = query.filter(SecurityEvent.event_type == event_type)
    if process_name:
        query = query.filter(SecurityEvent.process_name.ilike(f"%{process_name}%"))
    if start_time:
        query = query.filter(SecurityEvent.timestamp >= start_time)
    if end_time:
        query = query.filter(SecurityEvent.timestamp <= end_time)
    if is_synthetic is not None:
        query = query.filter(SecurityEvent.is_synthetic == is_synthetic)
    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            (SecurityEvent.command_line.ilike(search_fmt)) |
            (SecurityEvent.process_name.ilike(search_fmt)) |
            (SecurityEvent.file_path.ilike(search_fmt)) |
            (SecurityEvent.network_remote_ip.ilike(search_fmt))
        )

    total = query.count()
    events = (
        query.order_by(desc(SecurityEvent.timestamp))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return events, total


def get_event_by_id(db: Session, event_id: str) -> Optional[SecurityEvent]:
    """Retrieve a single security event by internal ID or event UUID."""
    if event_id.isdigit():
        return db.query(SecurityEvent).filter(SecurityEvent.id == int(event_id)).first()
    return db.query(SecurityEvent).filter(SecurityEvent.event_uuid == event_id).first()
