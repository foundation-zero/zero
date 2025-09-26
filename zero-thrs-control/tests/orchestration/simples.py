from datetime import datetime
from typing import Callable
from thrs.classes.control import ControlResult
from thrs.input_output.alarms import BaseAlarms
from thrs.input_output.base import ThrsModel
from thrs.input_output.definitions.sensor import FlowSensor
from thrs.orchestration.executor import ExecutionResult, Executor
from thrs.orchestration.cycler import Control


class SimpleInOut(ThrsModel):
    go_with_the: FlowSensor


class SimpleExecutor(Executor):
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


class SimpleParameters(ThrsModel):
    pass


class SimpleControl(Control[SimpleInOut, SimpleInOut, SimpleParameters]):
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
    def mode(self) -> str | None:
        return None

    @property
    def parameters(self) -> SimpleParameters:
        return SimpleParameters()


class SimpleAlarms(BaseAlarms[SimpleInOut, SimpleInOut]):
    pass
