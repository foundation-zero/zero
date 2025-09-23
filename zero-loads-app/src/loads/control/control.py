import asyncio
import logging

from contextlib import asynccontextmanager
from asyncio import Future
from aiomqtt import Client, Client as MqttClient, Message as MqttMessage

from loads.config import Settings

from .message import Case, Conditions, Message

logger = logging.getLogger("control")


POLLING_INTERVAL = 5


class LoadsControl:
    """Control process ingesting conditions via MQTT and ouputting the load case to MQTT"""

    def __init__(
        self,
        mqtt_client: Client,
        stub: bool = True,
        polling_interval: int = POLLING_INTERVAL,
    ):
        self._mqtt_client = mqtt_client
        self._conditions: Conditions | None = None
        self._first_message = Future()
        self._stub = stub
        self._polling_interval = polling_interval

    @asynccontextmanager
    @staticmethod
    async def init_from_settings(settings: Settings):
        async with MqttClient(
            settings.mqtt_host, settings.mqtt_port, identifier="loads_control"
        ) as mqtt_client:
            yield LoadsControl(mqtt_client=mqtt_client)

    async def run(self):
        if self._stub:
            asyncio.create_task(self.run_stub())

        # Listen for incoming sensor values
        asyncio.create_task(self._listen())

        await self._wait_for_values()
        while True:
            try:
                case = await self.determine_load_case()
                await self._send_mqtt_message(case)
                await asyncio.sleep(self._polling_interval)
            except Exception as e:
                logger.error(e)
                break

    async def run_stub(self):
        """Stub to publish conditions to MQTT for development purposes"""
        logger.info("Starting stub to publish conditions")
        while True:
            await self._mqtt_client.publish(
                "loads/risingwave/conditions",
                '{"awa": 45.0, "aws": 12.0, "pcs_mode": {"fwd": "propulsion", "aft": "idle"}, "sails": ["full-main-sail", "main-blade", "full-mizzen-sail"]}',
            )
            await asyncio.sleep(1)

    async def determine_load_case(self) -> Case:
        """Determine the load case by combining  the latest conditions with the computed sea state"""
        sea_state = await self._determine_sea_state()

        if self._conditions:
            return Case(
                sea_state=sea_state,
                awa=self._conditions.awa,
                aws=self._conditions.aws,
                pcs_mode=self._conditions.pcs_mode,
                sails=self._conditions.sails,
            )
        else:
            raise ValueError("self._conditions is None. Cannot determine load case.")

    async def _listen(self):
        """Listen for incoming MQTT messages and store them on the object instance"""
        await self._mqtt_client.subscribe("loads/risingwave/conditions", qos=1)

        async for message in self._mqtt_client.messages:
            logging.info(
                f"Received message on topic {message.topic}: {message.payload}"
            )
            if message.topic.matches("loads/risingwave/conditions"):
                self._conditions = self._parse_message(message, Conditions)
                if not self._first_message.done():
                    self._first_message.set_result(self._conditions)

    def _parse_message(
        self, message: MqttMessage, model: type[Conditions]
    ) -> Conditions:
        """Parse an incoming MQTT message into the specified model"""
        if not isinstance(message.payload, (str, bytes)):
            raise ValueError(f"Expected string or bytes, got {type(message.payload)}")
        return model.model_validate_json(message.payload)

    async def _determine_sea_state(self) -> str:
        """Placeholder: Determine sea state based on conditions"""
        return "wet"

    async def _wait_for_values(self):
        """Wait until the first message has been received"""
        return await self._first_message

    async def _send_mqtt_message(self, message: Message):
        logging.info(f"Publishing case to topic {message.TOPIC}")
        await self._mqtt_client.publish(
            message.TOPIC,
            message.model_dump_json(exclude_none=True),
            qos=1,
        )
