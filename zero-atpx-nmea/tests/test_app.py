import logging
from unittest.mock import AsyncMock

import pytest
from faststream.mqtt import MQTTBroker, TestMQTTBroker
from zmqtt import MQTTDisconnectedError

from zero_atpx_nmea.app import build_app
from zero_atpx_nmea.settings import InputMqttSettings, OutputMqttSettings


async def test_output_outage_logs_one_line_per_outage(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
):
    input_broker, output_broker = MQTTBroker(), MQTTBroker()
    publish = AsyncMock(side_effect=MQTTDisconnectedError("Connection lost"))
    monkeypatch.setattr(output_broker, "publish", publish)
    monkeypatch.setattr(InputMqttSettings, "make_broker", lambda _: input_broker)
    monkeypatch.setattr(OutputMqttSettings, "make_broker", lambda _: output_broker)
    build_app(
        InputMqttSettings(atpx_mqtt_host="localhost", atpx_mqtt_port=1883),
        OutputMqttSettings(mqtt_host="localhost", mqtt_port=1883),
    )
    caplog.set_level(logging.INFO, logger="zero_atpx_nmea")

    async with TestMQTTBroker(input_broker) as test_broker:
        for _ in range(3):
            await test_broker.publish("$HEROT,000.1,A*2A", "atpx/nmea0183/3143/ROT")
        publish.side_effect = None
        await test_broker.publish("$HEROT,000.1,A*2A", "atpx/nmea0183/3143/ROT")

    assert publish.await_count == 4
    assert [(r.levelname, r.message) for r in caplog.records] == [
        (
            "WARNING",
            "Publishing to the output broker failed (Connection lost), "
            "dropping messages until it is back",
        ),
        ("INFO", "Publishing again, dropped 3 message(s)"),
    ]
    assert "Traceback" not in caplog.text
