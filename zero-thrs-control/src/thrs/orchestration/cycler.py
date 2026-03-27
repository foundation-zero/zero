import warnings
from thrs.classes.executor import ExecutionResult
from thrs.input_output.alarms import BaseAlarms
from thrs.input_output.base import SimulationInputs
from thrs.orchestration.collector import Collector
from thrs.orchestration.executor import (
    Executor,
    SimulationExecutionResult,
    SimulationExecutor,
)
from thrs.classes.control import Control
from thrs.simulation.io_mapping import flatten_model_values


class Cycler:
    def __init__(self, control: Control, executor: Executor, alarms: BaseAlarms):
        self._control = control
        self._executor = executor
        self._alarms = alarms
        self._control_values = self._control.initial().values

    async def run(
        self, ticks: int, collector: Collector | None = None
    ) -> ExecutionResult | None:
        result = None
        for _ in range(ticks):
            result = await self._executor.tick(self._control_values)
            if isinstance(result, SimulationExecutionResult) and collector is not None:
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
                    str(self._control.mode),
                    result.timestamp,
                )
            self._control_values = self._control.control(result.sensor_values).values
            alarms = self._alarms.check(result.sensor_values, self._control_values)
            if alarms:
                warnings.warn(
                    f"Alarms detected: {alarms}"
                )  # TODO: properly handle alarms
        return result

    def update_simulation_inputs(self, simulation_inputs: SimulationInputs):
        if isinstance(self._executor, SimulationExecutor):
            self._executor.update_simulation_inputs(simulation_inputs)
        else:
            raise TypeError("Executor does not support updating simulation inputs")
