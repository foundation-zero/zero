"""Readiness and liveness over HTTP (docs/adr/0001-dependency-outages.md)."""

import asyncio
import logging
import os
import time
from collections.abc import AsyncIterator, Awaitable, Callable, Mapping
from contextlib import asynccontextmanager, suppress
from pathlib import Path
from typing import Annotated, NoReturn

from pydantic import Field, PositiveFloat
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

TERMINATION_LOG = Path("/dev/termination-log")
# The kubelet waits 1 s (timeoutSeconds) for a probe answer.
REQUEST_TIMEOUT = 1.0
NOT_FOUND = b"HTTP/1.1 404 Not Found\r\nConnection: close\r\nContent-Length: 0\r\n\r\n"

type Check = Callable[[], Awaitable[str | None]]
"""Returns ``None`` while the dependency is usable, otherwise why it is not."""


class HealthSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="HEALTH_", env_file=".env", extra="ignore"
    )

    port: int = 8080
    check_interval: PositiveFloat = 10.0
    check_timeout: PositiveFloat = 5.0
    # The kubelet resets its restart backoff only after 10 minutes of running.
    deadline_seconds: Annotated[float, Field(gt=600)] = 900.0


def exit_with_reason(reason: str) -> NoReturn:
    """Exit at once with ``reason`` as the container's termination message.

    ``os._exit`` because a graceful shutdown could wait on the very client
    that failed.
    """
    logger.critical("Exiting: %s", reason)
    try:
        TERMINATION_LOG.write_text(reason)
    except OSError:
        logger.debug("No %s to write to (not in Kubernetes?)", TERMINATION_LOG)
    logging.shutdown()
    os._exit(1)


class Health:
    """Runs ``checks`` on an interval and serves the last results.

    ``/health/ready`` fails while any check fails. ``/health/alive`` always
    answers, so it fails only when the event loop is blocked. Not ready for
    longer than the deadline exits the process.
    """

    def __init__(
        self,
        settings: HealthSettings,
        checks: Mapping[str, Check],
        *,
        clock: Callable[[], float] = time.monotonic,
        exit_process: Callable[[str], NoReturn] = exit_with_reason,
    ):
        self._settings = settings
        self._checks = checks
        self._clock = clock
        self._exit_process = exit_process
        self._reasons: dict[str, str | None] = dict.fromkeys(checks, "not checked yet")
        self._not_ready_since: float | None = clock()

    def failures(self) -> list[str]:
        return [
            f"{name}: {reason}"
            for name, reason in self._reasons.items()
            if reason is not None
        ]

    async def run_checks(self) -> None:
        async with asyncio.TaskGroup() as task_group:
            tasks = {
                name: task_group.create_task(self._run(check))
                for name, check in self._checks.items()
            }
        for name, task in tasks.items():
            reason = task.result()
            if reason != self._reasons[name]:
                if reason is None:
                    logger.info("%s: ready", name)
                else:
                    logger.warning("%s: not ready: %s", name, reason)
            self._reasons[name] = reason
        self._enforce_deadline(self._clock())

    async def _run(self, check: Check) -> str | None:
        timeout = self._settings.check_timeout
        try:
            async with asyncio.timeout(timeout):
                return await check()
        except TimeoutError:
            return f"no answer within {timeout:g} s"
        except Exception as exc:
            return f"{type(exc).__name__}: {exc}"

    def _enforce_deadline(self, now: float) -> None:
        if not (failures := self.failures()):
            self._not_ready_since = None
            return
        if self._not_ready_since is None:
            self._not_ready_since = now
        deadline = self._settings.deadline_seconds
        if now - self._not_ready_since >= deadline:
            self._exit_process(f"not ready for {deadline:g} s: {'; '.join(failures)}")

    @asynccontextmanager
    async def serve(self) -> AsyncIterator[None]:
        """Serve the endpoints and run the checks while the block runs."""
        server = await asyncio.start_server(self._respond, port=self._settings.port)
        async with server:
            monitor = asyncio.create_task(self._monitor())
            try:
                yield
            finally:
                monitor.cancel()
                with suppress(asyncio.CancelledError):
                    await monitor

    async def _monitor(self) -> None:
        while True:
            await self.run_checks()
            await asyncio.sleep(self._settings.check_interval)

    async def _respond(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        # uvicorn's Server.serve() replaces the SIGINT/SIGTERM handlers that
        # FastStream's app.run() installs; probes need only these few lines of
        # HTTP/1.1.
        try:
            async with asyncio.timeout(REQUEST_TIMEOUT):
                head = await reader.readuntil(b"\r\n\r\n")
                _, path, _ = head.split(b"\r\n", 1)[0].split(b" ", 2)
                match path:
                    case b"/health/ready":
                        writer.write(_response(self.failures()))
                    case b"/health/alive":
                        writer.write(_response([]))
                    case _:
                        writer.write(NOT_FOUND)
                await writer.drain()
        except (
            TimeoutError,
            ValueError,
            asyncio.IncompleteReadError,
            asyncio.LimitOverrunError,
            OSError,
        ) as exc:
            logger.debug("Dropped a health request: %r", exc)
        finally:
            writer.close()


def _response(failures: list[str]) -> bytes:
    if not failures:
        return b"HTTP/1.1 204 No Content\r\nConnection: close\r\n\r\n"
    body = "".join(f"{failure}\n" for failure in failures).encode()
    return (
        b"HTTP/1.1 500 Internal Server Error\r\n"
        b"Content-Type: text/plain; charset=utf-8\r\n"
        b"Connection: close\r\n"
        b"Content-Length: " + str(len(body)).encode() + b"\r\n\r\n" + body
    )
