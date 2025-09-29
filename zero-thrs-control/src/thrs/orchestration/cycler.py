import warnings
from thrs.input_output.alarms import BaseAlarms
from thrs.orchestration.collector import Collector
from thrs.orchestration.executor import Executor, SimulationExecutionResult
from thrs.classes.control import Control


class Cycler:
    def __init__(self, control: Control, executor: Executor, alarms: BaseAlarms):
        self._control = control
        self._executor = executor
        self._alarms = alarms

    async def run(self, ticks: int, collector: Collector):
        control_values = self._control.initial().values
        for _ in range(ticks):
            result = await self._executor.tick(control_values)
            if isinstance(result, SimulationExecutionResult):
                collector.collect(result.raw, self._control.mode, result.timestamp)
            control_values = self._control.control(result.sensor_values).values
            alarms = self._alarms.check(
                result.sensor_values, control_values, self._control
            )
            if alarms:
                warnings.warn(
                    f"Alarms detected: {alarms}"
                )  # TODO: properly handle alarms
