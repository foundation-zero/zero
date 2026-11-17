import logging
from collections.abc import MutableMapping
from typing import Any
from unittest.mock import AsyncMock

import pytest
from faststream.asgi import HttpHandler
from faststream.mqtt import MQTTBroker

from zero_atpx_nmea.health import make_health_asgi


class Brokers:
    """The two brokers, with their pings answering or not as a test sets."""

    def __init__(self) -> None:
        self.input_ping = AsyncMock(return_value=True)
        self.output_ping = AsyncMock(return_value=True)
        input_broker, output_broker = MQTTBroker(), MQTTBroker()
        input_broker.ping = self.input_ping
        output_broker.ping = self.output_ping
        self.health = make_health_asgi(
            {"atpx-mqtt": input_broker, "mqtt": output_broker}
        )


@pytest.fixture
def brokers() -> Brokers:
    return Brokers()


async def get_status(health: HttpHandler) -> int:
    sent: list[MutableMapping[str, Any]] = []

    async def receive() -> MutableMapping[str, Any]:
        return {"type": "http.request"}

    async def send(message: MutableMapping[str, Any]) -> None:
        sent.append(message)

    await health({"type": "http", "method": "GET", "path": "/health"}, receive, send)
    return next(m["status"] for m in sent if m["type"] == "http.response.start")


async def test_both_brokers_up_is_ready(brokers: Brokers) -> None:
    assert await get_status(brokers.health) == 204


@pytest.mark.parametrize(
    ("failing_ping", "name"), [("input_ping", "atpx-mqtt"), ("output_ping", "mqtt")]
)
async def test_either_broker_down_is_not_ready(
    brokers: Brokers, failing_ping: str, name: str, caplog: pytest.LogCaptureFixture
) -> None:
    getattr(brokers, failing_ping).return_value = False

    assert await get_status(brokers.health) == 500
    assert caplog.messages == [f"Not ready: {name} did not answer a ping"]


async def test_logs_only_changes_in_readiness(
    brokers: Brokers, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.INFO)

    await get_status(brokers.health)
    await get_status(brokers.health)
    brokers.output_ping.return_value = False
    await get_status(brokers.health)
    await get_status(brokers.health)
    brokers.input_ping.return_value = False
    await get_status(brokers.health)
    brokers.input_ping.return_value = True
    brokers.output_ping.return_value = True
    await get_status(brokers.health)

    assert caplog.messages == [
        "Ready: atpx-mqtt, mqtt answer pings",
        "Not ready: mqtt did not answer a ping",
        "Not ready: atpx-mqtt, mqtt did not answer a ping",
        "Ready: atpx-mqtt, mqtt answer pings",
    ]
