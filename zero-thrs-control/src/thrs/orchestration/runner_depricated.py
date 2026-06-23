import warnings
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta

from thrs.classes.control import Control
from thrs.control.base import ModuleDescription
from thrs.input_output.alarms import BaseAlarms
from thrs.input_output.base import (
    CombinedValues,
    SimulationInputs,
    SimulationValues,
    ThrsValues,
)
from thrs.orchestration.module import CombinedModule
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
        pass # TODO: Maapater depricate this, use ModuleSimulatorModel instead
        # with Fmu(self.fmu_path) as fmu:
        #     yield Simulation(
        #         self.sensor_values_cls,
        #         self.simulation_outputs_cls,
        #         fmu,
        #         self.simulation_inputs,
        #         self.start_time,
        #         self.tick_duration,
        #     )


@dataclass
class ModuleSimulatorModel:
    fmu_path: str
    module: CombinedModule
    simulation_inputs: SimulationInputs
    start_time: datetime = datetime.now()
    tick_duration: timedelta = timedelta(seconds=1)

    @contextmanager
    def simulation(self):
        pass # TODO: Maapater depricate this, use ModuleSimulatorModel instead
        # with Fmu(self.fmu_path) as fmu:
        #     yield Simulation(
        #         self.module.sensor_values_clss,
        #         self.module.simulation_outputs_cls,
        #         fmu,
        #         self.simulation_inputs,
        #         self.start_time,
        #         self.tick_duration,
        #     )


class Runner[S: ThrsValues, C: ThrsValues, P: ThrsValues, M: ThrsValues]:
    """Runs a module for a number of ticks."""

    def __init__(
        self,
        # TODO: Maapater depricate this, use ModuleSimulatorModel instead

        connector,
        # connector: Connector[S, C],
        control: Control[S, C, P, M],
        alarms: BaseAlarms[S, C, P],
    ):
        self._control = control
        self._connector = connector
        self._alarms = alarms
        self._control_values = self._control.initial().values

    @staticmethod
    def from_module(
        module: ModuleDescription[S, C, P, M] | CombinedModule,
        initial_control_parameters: P | CombinedValues,
        # TODO: Maapater depricate this, use ModuleSimulatorModel instead
        # connector: Connector[S, C],
        connector
    ) -> "Runner":
        return Runner(
            connector,
            module.control(initial_control_parameters, connector.time),  # type:ignore
            module.alarms(),  # type:ignore
        )

    async def run(self, n_ticks: int) -> None:
        for _ in range(n_ticks):
            sensor_values = await self._connector.transceive(self._control_values)
            self._control_values = self._control.control(sensor_values).values
            alarms = self._alarms.check(
                sensor_values, self._control_values, self._control.parameters
            )
            if alarms:
                warnings.warn(
                    f"Alarms detected: {alarms}"
                )  # TODO: properly handle alarms
