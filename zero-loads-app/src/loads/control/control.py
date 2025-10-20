import logging
from asyncio import Future
from contextlib import asynccontextmanager
from typing import Coroutine

from aiomqtt import Client
from aiomqtt import Client as MqttClient
from aiomqtt import Message as MqttMessage

from loads.config import Settings

from .message import Conditions, Message, SensorInput

logger = logging.getLogger("control")


class Control:
    """Control process ingesting sensor data via MQTT and outputting the conditions to MQTT"""

    def __init__(self, mqtt_client: Client):
        self._mqtt_client = mqtt_client
        self._sensor_input: SensorInput | None = None
        self._first_message: Future = Future()

    @asynccontextmanager
    @staticmethod
    async def init_from_settings(settings: Settings):
        async with MqttClient(
            settings.mqtt_host, settings.mqtt_port, identifier="loads_control"
        ) as mqtt_client:
            yield Control(mqtt_client=mqtt_client)

    async def run(self) -> Coroutine:
        await self._mqtt_client.subscribe("loads/sensor_input", qos=1)

        async def _run(self):
            async for message in self._mqtt_client.messages:
                if message.topic.matches("loads/sensor_input"):
                    self._sensor_input = self._parse_message(message, SensorInput)
                    if not self._first_message.done():
                        self._first_message.set_result(self._sensor_input)

                    conditions = await self._determine_conditions()
                    await self._send_mqtt_message(conditions)

        return _run(self)

    async def _determine_conditions(self) -> Conditions:
        """Determine the conditions by combining the sensor data with the computed sea state"""
        sea_state = await self._determine_sea_state()

        if self._sensor_input:
            return Conditions(
                sea_state=sea_state,
                awa=self._sensor_input.awa,
                aws=self._sensor_input.aws,
                pcs_mode=self._sensor_input.pcs_mode,
                sails=self._sensor_input.sails,
            )
        else:
            raise ValueError("self._sensor_input is None. Cannot determine conditions.")

    async def wait_for_values(self):
        """Wait until the first message has been received"""
        return await self._first_message

    async def _determine_sea_state(self) -> str:
        """Placeholder: Determine sea state based on conditions"""
        return "wet"

    def _parse_message(
        self, message: MqttMessage, model: type[Conditions]
    ) -> Conditions:
        """Parse an incoming MQTT message into the specified model"""
        if not isinstance(message.payload, (str, bytes)):
            raise ValueError(f"Expected string or bytes, got {type(message.payload)}")
        return model.model_validate_json(message.payload)

    async def _send_mqtt_message(self, message: Message):
        logging.info(f"Publishing messages to topic {message.TOPIC}")
        await self._mqtt_client.publish(
            message.TOPIC,
            message.model_dump_json(exclude_none=True),
            qos=1,
        )
