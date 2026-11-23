"""FastStream MQTT app: a thin shell over the pure `parser.parse` function.

Subscribes to A+T's `atpx/nmea0183/#` on the input broker; for each message,
parses it and republishes the resulting JSON envelope to
`atpx/processed/nmea/<type>/<sender>` on the output broker. Unparseable
sentences are logged and dropped, and so is everything that arrives while
the output broker is down. Parsing behavior lives in and is tested against the
pure `parse` function.
"""

import logging

from faststream.asgi import AsgiFastStream
from faststream.mqtt import MQTTMessage, QoS
from zmqtt import MQTTDisconnectedError

from zero_atpx_nmea.health import live, make_health_asgi
from zero_atpx_nmea.parser import parse
from zero_atpx_nmea.settings import InputMqttSettings, OutputMqttSettings

logger = logging.getLogger(__name__)

INPUT_TOPIC = "atpx/nmea0183/#"
OUTPUT_TOPIC_TEMPLATE = "atpx/processed/nmea/{type}/{sender}"


def build_app(
    input_settings: InputMqttSettings | None = None,
    output_settings: OutputMqttSettings | None = None,
) -> AsgiFastStream:
    """Wire up the input subscriber and output broker, and return the app.

    Two separate `MQTTBroker`s are used (even though locally they point at
    the same `vernemq` instance) because in production `ATPX_MQTT_HOST` is a
    different, unauthenticated broker on A+T's side.
    """
    input_settings = input_settings or InputMqttSettings()
    output_settings = output_settings or OutputMqttSettings()

    input_broker = input_settings.make_broker()
    output_broker = output_settings.make_broker()
    dropped: int = 0

    @input_broker.subscriber(INPUT_TOPIC, description="Raw A+T NMEA 0183 sentences")
    async def handle(raw_sentence: str, message: MQTTMessage) -> None:
        nonlocal dropped
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
        try:
            await output_broker.publish(envelope, out_topic, qos=QoS.AT_LEAST_ONCE)
        except MQTTDisconnectedError as exc:
            # Left to FastStream, every dropped message logs a traceback.
            if not dropped:
                logger.warning(
                    "Publishing to the output broker failed (%s), "
                    "dropping messages until it is back",
                    exc,
                )
            dropped += 1
            return
        if dropped:
            logger.info("Publishing again, dropped %d message(s)", dropped)
            dropped = 0

    # Both brokers start after the HTTP server is up, so /health answers while
    # they connect. FastStream starts and stops them in the order given; the
    # input broker is stopped first by hand, so the output broker outlives any
    # handler that publishes to it.
    async def stop_input_broker() -> None:
        await input_broker.stop()

    return AsgiFastStream(
        output_broker,
        input_broker,
        asgi_routes=[
            ("/health", make_health_asgi(input_broker, output_broker)),
            ("/live", live),
        ],
        on_shutdown=[stop_input_broker],
    )
