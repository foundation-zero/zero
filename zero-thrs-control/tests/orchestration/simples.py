from datetime import datetime
from typing import Callable

from thrs.classes.control import Control, ControlResult
from thrs.input_output.alarms import BaseAlarms
from thrs.input_output.base import SimulationInputs, SimulationValues, ThrsValues
from thrs.input_output.definitions.sensor import FlowSensor
from thrs.orchestration.connector import Connector, ExecutionResult
from thrs.orchestration.simulation import Simulation, SimulationResult


class SimpleInOut(ThrsValues):
    go_with_the: FlowSensor


class SimpleSimulationInputs(SimulationInputs):
    pass


class SimpleSimulationOutputs(SimulationValues):
    pass


class SimpleConnector(Connector):
    def __init__(self, start_time):
        self.controls = []
        self._start_time = start_time

    async def start(self):
        pass

    async def tick(self, control_values):
        self.controls.append(control_values)
        return ExecutionResult(timestamp=datetime.now(), sensor_values=control_values)

    @property
    def start_time(self):
        return self._start_time

    def time(self):
        return datetime.now()


class SimpleSimulation[
    S,
    I: SimulationInputs,
    O: SimulationValues,
](Simulation[S, S, I, O]):
    def __init__(self, start_time):
        self.controls = []
        self._start_time = start_time

    async def start(self):
        pass

    async def tick(self, control_values: S) -> SimulationResult[S, S, I, O]:
        self.controls.append(control_values)
        return ExecutionResult(timestamp=datetime.now(), sensor_values=control_values)  # type: ignore # TODO: make this make sense

    @property
    def start_time(self):
        return self._start_time

    def time(self):
        return datetime.now()


class SimpleParameters(ThrsValues):
    pass


class SimpleMode(ThrsValues):
    pass


class SimpleControl(Control[SimpleInOut, SimpleInOut, SimpleParameters, SimpleMode]):
    def __init__(self, parameters: SimpleParameters, time_fn: Callable[[], datetime]):
        self._parameters = parameters
        self._time = time_fn

    def initial(self) -> ControlResult[SimpleInOut]:
        return ControlResult(self._time(), SimpleInOut.zero())

    def control(self, sensor_values: SimpleInOut) -> ControlResult[SimpleInOut]:
        return ControlResult(self._time(), sensor_values)

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
