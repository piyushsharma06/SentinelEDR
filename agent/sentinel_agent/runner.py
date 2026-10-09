"""Agent runtime orchestrator managing collection loops, disk queueing, and flush cycles."""

import logging
import signal
import sys
import time
from typing import Optional
from sentinel_agent.config import AgentConfig
from sentinel_agent.queue import PersistentEventQueue
from sentinel_agent.transport import AgentTransport
from sentinel_agent.collectors.system import (
    get_or_create_stable_host_id,
    get_system_metadata,
    collect_agent_health
)
from sentinel_agent.collectors.process import ProcessCollector
from sentinel_agent.collectors.network import NetworkCollector
from sentinel_agent.collectors.file import DirectoryWatcher

logger = logging.getLogger("sentinel.agent")


class AgentRunner:
    """Manages collection loops, queuing, and background dispatching."""

    def __init__(self, config: AgentConfig):
        self.config = config
        self.host_id = get_or_create_stable_host_id()
        self.queue = PersistentEventQueue(
            db_path=config.queue_db_path,
            max_items=config.max_queue_items
        )
        self.transport = AgentTransport(config, self.host_id)

        # Collectors
        self.process_collector = ProcessCollector(self.host_id)
        self.network_collector = NetworkCollector(self.host_id)
        self.file_watcher: Optional[DirectoryWatcher] = None
        if config.file_monitoring_enabled:
            self.file_watcher = DirectoryWatcher(self.host_id, config.monitored_directory)

        self._running = False
        self._consecutive_errors = 0
        self._last_error = ""

    def start(self):
        """Start the agent collectors and dispatch loops."""
        self._running = True
        logger.info(f"Starting SentinelEDR Agent for host '{self.host_id}'...")

        # Perform enrollment if needed
        if not self.transport.api_key:
            if self.config.auto_enroll:
                sys_meta = get_system_metadata()
                logger.info("Attempting auto-enrollment with backend API...")
                key = self.transport.enroll(sys_meta["hostname"], sys_meta["os_platform"])
                if not key:
                    logger.warning("Agent auto-enrollment failed. Will buffer events locally until enrolled.")
            else:
                logger.warning("No agent API key provided and auto-enroll is disabled.")

        if self.file_watcher:
            self.file_watcher.start()

        last_proc_tick = 0.0
        last_net_tick = 0.0
        last_health_tick = 0.0
        last_flush_tick = 0.0

        try:
            while self._running:
                now = time.time()

                # 1. Process collector tick
                if now - last_proc_tick >= self.config.process_poll_interval:
                    try:
                        proc_events = self.process_collector.collect()
                        if proc_events:
                            self.queue.enqueue_batch(proc_events)
                            logger.debug(f"Collected {len(proc_events)} process events")
                    except Exception as e:
                        logger.error(f"Error in process collector: {e}")
                        self._consecutive_errors += 1
                        self._last_error = str(e)
                    last_proc_tick = now

                # 2. Network collector tick
                if now - last_net_tick >= self.config.network_poll_interval:
                    try:
                        net_events = self.network_collector.collect()
                        if net_events:
                            self.queue.enqueue_batch(net_events)
                            logger.debug(f"Collected {len(net_events)} network events")
                    except Exception as e:
                        logger.error(f"Error in network collector: {e}")
                        self._consecutive_errors += 1
                        self._last_error = str(e)
                    last_net_tick = now

                # 3. File collector drain (if active)
                if self.file_watcher:
                    try:
                        file_events = self.file_watcher.collect()
                        if file_events:
                            self.queue.enqueue_batch(file_events)
                    except Exception as e:
                        logger.error(f"Error in file collector: {e}")

                # 4. Agent health heartbeat tick
                if now - last_health_tick >= self.config.health_interval:
                    try:
                        health_evt = collect_agent_health(
                            host_id=self.host_id,
                            consecutive_errors=self._consecutive_errors,
                            last_error=self._last_error
                        )
                        self.queue.enqueue(health_evt)
                    except Exception as e:
                        logger.error(f"Error generating agent health event: {e}")
                    last_health_tick = now

                # 5. Flush queue to backend
                if now - last_flush_tick >= self.config.flush_interval_seconds:
                    self._flush_queue()
                    last_flush_tick = now

                time.sleep(1.0)

        except KeyboardInterrupt:
            logger.info("Agent received shutdown signal...")
        finally:
            self.stop()

    def _flush_queue(self):
        """Pop items from disk queue and deliver via transport."""
        queue_size = self.queue.size()
        if queue_size == 0:
            return

        batch_items = self.queue.peek_batch(limit=self.config.batch_size)
        if not batch_items:
            return

        row_ids = [item[0] for item in batch_items]
        event_payloads = [item[1] for item in batch_items]

        success, accepted, err = self.transport.send_events_batch(event_payloads)
        if success:
            self.queue.acknowledge_batch(row_ids)
            logger.info(f"Delivered {accepted} events to backend. Remaining queue depth: {self.queue.size()}")
            self._consecutive_errors = 0
            self._last_error = ""
        else:
            logger.warning(f"Failed to deliver {len(event_payloads)} events to backend ({err}). Events buffered in local queue.")
            self._consecutive_errors += 1
            self._last_error = err

    def stop(self):
        """Gracefully stop background collectors and close transport."""
        self._running = False
        if self.file_watcher:
            self.file_watcher.stop()
        self.transport.close()
        logger.info("SentinelEDR Agent shut down cleanly.")
