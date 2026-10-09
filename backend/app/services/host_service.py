"""Host service for managing enrolled endpoints."""

from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.host import Host
from app.models.alert import Alert
from app.schemas.host import HostRegisterRequest


def register_or_update_host(db: Session, data: HostRegisterRequest) -> Host:
    """Register a new host or update existing host heartbeat metadata."""
    now_utc = datetime.now(timezone.utc)
    host = db.query(Host).filter(Host.host_id == data.host_id).first()
    if host:
        host.hostname = data.hostname
        host.os_platform = data.os_platform
        if data.os_version:
            host.os_version = data.os_version
        host.agent_version = data.agent_version
        if data.ip_addresses:
            host.ip_addresses = data.ip_addresses
        if data.system_info:
            host.system_info = data.system_info
        host.last_seen = now_utc
        host.status = "online"
    else:
        host = Host(
            host_id=data.host_id,
            hostname=data.hostname,
            os_platform=data.os_platform,
            os_version=data.os_version,
            agent_version=data.agent_version,
            ip_addresses=data.ip_addresses,
            system_info=data.system_info,
            status="online",
            first_seen=now_utc,
            last_seen=now_utc,
            is_synthetic=data.is_synthetic
        )
        db.add(host)
    db.commit()
    db.refresh(host)
    return host


def get_hosts(
    db: Session,
    status_filter: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 50
) -> Tuple[List[dict], int]:
    """Retrieve paginated hosts with associated alert counts."""
    query = db.query(Host)

    if status_filter:
        query = query.filter(Host.status == status_filter)
    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            (Host.hostname.ilike(search_fmt)) |
            (Host.host_id.ilike(search_fmt)) |
            (Host.os_platform.ilike(search_fmt))
        )

    total = query.count()
    hosts = query.order_by(Host.last_seen.desc()).offset((page - 1) * page_size).limit(page_size).all()

    # Query active alerts count for each host
    results = []
    for h in hosts:
        active_alerts_cnt = (
            db.query(func.count(Alert.id))
            .filter(Alert.host_id == h.host_id, Alert.status.in_(["new", "acknowledged", "investigating"]))
            .scalar() or 0
        )
        results.append({
            "id": h.id,
            "host_id": h.host_id,
            "hostname": h.hostname,
            "os_platform": h.os_platform,
            "os_version": h.os_version,
            "agent_version": h.agent_version,
            "first_seen": h.first_seen,
            "last_seen": h.last_seen,
            "status": h.status,
            "ip_addresses": h.ip_addresses or [],
            "system_info": h.system_info or {},
            "is_synthetic": h.is_synthetic,
            "alerts_count": active_alerts_cnt
        })

    return results, total


def get_host_by_id(db: Session, host_id: str) -> Optional[dict]:
    """Get single host details with alert counts."""
    h = db.query(Host).filter((Host.host_id == host_id) | (Host.id == int(host_id) if host_id.isdigit() else False)).first()
    if not h:
        return None

    active_alerts_cnt = (
        db.query(func.count(Alert.id))
        .filter(Alert.host_id == h.host_id, Alert.status.in_(["new", "acknowledged", "investigating"]))
        .scalar() or 0
    )

    return {
        "id": h.id,
        "host_id": h.host_id,
        "hostname": h.hostname,
        "os_platform": h.os_platform,
        "os_version": h.os_version,
        "agent_version": h.agent_version,
        "first_seen": h.first_seen,
        "last_seen": h.last_seen,
        "status": h.status,
        "ip_addresses": h.ip_addresses or [],
        "system_info": h.system_info or {},
        "is_synthetic": h.is_synthetic,
        "alerts_count": active_alerts_cnt
    }
