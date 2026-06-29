import warnings
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Protocol

from thrs.classes.control import Control
from thrs.control.base import ModuleDescription
from thrs.input_output.alarms import BaseAlarms
from thrs.input_output.base import (
    CombinedValues,
    SimulationInputs,
    SimulationValues,
    ThrsValues,
)
from thrs.orchestration.connector import Connector
from thrs.orchestration.module import CombinedModule
from thrs.orchestration.simulation import Simulation, SimulationResult
from thrs.simulation.fmu import Fmu


@dataclass
class SimulatorModel:
    fmu_path: str
    sensor_values_cls: type[ThrsValues]
    control_values_cls: type[ThrsValues]
    simulation_outputs_cls: type[SimulationValues]
    control_cls: type[Control]
    alarms: BaseAlarms
    simulation_inputs: SimulationInputs
    start_time: datetime = datetime.now()
    tick_duration: timedelta = timedelta(seconds=1)

    @contextmanager
    def simulation(self):
        with Fmu(self.fmu_path) as fmu:
            yield Simulation(
                self.sensor_values_cls,
                self.simulation_outputs_cls,
                fmu,
                self.simulation_inputs,
                self.start_time,
                self.tick_duration,
            )


@dataclass
class ModuleSimulatorModel:
    fmu_path: str
    module: CombinedModule
    simulation_inputs: SimulationInputs
    start_time: datetime = datetime.now()
    tick_duration: timedelta = timedelta(seconds=1)

    @contextmanager
    def simulation(self):
        with Fmu(self.fmu_path) as fmu:
            yield Simulation(
                self.module.sensor_values_clss,
                self.module.simulation_outputs_cls,
                fmu,
                self.simulation_inputs,
                self.start_time,
                self.tick_duration,
            )


class Runner(Protocol):
    async def run(self, n_ticks: int) -> None: ...


class LockstepRunner[S, C, P, M: ThrsValues, I: SimulationInputs, O: SimulationValues](
    Runner
):
    """Runs a module for a number of ticks."""

    def __init__(
        self,
        control: Control[S, C, P, M],
        control_connector: Connector[S, C],
        simulation_module_name: str,
        simulation: Simulation[S, C, I, O],
        simulation_connector: Connector[C, S],
        alarms: BaseAlarms[S, C, P],
    ):
        self._control = control
        self._control_connector = control_connector
        self._simulation_module_name = simulation_module_name
        self._simulation = simulation
        self._simulation_connector = simulation_connector
        self._alarms = alarms
        self._control_values = self._control.initial()

    async def run(self, n_ticks: int) -> None:
        """Run simulation and control together."""
        for _ in range(n_ticks):
            await self._control_connector.send_control(self._control_values)
            sim_result: SimulationResult[S, C, I, O] = await self._simulation.tick(
                self._control_values
            )
            await self._simulation_connector.send_sensor_values(sim_result)
            await self._simulation_connector.send_computed_values(
                sim_result.computed_values
            )
            self._control_values = self._control.control(sim_result.sensor_values)
            alarms = self._alarms.check(
                sim_result.sensor_values, self._control_values, self._control.parameters
            )

            if alarms:
                warnings.warn(
                    f"Alarms detected: {alarms}"
                )  # TODO: properly handle alarms


class ControlRunner[S, C, P, M: ThrsValues](Runner):
    def __init__(
        self,
        connector: Connector[S, C],
        control: Control[S, C, P, M],
        alarms: BaseAlarms[S, C, P],
    ):
        self._connector = connector
        self._control = control
        self._alarms = alarms
        self._control_values = self._control.initial()

    @staticmethod
    def from_module(
        module: ModuleDescription[S, C, P, M] | CombinedModule,
        initial_control_parameters: P | CombinedValues,
        connector: Connector[S, C],
    ) -> "Runner":
        return Runner(
            connector,
            module.control(initial_control_parameters, connector.time),  # type:ignore
            module.alarms(),  # type:ignore
        )

    async def run(self, n_ticks: int) -> None:
        """Run control only, without simulation.
        1. Get sensor values from MQTT
        2. Send computed values and control values to MQTT
        3. Tick control with sensor values
        4. Send control values to MQTT
        5. Check for alarms
        """
        for _ in range(n_ticks):
            sensor_values = await self._connector.get_sensor_values_from_mqtt(
                self._control_values
            )

            # Send computed values (which is enriched sensor values)
            self._connector.send_sensor_values(sensor_values)

            self._control_values = self._control.control(sensor_values)
            self._connector.send_control_values(self._control_values)

            alarms = self._alarms.check(
                sensor_values, self._control_values, self._control.parameters
            )
            if alarms:
                warnings.warn(
                    f"Alarms detected: {alarms}"
                )  # TODO: properly handle alarms


class SimulationRunner[S, C, I: SimulationInputs, O: SimulationValues](Runner):
    def __init__(
        self,
        connector: Connector[C, S],
        simulation: Simulation[S, C, I, O],
    ):
        self._connector = connector
        self._simulation = simulation

    async def run(self, n_ticks: int) -> None:
        """Run simulation only, without control.
        1. Get control values from MQTT
        2. Tick simulation with control values
        3. Send sensor values to MQTT"""
        for _ in range(n_ticks):
            control_values = await self._connector.get_control_values_from_mqtt()
            sim_result = self._simulation.tick(control_values)
            await self._connector.send_sensor_values(sim_result.sensor_values)
            await self._connector.send_simulation_outputs(sim_result.simulation_outputs)
