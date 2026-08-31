from unittest.mock import AsyncMock, MagicMock

import pytest
from faststream.mqtt import MQTTBroker

from tests.conftest import FloatModel
from zero_modbus_bridge.io import AnnotationModbusTopic
from zero_modbus_bridge.publisher import (
    MQTTPublisher,
    MqttPublisher,
    ParametrizedMQTTPublisher,
)


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


class TestParametrizedMQTTPublisher:
    PARAMS = {
        "panel": {"description": "Panel", "enum": ["10P1", "10P2"]},
        "slug": {"description": "Slug", "enum": ["pump-a", "pump-b"]},
    }
    TEMPLATE = "power-tags/{panel}/{slug}"

    def _publisher(self) -> ParametrizedMQTTPublisher:
        broker = MQTTBroker("localhost:1883")
        return ParametrizedMQTTPublisher.create(
            broker, self.TEMPLATE, parameters=self.PARAMS
        )

    def test_placeholder_mismatch_raises(self):
        with pytest.raises(ValueError, match="placeholders"):
            ParametrizedMQTTPublisher.create(
                MQTTBroker("localhost:1883"),
                self.TEMPLATE,
                parameters={"panel": {"enum": ["10P1"]}},
            )

    def test_registered_on_broker(self):
        broker = MQTTBroker("localhost:1883")
        publisher = ParametrizedMQTTPublisher.create(
            broker, self.TEMPLATE, parameters=self.PARAMS
        )
        assert publisher in broker.publishers

    def test_schema_emits_parametrized_channel(self):
        pub = self._publisher()
        schema = pub.specification.get_schema()

        assert list(schema) == [self.TEMPLATE]  # key == address == template
        spec = schema[self.TEMPLATE]
        assert spec.bindings is not None
        assert spec.bindings.mqtt is not None
        assert spec.bindings.mqtt.topic == "power-tags/+/+"
        assert spec.operation.message.title == self.TEMPLATE + ":Message"
        assert pub.specification.include_in_schema

    def test_wildcard_topic(self):
        pub = self._publisher()
        assert pub.topic == self.TEMPLATE

    @pytest.mark.asyncio
    async def test_publish_creates_and_reuses_publisher(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        # Publishing against an un-started broker has no producer; the
        # delegation (not serialization) is what this test exercises.
        stock_publish = AsyncMock()
        monkeypatch.setattr(MQTTPublisher, "publish", stock_publish)

        broker = MQTTBroker("localhost:1883")
        pub = ParametrizedMQTTPublisher.create(
            broker, self.TEMPLATE, parameters=self.PARAMS
        )

        await pub.publish("power-tags/10P1/pump-a", FloatModel(value=1))
        await pub.publish("power-tags/10P1/pump-a", FloatModel(value=2))

        # Template + exactly one concrete (hidden) publisher.
        assert len(broker.publishers) == 2
        concrete = next(p for p in broker.publishers if p is not pub)
        assert isinstance(concrete, MQTTPublisher)
        assert concrete.topic == "power-tags/10P1/pump-a"
        assert not concrete.specification.include_in_schema
        assert stock_publish.await_count == 2

    @pytest.mark.asyncio
    async def test_publish_rejects_unknown_topic(self):
        broker = MQTTBroker("localhost:1883")
        pub = ParametrizedMQTTPublisher.create(
            broker, self.TEMPLATE, parameters=self.PARAMS
        )

        await pub.publish("other/10P1/pump-a", FloatModel(value=1))
        assert len(broker.publishers) == 1  # only the template

    @pytest.mark.asyncio
    async def test_publish_rejects_value_outside_enum(self):
        broker = MQTTBroker("localhost:1883")
        pub = ParametrizedMQTTPublisher.create(
            broker, self.TEMPLATE, parameters=self.PARAMS
        )

        await pub.publish("power-tags/10P9/pump-a", FloatModel(value=1))
        assert len(broker.publishers) == 1  # only the template
