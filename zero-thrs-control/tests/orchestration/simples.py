from datetime import datetime
from classes.control import ControlResult
from input_output.base import ThrsModel
from input_output.definitions.sensor import FlowSensor
from orchestration.executor import ExecutionResult, Executor
from orchestration.cycler import Control


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


class SimpleControl(Control[SimpleInOut, SimpleInOut]):
    def initial(self, time: datetime) -> ControlResult[SimpleInOut]:
        return ControlResult(time,SimpleInOut.zero())

    def control(self, sensor_values: SimpleInOut, time: datetime) -> ControlResult[SimpleInOut]:
        return ControlResult(time, sensor_values)
