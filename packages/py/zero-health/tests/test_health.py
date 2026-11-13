import asyncio
import logging
import socket
from typing import NoReturn

import pytest
from pydantic import ValidationError

from zero_health import Health, HealthSettings, exit_with_reason
from zero_health import health as health_module


class Exited(Exception):
    pass


def _exit(reason: str) -> NoReturn:
    raise Exited(reason)


class FakeClock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now


class Dependency:
    """A check whose answer the test sets, counting how often it is asked."""

    def __init__(self, reason: str | None = None) -> None:
        self.reason = reason
        self.calls = 0

    async def __call__(self) -> str | None:
        self.calls += 1
        return self.reason


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock()


@pytest.fixture
def settings() -> HealthSettings:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    return HealthSettings(port=port, check_interval=10, check_timeout=0.05)


def make_health(
    settings: HealthSettings, clock: FakeClock, **checks: Dependency
) -> Health:
    return Health(settings, checks, clock=clock, exit_process=_exit)


async def get(port: int, path: str) -> tuple[int, str]:
    reader, writer = await asyncio.open_connection("127.0.0.1", port)
    writer.write(f"GET {path} HTTP/1.1\r\nHost: localhost\r\n\r\n".encode())
    response = await reader.read()
    writer.close()
    head, body = response.decode().split("\r\n\r\n", 1)
    return int(head.split(" ")[1]), body


async def test_not_ready_until_checked(settings, clock):
    health = make_health(settings, clock, mqtt=Dependency())

    assert health.failures() == ["mqtt: not checked yet"]
    await health.run_checks()
    assert health.failures() == []


async def test_lists_every_failing_check(settings, clock):
    health = make_health(
        settings,
        clock,
        input=Dependency("ping failed (not connected)"),
        output=Dependency(),
        modbus=Dependency("connection refused"),
    )

    await health.run_checks()

    assert health.failures() == [
        "input: ping failed (not connected)",
        "modbus: connection refused",
    ]


async def test_slow_check_fails_on_timeout(settings, clock):
    async def hangs() -> str | None:
        await asyncio.sleep(1)
        return None

    health = Health(settings, {"mqtt": hangs}, clock=clock, exit_process=_exit)

    await health.run_checks()

    assert health.failures() == ["mqtt: no answer within 0.05 s"]


async def test_raising_check_fails_with_the_error(settings, clock):
    async def raises() -> str | None:
        raise ConnectionError("broker gone")

    health = Health(settings, {"mqtt": raises}, clock=clock, exit_process=_exit)

    await health.run_checks()

    assert health.failures() == ["mqtt: ConnectionError: broker gone"]


async def test_logs_each_change(settings, clock, caplog):
    mqtt = Dependency("ping failed")
    health = make_health(settings, clock, mqtt=mqtt)
    caplog.set_level(logging.INFO, logger="zero_health")

    await health.run_checks()
    await health.run_checks()
    mqtt.reason = None
    await health.run_checks()

    assert caplog.messages == ["mqtt: not ready: ping failed", "mqtt: ready"]


async def test_exits_when_not_ready_past_the_deadline(settings, clock):
    mqtt = Dependency("ping failed")
    health = make_health(settings, clock, mqtt=mqtt)

    clock.now = 899
    await health.run_checks()
    clock.now = 900
    with pytest.raises(Exited, match=r"^not ready for 900 s: mqtt: ping failed$"):
        await health.run_checks()


async def test_ready_restarts_the_deadline(settings, clock):
    mqtt = Dependency()
    health = make_health(settings, clock, mqtt=mqtt)

    clock.now = 800
    await health.run_checks()
    mqtt.reason = "ping failed"
    await health.run_checks()
    clock.now = 1600
    await health.run_checks()
    clock.now = 1700
    with pytest.raises(Exited):
        await health.run_checks()


def test_deadline_must_exceed_ten_minutes(monkeypatch):
    monkeypatch.setenv("HEALTH_DEADLINE_SECONDS", "600")

    with pytest.raises(ValidationError):
        HealthSettings()


async def test_endpoints_serve_the_last_results(settings, clock):
    mqtt = Dependency()
    modbus = Dependency("connection refused")
    health = make_health(settings, clock, mqtt=mqtt, modbus=modbus)

    async with health.serve():
        await asyncio.sleep(0.01)
        ready = await get(settings.port, "/health/ready")
        alive = await get(settings.port, "/health/alive")
        missing = await get(settings.port, "/metrics")

    assert ready == (500, "modbus: connection refused\n")
    assert alive == (204, "")
    assert missing == (404, "")
    assert (mqtt.calls, modbus.calls) == (1, 1)


async def test_ready_when_every_check_passes(settings, clock):
    health = make_health(settings, clock, mqtt=Dependency())

    async with health.serve():
        await asyncio.sleep(0.01)
        assert await get(settings.port, "/health/ready") == (204, "")


async def test_drops_malformed_requests(settings, clock):
    health = make_health(settings, clock, mqtt=Dependency())

    async with health.serve():
        reader, writer = await asyncio.open_connection("127.0.0.1", settings.port)
        writer.write(b"nonsense\r\n\r\n")
        assert await reader.read() == b""
        writer.close()


def test_exit_leaves_the_reason_as_termination_message(monkeypatch, tmp_path):
    termination_log = tmp_path / "termination-log"
    monkeypatch.setattr(health_module, "TERMINATION_LOG", termination_log)
    monkeypatch.setattr(health_module.os, "_exit", _exit)

    with pytest.raises(Exited):
        exit_with_reason("mqtt: ping failed")

    assert termination_log.read_text() == "mqtt: ping failed"


def test_exit_outside_kubernetes(monkeypatch, tmp_path):
    monkeypatch.setattr(health_module, "TERMINATION_LOG", tmp_path / "missing" / "log")
    monkeypatch.setattr(health_module.os, "_exit", _exit)

    with pytest.raises(Exited):
        exit_with_reason("mqtt: ping failed")
