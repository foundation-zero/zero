import warnings
from thrs.input_output.alarms import BaseAlarms
from thrs.orchestration.collector import Collector
from thrs.orchestration.executor import Executor, SimulationExecutionResult
from thrs.classes.control import Control
from thrs.simulation.io_mapping import flatten_model_values


class Cycler:
    def __init__(self, control: Control, executor: Executor, alarms: BaseAlarms):
        self._control = control
        self._executor = executor
        self._alarms = alarms
        self._control_values = self._control.initial().values

    async def run(self, ticks: int, collector: Collector):
        for _ in range(ticks):
            result = await self._executor.tick(self._control_values)
            if isinstance(result, SimulationExecutionResult):
                collector.collect(
                    {
                        **flatten_model_values(result.sensor_values, fmu_only=False),
                        **flatten_model_values(result.control_values, fmu_only=False),
                        **flatten_model_values(
                            result.simulation_outputs, fmu_only=False
                        ),
                        **flatten_model_values(
                            result.simulation_inputs, fmu_only=False
                        ),
                    },
                    self._control.mode,
                    result.timestamp,
                )
            self._control_values = self._control.control(result.sensor_values).values
            alarms = self._alarms.check(result.sensor_values, self._control_values)
            if alarms:
                warnings.warn(
                    f"Alarms detected: {alarms}"
                )  # TODO: properly handle alarms
