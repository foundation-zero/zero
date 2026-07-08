import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from thrs.input_output.base import (
    CombinedValues,
    SimulationInputs,
    SimulationValues,
    ThrsValues,
)
from thrs.orchestration.comms import SimulationChannels
from thrs.orchestration.module import ModuleClassMap
from thrs.simulation.fmu import FmuLike
from thrs.simulation.io_mapping import CombinedIoMapping, IoMapping, ThrsModelIoMapping

logger = logging.getLogger(__name__)


@dataclass
class SimulationResult[
    S,
    C,
    I: SimulationInputs,
    O: ThrsValues,
]:
    timestamp: datetime
    sensor_values: S
    control_values: C
    simulation_outputs: O
    simulation_inputs: I
    raw: dict[str, Any]


class Simulation[
    S,
    C,
    I: SimulationInputs,
    O: SimulationValues,
]:
    def __init__(
        self,
        sensor_values_clss: ModuleClassMap | type[ThrsValues],
        simulation_outputs_cls: type[O],
        fmu: FmuLike,
        simulation_inputs: I,
        start_time: datetime,
        tick_duration: timedelta,
    ):
        self._start_time = start_time
        self._ticks = 0
        self._tick_duration = tick_duration
        self._simulation_inputs = simulation_inputs
        self._simulation_outputs_cls = simulation_outputs_cls
        self._fmu = fmu
        self._io_mapping: IoMapping = (
            CombinedIoMapping(sensor_values_clss, simulation_outputs_cls)  # type: ignore
            if isinstance(sensor_values_clss, dict)
            else ThrsModelIoMapping(sensor_values_clss, simulation_outputs_cls)  # type: ignore
        )

    @property
    def tick_duration(self) -> timedelta:
        return self._tick_duration

    def time(self):
        return self._start_time + self._ticks * self._tick_duration

    def tick(self, control_values: C) -> SimulationResult[S, C, I, O]:
        logging.debug("Running simulation tick")
        time = self.time()

        simulation_inputs = self._simulation_inputs.get_values_at_time(time)
        fmu_inputs = self._io_mapping.generate_inputs(control_values, simulation_inputs)
        fmu_outputs = self._fmu.tick(fmu_inputs, self._tick_duration)
        sensor_values, simulation_outputs, raw = self._io_mapping.construct_outputs(
            fmu_inputs, fmu_outputs, simulation_inputs, time + self._tick_duration
        )

        self._ticks += 1
        return SimulationResult(
            timestamp=time,
            sensor_values=sensor_values,
            control_values=control_values,
            simulation_outputs=simulation_outputs,
            simulation_inputs=simulation_inputs,
            raw=raw,
        )

    def update_simulation_inputs(self, simulation_inputs: I):
        self._simulation_inputs = simulation_inputs


@dataclass
class SimulationDescription:
    simulation_outputs_cls: type[SimulationValues]
    fmu: FmuLike
    simulation_inputs: SimulationInputs


class SimulationUnit[
    S: ThrsValues | CombinedValues,
    C: ThrsValues | CombinedValues,
    I: SimulationInputs,
    O: SimulationValues,
]:
    channels: SimulationChannels[I, O]

    def __init__(
        self,
        simulation: Simulation[S, C, I, O],
        channels: SimulationChannels[I, O],
    ):
        self._simulation = simulation
        self._channels = channels

    async def sync_simulation_channels_state(self) -> C:
        """Synchronize control values and simulation inputs."""

        self.sync_simulation_inputs()

        control_values = self._channels.get_control_values()
        if control_values is None:
            control_values = await self._channels.wait_for_control_values()
        return control_values

    def execute_simulation_tick(
        self, control_values: C
    ) -> SimulationResult[S, C, I, O]:
        """Execute a simulation tick and send the results to the appropriate channels."""
        return self._simulation.tick(control_values)

    async def send_simulation_updates(
        self, sim_result: SimulationResult[S, C, I, O]
    ) -> None:
        """Send sensor values, simulation inputs, and simulation outputs to the appropriate channels."""
        await self._channels.send_sensor_values(sim_result.sensor_values)
        await self._channels.send_simulation_inputs(sim_result.simulation_inputs)
        await self._channels.send_simulation_outputs(sim_result.simulation_outputs)

    @property
    def tick_duration(self) -> timedelta:
        return self._simulation.tick_duration

    def time(self):
        return self._simulation.time()

    def sync_simulation_inputs(self):
        simulation_inputs = self._channels.get_simulation_inputs()
        if simulation_inputs is not None:
            self._simulation.update_simulation_inputs(simulation_inputs)
