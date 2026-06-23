import asyncio
import logging

from aiomqtt import Client

from thrs.input_output.base import CombinedValues, ThrsValues
from thrs.orchestration.connectors.base import CommConnector
from thrs.orchestration.connectors.mqtt.mapping import ModuleMqttMapping, MqttMapping
from thrs.orchestration.module import ModuleClassMap

logger = logging.getLogger(__name__)


class MqttSubscription:
    subscribed_on_host: bool = False
    values_typings: ModuleClassMap
    topic_prefix: str

    def __init__(self, values_typings: ModuleClassMap, topic_prefix: str):
        self.values_typings = values_typings
        self.topic_prefix = topic_prefix
        self.values_mqtt_mappings = ModuleMqttMapping(
            self.values_typings, self.topic_prefix
        )


class MqttConnector(CommConnector[CombinedValues, CombinedValues]):
    def __init__(
        self,
        mqtt_host: str,
        mqtt_port: int = 1883,
    ):
        self._mqtt_client = Client(hostname=mqtt_host, port=mqtt_port)
        self._running = False
        self._subscriptions: dict[ThrsValues, MqttSubscription] = {}
        self._control_topic_suffix_str = ""
        self.connection_open_event = asyncio.Event()

    async def _listen_to_sensors(self):
        """Listen to incoming MQTT messages and update corresponding values."""
        logger.info("MQTT connector listening to incoming messages")
        try:
            async with self._mqtt_client as client:
                async for message in client.messages:
                    matched_subscriptions: list[MqttSubscription] = [
                        sub
                        for values, sub in self._subscriptions.items()
                        if any(
                            message.topic.matches(topic)
                            for topic in sub.values_mqtt_mappings.subscribe_topics()
                        )
                    ]

                    if not matched_subscriptions:
                        continue

                    if not isinstance(message.payload, (str, bytes)):
                        raise ValueError(
                            f"Expected string or bytes, got {type(message.payload)}"
                        )

                    for match in matched_subscriptions:
                        match.values_mqtt_mappings.handle_message(
                            message.topic.value, message.payload
                        )

        except Exception as e:
            logger.error("Error inside MQTT client listening context loop: %s", e)

    async def _publish_by_mapping[T](
        self, client: Client, mapping: MqttMapping[T], value: T
    ):
        """Publish the given value to the MQTT broker using the given mapping."""
        payloads = mapping.split_to_topics(value)
        for topic, payload in payloads.items():
            topic = f"{topic}{self._control_topic_suffix_str}"
            await client.publish(topic, payload, qos=1)

    async def _subscribe_on_host(self, qos: int = 0):
        """Subscribes to all unsubscribed topics for all subscriptions on the host."""
        for _, sub in self._subscriptions.items():
            if not sub.subscribed_on_host:
                for topic in sub.values_mqtt_mappings.subscribe_topics():
                    await self._mqtt_client.subscribe(topic, qos=qos)

                sub.subscribed_on_host = True

    def _get_subscription_by_values(self, values: ThrsValues) -> MqttSubscription:
        """Return the subscription for the given values, or raise an exception."""
        if values not in self._subscriptions.keys():
            raise Exception(
                f"{self.send_values.__qualname__} unable to find subscription for values. "
                f"Please {self.subscribe.__qualname__}() values before reading or sending them."
            )

        return self._subscriptions[values]

    def _guard_running(self):
        """Guard that the connector is running."""
        if not self._running:
            raise Exception(
                f"MQTT connector not running, {self.run.__qualname__}() should be called in a thread, i.e. using create_task()"
            )

    async def run(self):
        """Subscribes to all topics and listens to incoming messages, until stopped."""
        self._running = True
        logger.info("MQTT connector started")
        try:
            await self._subscribe_on_host()
            logger.info(
                "MQTT connector subscribed to topics, starting to listen to incoming messages"
            )
            self.connection_open_event.set()
            await self._listen_to_sensors()
        finally:
            logger.info("MQTT connector stopped")
            self._running = False

    def read_values(self, values: ThrsValues) -> CombinedValues | None:
        """Return up-to-date values for the given values."""
        logger.debug("Reading values")
        self._guard_running()
        sub: MqttSubscription = self._get_subscription_by_values(values)
        return sub.values_mqtt_mappings.get_current_values()

    async def send_values(self, values: ThrsValues):
        """Publish the given values to the MQTT broker."""
        logging.debug("Publishing values")
        self._guard_running()
        sub: MqttSubscription = self._get_subscription_by_values(values)
        await self._publish_by_mapping(
            self._mqtt_client,
            sub.values_mqtt_mappings,
            values,
        )

    async def subscribe(self, values: ThrsValues, topic_prefix: str, qos: int = 0):
        """Subscribe to the given values."""
        if values in self._subscriptions.keys():
            return

        # Ensure you pass your real ModuleClassMap instance instead of None here if available.
        self._subscriptions[values] = MqttSubscription(
            values_typings={"": values},
            # values_typings=getattr(values, "values_typings", None),
            topic_prefix=topic_prefix,
        )

        # Only subscribe dynamically on host if the engine is already running
        if self._running:
            await self._subscribe_on_host(qos)
