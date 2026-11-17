import asyncio
import logging
from unittest.mock import ANY

import pytest

from zero_modbus_bridge.mqtt import RecoveringBroker, RecoveringClient

client_log = logging.getLogger("zmqtt.client")


async def test_client_lines_name_the_broker_without_tracebacks(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
):
    run_loops: list[asyncio.Task[None]] = []

    async def run_loop() -> None:
        client_log.warning("Connection lost, reconnecting...")

    async def connect(_: RecoveringClient) -> None:
        refused = ConnectionRefusedError(111, "Connect call failed")
        client_log.warning(
            "Connection failed, retrying in %.1fs", 2.0, exc_info=refused
        )
        run_loops.append(asyncio.create_task(run_loop()))

    monkeypatch.setattr(RecoveringClient, "connect", connect)
    await RecoveringBroker("broker:1883", name="mqtt").connect()
    await run_loops[0]

    assert caplog.messages == [
        "mqtt: Connection failed, retrying in 2.0s: "
        "ConnectionRefusedError: [Errno 111] Connect call failed",
        "mqtt: Connection lost, reconnecting...",
    ]
    assert "Traceback" not in caplog.text


def test_errors_keep_their_traceback(caplog: pytest.LogCaptureFixture):
    client_log.error("Failed", exc_info=RuntimeError("boom"))

    [record] = caplog.records
    assert (record.message, record.exc_info) == ("Failed", (RuntimeError, ANY, None))
