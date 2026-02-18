"""
Mock data generator for sail system MQTT topics.

Sail system PLC messages are flat JSON with PLC variable names as keys and
raw integer/boolean values (no MarpowerMessage wrapper).
"""

import asyncio
import json
import random
from typing import Any

from aiomqtt import Client

from zero_data.config import MQTTConfig
from zero_data.io_list.types import IOTopic
import logging

logger = logging.getLogger(__name__)


class SailSystemGenerator:
    def __init__(
        self,
        interval: int | float,
        mqtt_config: MQTTConfig,
        topics: list[IOTopic],
    ):
        self.interval = interval
        self.mqtt_config = mqtt_config
        self.topics = topics

    async def _send_messages(self, client: Client):
        logger.info(f"Sending sail system values to {len(self.topics)} topics")
        for topic in self.topics:
            payload = json.dumps(self._message(topic))
            await client.publish(topic.topic, payload)

    async def run(self):
        async with Client(self.mqtt_config.host, port=self.mqtt_config.port) as client:
            while True:
                sleep_task = asyncio.sleep(self.interval)
                send_task = self._send_messages(client)
                await asyncio.gather(send_task, sleep_task)

    def _message(self, topic: IOTopic) -> dict[str, Any]:
        """Generate a flat JSON message with PLC variable names as keys."""
        return {
            field.name: self._random_value(field.name, field.data_type)
            for field in topic.fields
        }

    @staticmethod
    def _parse_struct_fields(struct_type: str) -> list[tuple[str, str]]:
        """Parse STRUCT<name type, ...> into [(name, type)] pairs, handling nesting."""
        inner = struct_type[len("STRUCT<") : -1]
        tokens: list[str] = []
        depth = 0
        buf: list[str] = []
        for ch in inner:
            if ch == "<":
                depth += 1
                buf.append(ch)
            elif ch == ">":
                depth -= 1
                buf.append(ch)
            elif ch == "," and depth == 0:
                tokens.append("".join(buf).strip())
                buf = []
            else:
                buf.append(ch)
        if buf:
            tokens.append("".join(buf).strip())
        return [(t.split(" ", 1)[0], t.split(" ", 1)[1]) for t in tokens if " " in t]

    @staticmethod
    def _random_value(name: str, data_type: str) -> Any:
        if data_type.startswith("STRUCT<"):
            return {
                fname: SailSystemGenerator._random_value(fname, ftype)
                for fname, ftype in SailSystemGenerator._parse_struct_fields(data_type)
            }
        match data_type:
            case "BOOLEAN":
                return random.choice([True, False])
            case "INTEGER":
                if "position" in name.lower():
                    return random.randint(0, 1000)
                return random.randint(0, 2000)
            case "REAL":
                return random.normalvariate(mu=10, sigma=1.0)
        raise KeyError(f"Unknown type: {data_type}")
