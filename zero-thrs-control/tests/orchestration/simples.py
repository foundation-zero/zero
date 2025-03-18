from datetime import datetime
from input_output.base import ThrsModel
from input_output.definitions.sensor import FlowSensor
from orchestration.executor import ExecutionResult, Executor
from orchestration.interfacer import Control


class SimpleInOut(ThrsModel):
    go_with_the: FlowSensor


class SimpleExecutor(Executor):
    def __init__(self):
        self.controls = []

    async def start(self):
        pass

    async def tick(self, control_values):
        self.controls.append(control_values)
        return ExecutionResult(timestamp=datetime.now(), sensor_values=control_values)


class SimpleControl(Control[SimpleInOut, SimpleInOut]):
    def initial(self) -> SimpleInOut:
        return SimpleInOut.zero()

    def control(self, sensor_values: SimpleInOut) -> SimpleInOut:
        return sensor_values
