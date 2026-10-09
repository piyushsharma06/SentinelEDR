"""Command-line entry point for SentinelEDR Windows Endpoint Agent."""

import argparse
import json
import logging
import sys
from sentinel_agent import __version__
from sentinel_agent.config import load_agent_config
from sentinel_agent.runner import AgentRunner
from sentinel_agent.collectors.system import get_or_create_stable_host_id, get_system_metadata
from sentinel_agent.queue import PersistentEventQueue
from sentinel_agent.transport import AgentTransport


def configure_logging(level_name: str, log_file: str = None):
    level = getattr(logging, level_name.upper(), logging.INFO)
    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))

    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=handlers
    )


def show_status(config):
    host_id = get_or_create_stable_host_id()
    queue = PersistentEventQueue(config.queue_db_path, config.max_queue_items)
    transport = AgentTransport(config, host_id)
    is_healthy = transport.check_backend_health()
    meta = get_system_metadata()

    status_report = {
        "agent_version": __version__,
        "host_id": host_id,
        "backend_url": config.backend_url,
        "backend_reachable": is_healthy,
        "api_key_configured": bool(config.agent_api_key),
        "queue_depth": queue.size(),
        "max_queue_limit": config.max_queue_items,
        "file_monitoring_enabled": config.file_monitoring_enabled,
        "monitored_directory": config.monitored_directory if config.file_monitoring_enabled else "N/A",
        "system_metadata": meta
    }
    print(json.dumps(status_report, indent=2))


def main():
    parser = argparse.ArgumentParser(description="SentinelEDR Windows Endpoint Agent")
    parser.add_argument("--config", "-c", type=str, help="Path to config.yaml file")
    parser.add_argument("--status", action="store_true", help="Display agent health, queue depth, and host status")
    parser.add_argument("--enroll", action="store_true", help="Manually enroll agent with backend API")
    parser.add_argument("--version", "-v", action="version", version=f"SentinelEDR Agent v{__version__}")

    args = parser.parse_args()

    config = load_agent_config(args.config)
    configure_logging(config.log_level, config.log_file)

    if args.status:
        show_status(config)
        return

    if args.enroll:
        host_id = get_or_create_stable_host_id()
        meta = get_system_metadata()
        transport = AgentTransport(config, host_id)
        print(f"Enrolling host {host_id} ({meta['hostname']}) with {config.backend_url}...")
        key = transport.enroll(meta["hostname"], meta["os_platform"])
        if key:
            print(f"[SUCCESS] Agent enrolled successfully.")
            print(f"API Key: {key}")
            print("Save this key to agent/config.yaml or set SENTINEL_AGENT_API_KEY environment variable.")
        else:
            print("[FAILURE] Failed to enroll agent. Ensure backend is running and enrollment token matches.")
            sys.exit(1)
        return

    # Default: Run agent daemon
    runner = AgentRunner(config)
    runner.start()


if __name__ == "__main__":
    main()
