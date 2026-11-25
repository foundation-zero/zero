import asyncio
from asyncio import create_task
from datetime import UTC, datetime
from unittest import mock

import pytest
from aiomqtt import Client as MqttClient

from thrs.input_output.base import CombinedValues, Stamped, ThrsValues
from thrs.input_output.definitions import sensor
from thrs.input_output.definitions.control import Pump, Valve
from thrs.orchestration.comms import (
    ControlChannels,
    MqttConnector,
    SimulationChannels,
)
from thrs.orchestration.config import Config
from thrs.orchestration.module import ModuleDescription

pytestmark = pytest.mark.mqtt


class DemoComponent(ThrsValues):
    value: float = 0.0


class DemoParameters(ThrsValues):
    value: float = 0.0


class DemoMode(ThrsValues):
    mode: str = "manual"


class DemoControllerState(ThrsValues):
    state: DemoComponent = DemoComponent()


class DemoSimulationInputs(ThrsValues):
    target: float = 1.0


class DemoSimulationOutputs(ThrsValues):
    measured: float = 2.0


async def _wait_until(predicate, timeout_s: float = 2.0):
    async with asyncio.timeout(timeout_s):
        while not predicate():  # noqa: ASYNC110
            await asyncio.sleep(0.01)


async def test_actuated_control_values_roundtrip(
    settings: Config,
):
    """The simulator merges sensor values and actuated control values into one
    payload per component topic, like the AMCS publishes them. The control side
    picks both halves out of that shared payload, while plain-key commands on the
    Command topics must not complete the actuated mapping."""

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
            CombinedValues({"thrusters": SharedDemoControlValues.initial()}),
        )
        control_channels = ControlChannels(
            connector, settings, "thrusters", shared_module
        )

        connector_task = create_task(await connector.run())

        try:
            await simulation_channels.send_device_values(sensor_values, actuated)
            await _wait_until(
                lambda: (
                    control_channels.get_sensor_values() == shared_sensor_model
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
        finally:
            connector_task.cancel()
