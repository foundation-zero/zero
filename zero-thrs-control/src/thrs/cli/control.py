import datetime
import logging
from asyncio import TaskGroup, sleep
from typing import get_args

from aiomqtt import Client as MqttClient, Topic

from thrs.classes.control import Control
from thrs.control.modules.consumers import ConsumersControl, ConsumersParameters
from thrs.control.modules.pcm import PcmControl, PcmParameters
from thrs.control.modules.pvt import PvtControl, PvtParameters
from thrs.control.modules.thrusters import ThrustersControl, ThrustersParameters
from thrs.input_output.base import ThrsValues
from thrs.input_output.model_builder import PartialModelBuilder
from thrs.orchestration.config import Config
from thrs.orchestration.module import PartialMqttMapping

logger = logging.getLogger(__name__)


class Controller:
    def __init__(
        self,
        control_class: type[Control],
        parameters: ThrsValues,
        name: str,
        topic_prefix: str,
        control_topic_suffix: str = "Command",
    ):
        self.name = name
        self._interval = 1
        self._running = False
        self._topic_prefix = topic_prefix
        self._control_topic_suffix = control_topic_suffix

        # Time tracking - updated from sensor timestamps
        self._current_time = datetime.datetime.now()

        # Create control with our time method
        self.control = control_class(parameters, self.time)

        # Get the type parameters from Control
        type_params = get_args(control_class.__orig_bases__[0])
        self.sensor_values_type, self.control_values_type, self.parameters_type = (
            type_params
        )

        # Create MQTT mappings for sensor and control values
        self._sensor_mapping = PartialMqttMapping(
            self.sensor_values_type, topic_suffix=None
        )
        self._control_mapping = PartialMqttMapping(
            self.control_values_type, topic_suffix=control_topic_suffix
        )

        # Create builder to accumulate sensor messages
        self._sensor_builder = PartialModelBuilder(self.sensor_values_type)

    def time(self) -> datetime.datetime:
        """Get current time (updated from sensor timestamps)."""
        return self._current_time

    @property
    def sensor_subscribe_topic(self):
        """Topic pattern to subscribe to sensor values."""
        return f"{self.name}/{self._sensor_mapping.subscribe_topic()}"

    @property
    def control_topic_prefix(self):
        """Topic prefix for publishing control commands."""
        return self.name

    async def start(self, client):
        topic = f"{self._topic_prefix}/{self.sensor_subscribe_topic}"
        await client.subscribe(topic, qos=1)
        logger.info(f"Controller of {self.control} subscribed to sensor topic: {topic}")

    async def run(self, client):
        self._running = True
        try:
            # Send initial state before entering control loop
            await self._send_initial_state(client)

            async with TaskGroup() as tg:
                tg.create_task(self._listen_to_sensors(client))
                tg.create_task(sleep(self._interval))
        except Exception as e:
            logger.error(f"Controller run encountered an error: {e}")
            raise
        finally:
            self._running = False

    def _clean_topic(self, topic: Topic) -> str:
        return topic.value.removeprefix(f"{self._topic_prefix}/")

    async def _send_control_values(
        self, client: MqttClient, control_values: ThrsValues
    ):
        """Send control values to MQTT using the control mapping."""
        logging.debug(f"Publishing control values: {control_values}")

        # Split control values into individual topics
        topic_payloads = self._control_mapping.split_to_topics(control_values)

        for topic_suffix, payload in topic_payloads.items():
            topic = f"{self._topic_prefix}/{self.control_topic_prefix}/{topic_suffix}"
            logging.debug(f"Publishing to {topic}: {payload}")
            await client.publish(topic, payload, qos=1)

    async def _send_initial_state(self, client: MqttClient):
        """Send initial parameters and control values to MQTT on startup."""
        logger.info("Publishing initial controller state")

        # Publish parameters
        parameters_topic = f"{self._topic_prefix}/{self.name}/config/parameters"
        parameters_payload = self.control.parameters.model_dump_json(by_alias=True)
        logger.info(f"Publishing parameters to {parameters_topic}")
        await client.publish(parameters_topic, parameters_payload, qos=1, retain=True)

        # Publish initial control values
        initial_control = self.control.initial()
        logger.info(f"Publishing initial control values: {initial_control.values}")
        await self._send_control_values(client, initial_control.values)

    async def _listen_to_sensors(self, client):
        """Listen to sensor value messages, build complete sensor values, run control, publish commands."""
        logger.info("Starting to listen for sensor messages")
        async for message in client.messages:
            topic = self._clean_topic(message.topic)
            logger.debug(f"Received message on topic: {topic}")

            # Remove module prefix to get field topic (e.g., "thrusters/field-name" -> "field-name")
            if not topic.startswith(f"{self.name}/"):
                logger.debug(f"Ignoring topic {topic} - wrong module")
                continue

            field_topic = topic.removeprefix(f"{self.name}/")
            logger.debug(f"Field topic: {field_topic}")

            # Check if this topic is part of our sensor mapping
            if not self._sensor_mapping.has(field_topic):
                logger.debug(f"Ignoring topic {field_topic} - not in sensor mapping")
                continue

            # Validate payload type
            if not isinstance(message.payload, str | bytes):
                logger.warning(f"Invalid payload type: {type(message.payload)}")
                continue

            # Add sensor message to builder
            self._sensor_builder.input(field_topic, message.payload)
            logger.debug(f"Added sensor message to builder for topic: {field_topic}")

            # Try to build complete sensor values
            sensor_values = self._sensor_builder.result()
            if sensor_values is None:
                logger.debug("Incomplete sensor values, waiting for more messages")
                continue

            logger.info(f"Complete sensor values received: {sensor_values}")

            # Update current time from sensor timestamps
            # Find the most recent timestamp from all Stamped fields in sensor values
            timestamps = []
            for field_name in sensor_values.model_fields.keys():
                field_value = getattr(sensor_values, field_name)
                if hasattr(field_value, "__dict__"):
                    # Look for Stamped fields within this component
                    for sub_field_name, sub_field_value in field_value.__dict__.items():
                        if hasattr(sub_field_value, "timestamp"):
                            timestamps.append(sub_field_value.timestamp)

            if timestamps:
                self._current_time = max(timestamps)
                logger.debug(f"Updated controller time to: {self._current_time}")

            # Run control logic
            try:
                control_result = self.control.control(sensor_values)
                logger.info(
                    f"Control executed, mode: {self.control.mode}, values: {control_result.values}"
                )

                # Send control commands
                await self._send_control_values(client, control_result.values)
            except Exception as e:
                logger.error(f"Error running control logic: {e}", exc_info=True)


async def run_controller(settings: Config, controller: Controller):
    async with MqttClient(settings.mqtt_host, settings.mqtt_port) as client:
        await controller.start(client)
        await controller.run(client)


CONTROLLERS = [
    Controller(
        ThrustersControl,
        ThrustersParameters(),
        "thrusters",
        "thrs",
    ),
    Controller(
        PvtControl,
        PvtParameters(),
        "pvt",
        "thrs",
    ),
    Controller(
        PcmControl,
        PcmParameters(),
        "pcm",
        "thrs",
    ),
    Controller(
        ConsumersControl,
        ConsumersParameters(),
        "consumers",
        "thrs",
    ),
]


async def run_all():
    settings = Config()
    async with TaskGroup() as tg:
        for controller in CONTROLLERS:
            tg.create_task(run_controller(settings, controller))
