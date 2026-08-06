"""Relay-switching Modbus-to-MQTT bridge for hull temperature."""

import json
import logging

from faststream.mqtt import MQTTBroker, QoS
from jsonpath_ng import parse
from zero_modbus_bridge.bridge import ModbusBridge
from zero_modbus_bridge.io import ModbusTopic
from zero_modbus_bridge.settings import ModbusSettings

from zero_hull_temperature.addresses import HULL_TEMPERATURE_TOPIC, PATH, TOPIC
from zero_hull_temperature.mqtt import MqttValue

logger = logging.getLogger(__name__)


class RelaySwitchingBridge(ModbusBridge):
    """Modbus-to-MQTT bridge that activates a relay before each Modbus read."""

    def __init__(
        self,
        modbus,
        broker: MQTTBroker,
        topics: list[ModbusTopic],
        probe_interval: float = 10.0,
        *,
        activate_topic: str = TOPIC,
        activate_json_path: str = PATH,
    ):
        super().__init__(modbus, broker, topics, probe_interval)
        self._activate_topic = activate_topic
        self._activate_json_path = parse(activate_json_path)

    @staticmethod
    def from_settings(  # type: ignore[override]
        modbus_settings: ModbusSettings,
        broker: MQTTBroker,
        activate_topic: str = TOPIC,
        activate_json_path: str = PATH,
    ) -> "RelaySwitchingBridge":
        return RelaySwitchingBridge(
            modbus_settings.modbus_client(),
            broker,
            [HULL_TEMPERATURE_TOPIC],
            modbus_settings.modbus_probe_interval,
            activate_topic=activate_topic,
            activate_json_path=activate_json_path,
        )

    async def run_once(self) -> None:
        await self._send_activate(True)
        await super().run_once()

    async def _send_activate(self, activate: bool) -> None:
        payload = self._activate_json_path.update_or_create(
            {}, MqttValue.model_construct(value=activate).model_dump(by_alias=True)
        )
        await self._broker.publish(
            json.dumps(payload), self._activate_topic, qos=QoS.AT_LEAST_ONCE
        )
