import warnings
from thrs.input_output.alarms import BaseAlarms
from thrs.input_output.fmu_mapping import build_inputs_for_fmu
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
                computed_values = build_inputs_for_fmu(
                    result.sensor_values, "computed_fields"
                )
                collector.collect(
                    result.raw, self._control.mode, result.timestamp, computed_values
                )
            control_values = self._control.control(result.sensor_values).values
            alarms = self._alarms.check(result.sensor_values, control_values)
            if alarms:
                warnings.warn(
                    f"Alarms detected: {alarms}"
                )  # TODO: properly handle alarms
