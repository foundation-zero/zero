from asyncio import Queue, create_task
import asyncio
from typing import AsyncIterator

from aiomqtt import Client, Message
from pydantic import BaseModel
import pytest

from cli.simulation_controls import (
    AllowedModesMessage,
    ConnectMessage,
    MqttSequencer,
    PickModeMessage,
    RunCommandMessage,
    SchemaMessage,
    SetValuesMessage,
    SimulationControls,
    StartCommandMessage,
    StatusMessage,
    update_in_place,
)


from pydantic_partial import create_partial_model

from orchestration.config import Config


class NestedModel(BaseModel):
    b: int
    c: str


class Model[A](BaseModel):
    a: int
    nested: A


class AppliedNestingModel(Model[create_partial_model(NestedModel)]):
    pass


PartialModel = create_partial_model(AppliedNestingModel)


def test_update_in_place_unnested():
    actual_model = AppliedNestingModel(
        a=1,
        nested=NestedModel(b=2, c="test").model_dump(),
    )
    update_in_place(actual_model, PartialModel(a=2).model_dump(exclude_none=True))
    assert actual_model.a == 2


def test_update_in_place_nested():
    actual_model = AppliedNestingModel(
        a=1,
        nested=NestedModel(b=2, c="test").model_dump(),
    )
    update_in_place(
        actual_model, PartialModel(nested={"b": 3}).model_dump(exclude_none=True)
    )
    assert actual_model.nested.b == 3
    assert (
        actual_model.nested.c is None
    )  # We don't need update_in_place to allow partial nesting, model_copy doesn't handle nested update= params correctly, so this is the best behavior


def test_update_in_place_nested_stamped():

    class B(BaseModel):
        b: int

    class Nesting(BaseModel):
        a: B

    class Nested(BaseModel):
        nesting: Nesting

    actual_model = Nested(
        nesting=Nesting(
            a=B(b=1),
        )
    )
    update_in_place(
        actual_model,
        Nested(nesting=Nesting(a=B(b=2))).model_dump(exclude_none=True),
    )
    assert actual_model.nesting.a.b == 2


# From https://github.com/empicano/aiomqtt/blob/main/aiomqtt/client.py#L129
class MessagesIterator:
    """Dynamic view of the client's message queue."""

    def __init__(self, client: "FakeClient") -> None:
        self._client = client

    def __aiter__(self) -> AsyncIterator[Message]:
        return self

    async def __anext__(self) -> Message:
        return await self._client.queue.get()

    def __len__(self) -> int:
        """Return the number of messages in the message queue."""
        return self._client.queue.qsize()  # noqa: SLF001


class FakeClient:
    def __init__(self):
        self.subscriptions = set()
        self.queue = Queue()
        self.messages = MessagesIterator(self)

    async def subscribe(self, topic: str, qos: int = 0):
        self.subscriptions.add(topic)

    async def unsubscribe(self, topic: str):
        self.subscriptions.discard(topic)

    async def publish(self, topic: str, payload: str):
        if topic in self.subscriptions:
            await self.queue.put(
                Message(topic, payload, qos=0, retain=False, mid=5, properties=None)
            )


class AMessage(BaseModel):
    a: str


class BMessage(BaseModel):
    b: str


async def test_mqtt_sequencer():
    fake_client = FakeClient()
    sequencer = MqttSequencer(fake_client)  # type: ignore
    a_message_exp = await sequencer.expect("test/topic", AMessage)
    received = [False]

    async def _listen():
        await a_message_exp
        received[0] = True

    listen_task = create_task(_listen())
    await fake_client.publish("test/topic", BMessage(b="test").model_dump_json())
    await asyncio.sleep(0)  # Wait for the event loop to process the message
    assert not received[0], "Should not receive BMessage as AMessage"

    await fake_client.subscribe("test/wrong")
    await fake_client.publish("test/wrong", AMessage(a="test").model_dump_json())
    await asyncio.sleep(0)  # Wait for the event loop to process the message
    assert not received[
        0
    ], "Should not receive on different topic (even if client was interfered)"

    await fake_client.publish("test/topic", AMessage(a="test").model_dump_json())
    await asyncio.sleep(0)  # Wait for the event loop to process the message
    assert received[0], "Should receive AMessage after publishing on correct topic"
    listen_task.cancel()


settings = Config()  # type: ignore


async def _mqtt_client():
    async with Client(settings.mqtt_host, settings.mqtt_port) as client:
        yield client


mqtt_client = pytest.fixture(_mqtt_client)
mqtt_client2 = pytest.fixture(_mqtt_client)
mqtt_client3 = pytest.fixture(_mqtt_client)
mqtt_client4 = pytest.fixture(_mqtt_client)


@pytest.mark.timeout(10)
async def test_simulation_controls(
    mqtt_client, mqtt_client2, mqtt_client3, mqtt_client4
):
    test_client = mqtt_client4
    controls = SimulationControls(
        mqtt_client,
        mqtt_client2,
        mqtt_client3,
        "sensors",
        "controls",
    )

    sequencer = MqttSequencer(test_client)

    await_available = await sequencer.expect(StatusMessage.TOPIC, StatusMessage)
    run = create_task(controls.run())
    assert (await await_available).status == "available"
    allowed_modes = await sequencer.expect(
        AllowedModesMessage.TOPIC, AllowedModesMessage
    )
    await test_client.publish(ConnectMessage.TOPIC, "{}")
    modes = await allowed_modes
    assert set(modes.modes) == {"THRUSTERS"}

    schema = await sequencer.expect(SchemaMessage.TOPIC, SchemaMessage)
    await test_client.publish(PickModeMessage.TOPIC, '{"mode": "THRUSTERS"}')
    await schema

    ready = await sequencer.expect(StatusMessage.TOPIC, StatusMessage)
    await test_client.publish(SetValuesMessage.TOPIC, "{}")
    assert (await ready).status == "ready_to_start"

    running_ran = await sequencer.expect(StatusMessage.TOPIC, StatusMessage, count=2)
    await test_client.publish(
        StartCommandMessage.TOPIC,
        '{"start_time": "1995-01-17T00:00:00Z", "ticks": 30 }',
    )
    running, ran = await running_ran
    assert running.status == "running"
    assert ran.status == "ran"

    for _ in range(2):
        ready = await sequencer.expect(StatusMessage.TOPIC, StatusMessage)
        await test_client.publish(SetValuesMessage.TOPIC, "{}")
        assert (await ready).status == "ready_to_run"
        running_ran = await sequencer.expect(
            StatusMessage.TOPIC, StatusMessage, count=2
        )
        await test_client.publish(RunCommandMessage.TOPIC, '{ "ticks": 30 }')
        running, ran = await running_ran
        assert running.status == "running"
        assert ran.status == "ran"

    run.cancel()
