from unittest.mock import AsyncMock, MagicMock

import pytest

from tests.conftest import FloatModel
from zero_modbus_bridge.io import AnnotationModbusTopic
from zero_modbus_bridge.publisher import MqttPublisher


@pytest.mark.asyncio
async def test_publisher_registers_and_publishes():
    mock_pub = MagicMock()
    mock_pub.publish = AsyncMock()
    mock_broker = MagicMock()
    mock_broker.publisher.return_value = mock_pub

    topic = AnnotationModbusTopic(topic="test/p", model=FloatModel)
    pub = MqttPublisher(mock_broker, [topic])
    await pub.publish("test/p", FloatModel(value=1))
    mock_pub.publish.assert_called_once_with(FloatModel(value=1))


@pytest.mark.asyncio
async def test_publisher_unknown_topic_noop():
    mock_broker = MagicMock()
    pub = MqttPublisher(mock_broker, [])
    await pub.publish("unknown", FloatModel(value=1))
