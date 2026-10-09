"""Deterministic Synthetic Demo Data Generator for SentinelEDR.

This module simulates realistic SOC analyst telemetry and threat detection workflows
without executing actual malware, network attacks, or invasive system actions.
"""

import logging
import sys
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.database.session import SessionLocal, engine, Base
from app.models import (
    Host,
    SecurityEvent,
    DetectionRule,
    Alert,
    Incident,
    AnalystUser,
    AuditLog
)
from app.detection.rule_loader import sync_rules_to_db
from app.services.event_service import ingest_events_batch
from app.schemas.event import NormalizedEvent

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("sentinel.demo.seed")


def clear_synthetic_data(db: Session):
    """Clean up previous synthetic demo records to ensure idempotency."""
    logger.info("Cleaning up previous synthetic demo records...")
    from sqlalchemy import text
    try:
        db.execute(text("DELETE FROM alert_events"))
        db.query(Incident).filter(Incident.is_synthetic == True).delete(synchronize_session=False)
        db.query(Alert).filter(Alert.is_synthetic == True).delete(synchronize_session=False)
        db.query(SecurityEvent).filter(SecurityEvent.is_synthetic == True).delete(synchronize_session=False)
        db.query(Host).filter(Host.is_synthetic == True).delete(synchronize_session=False)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.warning(f"Note during clear: {e}")
    logger.info("Previous synthetic records cleared.")


def seed_demo_data(db: Session):
    """Seed comprehensive deterministic synthetic endpoints, telemetry, alerts, and incidents."""
    Base.metadata.create_all(bind=engine)
    sync_rules_to_db(db)
    clear_synthetic_data(db)

    now = datetime.now(timezone.utc)
    t_minus_1h = now - timedelta(hours=1)
    t_minus_45m = now - timedelta(minutes=45)
    t_minus_30m = now - timedelta(minutes=30)
    t_minus_15m = now - timedelta(minutes=15)
    t_minus_5m = now - timedelta(minutes=5)

    logger.info("Creating synthetic endpoints...")
    host1 = Host(
        host_id="HOST-DEMO-FIN01",
        hostname="FIN-WIN11-EXEC",
        os_platform="Windows",
        os_version="11 Enterprise 23H2",
        agent_version="1.0.0",
        first_seen=now - timedelta(days=7),
        last_seen=now - timedelta(minutes=1),
        status="online",
        ip_addresses=["10.0.50.42"],
        system_info={"cpu": "Intel Core i7-13700", "memory_mb": 32768, "domain": "CORP.SENTINEL.LOCAL"},
        is_synthetic=True
    )
    host2 = Host(
        host_id="HOST-DEMO-DEV02",
        hostname="ENG-WIN10-WS02",
        os_platform="Windows",
        os_version="10 Pro 22H2",
        agent_version="1.0.0",
        first_seen=now - timedelta(days=14),
        last_seen=now - timedelta(minutes=3),
        status="online",
        ip_addresses=["10.0.20.15"],
        system_info={"cpu": "AMD Ryzen 7 5800X", "memory_mb": 65536, "domain": "CORP.SENTINEL.LOCAL"},
        is_synthetic=True
    )
    host3 = Host(
        host_id="HOST-DEMO-SRV03",
        hostname="DMZ-WEB-SRV01",
        os_platform="Windows",
        os_version="Server 2022 Datacenter",
        agent_version="1.0.0",
        first_seen=now - timedelta(days=30),
        last_seen=now - timedelta(hours=2),
        status="degraded",
        ip_addresses=["10.0.100.5"],
        system_info={"cpu": "Intel Xeon Gold 6330", "memory_mb": 131072, "role": "IIS Reverse Proxy"},
        is_synthetic=True
    )
    db.add_all([host1, host2, host3])
    db.commit()

    # Generate synthetic telemetry stream
    logger.info("Generating synthetic security events stream...")

    synthetic_events = [
        # --- BENIGN BASELINE TELEMETRY ---
        NormalizedEvent(
            event_uuid="EVT-SYN-001-EXPLORER",
            host_id="HOST-DEMO-FIN01",
            event_type="process_creation",
            timestamp=t_minus_1h,
            is_synthetic=True,
            data={
                "process_name": "explorer.exe",
                "process_id": 1420,
                "process_path": "C:\\Windows\\explorer.exe",
                "parent_process_name": "userinit.exe",
                "command_line": "C:\\Windows\\explorer.exe",
                "username": "SENTINEL\\jdoe"
            }
        ),
        NormalizedEvent(
            event_uuid="EVT-SYN-002-CHROME",
            host_id="HOST-DEMO-FIN01",
            event_type="process_creation",
            timestamp=t_minus_1h + timedelta(minutes=5),
            is_synthetic=True,
            data={
                "process_name": "chrome.exe",
                "process_id": 3840,
                "process_path": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                "parent_process_name": "explorer.exe",
                "command_line": "\"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe\" --type=normal",
                "username": "SENTINEL\\jdoe"
            }
        ),

        # --- ATTACK CHAIN 1: SPEARPHISHING TO POWERSHELL EXECUTION ---
        # 1. Word opened
        NormalizedEvent(
            event_uuid="EVT-SYN-003-WORD",
            host_id="HOST-DEMO-FIN01",
            event_type="process_creation",
            timestamp=t_minus_45m,
            is_synthetic=True,
            data={
                "process_name": "winword.exe",
                "process_id": 5120,
                "process_path": "C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE",
                "parent_process_name": "explorer.exe",
                "command_line": "\"C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE\" \"C:\\Users\\jdoe\\Downloads\\Invoice_Q3_Approved.docx\"",
                "username": "SENTINEL\\jdoe"
            }
        ),
        # 2. Word spawns PowerShell (Triggers RULE-001)
        NormalizedEvent(
            event_uuid="EVT-SYN-004-WORD-PS",
            host_id="HOST-DEMO-FIN01",
            event_type="process_creation",
            timestamp=t_minus_45m + timedelta(seconds=12),
            is_synthetic=True,
            data={
                "process_name": "powershell.exe",
                "process_id": 7890,
                "process_path": "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe",
                "parent_process_id": 5120,
                "parent_process_name": "winword.exe",
                "command_line": "powershell.exe -windowstyle hidden -ExecutionPolicy Bypass -enc SQBFAFgA...",
                "username": "SENTINEL\\jdoe"
            }
        ),
        # 3. Encoded PowerShell command execution (Triggers RULE-002)
        NormalizedEvent(
            event_uuid="EVT-SYN-005-CLI-BYPASS",
            host_id="HOST-DEMO-FIN01",
            event_type="process_creation",
            timestamp=t_minus_45m + timedelta(seconds=15),
            is_synthetic=True,
            data={
                "process_name": "powershell.exe",
                "process_id": 7890,
                "parent_process_name": "winword.exe",
                "command_line": "powershell.exe -w hidden bypass -enc SQBFAFgA...",
                "username": "SENTINEL\\jdoe"
            }
        ),
        # 4. Outbound network connection from powershell (Triggers RULE-004)
        NormalizedEvent(
            event_uuid="EVT-SYN-006-C2-NET",
            host_id="HOST-DEMO-FIN01",
            event_type="network_connection",
            timestamp=t_minus_30m,
            is_synthetic=True,
            data={
                "process_id": 7890,
                "process_name": "powershell.exe",
                "local_address": "10.0.50.42",
                "local_port": 49832,
                "remote_address": "198.51.100.23",
                "remote_port": 443,
                "protocol": "tcp",
                "status": "ESTABLISHED"
            }
        ),
        # 5. Staged payload dropped in Temp (Triggers RULE-003)
        NormalizedEvent(
            event_uuid="EVT-SYN-007-TEMP-EXEC",
            host_id="HOST-DEMO-FIN01",
            event_type="process_creation",
            timestamp=t_minus_15m,
            is_synthetic=True,
            data={
                "process_name": "updater_stager.exe",
                "process_id": 9104,
                "process_path": "C:\\Users\\jdoe\\AppData\\Local\\Temp\\updater_stager.exe",
                "parent_process_name": "powershell.exe",
                "command_line": "\"C:\\Users\\jdoe\\AppData\\Local\\Temp\\updater_stager.exe\" --silent",
                "username": "SENTINEL\\jdoe"
            }
        ),

        # --- ATTACK CHAIN 2: HONEYPOT DIRECTORY TAMPERING ---
        NormalizedEvent(
            event_uuid="EVT-SYN-008-FILE-LOCKED",
            host_id="HOST-DEMO-DEV02",
            event_type="file_activity",
            timestamp=t_minus_30m,
            is_synthetic=True,
            data={
                "file_path": "C:\\Honeypot\\Customer_Database.sqlite.locked",
                "file_name": "Customer_Database.sqlite.locked",
                "extension": ".locked",
                "file_size": 4194304,
                "action": "created",
                "process_id": 4412,
                "process_name": "unknown_proc.exe"
            }
        ),

        # --- ATTACK CHAIN 3: AGENT HEALTH SENSOR TAMPERING ---
        NormalizedEvent(
            event_uuid="EVT-SYN-009-HEALTH-DEGRADED",
            host_id="HOST-DEMO-SRV03",
            event_type="agent_health",
            timestamp=t_minus_5m,
            is_synthetic=True,
            data={
                "status": "degraded",
                "consecutive_collection_errors": 5,
                "last_error_message": "Network transport timeout connecting to ingestion gateway",
                "agent_version": "1.0.0",
                "memory_usage_mb": 42.5
            }
        )
    ]

    # Ingest events through standard pipeline so rules evaluate and create alerts
    logger.info("Ingesting events and triggering detection engine...")
    accepted, rejected, duplicates, alerts_gen = ingest_events_batch(db, synthetic_events)
    logger.info(f"Ingestion complete: {accepted} accepted, {alerts_gen} alerts generated.")

    # Find generated alerts for linking
    alerts = db.query(Alert).filter(Alert.is_synthetic == True).all()

    # Pre-populate Incident 1: Phishing to Execution
    inc1_alerts = [a.alert_id for a in alerts if a.host_id == "HOST-DEMO-FIN01"]
    if inc1_alerts:
        inc1 = Incident(
            incident_id="INC-DEMO-PHISH-01",
            title="Suspicious Office Macro Spawning PowerShell & Beaconing on FIN-WIN11-EXEC",
            description="Analyst investigation of spearphishing document Invoice_Q3_Approved.docx spawning PowerShell with execution policy bypass, followed by outbound C2 socket activity to 198.51.100.23.",
            severity="high",
            status="investigating",
            assigned_to="admin",
            investigation_notes=[
                {
                    "id": "note-001",
                    "author": "admin",
                    "text": "Alert triage confirmed winword.exe spawned powershell.exe with -WindowStyle Hidden. Endpoint isolated from production VLAN.",
                    "timestamp": (now - timedelta(minutes=35)).isoformat()
                },
                {
                    "id": "note-002",
                    "author": "admin",
                    "text": "Outbound connection to 198.51.100.23:443 analyzed against threat intelligence feed. Stager payload in %TEMP% preserved for reverse engineering.",
                    "timestamp": (now - timedelta(minutes=20)).isoformat()
                }
            ],
            created_at=t_minus_45m,
            updated_at=now - timedelta(minutes=20),
            is_synthetic=True
        )
        db.add(inc1)
        db.flush()

        for a in alerts:
            if a.alert_id in inc1_alerts:
                a.incident_id = inc1.incident_id
                a.status = "investigating"
                a.assigned_to = "admin"

    # Pre-populate Incident 2: Ransomware honeypot
    inc2_alerts = [a.alert_id for a in alerts if a.host_id == "HOST-DEMO-DEV02"]
    if inc2_alerts:
        inc2 = Incident(
            incident_id="INC-DEMO-RANSOM-02",
            title="Potential Ransomware Encryption Detected in Monitored Directory",
            description="Monitored honeypot directory detected creation of .locked extension on ENG-WIN10-WS02.",
            severity="medium",
            status="open",
            assigned_to="admin",
            investigation_notes=[
                {
                    "id": "note-003",
                    "author": "admin",
                    "text": "File rename anomaly flagged. Investigating source process PID 4412.",
                    "timestamp": (now - timedelta(minutes=25)).isoformat()
                }
            ],
            created_at=t_minus_30m,
            updated_at=now - timedelta(minutes=25),
            is_synthetic=True
        )
        db.add(inc2)
        db.flush()

        for a in alerts:
            if a.alert_id in inc2_alerts:
                a.incident_id = inc2.incident_id
                a.status = "investigating"

    # Add audit log
    audit_entry = AuditLog(
        actor_username="system:demo_seeder",
        action="demo.seeded",
        resource_type="system",
        resource_id="demo_data",
        details={
            "endpoints_created": 3,
            "events_ingested": len(synthetic_events),
            "alerts_created": len(alerts),
            "incidents_created": 2
        },
        timestamp=now
    )
    db.add(audit_entry)

    db.commit()
    logger.info("=================================================================")
    logger.info("SYNTHETIC DEMO DATA GENERATION COMPLETED SUCCESSFULLY!")
    logger.info(f" - Enrolled Endpoints : 3 ({host1.hostname}, {host2.hostname}, {host3.hostname})")
    logger.info(f" - Telemetry Events   : {len(synthetic_events)}")
    logger.info(f" - Alerts Generated   : {len(alerts)}")
    logger.info(f" - Incidents Seeded   : 2 (INC-DEMO-PHISH-01, INC-DEMO-RANSOM-02)")
    logger.info("All records are safely marked with is_synthetic=True.")
    logger.info("=================================================================")


def main():
    db = SessionLocal()
    try:
        seed_demo_data(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
