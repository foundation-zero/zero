import asyncio
from asyncio import create_task, sleep
from contextlib import suppress
from typing import cast

import pytest
from aiomqtt import Client

from thrs.control.modules.thrusters import ThrustersParameters
from thrs.input_output.model_builder import PartialModelBuilder
from thrs.input_output.modules.thrusters import (
    ThrustersControlValues,
    ThrustersSimulationInputs,
    ThrustersSimulationOutputs,
)
from thrs.orchestration.comms import DirectivesChannels, MqttConnector
from thrs.orchestration.config import Config
from thrs.orchestration.setup import setup_control, setup_simulation
from thrs.runtime.descriptions.simulation import lookup_mode
from thrs.runtime.directives import DirectiveHandling
from thrs.runtime.messages import SimulationStatusMessage
from thrs.runtime.runners.lockstep import LockstepRunner
from thrs.runtime.runtime import Runtime

pytestmark = pytest.mark.mqtt


async def _mqtt_client(settings: Config):
    async with Client(settings.mqtt_host, settings.mqtt_port) as client:
        yield client


mqtt_client = pytest.fixture(_mqtt_client)
mqtt_client2 = pytest.fixture(_mqtt_client)
mqtt_client3 = pytest.fixture(_mqtt_client)
mqtt_client4 = pytest.fixture(_mqtt_client)


async def test_simulation_run_start_stop(
    mqtt_client: Client,
    mqtt_client2: Client,
    mqtt_client3: Client,
    mqtt_client4: Client,
    settings: Config,
):
    # Verifies the simulation can transition from available to running and back to available.
    status_topic = f"{settings.mqtt_simulator_topic_prefix}/status"

    controls_client = mqtt_client
    runtime_client = mqtt_client2
    test_client = mqtt_client3
    status_client = mqtt_client4

    mode = lookup_mode("thrusters")
    connector = MqttConnector(runtime_client)
    simulation, simulation_channels = setup_simulation(connector, settings, mode)
    control, control_channels, alarms = setup_control(
        connector, settings, mode, simulation.time
    )
    runner = LockstepRunner(
        control=control,
        control_channels=control_channels,
        alarms=alarms,
        simulation=simulation,
        simulation_channels=simulation_channels,
    )
    runtime = Runtime(
        runner=runner,
        connector=connector,
        tick_duration=simulation.tick_duration,
        directive_handling=DirectiveHandling(
            DirectivesChannels(connector, settings),
            mode,
            simulation.time,
        ),
    )

    await runtime.clear_previous()
    await test_client.subscribe(f"{settings.mqtt_devices_topic_prefix}/thrusters/#")
    await status_client.subscribe(status_topic)

    run_task = create_task(runtime.start())
    try:
        available = await anext(status_client.messages)
        assert available.topic.value == status_topic
        assert isinstance(available.payload, str | bytes)
        assert (
            SimulationStatusMessage.model_validate_json(available.payload).status
            == "available"
        )

        await controls_client.publish(
            f"{settings.mqtt_simulator_topic_prefix}/play",
            "{}",
            qos=1,
        )
        running = await anext(status_client.messages)
        assert isinstance(running.payload, str | bytes)
        assert (
            SimulationStatusMessage.model_validate_json(running.payload).status
            == "running"
        )

        await sleep(5.1)
        amount_before_pause = len(test_client.messages)
        assert amount_before_pause > 0

        await controls_client.publish(
            f"{settings.mqtt_simulator_topic_prefix}/pause",
            "{}",
            qos=1,
        )
        paused = None
        for _ in range(3):
            status_message = await anext(status_client.messages)
            if not isinstance(status_message.payload, str | bytes):
                continue
            if not status_message.payload:
                continue
            with suppress(Exception):
                if (
                    SimulationStatusMessage.model_validate_json(
                        status_message.payload
                    ).status
                    == "available"
                ):
                    paused = status_message
                    break

        assert paused is not None
        amount_after_pause = len(test_client.messages)
        assert (
            amount_after_pause >= amount_before_pause
        )  # simulation may still finish the current step before pause fully settles
        assert (
            amount_after_pause - amount_before_pause <= 20
        )  # bounded extra messages from at most one in-flight step
    finally:
        run_task.cancel()
        with suppress(asyncio.CancelledError):
            await run_task


async def test_simulation_run_playback_rate(
    mqtt_client: Client,
    mqtt_client2: Client,
    mqtt_client3: Client,
    mqtt_client4: Client,
    settings: Config,
):
    # Verifies a higher playback rate produces more simulation output messages in equal wall time.
    status_topic = f"{settings.mqtt_simulator_topic_prefix}/status"
    outputs_topic = f"{settings.mqtt_simulator_topic_prefix}/simulation-outputs"

    controls_client = mqtt_client
    runtime_client = mqtt_client2
    test_client = mqtt_client3
    status_client = mqtt_client4

    mode = lookup_mode("thrusters")
    connector = MqttConnector(runtime_client)
    simulation, simulation_channels = setup_simulation(connector, settings, mode)
    control, control_channels, alarms = setup_control(
        connector, settings, mode, simulation.time
    )
    runner = LockstepRunner(
        control=control,
        control_channels=control_channels,
        alarms=alarms,
        simulation=simulation,
        simulation_channels=simulation_channels,
    )
    runtime = Runtime(
        runner=runner,
        connector=connector,
        tick_duration=simulation.tick_duration,
        directive_handling=DirectiveHandling(
            DirectivesChannels(connector, settings),
            mode,
            simulation.time,
        ),
    )

    await runtime.clear_previous()
    await status_client.subscribe(status_topic)
    await test_client.subscribe(outputs_topic)

    run_task = create_task(runtime.start())
    try:
        available = await anext(status_client.messages)
        assert isinstance(available.payload, str | bytes)
        assert (
            SimulationStatusMessage.model_validate_json(available.payload).status
            == "available"
        )

        await controls_client.publish(
            f"{settings.mqtt_simulator_topic_prefix}/play",
            '{"playback_rate": 1}',
            qos=1,
        )
        running = await anext(status_client.messages)
        assert isinstance(running.payload, str | bytes)
        assert (
            SimulationStatusMessage.model_validate_json(running.payload).status
            == "running"
        )

        await sleep(2.6)
        await controls_client.publish(
            f"{settings.mqtt_simulator_topic_prefix}/pause",
            "{}",
            qos=1,
        )
        available = await anext(status_client.messages)
        assert isinstance(available.payload, str | bytes)
        assert (
            SimulationStatusMessage.model_validate_json(available.payload).status
            == "available"
        )

        rate_1_count = 0
        while len(test_client.messages) != 0:
            msg = await anext(test_client.messages)
            if msg.topic.value == outputs_topic:
                rate_1_count += 1

        await controls_client.publish(
            f"{settings.mqtt_simulator_topic_prefix}/play",
            '{"playback_rate": 2}',
            qos=1,
        )
        running = None
        for _ in range(2):
            status_message = await anext(status_client.messages)
            assert isinstance(status_message.payload, str | bytes)
            if (
                SimulationStatusMessage.model_validate_json(
                    status_message.payload
                ).status
                == "running"
            ):
                running = status_message
                break

        assert running is not None
        await sleep(2.6)
        await controls_client.publish(
            f"{settings.mqtt_simulator_topic_prefix}/pause",
            "{}",
            qos=1,
        )
        available = await anext(status_client.messages)
        assert isinstance(available.payload, str | bytes)
        assert (
            SimulationStatusMessage.model_validate_json(available.payload).status
            == "available"
        )

        rate_2_count = 0
        while len(test_client.messages) != 0:
            msg = await anext(test_client.messages)
            if msg.topic.value == outputs_topic:
                rate_2_count += 1

        assert rate_1_count > 0
        assert rate_2_count > rate_1_count
    finally:
        run_task.cancel()
        with suppress(asyncio.CancelledError):
            await run_task


async def test_simulation_run_step(
    mqtt_client: Client,
    mqtt_client2: Client,
    mqtt_client3: Client,
    mqtt_client4: Client,
    settings: Config,
):
    # Verifies step directives progress the simulation and publish outputs for each requested duration.
    status_topic = f"{settings.mqtt_simulator_topic_prefix}/status"
    outputs_topic = f"{settings.mqtt_simulator_topic_prefix}/simulation-outputs"

    controls_client = mqtt_client
    runtime_client = mqtt_client2
    test_client = mqtt_client3
    status_client = mqtt_client4

    mode = lookup_mode("thrusters")
    connector = MqttConnector(runtime_client)
    simulation, simulation_channels = setup_simulation(connector, settings, mode)
    control, control_channels, alarms = setup_control(
        connector, settings, mode, simulation.time
    )
    runner = LockstepRunner(
        control=control,
        control_channels=control_channels,
        alarms=alarms,
        simulation=simulation,
        simulation_channels=simulation_channels,
    )
    runtime = Runtime(
        runner=runner,
        connector=connector,
        tick_duration=simulation.tick_duration,
        directive_handling=DirectiveHandling(
            DirectivesChannels(connector, settings),
            mode,
            simulation.time,
        ),
    )

    await runtime.clear_previous()
    await status_client.subscribe(status_topic)
    await test_client.subscribe(outputs_topic)

    run_task = create_task(runtime.start())
    try:
        available = await anext(status_client.messages)
        assert isinstance(available.payload, str | bytes)
        assert (
            SimulationStatusMessage.model_validate_json(available.payload).status
            == "available"
        )

        await controls_client.publish(
            f"{settings.mqtt_simulator_topic_prefix}/step",
            '{"seconds": 1}',
            qos=1,
        )
        stepping = await anext(status_client.messages)
        assert isinstance(stepping.payload, str | bytes)
        assert (
            SimulationStatusMessage.model_validate_json(stepping.payload).status
            == "stepping"
        )

        available = await anext(status_client.messages)
        assert isinstance(available.payload, str | bytes)
        assert (
            SimulationStatusMessage.model_validate_json(available.payload).status
            == "available"
        )

        await sleep(0.2)
        step_1_outputs = 0
        while len(test_client.messages) != 0:
            msg = await anext(test_client.messages)
            if msg.topic.value == outputs_topic:
                step_1_outputs += 1

        await controls_client.publish(
            f"{settings.mqtt_simulator_topic_prefix}/step",
            '{"seconds": 2}',
            qos=1,
        )
        stepping = await anext(status_client.messages)
        assert isinstance(stepping.payload, str | bytes)
        assert (
            SimulationStatusMessage.model_validate_json(stepping.payload).status
            == "stepping"
        )

        available = await anext(status_client.messages)
        assert isinstance(available.payload, str | bytes)
        assert (
            SimulationStatusMessage.model_validate_json(available.payload).status
            == "available"
        )

        await sleep(0.2)
        step_2_outputs = 0
        while len(test_client.messages) != 0:
            msg = await anext(test_client.messages)
            if msg.topic.value == outputs_topic:
                step_2_outputs += 1

        assert step_1_outputs >= 1
        assert step_2_outputs >= step_1_outputs
    finally:
        run_task.cancel()
        with suppress(asyncio.CancelledError):
            await run_task


async def test_simulation_controls_automated_control(
    mqtt_client: Client,
    mqtt_client2: Client,
    mqtt_client3: Client,
    mqtt_client4: Client,
    settings: Config,
):
    # Verifies switching to automatic mode results in non-default automatic control outputs.
    status_topic = f"{settings.mqtt_simulator_topic_prefix}/status"
    set_automation_topic = (
        f"{settings.mqtt_controller_topic_prefix}/thrusters/automation-mode/"
        f"{settings.mqtt_controller_topic_suffix}"
    )

    controls_client = mqtt_client
    runtime_client = mqtt_client2
    test_client = mqtt_client3
    status_client = mqtt_client4

    mode = lookup_mode("thrusters")
    connector = MqttConnector(runtime_client)
    simulation, simulation_channels = setup_simulation(connector, settings, mode)
    control, control_channels, alarms = setup_control(
        connector, settings, mode, simulation.time
    )
    runner = LockstepRunner(
        control=control,
        control_channels=control_channels,
        alarms=alarms,
        simulation=simulation,
        simulation_channels=simulation_channels,
    )
    runtime = Runtime(
        runner=runner,
        connector=connector,
        tick_duration=simulation.tick_duration,
        directive_handling=DirectiveHandling(
            DirectivesChannels(connector, settings),
            mode,
            simulation.time,
        ),
    )

    await runtime.clear_previous()
    await test_client.subscribe(
        f"{settings.mqtt_devices_topic_prefix}/thrusters/+/{settings.mqtt_control_topic_suffix}"
    )
    await status_client.subscribe(status_topic)

    run_task = create_task(runtime.start())
    try:
        available = await anext(status_client.messages)
        assert available.topic.value == status_topic
        assert isinstance(available.payload, str | bytes)
        assert (
            SimulationStatusMessage.model_validate_json(available.payload).status
            == "available"
        )
        assert len(test_client.messages) == 0

        await controls_client.publish(
            set_automation_topic,
            '{"mode":"automatic"}',
            qos=1,
        )
        await controls_client.publish(
            f"{settings.mqtt_simulator_topic_prefix}/play",
            "{}",
            qos=1,
        )

        running = await anext(status_client.messages)
        assert isinstance(running.payload, str | bytes)
        assert (
            SimulationStatusMessage.model_validate_json(running.payload).status
            == "running"
        )

        await sleep(5.1)
        assert len(test_client.messages) > 0

        await controls_client.publish(
            f"{settings.mqtt_simulator_topic_prefix}/pause",
            "{}",
            qos=1,
        )
        paused = None
        for _ in range(3):
            status_message = await anext(status_client.messages)
            if not isinstance(status_message.payload, str | bytes):
                continue
            if not status_message.payload:
                continue
            with suppress(Exception):
                if (
                    SimulationStatusMessage.model_validate_json(
                        status_message.payload
                    ).status
                    == "available"
                ):
                    paused = status_message
                    break

        assert paused is not None

        control_builder = PartialModelBuilder(ThrustersControlValues)
        while len(test_client.messages) != 0:
            msg = await anext(test_client.messages)
            if not msg.topic.value.endswith(settings.mqtt_control_topic_suffix):
                continue
            field_name = msg.topic.value.split("/")[-2].replace("-", "_")
            if field_name in ThrustersControlValues.model_fields:
                payload = msg.payload
                if isinstance(payload, bytearray):
                    payload = bytes(payload)
                assert isinstance(payload, str | bytes)
                control_builder.input(field_name, payload)

        control_values = control_builder.result()
        assert control_values is not None
        assert control_values.thrusters_switch_recovery.setpoint.value > 0
    finally:
        run_task.cancel()
        with suppress(asyncio.CancelledError):
            await run_task


async def test_simulation_controls_set_parameters(
    mqtt_client: Client,
    mqtt_client2: Client,
    mqtt_client3: Client,
    mqtt_client4: Client,
    settings: Config,
):
    # Verifies runtime applies updated controller parameters sent over MQTT.
    status_topic = f"{settings.mqtt_simulator_topic_prefix}/status"
    parameters_topic = f"{settings.mqtt_controller_topic_prefix}/thrusters/parameters"
    set_parameters_topic = (
        f"{settings.mqtt_controller_topic_prefix}/thrusters/parameters/"
        f"{settings.mqtt_controller_topic_suffix}"
    )

    controls_client = mqtt_client
    runtime_client = mqtt_client2
    test_client = mqtt_client3
    status_client = mqtt_client4

    mode = lookup_mode("thrusters")
    connector = MqttConnector(runtime_client)
    simulation, simulation_channels = setup_simulation(connector, settings, mode)
    control, control_channels, alarms = setup_control(
        connector, settings, mode, simulation.time
    )
    runner = LockstepRunner(
        control=control,
        control_channels=control_channels,
        alarms=alarms,
        simulation=simulation,
        simulation_channels=simulation_channels,
    )
    runtime = Runtime(
        runner=runner,
        connector=connector,
        tick_duration=simulation.tick_duration,
        directive_handling=DirectiveHandling(
            DirectivesChannels(connector, settings),
            mode,
            simulation.time,
        ),
    )

    await runtime.clear_previous()
    await status_client.subscribe(status_topic)
    await test_client.subscribe(parameters_topic)

    run_task = create_task(runtime.start())
    try:
        available = await anext(status_client.messages)
        assert isinstance(available.payload, str | bytes)
        assert (
            SimulationStatusMessage.model_validate_json(available.payload).status
            == "available"
        )

        await controls_client.publish(
            f"{settings.mqtt_simulator_topic_prefix}/step",
            '{"seconds": 1}',
            qos=1,
        )
        parameters = await anext(test_client.messages)
        assert parameters.topic.value == parameters_topic
        assert isinstance(parameters.payload, str | bytes | bytearray)
        parsed_initial = ThrustersParameters.model_validate_json(parameters.payload)

        new_parameters = parsed_initial.model_copy(update={"cooling_flow": 999})
        await controls_client.publish(
            set_parameters_topic,
            new_parameters.model_dump_json(),
            qos=1,
        )

        await controls_client.publish(
            f"{settings.mqtt_simulator_topic_prefix}/step",
            '{"seconds": 1}',
            qos=1,
        )

        async with asyncio.timeout(5.0):
            while True:
                updated = await anext(test_client.messages)
                if updated.topic.value != parameters_topic:
                    continue
                assert isinstance(updated.payload, str | bytes | bytearray)
                parsed_updated = ThrustersParameters.model_validate_json(
                    updated.payload
                )
                if parsed_updated.cooling_flow == 999:
                    break

        assert parsed_updated.cooling_flow == 999
    finally:
        run_task.cancel()
        with suppress(asyncio.CancelledError):
            await run_task


async def test_simulation_controls_set_simulation_inputs(
    mqtt_client: Client,
    mqtt_client2: Client,
    mqtt_client3: Client,
    mqtt_client4: Client,
    settings: Config,
):
    # Verifies externally provided simulation inputs are accepted and reflected in later ticks.
    status_topic = f"{settings.mqtt_simulator_topic_prefix}/status"
    simulation_inputs_topic = (
        f"{settings.mqtt_simulator_topic_prefix}/simulation-inputs"
    )
    set_inputs_topic = (
        f"{settings.mqtt_simulator_topic_prefix}/simulation-inputs/"
        f"{settings.mqtt_simulator_topic_suffix}"
    )

    controls_client = mqtt_client
    runtime_client = mqtt_client2
    test_client = mqtt_client3
    status_client = mqtt_client4

    mode = lookup_mode("thrusters")
    connector = MqttConnector(runtime_client)
    simulation, simulation_channels = setup_simulation(connector, settings, mode)
    control, control_channels, alarms = setup_control(
        connector, settings, mode, simulation.time
    )
    runner = LockstepRunner(
        control=control,
        control_channels=control_channels,
        alarms=alarms,
        simulation=simulation,
        simulation_channels=simulation_channels,
    )
    runtime = Runtime(
        runner=runner,
        connector=connector,
        tick_duration=simulation.tick_duration,
        directive_handling=DirectiveHandling(
            DirectivesChannels(connector, settings),
            mode,
            simulation.time,
        ),
    )

    await runtime.clear_previous()
    await status_client.subscribe(status_topic)
    await test_client.subscribe(simulation_inputs_topic)

    run_task = create_task(runtime.start())
    try:
        available = await anext(status_client.messages)
        assert isinstance(available.payload, str | bytes)
        assert (
            SimulationStatusMessage.model_validate_json(available.payload).status
            == "available"
        )

        await controls_client.publish(
            f"{settings.mqtt_simulator_topic_prefix}/step",
            '{"seconds": 1}',
            qos=1,
        )
        initial_inputs = await anext(test_client.messages)
        assert initial_inputs.topic.value == simulation_inputs_topic
        assert isinstance(initial_inputs.payload, str | bytes | bytearray)
        initial_model = ThrustersSimulationInputs.model_validate_json(
            initial_inputs.payload
        )
        assert cast(float, initial_model.thrusters_thruster_aft.heat_flow.value) != 0.0

        new_inputs = ThrustersSimulationInputs.zero()
        await controls_client.publish(
            set_inputs_topic,
            new_inputs.model_dump_json(),
            qos=1,
        )

        updated_model = None
        for _ in range(2):
            await controls_client.publish(
                f"{settings.mqtt_simulator_topic_prefix}/step",
                '{"seconds": 1}',
                qos=1,
            )
            updated_inputs = await anext(test_client.messages)
            if updated_inputs.topic.value != simulation_inputs_topic:
                continue
            assert isinstance(updated_inputs.payload, str | bytes | bytearray)
            updated_model = ThrustersSimulationInputs.model_validate_json(
                updated_inputs.payload
            )
            if cast(float, updated_model.thrusters_thruster_aft.heat_flow.value) == 0.0:
                break

        assert updated_model is not None
        assert cast(float, updated_model.thrusters_thruster_aft.heat_flow.value) == 0.0
    finally:
        run_task.cancel()
        with suppress(asyncio.CancelledError):
            await run_task


async def test_simulation_controls_simulation_output(
    mqtt_client: Client,
    mqtt_client2: Client,
    mqtt_client3: Client,
    mqtt_client4: Client,
    settings: Config,
):
    # Verifies simulation outputs are published with physically valid values while running.
    status_topic = f"{settings.mqtt_simulator_topic_prefix}/status"
    simulation_outputs_topic = (
        f"{settings.mqtt_simulator_topic_prefix}/simulation-outputs"
    )

    controls_client = mqtt_client
    runtime_client = mqtt_client2
    test_client = mqtt_client3
    status_client = mqtt_client4

    mode = lookup_mode("thrusters")
    connector = MqttConnector(runtime_client)
    simulation, simulation_channels = setup_simulation(connector, settings, mode)
    control, control_channels, alarms = setup_control(
        connector, settings, mode, simulation.time
    )
    runner = LockstepRunner(
        control=control,
        control_channels=control_channels,
        alarms=alarms,
        simulation=simulation,
        simulation_channels=simulation_channels,
    )
    runtime = Runtime(
        runner=runner,
        connector=connector,
        tick_duration=simulation.tick_duration,
        directive_handling=DirectiveHandling(
            DirectivesChannels(connector, settings),
            mode,
            simulation.time,
        ),
    )

    await runtime.clear_previous()
    await status_client.subscribe(status_topic)
    await test_client.subscribe(simulation_outputs_topic)

    run_task = create_task(runtime.start())
    try:
        available = await anext(status_client.messages)
        assert isinstance(available.payload, str | bytes)
        assert (
            SimulationStatusMessage.model_validate_json(available.payload).status
            == "available"
        )

        await controls_client.publish(
            f"{settings.mqtt_simulator_topic_prefix}/play",
            "{}",
            qos=1,
        )
        running = await anext(status_client.messages)
        assert isinstance(running.payload, str | bytes)
        assert (
            SimulationStatusMessage.model_validate_json(running.payload).status
            == "running"
        )

        simulation_output = await anext(test_client.messages)
        assert simulation_output.topic.value == simulation_outputs_topic
        assert isinstance(simulation_output.payload, str | bytes | bytearray)
        output_model = ThrustersSimulationOutputs.model_validate_json(
            simulation_output.payload
        )
        assert cast(float, output_model.thrusters_pcm_return.temperature.value) > 0
    finally:
        run_task.cancel()
        with suppress(asyncio.CancelledError):
            await run_task
