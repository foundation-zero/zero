import asyncio
from asyncio import create_task
from datetime import UTC, datetime
from unittest import mock

import pytest
from aiomqtt import Client as MqttClient

from thrs.control.switching import AutomationMode, SwitchingControlMode
from thrs.input_output.base import CombinedValues, Stamped, ThrsValues
from thrs.input_output.definitions import sensor
from thrs.input_output.definitions.control import Pump, Valve
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


class DemoMqttSensorValues(ThrsValues):
    value: DemoComponent = DemoComponent()


class DemoControlValues(ThrsValues):
    command: DemoComponent = DemoComponent()


class DemoParameters(ThrsValues):
    value: float = 0.0


class DemoMode(ThrsValues):
    mode: str = "manual"


class DemoControllerState(ThrsValues):
    state: str = "ok"


class DemoSimulationInputs(ThrsValues):
    target: float = 1.0


class DemoSimulationOutputs(ThrsValues):
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
        simulation_channels = SimulationChannels(
            connector,
            settings,
            {"thrusters": DemoMqttSensorValues},
            {"thrusters": DemoControlValues},
            DemoSimulationInputs,
            DemoSimulationOutputs,
        )

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

            await simulation_channels.send_sensor_values(
                CombinedValues(
                    {"thrusters": DemoMqttSensorValues(value=DemoComponent(value=1.0))}
                )
            )
            await simulation_channels.send_actuated_control_values(
                CombinedValues({"thrusters": expected_control_values})
            )
            await control_channels.send_control_values(expected_control_values)
            await control_channels.send_manual_control(expected_manual_values)
            await control_channels.send_parameters(expected_parameters)
            await control_channels.send_controller_state(expected_state)
            await control_channels.send_control_modes(expected_mode)
            await asyncio.sleep(0.1)

            await _wait_until(
                lambda: (
                    api_channels.get_actuated_control_values()
                    == expected_control_values
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


async def test_actuated_control_values_roundtrip(
    settings: Config,
):
    """The simulator merges sensor values and actuated control values into one
    payload per component topic, like the AMCS publishes them. The control and
    API sides pick both halves out of that shared payload, while sensors-only
    payloads and plain-key commands on the Command topics must not complete
    the actuated mapping."""

    class SharedDemoSensorValues(ThrsValues):
        pump: sensor.Pump
        temperature: sensor.TemperatureSensor

    class SharedDemoControlValues(ThrsValues):
        pump: Pump
        valve: Valve

    shared_module = ModuleDescription(
        SharedDemoSensorValues,
        SharedDemoControlValues,
        DemoParameters,
        lambda *_args, **_kwargs: mock.Mock(),
        DemoMode,
        DemoControllerState,
        mock.Mock,
    )

    shared_sensor_model = SharedDemoSensorValues(
        pump=sensor.Pump(
            speed=Stamped.stamp(50.0),
            flow=Stamped.stamp(20.0),
        ),
        temperature=sensor.TemperatureSensor(temperature=Stamped.stamp(25.0)),
    )
    sensor_values = CombinedValues({"thrusters": shared_sensor_model})
    shared_control_model = SharedDemoControlValues(
        pump=Pump(
            dutypoint=Stamped(
                value=0.4,
                timestamp=datetime(2026, 1, 2, tzinfo=UTC),
            ),
            on=Stamped(
                value=True,
                timestamp=datetime(2026, 1, 2, tzinfo=UTC),
            ),
        ),
        valve=Valve(
            setpoint=Stamped(
                value=0.6,
                timestamp=datetime(2026, 1, 2, tzinfo=UTC),
            )
        ),
    )
    actuated = CombinedValues({"thrusters": shared_control_model})
    commanded_model = SharedDemoControlValues(
        pump=Pump(
            dutypoint=Stamped(
                value=0.3,
                timestamp=datetime(2026, 1, 1, tzinfo=UTC),
            ),
            on=Stamped(
                value=True,
                timestamp=datetime(2026, 1, 1, tzinfo=UTC),
            ),
        ),
        valve=Valve(
            setpoint=Stamped(
                value=0.5,
                timestamp=datetime(2026, 1, 1, tzinfo=UTC),
            )
        ),
    )

    async with MqttClient(settings.mqtt_host, settings.mqtt_port) as mqtt_client:
        connector = MqttConnector(mqtt_client)

        simulation_channels = SimulationChannels(
            connector,
            settings,
            {"thrusters": SharedDemoSensorValues},
            {"thrusters": SharedDemoControlValues},
            DemoSimulationInputs,
            DemoSimulationOutputs,
        )
        control_channels = ControlChannels(
            connector, settings, "thrusters", shared_module
        )
        api_channels = ControlApiChannels(
            connector, settings, "thrusters", shared_module
        )

        connector_task = create_task(await connector.run())

        try:
            await simulation_channels.send_sensor_values(sensor_values)
            await asyncio.sleep(0.1)
            # Assert sensor values are not received, because the actuated control values have not been sent yet, so the merged payload is not complete.
            assert control_channels.get_sensor_values() is None
            assert api_channels.get_sensor_values() is None
            assert control_channels.get_actuated_control_values() is None
            assert api_channels.get_actuated_control_values() is None

            # The merged publish completes both mappings on both sides.
            await simulation_channels.send_actuated_control_values(actuated)
            await _wait_until(
                lambda: (
                    control_channels.get_sensor_values() == shared_sensor_model
                    and api_channels.get_sensor_values() == shared_sensor_model
                    and api_channels.get_actuated_control_values() is not None
                    and api_channels.get_actuated_control_values()
                    == shared_control_model
                    and control_channels.get_actuated_control_values() is not None
                    and control_channels.get_actuated_control_values()
                    == shared_control_model
                )
            )
            # Plain-key commands on the Command topics are not actuated values:
            # publishing one must leave the actuated mappings untouched.
            await control_channels.send_control_values(commanded_model)
            await asyncio.sleep(0.1)
            assert (
                control_channels.get_actuated_control_values() == shared_control_model
            )
            assert api_channels.get_actuated_control_values() == shared_control_model
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
