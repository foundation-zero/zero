from asyncio import create_task, sleep

from aiomqtt import Client
from pydantic import BaseModel
import pytest

from thrs.cli.simulation_controls import (
    ParametersMessage,
    SimulationStatusMessage,
    SimulationControls,
    update_in_place,
)


from pydantic_partial import create_partial_model

from thrs.control.modules.thrusters import ThrustersParameters
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


settings = Config()  # type: ignore


async def _mqtt_client():
    async with Client(settings.mqtt_host, settings.mqtt_port) as client:
        yield client


mqtt_client = pytest.fixture(_mqtt_client)
mqtt_client2 = pytest.fixture(_mqtt_client)
mqtt_client3 = pytest.fixture(_mqtt_client)
mqtt_client4 = pytest.fixture(_mqtt_client)
mqtt_client5 = pytest.fixture(_mqtt_client)


@pytest.mark.timeout(30)
async def test_simulation_run_start_stop(
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

    await controls.clear_previous()

    await test_client.subscribe("thrs/sensors")
    await test_client.subscribe("thrs/controls")
    await status_client.subscribe("thrs/simulation/status")

    run_task = create_task(controls.run("THRUSTERS"))
    try:
        available = await anext(status_client.messages)
        assert available.topic.value == "thrs/simulation/status"
        assert isinstance(available.payload, str | bytes)
        assert (
            SimulationStatusMessage.model_validate_json(available.payload).status
            == "available"
        )
        assert len(test_client.messages) == 0

        await controls_client.publish("thrs/simulation/play", "{}", qos=1)
        running = await anext(status_client.messages)
        assert isinstance(running.payload, str | bytes)
        assert (
            SimulationStatusMessage.model_validate_json(running.payload).status
            == "running"
        )
        await sleep(5.1)
        assert len(test_client.messages) > 0
        amount_before_pause = len(test_client.messages)
        await controls_client.publish("thrs/simulation/pause", "{}", qos=1)
        available = await anext(status_client.messages)
        assert isinstance(available.payload, str | bytes)
        assert (
            SimulationStatusMessage.model_validate_json(available.payload).status
            == "available"
        )
        amount_after_pause = len(test_client.messages)
        assert (
            amount_after_pause == amount_before_pause
        )  # simulation could still have been running and need to finish the step or just sent the controls, but hasn't yet received the sensors back

    finally:
        run_task.cancel()


@pytest.mark.timeout(30)
async def test_simulation_run_playback_rate(
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

    run_task = create_task(controls.run("THRUSTERS"))
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
async def test_simulation_run_step(
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

    await controls.clear_previous()

    await test_client.subscribe("thrs/sensors")
    await test_client.subscribe("thrs/controls")
    await status_client.subscribe("thrs/simulation/status")

    run_task = create_task(controls.run("THRUSTERS"))
    try:
        available = await anext(status_client.messages)
        assert available.topic.value == "thrs/simulation/status"
        assert isinstance(available.payload, str | bytes)
        assert (
            SimulationStatusMessage.model_validate_json(available.payload).status
            == "available"
        )
        await sleep(0.1)  # Wait for controls to listen for step

        await controls_client.publish("thrs/simulation/step", '{"seconds": 1}', qos=1)

        stepping = await anext(status_client.messages)
        assert stepping.topic.value == "thrs/simulation/status"
        assert isinstance(stepping.payload, str | bytes)
        assert (
            SimulationStatusMessage.model_validate_json(stepping.payload).status
            == "stepping"
        )

        msg1 = await anext(test_client.messages)
        msg2 = await anext(test_client.messages)

        available = await anext(status_client.messages)
        assert available.topic.value == "thrs/simulation/status"
        assert isinstance(available.payload, str | bytes)
        assert (
            SimulationStatusMessage.model_validate_json(available.payload).status
            == "available"
        )

        assert msg1.topic.value == "thrs/controls"
        assert msg2.topic.value == "thrs/sensors"

        await controls_client.publish("thrs/simulation/step", '{"seconds": 2}', qos=1)

        stepping = await anext(status_client.messages)
        assert stepping.topic.value == "thrs/simulation/status"
        assert isinstance(stepping.payload, str | bytes)
        assert (
            SimulationStatusMessage.model_validate_json(stepping.payload).status
            == "stepping"
        )

        available = await anext(status_client.messages)
        assert available.topic.value == "thrs/simulation/status"
        assert isinstance(available.payload, str | bytes)
        assert (
            SimulationStatusMessage.model_validate_json(available.payload).status
            == "available"
        )

        assert len(test_client.messages) == 4

    finally:
        run_task.cancel()


async def test_simulation_controls_automated_control(
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

    await controls.clear_previous()

    await test_client.subscribe("thrs/sensors")
    await test_client.subscribe("thrs/controls")
    await status_client.subscribe("thrs/simulation/status")

    run_task = create_task(controls.run("THRUSTERS"))

    try:
        available = await anext(status_client.messages)
        assert available.topic.value == "thrs/simulation/status"
        assert isinstance(available.payload, str | bytes)
        assert (
            SimulationStatusMessage.model_validate_json(available.payload).status
            == "available"
        )
        assert len(test_client.messages) == 0
        await controls_client.publish(
            "thrs/controls/set_automation", '{"enabled": true}', qos=1
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


@pytest.mark.timeout(5)
async def test_simulation_controls_set_parameters(
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

    await controls.clear_previous()

    await test_client.subscribe("thrs/parameters")
    await status_client.subscribe("thrs/simulation/status")

    run_task = create_task(controls.run("THRUSTERS"))
    try:
        available = await anext(status_client.messages)
        assert available.topic.value == "thrs/simulation/status"
        assert isinstance(available.payload, str | bytes)
        assert (
            SimulationStatusMessage.model_validate_json(available.payload).status
            == "available"
        )
        parameters = await anext(test_client.messages)
        assert parameters.topic.value == "thrs/parameters"
        assert isinstance(parameters.payload, str | bytes)
        params_model = ParametersMessage.model_validate_json(parameters.payload)
        assert params_model == ParametersMessage(parameters=ThrustersParameters())

        new_parameters = ThrustersParameters(cooling_flow=999)
        await controls_client.publish(
            "thrs/controls/set_parameters",
            ParametersMessage(parameters=new_parameters).model_dump_json(),
            qos=1,
        )

        parameters = await anext(test_client.messages)
        assert parameters.topic.value == "thrs/parameters"
        assert isinstance(parameters.payload, str | bytes)
        params_model = ParametersMessage.model_validate_json(parameters.payload)
        assert params_model.parameters == new_parameters
    finally:
        run_task.cancel()
