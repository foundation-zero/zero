import logging
import warnings

from thrs.classes.control import Control
from thrs.input_output.alarms import BaseAlarms
from thrs.input_output.base import (
    CombinedValues,
)
from thrs.orchestration.connector import Connector
from thrs.orchestration.simulation import Simulation


class Runner[S, C, P, M, CV]:
    """Runs a module for a number of ticks."""

    def __init__(
        self,
        control_connector: Connector[S, C, CV],
        simulation_module_name: str,
        simulation: Simulation | None,
        simulation_connector: Connector[C, S, CombinedValues] | None,
        control: Control[S, C, P, M, CV],
        alarms: BaseAlarms[S, C, P],
    ):
        self._control = control
        self._control_connector = control_connector
        self._simulation_module_name = simulation_module_name
        self._simulation = simulation
        self._simulation_connector = simulation_connector
        self._alarms = alarms
        self._control_values, self._controller_state = self._control.initial()

    async def run(self, n_ticks: int) -> None:
        for _ in range(n_ticks):
            sensor_values = await self._control_connector.transceive(
                self._control_values,
                self._controller_state,  # type: ignore
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

            self._control_values, self._controller_state = self._control.control(
                sensor_values
            )  # type: ignore
            alarms = self._alarms.check(
                sensor_values,  # type: ignore
                self._control_values,  # type: ignore
                self._controller_state,  # type: ignore
            )
            if alarms:
                warnings.warn(
                    f"Alarms detected: {alarms}"
                )  # TODO: properly handle alarms
