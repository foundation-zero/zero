"""FastStream MQTT app: a thin shell over the pure `parser.parse` function.

Subscribes to A+T's `atpx/nmea0183/#` on the input broker; for each message,
parses it and republishes the resulting JSON envelope to
`atpx/processed/nmea/<type>/<sender>` on the output broker. Unparseable
sentences are logged and dropped. Not unit-tested — all parsing behavior
lives in and is tested against the pure `parse` function.
"""

import logging

from faststream import FastStream
from faststream.mqtt import MQTTMessage, QoS

from zero_atpx_nmea.parser import parse
from zero_atpx_nmea.settings import InputMqttSettings, OutputMqttSettings

logger = logging.getLogger(__name__)

INPUT_TOPIC = "atpx/nmea0183/#"
OUTPUT_TOPIC_TEMPLATE = "atpx/processed/nmea/{type}/{sender}"


def build_app(
    input_settings: InputMqttSettings | None = None,
    output_settings: OutputMqttSettings | None = None,
) -> FastStream:
    """Wire up the input subscriber and output broker, and return the app.

    Two separate `MQTTBroker`s are used (even though locally they point at
    the same `vernemq` instance) because in production `ATPX_MQTT_HOST` is a
    different, unauthenticated broker on A+T's side.
    """
    # Required fields are sourced from the environment by pydantic-settings
    # at runtime; pyright can't see that, hence the ignores below.
    input_settings = input_settings or InputMqttSettings()  # type: ignore[call-arg]
    output_settings = output_settings or OutputMqttSettings()  # type: ignore[call-arg]

    input_broker = input_settings.make_broker()
    output_broker = output_settings.make_broker()

    @input_broker.subscriber(INPUT_TOPIC, description="Raw A+T NMEA 0183 sentences")
    async def handle(raw_sentence: str, message: MQTTMessage) -> None:
        topic = message.raw_message.topic
        envelope = parse(raw_sentence, topic)
        if envelope is None:
            logger.warning(
                f"dropping unparseable NMEA sentence on {topic}: {raw_sentence!r}"
            )
            return

        out_topic = OUTPUT_TOPIC_TEMPLATE.format(
            type=envelope["type"], sender=envelope["sender"]
        )
        await output_broker.publish(envelope, out_topic, qos=QoS.AT_LEAST_ONCE)

    # FastStream manages only input_broker (which owns the subscriber). These
    # hooks start the output broker before it and stop it after it, so the
    # output producer stays connected for as long as a handler might publish —
    # otherwise a message could be handled before output_broker finishes
    # connecting, or after it has disconnected.
    async def start_output_broker() -> None:
        await output_broker.start()

    async def stop_output_broker() -> None:
        await output_broker.stop()

    return FastStream(
        input_broker,
        on_startup=[start_output_broker],
        after_shutdown=[stop_output_broker],
    )
