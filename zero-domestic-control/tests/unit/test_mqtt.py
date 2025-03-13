from zero_domestic_control.messages import Message
from zero_domestic_control.mqtt import send_message


class MessageWithIdInTopic(Message):
    TOPIC = "test/:id"
    id: str
    value: int


class MessageWithoutIdInTopic(Message):
    TOPIC = "test"
    id: str
    value: int


async def test_message_with_id_in_topic(mocker):
    mqtt_mock = mocker.AsyncMock()
    await send_message(mqtt_mock, MessageWithIdInTopic(id="1", value=1))
    mqtt_mock.publish.assert_called_with("test/1", '{"value":1}', qos=1)


async def test_message_without_id_in_topic(mocker):
    mqtt_mock = mocker.AsyncMock()
    await send_message(mqtt_mock, MessageWithoutIdInTopic(id="1", value=1))
    mqtt_mock.publish.assert_called_with("test", '{"id":"1","value":1}', qos=1)
