"""Readiness status file and the 15 minute not-ready deadline (docs/adr/0001).

Each required dependency reports itself ready or not ready. The status goes to
a file that the chart's exec readiness probe prints, so the reason shows up in
the pod's `Readiness probe failed` events. After 15 minutes not ready the
process exits with the reason as its termination message.

The deadline is checked whenever a dependency reports itself not ready, so the
callers must report every failed attempt, not only the first one.

Copied from zero-modbus-bridge, with the status line of zero-battery-cells.
"""

import logging
import os
import time
from collections.abc import Callable, Iterable
from datetime import UTC, datetime
from pathlib import Path
from typing import NoReturn

logger = logging.getLogger(__name__)

# On the emptyDir the chart mounts at /tmp; its readiness probe reads it.
STATUS_FILE = Path("/tmp/ready")
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
    """Ready once every required dependency has reported itself ready.

    The status file holds one line, such as
    ``not ready: mqtt: CONNACK refused (return code 135) since 13:02:05 UTC``.
    """

    def __init__(
        self,
        status_file: Path,
        dependencies: Iterable[str],
        deadline_seconds: float = DEADLINE_SECONDS,
        *,
        clock: Callable[[], float] = time.monotonic,
        exit_process: Callable[[str], NoReturn] = exit_with_reason,
    ):
        """Start not ready on each of ``dependencies``, and write the status file.

        Writing at once replaces the status a previous container left on the
        emptyDir, which outlives container restarts.
        """
        self._status_file = status_file
        self._deadline_seconds = deadline_seconds
        self._clock = clock
        self._exit_process = exit_process
        # Each dependency's (ready, reason), in the order they were given.
        self._states = {name: (False, "connecting") for name in dependencies}
        # When the pod last became ready or not ready; the deadline counts from here.
        self._since = clock()
        self._since_clock = _utc_clock()
        self._status = ""
        self._write()

    @property
    def status(self) -> str:
        return self._status

    def ready(self, dependency: str, reason: str) -> None:
        self._set(dependency, True, reason)

    def not_ready(self, dependency: str, reason: str) -> None:
        """A new reason while already not ready keeps the deadline running."""
        self._set(dependency, False, reason)
        if self._clock() - self._since >= self._deadline_seconds:
            self.exit(f"not ready for {self._deadline_seconds / 60:g} min")

    def exit(self, reason: str) -> NoReturn:
        """Exit with ``reason`` plus the current status as termination message."""
        self._exit_process(f"{reason} ({self._status})")

    def _is_ready(self) -> bool:
        return all(ready for ready, _ in self._states.values())

    def _set(self, dependency: str, ready: bool, reason: str) -> None:
        was_ready = self._is_ready()
        self._states[dependency] = (ready, reason)
        if self._is_ready() != was_ready:
            self._since = self._clock()
            self._since_clock = _utc_clock()
        self._write()

    def _write(self) -> None:
        # Not ready lists only the dependencies that are down.
        is_ready = self._is_ready()
        details = "; ".join(
            f"{name}: {reason}"
            for name, (ready, reason) in self._states.items()
            if is_ready or not ready
        )
        state = "ready" if is_ready else "not ready"
        status = f"{state}: {details} since {self._since_clock} UTC"
        if status == self._status:
            return
        logger.info("Readiness: %s", status)
        self._status = status
        # Write and rename, so the probe never reads a half-written file.
        partial = self._status_file.with_name(f".{self._status_file.name}.partial")
        try:
            partial.write_text(f"{status}\n")
            partial.replace(self._status_file)
        except OSError as exc:
            logger.error("Failed to write readiness to %s: %s", self._status_file, exc)


def _utc_clock() -> str:
    return datetime.now(UTC).strftime("%H:%M:%S")
