import logging
import warnings
from dataclasses import dataclass
from datetime import datetime, timedelta

from thrs.classes.control import Control
from thrs.input_output.alarms import BaseAlarms
from thrs.input_output.base import (
    CombinedValues,
    SimulationInputs,
    SimulationValues,
    ThrsValues,
)
from thrs.orchestration.connector import Connector
from thrs.orchestration.simulation import Simulation
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

    def simulation(self) -> Simulation:
        return Simulation(
            self.sensor_values_cls,
            self.simulation_outputs_cls,
            Fmu(self.fmu_path),
            self.simulation_inputs,
            self.start_time,
            self.tick_duration,
        )


class Runner[S, C, P, M]:
    """Runs a module for a number of ticks."""

    def __init__(
        self,
        control_connector: Connector[S, C, M],
        simulation_module_name: str,
        simulation: Simulation | None,
        simulation_connector: Connector[C, S, CombinedValues] | None,
        control: Control[S, C, P, M],
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
        for _ in range(n_ticks):
            sensor_values = await self._control_connector.transceive(
                self._control_values,
                CombinedValues({}),  # type: ignore
            )
            if self._simulation_connector and self._simulation:
                logging.debug("Executing simulation")
                simulation_result = self._simulation.tick(self._control_values)

                # If there is a simulation, we run it and use its sensor values
                sensor_values = simulation_result.sensor_values

                # But also send them to mqtt
                await self._simulation_connector.transceive(
                    simulation_result.sensor_values,
                    CombinedValues(  # type: ignore
                        {
                            self._simulation_module_name: simulation_result.simulation_outputs
                        }
                    ),
                )

            self._control_values = self._control.control(sensor_values)  # type: ignore
            alarms = self._alarms.check(
                sensor_values,  # type: ignore
                self._control_values,  # type: ignore
                self._control.parameters,  # type: ignore
            )
            if alarms:
                warnings.warn(
                    f"Alarms detected: {alarms}"
                )  # TODO: properly handle alarms
