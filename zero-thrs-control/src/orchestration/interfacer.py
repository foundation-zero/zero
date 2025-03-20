from orchestration.collector import Collector
from orchestration.executor import Executor, SimulationExecutionResult
from classes.control import Control


class Interfacer:
    def __init__(self, control: Control, executor: Executor):
        self._control = control
        self._executor = executor

    async def run(self, times: int, collector: Collector):
        control_values = self._control.initial(
            self._executor._start_time
        ).values
        for _ in range(times):
            result = await self._executor.tick(control_values)
            if isinstance(result, SimulationExecutionResult):
                collector.collect(result.raw, result.timestamp)
            control_values = self._control.control(result.sensor_values, result.timestamp).values