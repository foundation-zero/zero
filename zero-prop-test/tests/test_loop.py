import json
from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from zero_prop_test.io_link import Client as IoLinkClient, IoLinkDevice, Sm6120
from zero_prop_test.loop import Loop
from zero_prop_test.modbus import (
    Address as ModbusAddress,
    Client as ModbusClient,
    Register,
    RegisterType,
)
from zero_prop_test.settings import Settings


@pytest.fixture
def settings() -> Settings:
    return Settings(
        iolink_host="127.0.0.1",
        iolink_port=1,
        modbus_host="127.0.0.1",
        modbus_port=2,
        twincat_self_netid="1.2.3.4.5.6",
        twincat_ip="192.168.0.10",
        twincat_netid="5.6.7.8.9.10",
        twincat_username="user",
        twincat_password="password",
        twincat_route_name="route",
        mqtt_host="broker.local",
        mqtt_port=1883,
        mqtt_username="mqtt-user",
        mqtt_password="mqtt-password",
    )


@pytest.fixture
def loop() -> Loop:
    return Loop(mqtt=MagicMock(), interval=timedelta(seconds=1))


async def test_from_settings_creates_loop_with_mqtt_from_settings(settings: Settings):
    iolink = MagicMock(spec=IoLinkClient)
    interval = timedelta(seconds=10)

    with patch("zero_prop_test.loop.MqttClient") as mock_mqtt_cls:
        mock_mqtt_instance = MagicMock()
        mock_mqtt_cls.return_value = mock_mqtt_instance

        async with Loop.from_settings(
            settings, iolink_client=iolink, interval=interval
        ):
            pass

    mock_mqtt_cls.assert_called_once_with(
        hostname=settings.mqtt_host,
        port=settings.mqtt_port,
        username=settings.mqtt_username,
        password=settings.mqtt_password,
    )


async def test_tick_publishes_json_to_mqtt(loop: Loop):
    iolink = AsyncMock(spec=IoLinkClient)
    device = IoLinkDevice("flow", "tag", "192.168.1.2", 1, Sm6120)
    iolink.query.return_value = 7.5

    loop._iolink_client = iolink
    loop._mqtt.publish = AsyncMock()
    await loop.tick([device])

    loop._mqtt.publish.assert_awaited_once()
    topic, payload = loop._mqtt.publish.call_args.args
    assert topic == "prop-test/data"

    data = json.loads(payload)
    assert "timestamp" in data
    assert data["devices"]["flow"] == 7.5


async def test_tick_message_contains_all_collected_devices(loop: Loop):
    modbus = MagicMock(spec=ModbusClient)
    register = Register[float](
        address=0, scaling=None, datatype=float, type=RegisterType.HOLDING
    )
    addresses = [
        ModbusAddress(name="sensor-a", yard_tag="tag-a", register=register),
        ModbusAddress(name="sensor-b", yard_tag="tag-b", register=register),
    ]
    modbus.query.return_value = 1.0

    loop._modbus_client = modbus
    loop._mqtt.publish = AsyncMock()
    await loop.tick(addresses)

    _, payload = loop._mqtt.publish.call_args.args
    data = json.loads(payload)
    assert set(data["devices"].keys()) == {"sensor-a", "sensor-b"}
