import asyncio
import logging

from contextlib import asynccontextmanager
from aiomqtt import Client, Client as MqttClient

from loads.config import Settings


logger = logging.getLogger("control")


INTERVAL = 5


class SensorStub:
    def __init__(
        self,
        mqtt_client: Client,
        topic: str = "loads/risingwave/conditions",
        interval: int = INTERVAL,
    ):
        self._mqtt_client = mqtt_client
        self._topic = topic
        self._interval = interval

    @asynccontextmanager
    @staticmethod
    async def init_from_settings(settings: Settings):
        async with MqttClient(
            settings.mqtt_host, settings.mqtt_port, identifier="loads_sensor_stub"
        ) as mqtt_client:
            yield SensorStub(mqtt_client=mqtt_client)

    async def run(self):
        """Stub to publish conditions to MQTT for development purposes"""
        logger.info("Starting stub to publish conditions")
        while True:
            await self._mqtt_client.publish(
                f"{self._topic}",
                '{"awa": 45.0, "aws": 12.0, "pcs_mode": {"fwd": "propulsion", "aft": "idle"}, "sails": ["full-main-sail", "main-blade", "full-mizzen-sail"]}',
            )
            await asyncio.sleep(self._interval)
