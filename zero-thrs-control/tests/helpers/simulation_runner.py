from typing import Any, Callable, cast

from tests.helpers.collector import Collector
from thrs.classes.control import Control, ControlMode
from thrs.input_output.alarms import BaseAlarms
from thrs.input_output.base import (
    CombinedValues,
    SimulationInputs,
    SimulationValues,
    ThrsValues,
)
from thrs.input_output.fmu_mapping import build_fmu_key_mapping
from thrs.orchestration.comms import SimulationChannels
from thrs.orchestration.simulation import Simulation, SimulationUnit
from thrs.simulation.io_mapping import flatten_model_values


def _flatten_for_collector(values: ThrsValues | CombinedValues) -> dict[str, float]:
    if isinstance(values, CombinedValues):
        return {
            key: value
            for model in values.values.values()
            for key, value in flatten_model_values(
                model,
                build_fmu_key_mapping(type(model), fmu_only=False),
            ).items()
        }

    return flatten_model_values(
        values,
        build_fmu_key_mapping(type(values), fmu_only=False),
    )


class _CombinedControlAdapter[
    S: CombinedValues,
    C: CombinedValues,
    P,
    M,
    CS: CombinedValues,
]:
    def __init__(
        self,
        controls: dict[str, Control[ThrsValues, ThrsValues, P, M, ThrsValues]],
    ) -> None:
        self._controls = controls
        self.parameters = CombinedValues(
            {
                name: cast(ThrsValues, control.parameters)
                for name, control in self._controls.items()
            }
        )

    def update_parameters(self, parameters: CombinedValues):
        self.parameters = parameters
        for name, control in self._controls.items():
            if name in parameters.values:
                control.update_parameters(cast(P, parameters.values[name]))

    def initial(self) -> tuple[CombinedValues, CombinedValues]:
        initials = {name: control.initial() for name, control in self._controls.items()}
        return (
            CombinedValues(
                {name: control_values for name, (control_values, _) in initials.items()}
            ),
            CombinedValues(
                {
                    name: controller_state
                    for name, (_, controller_state) in initials.items()
                }
            ),
        )

    def control(
        self, sensor_values: CombinedValues
    ) -> tuple[CombinedValues, CombinedValues]:
        results = {
            name: control.initial()
            if (sensors := sensor_values.values.get(name)) is None
            else control.control(cast(ThrsValues, sensors))
            for name, control in self._controls.items()
        }
        return (
            CombinedValues(
                {name: control_values for name, (control_values, _) in results.items()}
            ),
            CombinedValues(
                {
                    name: controller_state
                    for name, (_, controller_state) in results.items()
                }
            ),
        )

    def mode(self) -> ControlMode:
        return ControlMode(
            **{name: control.mode for name, control in self._controls.items()}
        )


class _CombinedAlarmsAdapter:
    def __init__(self, alarms: dict[str, BaseAlarms]):
        self._alarms = alarms

    def check(
        self,
        sensor_values: CombinedValues,
        control_values: CombinedValues,
        parameters: CombinedValues,
    ) -> list[Any]:
        return [
            result
            for name, alarms in self._alarms.items()
            if (s := sensor_values.values.get(name)) is not None
            and (c := control_values.values.get(name)) is not None
            and (p := parameters.values.get(name)) is not None
            for result in alarms.check(s, c, p)
        ]


class SimulationTestRunner[
    S: ThrsValues | CombinedValues,
    C: ThrsValues | CombinedValues,
    I: SimulationInputs,
    O: SimulationValues,
    P,
    M,
    CS: ThrsValues | CombinedValues,
]:
    """Runs a module for a number of ticks

    Allows for a pluggable collector to collect execution results during the run.
    """

    def __init__(
        self,
        simulation: Simulation[S, C, I, O],
        control: Control[S, C, P, M, CS]
        | dict[str, Control[ThrsValues, ThrsValues, Any, Any, ThrsValues]],
        alarms: BaseAlarms | dict[str, BaseAlarms],
    ):
        if isinstance(control, dict):
            combined_control = cast(
                Control,
                _CombinedControlAdapter(
                    cast(
                        dict[
                            str, Control[ThrsValues, ThrsValues, Any, Any, ThrsValues]
                        ],
                        control,
                    )
                ),
            )
            combined_alarms = cast(
                BaseAlarms, _CombinedAlarmsAdapter(cast(dict[str, BaseAlarms], alarms))
            )
            self._control = combined_control
            self._alarms = combined_alarms
        else:
            self._control = control
            self._alarms = cast(BaseAlarms, alarms)

        self._control_values, self._controller_state = self._control.initial()
        self._simulation_module = SimulationUnit(
            simulation, cast(SimulationChannels, None)
        )
        self._simulation = simulation

    def update_simulation_inputs(self, simulation_inputs: I):
        self._simulation.update_simulation_inputs(simulation_inputs)

    def tick(self, collector: Collector | None = None) -> tuple[S | None, C, CS]:
        result = self._simulation_module.execute_simulation_tick(self._control_values)

        self._alarms.check(
            result.sensor_values, self._control_values, self._control.parameters
        )

        if collector is not None:
            collector.collect(  # TODO: fix the fmu key mapping here, this is just a quick fix to get the tests working
                {
                    **_flatten_for_collector(result.sensor_values),
                    **_flatten_for_collector(result.control_values),
                    **_flatten_for_collector(self._controller_state),
                    **_flatten_for_collector(result.simulation_outputs),
                    **_flatten_for_collector(result.simulation_inputs),
                },
                str(self._control.mode),
                result.timestamp,
            )

        self._control_values, self._controller_state = self._control.control(
            result.sensor_values
        )

        return result.sensor_values, self._control_values, self._controller_state

    def run(
        self, n_ticks: int, collector: Collector | None = None
    ) -> tuple[S | None, C, CS]:
        result = (None, self._control_values, self._controller_state)
        for _ in range(n_ticks):
            result = self.tick(collector)
        return result

    def run_until(
        self,
        condition: Callable[[S | None, C, CS], bool],
        collector: Collector | None = None,
    ) -> tuple[S | None, C, CS]:
        result = self.tick(collector)
        while not condition(*result):
            result = self.tick(collector)
        return result
