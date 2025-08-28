import warnings
from input_output.alarms import BaseAlarms
from orchestration.collector import Collector
from orchestration.executor import Executor, SimulationExecutionResult
from classes.control import Control


class Cycler:
    def __init__(self, control: Control, executor: Executor, alarms: BaseAlarms):
        self._control = control
        self._executor = executor
        self._alarms = alarms

    async def run(self, times: int, collector: Collector):
        control_values = self._control.initial(self._executor.start_time).values #TODO: should we use the _current_values here? this initiates the FMU with whatever the initial control values are set to
        for _ in range(times):
            result = await self._executor.tick(control_values)
            if isinstance(result, SimulationExecutionResult):
                collector.collect(result.raw, self._control.mode, result.timestamp)
            control_values = self._control.control(
                result.sensor_values, result.timestamp
            ).values
            alarms = self._alarms.check(
                result.sensor_values, control_values, self._control
            )
            if alarms:
                warnings.warn(f"Alarms detected: {alarms}") #TODO: properly handle alarms
