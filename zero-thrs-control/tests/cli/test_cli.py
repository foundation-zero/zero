import asyncio
import logging
from asyncio import create_task, sleep
from contextlib import suppress
from typing import cast
from unittest import mock

import pytest
from aiomqtt import Client

from thrs.classes.database import PostgresDatabase
from thrs.classes.persistence.engine import NoopPersistentEngine
from thrs.classes.persistence.manager import PersistManager
from thrs.control.modules.thrusters import ThrustersParameters
from thrs.control.switching import AutomationMode
from thrs.input_output.definitions.wire_context import AMCS_WRITE_CONTEXT
from thrs.input_output.model_builder import PartialModelBuilder
from thrs.input_output.modules.thrusters import (
    ThrustersControlValues,
    ThrustersSimulationInputs,
    ThrustersSimulationOutputs,
)
from thrs.orchestration.comms import DirectivesChannels, MqttConnector
from thrs.orchestration.config import Config
from thrs.orchestration.setup import setup_control_modules, setup_simulation_module
from thrs.runtime.descriptions.simulation import Mode, lookup_mode
from thrs.runtime.directives import DirectiveHandling
from thrs.runtime.messages import SimulationStatusMessage
from thrs.runtime.runners.lockstep import LockstepRunner
from thrs.runtime.runtime import Runtime

pytestmark = pytest.mark.mqtt

logger = logging.getLogger(__name__)


async def _mqtt_client(settings: Config):
    async with Client(settings.mqtt_host, settings.mqtt_port) as client:
        yield client


controls_client = pytest.fixture(_mqtt_client)
runtime_client = pytest.fixture(_mqtt_client)
test_client = pytest.fixture(_mqtt_client)
status_client = pytest.fixture(_mqtt_client)


def setup_lockstep(
    mode: Mode,
    settings: Config,
    mqtt_client: Client,
    database: PostgresDatabase | None = None,
    machine_state_logging_service_enabled: bool = False,
) -> Runtime:
    """Test helper mirroring LockstepCmd.setup() from the CLI."""
    connector = MqttConnector(mqtt_client)

    if mode.simulation_description is None:
        raise ValueError("simulation must be defined for lockstep mode")

    simulation_module = setup_simulation_module(
        connector,
        settings,
        mode.control_modules,
        mode.simulation_description,
    )

    control_modules = setup_control_modules(
        connector,
        settings,
        mode.control_modules,
        time_fn=simulation_module.time,
        database=database or mock.Mock(spec=PostgresDatabase),
        machine_state_logging_service_enabled=machine_state_logging_service_enabled,
    )

    for module in control_modules:
        module.set_automation_mode(AutomationMode(mode="automatic"))

    persistence = PersistManager(NoopPersistentEngine())
    runner = LockstepRunner(control_modules, simulation_module, persistence)

    directive_handling = DirectiveHandling(
        DirectivesChannels(connector, settings),
        mode,
        simulation_module.time,
    )
    return Runtime(
        runner,
        connector,
        simulation_module.tick_duration,
        directive_handling,
    )


@pytest.mark.timeout(30)
@pytest.mark.slow
async def test_simulation_run_start_stop(
    controls_client: Client,
    runtime_client: Client,
    test_client: Client,
    status_client: Client,
    settings: Config,
):
    # Verifies the simulation can transition from available to running and back to available.
    status_topic = f"{settings.mqtt_simulator_topic_prefix}/status"

    runtime = setup_lockstep(
        lookup_mode("thrusters"),
        settings,
        runtime_client,
    )

    await runtime.clear_previous()
    await test_client.subscribe(
        f"{settings.mqtt_devices_topic_prefix}/500000-thrs/thrusters/#"
    )
    await status_client.subscribe(status_topic)

    run_task = create_task(runtime.start())
    try:
        logger.info("Waiting on message")
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
        logger.info("Waiting on message")
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
            logger.info("Waiting on message")
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


@pytest.mark.timeout(30)
@pytest.mark.slow
async def test_simulation_run_playback_rate(
    controls_client: Client,
    runtime_client: Client,
    test_client: Client,
    status_client: Client,
    settings: Config,
):
    # Verifies a higher playback rate produces more simulation output messages in equal wall time.
    status_topic = f"{settings.mqtt_simulator_topic_prefix}/status"
    outputs_topic = f"{settings.mqtt_simulator_topic_prefix}/simulation-outputs"

    runtime = setup_lockstep(
        lookup_mode("thrusters"),
        settings,
        runtime_client,
    )

    await runtime.clear_previous()
    await status_client.subscribe(status_topic)
    await test_client.subscribe(outputs_topic)

    run_task = create_task(runtime.start())
    try:
        logger.info("Waiting on message")
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
        logger.info("Waiting on message")
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
        logger.info("Waiting on message")
        available = await anext(status_client.messages)
        assert isinstance(available.payload, str | bytes)
        assert (
            SimulationStatusMessage.model_validate_json(available.payload).status
            == "available"
        )

        rate_1_count = 0
        while len(test_client.messages) != 0:
            logger.info("Waiting on message")
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
            logger.info("Waiting on message")
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
        logger.info("Waiting on message")
        available = await anext(status_client.messages)
        assert isinstance(available.payload, str | bytes)
        assert (
            SimulationStatusMessage.model_validate_json(available.payload).status
            == "available"
        )

        rate_2_count = 0
        while len(test_client.messages) != 0:
            logger.info("Waiting on message")
            msg = await anext(test_client.messages)
            if msg.topic.value == outputs_topic:
                rate_2_count += 1

        assert rate_1_count > 0
        assert rate_2_count > rate_1_count
    finally:
        run_task.cancel()
        with suppress(asyncio.CancelledError):
            await run_task


@pytest.mark.timeout(5)
@pytest.mark.slow
async def test_simulation_run_step(
    controls_client: Client,
    runtime_client: Client,
    test_client: Client,
    status_client: Client,
    settings: Config,
):
    # Verifies step directives progress the simulation and publish outputs for each requested duration.
    status_topic = f"{settings.mqtt_simulator_topic_prefix}/status"
    outputs_topic = f"{settings.mqtt_simulator_topic_prefix}/simulation-outputs"

    runtime = setup_lockstep(
        lookup_mode("thrusters"),
        settings,
        runtime_client,
    )

    await runtime.clear_previous()
    await status_client.subscribe(status_topic)
    await test_client.subscribe(outputs_topic)

    run_task = create_task(runtime.start())
    try:
        logger.info("Waiting on message")
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
        logger.info("Waiting on message")
        stepping = await anext(status_client.messages)
        assert isinstance(stepping.payload, str | bytes)
        assert (
            SimulationStatusMessage.model_validate_json(stepping.payload).status
            == "stepping"
        )

        logger.info("Waiting on message")
        available = await anext(status_client.messages)
        assert isinstance(available.payload, str | bytes)
        assert (
            SimulationStatusMessage.model_validate_json(available.payload).status
            == "available"
        )

        await sleep(0.2)
        step_1_outputs = 0
        while len(test_client.messages) != 0:
            logger.info("Waiting on message")
            msg = await anext(test_client.messages)
            if msg.topic.value == outputs_topic:
                step_1_outputs += 1

        await controls_client.publish(
            f"{settings.mqtt_simulator_topic_prefix}/step",
            '{"seconds": 2}',
            qos=1,
        )
        logger.info("Waiting on message")
        stepping = await anext(status_client.messages)
        assert isinstance(stepping.payload, str | bytes)
        assert (
            SimulationStatusMessage.model_validate_json(stepping.payload).status
            == "stepping"
        )

        logger.info("Waiting on message")
        available = await anext(status_client.messages)
        assert isinstance(available.payload, str | bytes)
        assert (
            SimulationStatusMessage.model_validate_json(available.payload).status
            == "available"
        )

        await sleep(0.2)
        step_2_outputs = 0
        while len(test_client.messages) != 0:
            logger.info("Waiting on message")
            msg = await anext(test_client.messages)
            if msg.topic.value == outputs_topic:
                step_2_outputs += 1

        assert step_1_outputs >= 1
        assert step_2_outputs >= step_1_outputs
    finally:
        run_task.cancel()
        with suppress(asyncio.CancelledError):
            await run_task


@pytest.mark.timeout(10)
@pytest.mark.slow
async def test_simulation_controls_automated_control(
    controls_client: Client,
    runtime_client: Client,
    test_client: Client,
    status_client: Client,
    settings: Config,
):
    # Verifies switching to automatic mode results in non-default automatic control outputs.
    status_topic = f"{settings.mqtt_simulator_topic_prefix}/status"
    set_automation_topic = (
        f"{settings.mqtt_controller_topic_prefix}/thrusters/automation-mode/"
        f"{settings.mqtt_controller_topic_suffix}"
    )

    runtime = setup_lockstep(
        lookup_mode("thrusters"),
        settings,
        runtime_client,
    )

    await runtime.clear_previous()
    await test_client.subscribe(
        f"{settings.mqtt_devices_topic_prefix}/500000-thrs/thrusters/+/{settings.mqtt_control_topic_suffix}"
    )
    await status_client.subscribe(status_topic)

    run_task = create_task(runtime.start())
    try:
        logger.info("Waiting on message")
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

        logger.info("Waiting on message")
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
            logger.info("Waiting on message")
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

        control_builder = PartialModelBuilder(
            ThrustersControlValues, validation_context=AMCS_WRITE_CONTEXT
        )
        while len(test_client.messages) != 0:
            logger.info("Waiting on message")
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


@pytest.mark.timeout(5)
@pytest.mark.slow
async def test_simulation_controls_set_parameters(
    controls_client: Client,
    runtime_client: Client,
    test_client: Client,
    status_client: Client,
    settings: Config,
):
    # Verifies runtime applies updated controller parameters sent over MQTT.
    status_topic = f"{settings.mqtt_simulator_topic_prefix}/status"
    parameters_topic = f"{settings.mqtt_controller_topic_prefix}/thrusters/parameters"
    set_parameters_topic = (
        f"{settings.mqtt_controller_topic_prefix}/thrusters/parameters/"
        f"{settings.mqtt_controller_topic_suffix}"
    )

    runtime = setup_lockstep(
        lookup_mode("thrusters"),
        settings,
        runtime_client,
    )

    await runtime.clear_previous()
    await status_client.subscribe(status_topic)
    await test_client.subscribe(parameters_topic)

    run_task = create_task(runtime.start())
    try:
        logger.info("Waiting on message")
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
        logger.info("Waiting on message")
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
                logger.info("Waiting on message")
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


@pytest.mark.timeout(5)
@pytest.mark.slow
async def test_simulation_controls_set_simulation_inputs(
    controls_client: Client,
    runtime_client: Client,
    test_client: Client,
    status_client: Client,
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

    runtime = setup_lockstep(
        lookup_mode("thrusters"),
        settings,
        runtime_client,
    )

    await runtime.clear_previous()
    await status_client.subscribe(status_topic)
    await test_client.subscribe(simulation_inputs_topic)

    run_task = create_task(runtime.start())
    try:
        logger.info("Waiting on message")
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
        logger.info("Waiting on message")
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
            logger.info("Waiting on message")
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


@pytest.mark.timeout(10)
@pytest.mark.slow
async def test_simulation_controls_simulation_output(
    controls_client: Client,
    runtime_client: Client,
    test_client: Client,
    status_client: Client,
    settings: Config,
):
    # Verifies simulation outputs are published with physically valid values while running.
    status_topic = f"{settings.mqtt_simulator_topic_prefix}/status"
    simulation_outputs_topic = (
        f"{settings.mqtt_simulator_topic_prefix}/simulation-outputs"
    )

    runtime = setup_lockstep(
        lookup_mode("thrusters"),
        settings,
        runtime_client,
    )

    await runtime.clear_previous()
    await status_client.subscribe(status_topic)
    await test_client.subscribe(simulation_outputs_topic)

    run_task = create_task(runtime.start())
    try:
        logger.info("Waiting on message")
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
        logger.info("Waiting on message")
        running = await anext(status_client.messages)
        assert isinstance(running.payload, str | bytes)
        assert (
            SimulationStatusMessage.model_validate_json(running.payload).status
            == "running"
        )

        logger.info("Waiting on message")
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
