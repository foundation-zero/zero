from asyncio import Queue, create_task, sleep
import asyncio
from typing import AsyncIterator

from aiomqtt import Client, Message
from pydantic import BaseModel
import pytest

from thrs.cli.simulation_controls import (
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

from thrs.input_output.modules.thrusters import ThrustersControlValues
from thrs.orchestration.config import Config


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

    async def publish(
        self, topic: str, payload: str, qos: int = 0, retain: bool = False
    ):
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
    assert not received[0], (
        "Should not receive on different topic (even if client was interfered)"
    )

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
mqtt_client5 = pytest.fixture(_mqtt_client)


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

    await test_client.publish(
        "thrs/simulation/status", b"", qos=1, retain=True
    )  # Clear previous status
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


@pytest.mark.timeout(30)
async def test_simulation_run_blind_start_stop(
    mqtt_client: Client,
    mqtt_client2: Client,
    mqtt_client3: Client,
    mqtt_client4: Client,
    mqtt_client5: Client,
):
    controls_client = mqtt_client
    control_client = mqtt_client2
    sensors_client = mqtt_client3
    test_client = mqtt_client4
    status_client = mqtt_client5
    controls = SimulationControls(
        controls_client,
        control_client,
        sensors_client,
        "thrs/sensors",
        "thrs/controls",
    )

    await test_client.subscribe("thrs/sensors")
    await test_client.subscribe("thrs/controls")
    await status_client.publish(
        "thrs/simulation/status", b"", qos=1, retain=True
    )  # Clear previous status
    await status_client.subscribe("thrs/simulation/status")

    run_task = create_task(controls.run_blind("THRUSTERS"))
    try:
        available = await anext(status_client.messages)
        assert available.topic.value == "thrs/simulation/status"
        assert isinstance(available.payload, str | bytes)
        assert (
            StatusMessage.model_validate_json(available.payload).status == "available"
        )
        assert len(test_client.messages) == 0

        await controls_client.publish("thrs/simulation/play", "{}", qos=1)
        running = await anext(status_client.messages)
        assert isinstance(running.payload, str | bytes)
        assert StatusMessage.model_validate_json(running.payload).status == "running"
        await sleep(5.1)
        assert len(test_client.messages) > 0
        amount_before_pause = len(test_client.messages)
        await controls_client.publish("thrs/simulation/pause", "{}", qos=1)
        available = await anext(status_client.messages)
        assert isinstance(available.payload, str | bytes)
        assert (
            StatusMessage.model_validate_json(available.payload).status == "available"
        )
        amount_after_pause = len(test_client.messages)
        assert (
            amount_after_pause == amount_before_pause
        )  # simulation could still have been running and need to finish the step or just sent the controls, but hasn't yet received the sensors back

    finally:
        run_task.cancel()


@pytest.mark.timeout(30)
async def test_simulation_run_blind_playback_rate(
    mqtt_client: Client,
    mqtt_client2: Client,
    mqtt_client3: Client,
    mqtt_client4: Client,
):
    controls_client = mqtt_client
    control_client = mqtt_client2
    sensors_client = mqtt_client3
    test_client = mqtt_client4
    controls = SimulationControls(
        controls_client,
        control_client,
        sensors_client,
        "thrs/sensors",
        "thrs/controls",
    )

    await test_client.subscribe("thrs/sensors")
    await test_client.subscribe("thrs/controls")

    run_task = create_task(controls.run_blind("THRUSTERS"))
    try:
        await sleep(0.1)  # Wait for controls to listen for play
        await controls_client.publish(
            "thrs/simulation/play", '{ "playback_rate": 1 }', qos=1
        )
        await anext(test_client.messages)
        await anext(test_client.messages)  # Wait for first messages

        await sleep(5.1)
        await controls_client.publish("thrs/simulation/pause", "{}", qos=1)
        assert len(test_client.messages) == 10
        while len(test_client.messages) != 0:
            await anext(test_client.messages)  # Drain the messages

        await controls_client.publish(
            "thrs/simulation/play", '{ "playback_rate": 2 }', qos=1
        )
        await anext(test_client.messages)
        await anext(test_client.messages)  # Wait for first messages
        await sleep(5.1)
        await controls_client.publish("thrs/simulation/pause", "{}", qos=1)
        assert len(test_client.messages) == 20
    finally:
        run_task.cancel()


@pytest.mark.timeout(5)
async def test_simulation_run_blind_step(
    mqtt_client: Client,
    mqtt_client2: Client,
    mqtt_client3: Client,
    mqtt_client4: Client,
    mqtt_client5: Client,
):
    controls_client = mqtt_client
    control_client = mqtt_client2
    sensors_client = mqtt_client3
    test_client = mqtt_client4
    status_client = mqtt_client5
    controls = SimulationControls(
        controls_client,
        control_client,
        sensors_client,
        "thrs/sensors",
        "thrs/controls",
    )

    await test_client.subscribe("thrs/sensors")
    await test_client.subscribe("thrs/controls")
    await status_client.publish(
        "thrs/simulation/status", b"", qos=1, retain=True
    )  # Clear previous status
    await status_client.subscribe("thrs/simulation/status")

    run_task = create_task(controls.run_blind("THRUSTERS"))
    try:
        available = await anext(status_client.messages)
        assert available.topic.value == "thrs/simulation/status"
        assert isinstance(available.payload, str | bytes)
        assert (
            StatusMessage.model_validate_json(available.payload).status == "available"
        )
        await sleep(0.1)  # Wait for controls to listen for step

        await controls_client.publish("thrs/simulation/step", '{"seconds": 1}', qos=1)

        stepping = await anext(status_client.messages)
        assert stepping.topic.value == "thrs/simulation/status"
        assert isinstance(stepping.payload, str | bytes)
        assert StatusMessage.model_validate_json(stepping.payload).status == "stepping"

        msg1 = await anext(test_client.messages)
        msg2 = await anext(test_client.messages)

        available = await anext(status_client.messages)
        assert available.topic.value == "thrs/simulation/status"
        assert isinstance(available.payload, str | bytes)
        assert (
            StatusMessage.model_validate_json(available.payload).status == "available"
        )

        assert msg1.topic.value == "thrs/controls"
        assert msg2.topic.value == "thrs/sensors"

        await controls_client.publish("thrs/simulation/step", '{"seconds": 2}', qos=1)

        stepping = await anext(status_client.messages)
        assert stepping.topic.value == "thrs/simulation/status"
        assert isinstance(stepping.payload, str | bytes)
        assert StatusMessage.model_validate_json(stepping.payload).status == "stepping"

        available = await anext(status_client.messages)
        assert available.topic.value == "thrs/simulation/status"
        assert isinstance(available.payload, str | bytes)
        assert (
            StatusMessage.model_validate_json(available.payload).status == "available"
        )

        assert len(test_client.messages) == 4

    finally:
        run_task.cancel()


async def test_simulation_controls_blind_automated_control(
    mqtt_client, mqtt_client2, mqtt_client3, mqtt_client4, mqtt_client5
):
    controls_client = mqtt_client
    control_client = mqtt_client2
    sensors_client = mqtt_client3
    test_client = mqtt_client4
    status_client = mqtt_client5
    controls = SimulationControls(
        controls_client,
        control_client,
        sensors_client,
        "thrs/sensors",
        "thrs/controls",
    )

    await test_client.subscribe("thrs/sensors")
    await test_client.subscribe("thrs/controls")
    await status_client.publish(
        "thrs/simulation/status", b"", qos=1, retain=True
    )  # Clear previous status
    await status_client.subscribe("thrs/simulation/status")

    run_task = create_task(controls.run_blind("THRUSTERS"))
    try:
        available = await anext(status_client.messages)
        assert available.topic.value == "thrs/simulation/status"
        assert isinstance(available.payload, str | bytes)
        assert (
            StatusMessage.model_validate_json(available.payload).status == "available"
        )
        assert len(test_client.messages) == 0
        await controls_client.publish(
            "thrs/controls/switch_automation_mode", '{"mode": "automatic"}', qos=1
        )

        await controls_client.publish("thrs/simulation/play", "{}", qos=1)
        _running = await anext(status_client.messages)
        await sleep(5.1)

        assert len(test_client.messages) > 0
        control_values = None
        while len(test_client.messages) != 0:
            msg = await anext(test_client.messages)
            if msg.topic.matches("thrs/controls"):
                control_values = ThrustersControlValues.model_validate_json(msg.payload)

        assert control_values is not None
        assert control_values.thrusters_shutoff_recovery.setpoint.value > 0

    finally:
        run_task.cancel()
