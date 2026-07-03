import warnings
from typing import Protocol

from thrs.classes.control import Control
from thrs.input_output.alarms import BaseAlarms
from thrs.input_output.base import (
    CombinedValues,
    SimulationInputs,
    SimulationValues,
)
from thrs.orchestration.connector import Connector
from thrs.orchestration.simulation import Simulation, SimulationResult


class Runner(Protocol):
    async def run(self, n_ticks: int) -> None: ...


class LockstepRunner[
    S,
    C,
    P,
    M,
    I: SimulationInputs,
    O: SimulationValues,
    CS,
](Runner):
    """Runs a module for a number of ticks."""

    def __init__(
        self,
        control: Control[S, C, P, M, CS],
        control_connector: Connector[S, C],
        simulation_module_name: str,
        simulation: Simulation[S, C, I, O],
        simulation_connector: Connector[C, S],
        alarms: BaseAlarms[S, C, P],
        mode_name: str,
    ):
        self._control = control
        self._control_connector = control_connector
        self._simulation_module_name = simulation_module_name
        self._simulation = simulation
        self._simulation_connector = simulation_connector
        self._alarms = alarms
        self._control_values, self._controller_state = self._control.initial()
        self._mode_name = mode_name  # TODO: Remove this 'mode_name' parameter when 'CombinedValues' is removed as controller_state type

    async def run(self, n_ticks: int) -> None:
        """Run simulation and control together."""
        for _ in range(n_ticks):
            await self._control_connector.send_output(self._control_values)

            sim_result: SimulationResult[S, C, I, O] = self._simulation.tick(
                self._control_values
            )
            await self._simulation_connector.send_computed_input(
                sim_result.sensor_values
            )
            await self._simulation_connector.send_output(sim_result.sensor_values)
            await self._simulation_connector.send_controller_state(
                CombinedValues(values={self._mode_name: sim_result.simulation_outputs})
            )

            self._control_values, self._controller_state = self._control.control(
                sim_result.sensor_values
            )
            alarms = self._alarms.check(
                sim_result.sensor_values, self._control_values, self._control.parameters
            )

            if alarms:
                warnings.warn(
                    f"Alarms detected: {alarms}"
                )  # TODO: properly handle alarms


class ControlRunner[S, C, P, M, CS](Runner):
    def __init__(
        self,
        connector: Connector[S, C],
        control: Control[S, C, P, M, CS],
        alarms: BaseAlarms[S, C, P],
    ):
        self._connector = connector
        self._control = control
        self._alarms = alarms
        self._control_values, self._controller_state = self._control.initial()

    async def run(self, n_ticks: int) -> None:
        """Run control only, without simulation.
        1. Get sensor values from MQTT
        2. Send computed values and control values to MQTT
        3. Tick control with sensor values
        4. Send control values to MQTT
        5. Check for alarms
        """
        for _ in range(n_ticks):
            sensor_values = await self._connector.get_input_values()

            # Computed values are added (using a builder()) to sensor values when they are received from mqtt and
            # should therefore be exposed to MQTT.
            await self._connector.send_computed_input(sensor_values)

            self._control_values, self._controller_state = self._control.control(
                sensor_values
            )

            await self._connector.send_output(self._control_values)
            await self._connector.send_controller_state(self._controller_state)

            self._check_alarms(sensor_values)

    def _check_alarms(self, sensor_values):
        alarms = self._alarms.check(
            sensor_values, self._control_values, self._control.parameters
        )
        if alarms:
            warnings.warn(f"Alarms detected: {alarms}")  # TODO: properly handle alarms


class SimulationRunner[S, C, I: SimulationInputs, O: SimulationValues](Runner):
    def __init__(
        self,
        connector: Connector[C, S],
        simulation: Simulation[S, C, I, O],
        mode_name: str,  # TODO: Remove this 'mode_name' parameter when 'CombinedValues' is removed as controller_state type
    ):
        self._connector = connector
        self._simulation = simulation
        self._mode_name = mode_name

    async def run(self, n_ticks: int) -> None:
        """Run simulation only, without control.
        1. Get control values from MQTT
        2. Tick simulation with control values
        3. Send sensor values to MQTT
        4. Send simulation outputs to MQTT"""

        for _ in range(n_ticks):
            control_values = await self._connector.get_input_values()
            sim_result = self._simulation.tick(control_values)
            await self._connector.send_output(
                sim_result.sensor_values
            )  # Simulator creates sensor_values, so treat them as output values

            await self._connector.send_controller_state(
                CombinedValues(values={self._mode_name: sim_result.simulation_outputs})
            )
