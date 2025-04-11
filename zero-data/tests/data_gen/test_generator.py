import asyncio
import json
from unittest.mock import AsyncMock, patch

from io_processing.config import MQTTConfig
from io_processing.data_gen.generator import Generator
from io_processing.io_list.types import IOTopic, IOValue
import random


async def test_generator():
    mqtt_config = MQTTConfig(host="mocked", port=1885)
    topics = [
        IOTopic("a", [IOValue("field1", "BOOLEAN"), IOValue("field2", "REAL")]),
        IOTopic("b", [IOValue("field1", "BIGINT"), IOValue("field2", "INTEGER")]),
    ]
    source = "test"

    mock_client = AsyncMock()
    # Ensure it works with "async with"
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = mock_client

    with patch("io_processing.data_gen.generator.Client", return_value=mock_client):
        random.seed(1)

        gen = Generator(1, mqtt_config, topics, source)

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
                topics[0].topic,
                json.dumps({"field1": True, "field2": 10.60040562252202}),
            ),
            (
                topics[1].topic,
                json.dumps({"field1": 8, "field2": 5}),
            ),
        ]

        actual_calls = [
            (call.args[0], call.args[1]) for call in mock_client.publish.call_args_list
        ]

        assert actual_calls == expected_calls


async def test_context_manager_async():
    mock = AsyncMock()

    mock.__aenter__.return_value = mock
    mock.__aexit__.return_value = mock

    async with mock as a:
        await a.publish("test", payload="test")

    mock.publish.assert_called_with("test", payload="test")
