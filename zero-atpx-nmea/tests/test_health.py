from collections.abc import MutableMapping
from typing import Any
from unittest.mock import AsyncMock

import pytest
from faststream.asgi import HttpHandler
from faststream.mqtt import MQTTBroker

from zero_atpx_nmea.health import live, make_health_asgi


def broker(*, answers: bool) -> MQTTBroker:
    mqtt_broker = MQTTBroker()
    mqtt_broker.ping = AsyncMock(return_value=answers)
    return mqtt_broker


async def get_status(health: HttpHandler) -> int:
    sent: list[MutableMapping[str, Any]] = []

    async def receive() -> MutableMapping[str, Any]:
        return {"type": "http.request"}

    async def send(message: MutableMapping[str, Any]) -> None:
        sent.append(message)

    await health({"type": "http", "method": "GET", "path": "/health"}, receive, send)
    return next(m["status"] for m in sent if m["type"] == "http.response.start")


@pytest.mark.parametrize(
    ("input_answers", "output_answers", "status"),
    [(True, True, 204), (False, True, 500), (True, False, 500)],
)
async def test_ready_only_while_both_brokers_answer(
    input_answers: bool, output_answers: bool, status: int
) -> None:
    health = make_health_asgi(
        broker(answers=input_answers), broker(answers=output_answers)
    )

    assert await get_status(health) == status


async def test_live_without_checking_the_brokers() -> None:
    assert await get_status(live) == 204
