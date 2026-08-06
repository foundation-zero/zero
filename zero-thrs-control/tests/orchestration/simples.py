from collections.abc import Callable
from datetime import UTC, datetime

from thrs.classes.control import Control
from thrs.classes.machine_state_logger import (
    MachineStateLoggingServiceNoop,
    StateLogger,
)
from thrs.input_output.alarms import BaseAlarms
from thrs.input_output.base import ThrsValues
from thrs.input_output.definitions.sensor import FlowSensor
from thrs.orchestration.simulation import Simulation, SimulationResult


class SimpleInOut(ThrsValues):
    go_with_the: FlowSensor


class SimpleSimulationInputs(ThrsValues):
    pass


class SimpleSimulationOutputs(ThrsValues):
    pass


class SimpleSimulation(
    Simulation[
        SimpleInOut, SimpleInOut, SimpleSimulationInputs, SimpleSimulationOutputs
    ]
):
    def __init__(self, start_time):
        self.controls = []
        self._start_time = start_time

    async def start(self):
        pass

    def tick(
        self, control_values: SimpleInOut
    ) -> SimulationResult[
        SimpleInOut, SimpleInOut, SimpleSimulationInputs, SimpleSimulationOutputs
    ]:
        self.controls.append(control_values)
        return SimulationResult(
            timestamp=datetime.now(UTC),
            sensor_values=control_values,
            control_values=control_values,
            simulation_outputs=SimpleSimulationOutputs(),
            simulation_inputs=SimpleSimulationInputs(),
            raw={},
        )

    @property
    def start_time(self):
        return self._start_time

    def time(self):
        return datetime.now(UTC)


class SimpleParameters(ThrsValues):
    pass


class SimpleMode(ThrsValues):
    pass


class SimpleControllerState(ThrsValues):
    pass


class SimpleControl(
    Control[
        SimpleInOut, SimpleInOut, SimpleParameters, SimpleMode, SimpleControllerState
    ]
):
    def __init__(self, parameters: SimpleParameters, time_fn: Callable[[], datetime]):
        self._parameters = parameters
        self._time = time_fn
        self.state_logger: StateLogger = MachineStateLoggingServiceNoop()

    def initial(self) -> tuple[SimpleInOut, SimpleControllerState]:
        return (SimpleInOut.zero(), SimpleControllerState())

    def control(
        self, sensor_values: SimpleInOut
    ) -> tuple[SimpleInOut, SimpleControllerState]:
        return (sensor_values, SimpleControllerState())

    @staticmethod
    def modes() -> list[str]:
        return []

    @staticmethod
    def initial_mode() -> str:
        return ""

    @property
    def mode(self) -> SimpleMode | None:
        return None

    @property
    def parameters(self) -> SimpleParameters:
        return SimpleParameters()

    def update_parameters(self, parameters: SimpleParameters):
        pass


class SimpleAlarms(BaseAlarms[SimpleInOut, SimpleInOut, SimpleParameters]):
    pass
