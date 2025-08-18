import asyncio
from typing import Any
from unittest.mock import AsyncMock, patch

from pydantic import TypeAdapter
from zero_data.config import MQTTConfig
from zero_data.data_gen.generator import Generator, MarpowerMessage
from zero_data.io_list.types import IOTopic, IOValue
import random
import datetime
from freezegun import freeze_time


async def test_generator():
    mqtt_config = MQTTConfig(host="mocked", port=1885)
    topics = [
        IOTopic("a", [IOValue("field1", "BOOLEAN"), IOValue("field2", "REAL")]),
        IOTopic("b", [IOValue("field1", "BIGINT"), IOValue("field2", "INTEGER")]),
    ]

    mock_client = AsyncMock()
    # Ensure it works with "async with"
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = mock_client

    jsonfyier = TypeAdapter(dict[str, dict[str, Any]])
    now = datetime.datetime.now(datetime.UTC)

    with patch("zero_data.data_gen.generator.Client", return_value=mock_client):
        random.seed(1)

        gen = Generator(1, mqtt_config, topics)
        with freeze_time(now, real_asyncio=True):
            try:
                async with asyncio.timeout(0.1):
                    await gen.run()
            except asyncio.TimeoutError:
                pass

            # Ensure the MQTT client was created once
            mock_client.__aenter__.assert_called_once()
            # Verify the publish calls
            expected_calls = [
                (
                    "a",
                    jsonfyier.dump_json(
                        {
                            "field1": MarpowerMessage(
                                value=True, timestamp=now, is_valid=True, has_value=True
                            ).model_dump(by_alias=True),
                            "field2": MarpowerMessage(
                                value=10.60040562252202,
                                timestamp=now,
                                is_valid=True,
                                has_value=True,
                            ).model_dump(by_alias=True),
                        }
                    ),
                ),
                (
                    "b",
                    jsonfyier.dump_json(
                        {
                            "field1": MarpowerMessage(
                                value=8, timestamp=now, is_valid=True, has_value=True
                            ).model_dump(by_alias=True),
                            "field2": MarpowerMessage(
                                value=5, timestamp=now, is_valid=True, has_value=True
                            ).model_dump(by_alias=True),
                        }
                    ),
                ),
            ]

            actual_calls = [
                (call.args[0], call.args[1])
                for call in mock_client.publish.call_args_list
            ]

            assert actual_calls == expected_calls


async def test_context_manager_async():
    mock = AsyncMock()

    mock.__aenter__.return_value = mock
    mock.__aexit__.return_value = mock

    async with mock as a:
        await a.publish("test", payload="test")

    mock.publish.assert_called_with("test", payload="test")
