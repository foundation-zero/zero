import asyncio
from asyncio import create_task
from datetime import datetime
from unittest import mock

import pytest
from aiomqtt import Client as MqttClient

from thrs.control.switching import AutomationMode, SwitchingControlMode
from thrs.input_output.base import (
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
from thrs.orchestration.module import ModuleDescription
from thrs.runtime.messages import SimulationStatusMessage

pytestmark = pytest.mark.mqtt


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
        mock.Mock,
    )


def _listener_for_topic(connector: MqttConnector, topic: str):
    return next(
        listener
        for listener in connector._listeners
        if topic in listener.subscribe_topics()
    )


async def _wait_until(predicate, timeout_s: float = 2.0):
    async with asyncio.timeout(timeout_s):
        while not predicate():  # noqa: ASYNC110
            await asyncio.sleep(0.01)


async def test_control_channels_to_control_api_channels_roundtrip_all_channels(
    settings: Config, demo_module: ModuleDescription
):
    async with MqttClient(settings.mqtt_host, settings.mqtt_port) as mqtt_client:
        connector = MqttConnector(mqtt_client)

        control_channels = ControlChannels(
            connector, settings, "thrusters", demo_module
        )

        api_channels = ControlApiChannels(connector, settings, "thrusters", demo_module)

        connector_task = create_task(await connector.run())

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

            await control_channels.send_control_values(expected_control_values)
            await control_channels.send_manual_control(expected_manual_values)
            await control_channels.send_parameters(expected_parameters)
            await control_channels.send_controller_state(expected_state)
            await control_channels.send_control_modes(expected_mode)
            await asyncio.sleep(0.1)

            await _wait_until(
                lambda: (
                    api_channels.get_control_values() == expected_control_values
                    and api_channels.get_manual_values() == expected_manual_values
                    and api_channels.get_parameters() == expected_parameters
                    and api_channels.get_controller_state() == expected_state
                    and api_channels.get_control_modes() == expected_mode
                )
            )
        finally:
            connector_task.cancel()


async def test_control_api_channels_to_control_channels_roundtrip_shared_channels(
    settings: Config, demo_module: ModuleDescription
):
    async with MqttClient(settings.mqtt_host, settings.mqtt_port) as mqtt_client:
        connector = MqttConnector(mqtt_client)

        control_channels = ControlChannels(
            connector, settings, "thrusters", demo_module
        )

        api_channels = ControlApiChannels(connector, settings, "thrusters", demo_module)

        connector_task = create_task(await connector.run())

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
                lambda: (
                    control_channels.get_manual_controls() is not None
                    and control_channels.get_parameters() is not None
                    and control_channels.get_automation_modes() is not None
                )
            )

            manual_values = control_channels.get_manual_controls()
            parameters = control_channels.get_parameters()
            automation_modes = control_channels.get_automation_modes()

            assert manual_values is not None
            assert parameters is not None
            assert automation_modes is not None

            assert manual_values == expected_manual_values
            assert parameters == expected_parameters
            assert automation_modes == expected_mode
        finally:
            connector_task.cancel()


async def test_simulation_channels_to_simulation_api_channels_roundtrip_all_channels(
    settings: Config,
):
    async with MqttClient(settings.mqtt_host, settings.mqtt_port) as mqtt_client:
        connector = MqttConnector(mqtt_client)

        simulation_channels = SimulationChannels(
            connector,
            settings,
            {"thrusters": DemoSensorValues},
            {"thrusters": DemoControlValues},
            DemoSimulationInputs,
            DemoSimulationOutputs,
        )

        api_channels = SimulationApiChannels(
            connector, settings, DemoSimulationInputs, DemoSimulationOutputs
        )

        connector_task = create_task(await connector.run())

        try:
            sim_to_api_inputs = DemoSimulationInputs(target=10.0)
            sim_to_api_outputs = DemoSimulationOutputs(measured=21.0)
            api_to_sim_inputs = DemoSimulationInputs(target=42.0)

            await simulation_channels.send_simulation_inputs(sim_to_api_inputs)
            await simulation_channels.send_simulation_outputs(sim_to_api_outputs)

            await _wait_until(
                lambda: (
                    api_channels.get_simulation_inputs() == sim_to_api_inputs
                    and api_channels.get_simulation_outputs() == sim_to_api_outputs
                )
            )

            await api_channels.send_simulation_inputs(api_to_sim_inputs)

            await _wait_until(
                lambda: simulation_channels.get_simulation_inputs() == api_to_sim_inputs
            )
        finally:
            connector_task.cancel()


async def test_directives_channels_to_directives_api_channels_roundtrip_all_channels(
    settings: Config,
):
    async with MqttClient(settings.mqtt_host, settings.mqtt_port) as mqtt_client:
        connector = MqttConnector(mqtt_client)

        directives_channels = DirectivesChannels(connector, settings)

        api_channels = DirectivesApiChannels(connector, settings)

        connector_task = create_task(await connector.run())

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
                lambda: (
                    received.get("playback_rate") == 1.25
                    and received.get("seconds") == 2.5
                    and received.get("paused") is True
                )
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
            connector_task.cancel()
