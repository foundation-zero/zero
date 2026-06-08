from asyncio import create_task, sleep

import pytest
from aiomqtt import Client

from thrs.cli.simulation_controls import (
    ParametersMessage,
    SimulationControls,
    SimulationInputMessage,
    SimulationStatusMessage,
)
from thrs.control.modules.thrusters import ThrustersParameters
from thrs.input_output.model_builder import PartialModelBuilder
from thrs.input_output.modules.thrusters import (
    ThrustersControlValues,
    ThrustersSimulationInputs,
    ThrustersSimulationOutputs,
)
from thrs.orchestration.config import Config
from thrs.utils.string import dash_to_snake

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
        "thrs",
    )

    await controls.clear_previous()

    await test_client.subscribe("thrs/thrusters/+")
    await status_client.subscribe("thrs/simulation/status")

    run_task = create_task(controls.run("thrusters"))
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
        "thrs",
    )

    await test_client.subscribe("thrs/thrusters/thrusters-temperature-aft-return")

    run_task = create_task(controls.run("thrusters"))
    try:
        await sleep(0.1)  # Wait for controls to listen for play
        await controls_client.publish(
            "thrs/simulation/play", '{ "playback_rate": 1 }', qos=1
        )
        await anext(test_client.messages)
        await anext(test_client.messages)  # Wait for first messages

        await sleep(5.1)
        await controls_client.publish("thrs/simulation/pause", "{}", qos=1)
        assert len(test_client.messages) == 5
        while len(test_client.messages) != 0:
            await anext(test_client.messages)  # Drain the messages

        await controls_client.publish(
            "thrs/simulation/play", '{ "playback_rate": 2 }', qos=1
        )
        await anext(test_client.messages)
        await anext(test_client.messages)  # Wait for first messages
        await sleep(5.1)
        await controls_client.publish("thrs/simulation/pause", "{}", qos=1)
        assert len(test_client.messages) == 10
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
        "thrs",
    )

    await controls.clear_previous()

    await test_client.subscribe("thrs/thrusters/thrusters-pump-1")
    await test_client.subscribe(
        f"thrs/thrusters/thrusters-pump-1/{settings.mqtt_control_topic_suffix}"
    )
    await status_client.subscribe("thrs/simulation/status")

    run_task = create_task(controls.run("thrusters"))
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

        assert (
            msg1.topic.value
            == f"thrs/thrusters/thrusters-pump-1/{settings.mqtt_control_topic_suffix}"
        )
        assert msg2.topic.value == "thrs/thrusters/thrusters-pump-1"

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

        await sleep(0.5)
        assert len(test_client.messages) == 4

    finally:
        run_task.cancel()


@pytest.mark.timeout(10)
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
        "thrs",
    )

    await controls.clear_previous()

    await test_client.subscribe(
        f"thrs/thrusters/+/{settings.mqtt_control_topic_suffix}"
    )
    await status_client.subscribe("thrs/simulation/status")

    run_task = create_task(controls.run("thrusters"))

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
            "thrs/thrusters/controls/set_automation", '{"enabled": true}', qos=1
        )

        await controls_client.publish("thrs/simulation/play", "{}", qos=1)
        _running = await anext(status_client.messages)
        await sleep(5.1)

        assert len(test_client.messages) > 0
        control_builder = PartialModelBuilder(ThrustersControlValues)
        while len(test_client.messages) != 0:
            msg = await anext(test_client.messages)
            if msg.topic.value.endswith(settings.mqtt_control_topic_suffix):
                control_builder.input(
                    dash_to_snake(msg.topic.value.split("/")[-2]), msg.payload
                )
        control_values = control_builder.result()

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
        "thrs",
    )

    await controls.clear_previous()

    await test_client.subscribe("thrs/thrusters/config/parameters")
    await status_client.subscribe("thrs/simulation/status")

    run_task = create_task(controls.run("thrusters"))
    try:
        available = await anext(status_client.messages)
        assert available.topic.value == "thrs/simulation/status"
        assert isinstance(available.payload, str | bytes)
        assert (
            SimulationStatusMessage.model_validate_json(available.payload).status
            == "available"
        )
        parameters = await anext(test_client.messages)
        assert parameters.topic.value == "thrs/thrusters/config/parameters"
        assert isinstance(parameters.payload, str | bytes)
        params_model = ParametersMessage[ThrustersParameters].model_validate_json(
            parameters.payload
        )
        assert params_model == ParametersMessage(
            parameters=ThrustersParameters(), module="thrusters"
        )

        new_parameters = ThrustersParameters(cooling_flow=999)
        await controls_client.publish(
            "thrs/thrusters/controls/set_parameters",
            ParametersMessage(
                parameters=new_parameters, module="thrusters"
            ).model_dump_json(),
            qos=1,
        )

        parameters = await anext(test_client.messages)
        assert parameters.topic.value == "thrs/thrusters/config/parameters"
        assert isinstance(parameters.payload, str | bytes)
        params_model = ParametersMessage[ThrustersParameters].model_validate_json(
            parameters.payload
        )
        assert params_model.parameters == new_parameters
    finally:
        run_task.cancel()


@pytest.mark.timeout(5)
async def test_simulation_controls_set_simulation_inputs(
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
        "thrs",
    )

    await controls.clear_previous()

    await test_client.subscribe("thrs/simulation/inputs")
    await status_client.subscribe("thrs/simulation/status")

    run_task = create_task(controls.run("thrusters"))
    try:
        available = await anext(status_client.messages)
        assert available.topic.value == "thrs/simulation/status"
        assert isinstance(available.payload, str | bytes)
        assert (
            SimulationStatusMessage.model_validate_json(available.payload).status
            == "available"
        )
        simulation_inputs = await anext(test_client.messages)
        assert simulation_inputs.topic.value == "thrs/simulation/inputs"
        assert isinstance(simulation_inputs.payload, str | bytes)
        inputs_model = SimulationInputMessage[
            ThrustersSimulationInputs
        ].model_validate_json(simulation_inputs.payload)
        assert inputs_model.inputs.thrusters_aft.heat_flow.value != 0.0  # type: ignore

        new_inputs = ThrustersSimulationInputs.zero()
        await controls_client.publish(
            "thrs/simulation/set_inputs",
            SimulationInputMessage(inputs=new_inputs).model_dump_json(),
            qos=1,
        )

        simulation_inputs = await anext(test_client.messages)
        assert simulation_inputs.topic.value == "thrs/simulation/inputs"
        assert isinstance(simulation_inputs.payload, str | bytes)
        inputs_model = SimulationInputMessage[
            ThrustersSimulationInputs
        ].model_validate_json(simulation_inputs.payload)
        assert inputs_model.inputs.thrusters_aft.heat_flow.value == 0.0  # type: ignore
    finally:
        run_task.cancel()


@pytest.mark.timeout(10)
async def test_simulation_controls_simulation_output(
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
        "thrs",
    )

    await controls.clear_previous()

    await test_client.subscribe("thrs/simulation/outputs")
    await status_client.subscribe("thrs/simulation/status")

    run_task = create_task(controls.run("thrusters"))
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

        simulation_output = await anext(test_client.messages)
        assert simulation_output.topic.value == "thrs/simulation/outputs"
        assert isinstance(simulation_output.payload, str | bytes)
        module_return_temperature = ThrustersSimulationOutputs.model_validate_json(
            simulation_output.payload
        ).thrusters_module_return.temperature.value
        assert isinstance(module_return_temperature, float)
        assert module_return_temperature > 0

    finally:
        run_task.cancel()
