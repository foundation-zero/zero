import logging
from unittest.mock import AsyncMock

import pytest
from faststream.mqtt import MQTTBroker, TestMQTTBroker
from zmqtt import MQTTDisconnectedError

from zero_atpx_nmea.app import build_app


async def test_output_outage_logs_one_line_per_outage(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
):
    input_broker, output_broker = MQTTBroker(), MQTTBroker()
    publish = AsyncMock(side_effect=MQTTDisconnectedError("Connection lost"))
    monkeypatch.setattr(output_broker, "publish", publish)
    build_app(input_broker, output_broker)
    caplog.set_level(logging.INFO, logger="zero_atpx_nmea")

    async with TestMQTTBroker(input_broker) as broker:
        for _ in range(3):
            await broker.publish("$HEROT,000.1,A*2A", "atpx/nmea0183/3143/ROT")
        publish.side_effect = None
        await broker.publish("$HEROT,000.1,A*2A", "atpx/nmea0183/3143/ROT")

    assert publish.await_count == 4
    assert [(r.levelname, r.message) for r in caplog.records] == [
        ("WARNING", "mqtt-output: Connection lost, dropping messages until it is back"),
        ("INFO", "mqtt-output: publishing again, dropped 3 message(s)"),
    ]
    assert "Traceback" not in caplog.text
