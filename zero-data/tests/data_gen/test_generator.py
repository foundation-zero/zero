import asyncio
import datetime
import random
from typing import Any
from unittest.mock import AsyncMock, call, patch

from freezegun import freeze_time
from pydantic import TypeAdapter

from zero_data.config import MQTTConfig
from zero_data.data_gen.marpower_generator import MarpowerGenerator, MarpowerStruct
from zero_data.io_list.enums import AmcsControlMode, PumpControlMode
from zero_data.io_list.types import IOTopic, IOValue


async def test_marpower_generator():
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

    expected_calls = [
        call(
            "a",
            jsonfyier.dump_json(
                {
                    "field1": MarpowerStruct(
                        value=True, timestamp=now, is_valid=True, has_value=True
                    ).model_dump(mode="json", by_alias=True),
                    "field2": MarpowerStruct(
                        value=10.60040562252202,
                        timestamp=now,
                        is_valid=True,
                        has_value=True,
                    ).model_dump(mode="json", by_alias=True),
                }
            ),
        ),
        call(
            "b",
            jsonfyier.dump_json(
                {
                    "field1": MarpowerStruct(
                        value=8, timestamp=now, is_valid=True, has_value=True
                    ).model_dump(mode="json", by_alias=True),
                    "field2": MarpowerStruct(
                        value=5, timestamp=now, is_valid=True, has_value=True
                    ).model_dump(mode="json", by_alias=True),
                }
            ),
        ),
    ]

    with patch("zero_data.data_gen.generator.Client", return_value=mock_client):
        random.seed(1)

        gen = MarpowerGenerator(1, mqtt_config, topics)
        with freeze_time(now, real_asyncio=True):
            try:
                async with asyncio.timeout(0.1):
                    await gen.run()
            except asyncio.TimeoutError:
                pass

            # Ensure the MQTT client was created once
            mock_client.__aenter__.assert_called_once()
            # Verify the publish calls

            assert mock_client.publish.call_args_list == expected_calls


def test_marpower_generator_picks_named_values_for_enum_fields():
    mode = IOTopic("marpower/500000-thrs/dhw/mode", [IOValue("Mode", "INTEGER")])
    pump = IOTopic(
        "marpower/500000-thrs/dhw/dhw-pump-boiler",
        [IOValue("CC_ControlMode", "INTEGER"), IOValue("Starts", "INTEGER")],
    )
    gen = MarpowerGenerator(1, MQTTConfig(host="mocked", port=1885), [mode, pump])
    random.seed(1)

    messages = [
        gen.generate_message(topic) for _ in range(50) for topic in (mode, pump)
    ]

    modes = {message["Mode"]["Value"] for message in messages if "Mode" in message}
    control_modes = {
        message["CC_ControlMode"]["Value"]
        for message in messages
        if "CC_ControlMode" in message
    }
    starts = {message["Starts"]["Value"] for message in messages if "Starts" in message}
    assert modes <= set(AmcsControlMode)
    assert control_modes <= set(PumpControlMode)
    # Other integers stay random.
    assert not starts <= {1, 3, 4}


async def test_context_manager_async():
    mock = AsyncMock()

    mock.__aenter__.return_value = mock
    mock.__aexit__.return_value = mock

    async with mock as a:
        await a.publish("test", payload="test")

    mock.publish.assert_called_with("test", payload="test")
