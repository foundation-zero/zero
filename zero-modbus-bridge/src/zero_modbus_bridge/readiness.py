"""Readiness status file and the 15 minute not-ready deadline (docs/adr/0001).

Each required dependency reports itself ready or not ready. The status goes to
a file that the chart's exec readiness probe prints, so the reason shows up in
the pod's `Readiness probe failed` events. After 15 minutes not ready the
process exits with the reason as its termination message.

The deadline is checked whenever a dependency reports itself not ready, so the
callers must report every failed attempt, not only the first one.

Self-contained on purpose: apps that don't use zero-modbus-bridge copy this file.
"""

import logging
import os
import time
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import NoReturn

logger = logging.getLogger(__name__)

DEADLINE_SECONDS = 15 * 60
TERMINATION_LOG = Path("/dev/termination-log")


def exit_with_reason(reason: str) -> NoReturn:
    """Exit at once with ``reason`` as the container's termination message.

    ``os._exit`` because this runs inside client tasks, where a ``SystemExit``
    would start a graceful shutdown that waits on the very client that failed.
    """
    logger.critical("Exiting: %s", reason)
    try:
        TERMINATION_LOG.write_text(reason)
    except OSError:
        logger.debug("No %s to write to (not in Kubernetes?)", TERMINATION_LOG)
    logging.shutdown()
    os._exit(1)


class Readiness:
    """Ready while no dependency reports itself not ready."""

    def __init__(
        self,
        status_file: Path | None,
        deadline_seconds: float = DEADLINE_SECONDS,
        *,
        clock: Callable[[], float] = time.monotonic,
        exit_process: Callable[[str], NoReturn] = exit_with_reason,
    ):
        """``status_file`` is None for one-shot commands that have no probe."""
        self._status_file = status_file
        self._deadline_seconds = deadline_seconds
        self._clock = clock
        self._exit_process = exit_process
        self._reasons: dict[str, str] = {}
        self._not_ready_at: float | None = None
        self._not_ready_since = ""
        self._status = ""

    @property
    def status(self) -> str:
        return self._status

    def ready(self, dependency: str) -> None:
        self._reasons.pop(dependency, None)
        if not self._reasons:
            self._not_ready_at = None
        self._write()

    def not_ready(self, dependency: str, reason: str) -> None:
        if self._not_ready_at is None:
            self._not_ready_at = self._clock()
            self._not_ready_since = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        self._reasons[dependency] = reason
        self._write()
        if self._clock() - self._not_ready_at >= self._deadline_seconds:
            self.exit(f"not ready for {self._deadline_seconds / 60:g} min")

    def exit(self, reason: str) -> NoReturn:
        """Exit with ``reason`` plus the current status as termination message."""
        self._exit_process(f"{reason} ({self._status})" if self._status else reason)

    def _write(self) -> None:
        details = "; ".join(f"{name}: {why}" for name, why in self._reasons.items())
        status = (
            f"not ready since {self._not_ready_since}: {details}"
            if details
            else "ready"
        )
        if status == self._status:
            return
        logger.info("Readiness: %s", status)
        self._status = status
        if self._status_file is None:
            return
        # Write and rename, so the probe never reads a half-written file.
        partial = self._status_file.with_name(f".{self._status_file.name}.partial")
        partial.write_text(f"{status}\n")
        partial.replace(self._status_file)
