import asyncio
from asyncio import create_task
from datetime import datetime
from unittest import mock

import pytest
from aiomqtt import Client as MqttClient

from thrs.control.switching import AutomationMode, SwitchingControlMode
from thrs.input_output.base import (
    CombinedValues,
    SimulationInputs,
    SimulationValues,
    ThrsValues,
)
from thrs.orchestration.comms import (
    ControlApiChannels,
    ControlChannels,
    DirectivesApiChannels,
    DirectivesChannels,
    MqttConnector,
    SimulationApiChannels,
    SimulationChannels,
)
from thrs.orchestration.config import Config
from thrs.orchestration.module import CombinedModule, ModuleDescription
from thrs.runtime.messages import SimulationStatusMessage


class DemoSensorValues(ThrsValues):
    value: float = 0.0


class DemoComponent(ThrsValues):
    value: float = 0.0


class DemoControlValues(ThrsValues):
    command: DemoComponent = DemoComponent()


class DemoParameters(ThrsValues):
    value: float = 0.0


class DemoMode(ThrsValues):
    mode: str = "manual"


class DemoControllerState(ThrsValues):
    state: str = "ok"


class DemoSimulationInputs(SimulationInputs):
    target: float = 1.0


class DemoSimulationOutputs(SimulationValues):
    measured: float = 2.0


@pytest.fixture
def demo_module() -> ModuleDescription:
    return ModuleDescription(
        DemoSensorValues,
        DemoControlValues,
        DemoParameters,
        lambda *_args, **_kwargs: mock.Mock(),
        DemoMode,
        DemoControllerState,
        lambda: mock.Mock(),
    )


def _listener_for_topic(connector: MqttConnector, topic: str):
    return next(
        listener
        for listener in connector._listeners
        if topic in listener.subscribe_topics()
    )


async def _wait_until(predicate, timeout_s: float = 2.0):
    async with asyncio.timeout(timeout_s):
        while not predicate():
            await asyncio.sleep(0.01)


async def test_control_channels_to_control_api_channels_roundtrip_all_channels(
    settings: Config, demo_module: ModuleDescription
):
    async with (
        MqttClient(settings.mqtt_host, settings.mqtt_port) as control_client,
        MqttClient(settings.mqtt_host, settings.mqtt_port) as api_client,
    ):
        control_connector = MqttConnector(control_client)
        api_connector = MqttConnector(api_client)

        combined_module = CombinedModule(modules={"thrusters": demo_module})

        control_channels = ControlChannels(control_connector, settings, combined_module)
        control_task = create_task(await control_connector.run())

        api_channels = ControlApiChannels(
            api_connector, settings, "thrusters", demo_module
        )
        api_task = create_task(await api_connector.run())

        try:
            expected_control_values = DemoControlValues(
                command=DemoComponent(value=10.5)
            )
            expected_manual_values = DemoControlValues(
                command=DemoComponent(value=22.0)
            )
            expected_parameters = DemoParameters(value=3.14)
            expected_state = DemoControllerState(state="running")
            expected_mode = SwitchingControlMode(
                automatic_mode=DemoMode(mode="automatic")
            )

            await control_channels.send_control_values(
                CombinedValues(values={"thrusters": expected_control_values})
            )
            await control_channels.send_manual_control(
                CombinedValues(values={"thrusters": expected_manual_values})
            )
            await control_channels.send_parameters(
                CombinedValues(values={"thrusters": expected_parameters})
            )
            await control_channels.send_controller_state(
                CombinedValues(values={"thrusters": expected_state})
            )
            await control_channels.send_control_modes(
                CombinedValues(values={"thrusters": expected_mode})
            )
            await asyncio.sleep(0.1)

            await _wait_until(
                lambda: api_channels.get_control_values() == expected_control_values
                and api_channels.get_manual_values() == expected_manual_values
                and api_channels.get_parameters() == expected_parameters
                and api_channels.get_controller_state() == expected_state
                and api_channels.get_control_modes() == expected_mode
            )
        finally:
            control_task.cancel()
            api_task.cancel()


async def test_control_api_channels_to_control_channels_roundtrip_shared_channels(
    settings: Config, demo_module: ModuleDescription
):
    combined_module = CombinedModule(modules={"thrusters": demo_module})

    async with (
        MqttClient(settings.mqtt_host, settings.mqtt_port) as control_client,
        MqttClient(settings.mqtt_host, settings.mqtt_port) as api_client,
    ):
        control_connector = MqttConnector(control_client)
        api_connector = MqttConnector(api_client)

        control_channels = ControlChannels(control_connector, settings, combined_module)
        control_task = create_task(await control_connector.run())

        api_channels = ControlApiChannels(
            api_connector, settings, "thrusters", demo_module
        )
        api_task = create_task(await api_connector.run())

        try:
            expected_manual_values = DemoControlValues(
                command=DemoComponent(value=12.0)
            )
            expected_parameters = DemoParameters(value=8.5)
            expected_mode = AutomationMode(mode="automatic")

            await api_channels.send_manual_values(expected_manual_values)
            await api_channels.send_parameters(expected_parameters)
            await api_channels.send_automation_mode(expected_mode)

            await _wait_until(
                lambda: control_channels.get_manual_controls() is not None
                and control_channels.get_parameters() is not None
                and (automation_mode := control_channels.get_automation_modes())
                is not None
                and "thrusters" in automation_mode.values
            )

            manual_values = control_channels.get_manual_controls()
            parameters = control_channels.get_parameters()
            automation_modes = control_channels.get_automation_modes()

            assert manual_values is not None
            assert parameters is not None
            assert automation_modes is not None

            assert manual_values.values["thrusters"] == expected_manual_values
            assert parameters.values["thrusters"] == expected_parameters
            assert automation_modes.values["thrusters"] == expected_mode
        finally:
            control_task.cancel()
            api_task.cancel()


async def test_simulation_channels_to_simulation_api_channels_roundtrip_all_channels(
    settings: Config,
):
    async with (
        MqttClient(settings.mqtt_host, settings.mqtt_port) as simulation_client,
        MqttClient(settings.mqtt_host, settings.mqtt_port) as api_client,
    ):
        simulation_connector = MqttConnector(simulation_client)
        connector = MqttConnector(api_client)

        simulation_channels = SimulationChannels(
            connector,
            settings,
            {"thrusters": DemoSensorValues},
            {"thrusters": DemoControlValues},
            DemoSimulationInputs,
            DemoSimulationOutputs,
        )
        simulation_task = create_task(await simulation_connector.run())

        api_channels = SimulationApiChannels(
            connector, settings, DemoSimulationInputs, DemoSimulationOutputs
        )
        api_task = create_task(await connector.run())

        try:
            sim_to_api_inputs = DemoSimulationInputs(target=10.0)
            sim_to_api_outputs = DemoSimulationOutputs(measured=21.0)
            api_to_sim_inputs = DemoSimulationInputs(target=42.0)

            await simulation_channels.send_simulation_inputs(sim_to_api_inputs)
            await simulation_channels.send_simulation_outputs(sim_to_api_outputs)

            await _wait_until(
                lambda: api_channels.get_simulation_inputs() == sim_to_api_inputs
                and api_channels.get_simulation_outputs() == sim_to_api_outputs
            )

            await api_channels.send_simulation_inputs(api_to_sim_inputs)

            await _wait_until(
                lambda: simulation_channels.get_simulation_inputs() == api_to_sim_inputs
            )
        finally:
            simulation_task.cancel()
            api_task.cancel()


async def test_directives_channels_to_directives_api_channels_roundtrip_all_channels(
    settings: Config,
):
    async with (
        MqttClient(settings.mqtt_host, settings.mqtt_port) as directives_client,
        MqttClient(settings.mqtt_host, settings.mqtt_port) as api_client,
    ):
        directives_connector = MqttConnector(directives_client)
        api_connector = MqttConnector(api_client)

        directives_channels = DirectivesChannels(api_connector, settings)
        directives_task = create_task(await directives_connector.run())

        api_channels = DirectivesApiChannels(api_connector, settings)
        api_task = create_task(await api_connector.run())

        try:
            received: dict[str, object] = {}

            directives_channels.on_play(
                lambda msg: received.update(playback_rate=msg.playback_rate)
            )
            directives_channels.on_step(
                lambda msg: received.update(seconds=msg.seconds)
            )
            directives_channels.on_pause(lambda _msg: received.update(paused=True))

            await api_channels.send_play(1.25)
            await api_channels.send_step(2.5)
            await api_channels.send_pause()

            await _wait_until(
                lambda: received.get("playback_rate") == 1.25
                and received.get("seconds") == 2.5
                and received.get("paused") is True
            )

            status = SimulationStatusMessage(
                mode="thrusters",
                status="available",
                control_modules=["thrusters"],
                simulation_time=datetime.fromtimestamp(0),
            )
            await directives_channels.send_simulation_status(status)

            await _wait_until(lambda: api_channels.get_simulation_status() == status)
        finally:
            directives_task.cancel()
            api_task.cancel()
