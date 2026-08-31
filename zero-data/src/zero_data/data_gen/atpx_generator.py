"""
Mock data generator for ATPX (A+T) MQTT traffic.

Unlike Marpower/SailSystem, ATPX has no "one topic, many fields" JSON model:
vector's `atpx_1_parse.vrl` consumes one MQTT message per (field, source) on
topic `atpx/<field-id>/<source>`, with a bare numeric string payload. Every
message lands as one row in the `atpx_raw` table (a pivot view produces the
wide shape later), so this generator simply publishes one value per classified
field for each reporting source every cycle — no grouping or merge windows.
"""

import logging
import random

from aiomqtt import Client

from zero_data.config import MQTTConfig
from zero_data.data_gen.generator import BaseGenerator

logger = logging.getLogger(__name__)

_ATPROCESSOR_SENDER = 15  # ATProcessor sender id
_SOURCES = [
    (_ATPROCESSOR_SENDER << 8) | instance for instance in (0, 1)
]  # [3840, 3841]


class AtpxGenerator(BaseGenerator):
    def __init__(
        self,
        interval: int | float,
        mqtt_config: MQTTConfig,
        field_ids: list[int],
        topic_prefix: str = "atpx",
    ):
        super().__init__(interval, mqtt_config)
        self._field_ids = field_ids
        self._topic_prefix = topic_prefix

    def serialize_message(self, message) -> str:
        return str(message)

    def _generate_value(self) -> float:
        return round(random.uniform(0.0, 100.0), 2)

    async def send_messages(self, client: Client):
        """Publish one value per field, for every source."""
        logger.info(f"Sending ATPX values for {len(self._field_ids)} fields")
        for field_id in self._field_ids:
            for source in _SOURCES:
                payload = self.serialize_message(self._generate_value())
                topic = f"{self._topic_prefix}/{field_id}/{source}"
                await client.publish(topic, payload)
