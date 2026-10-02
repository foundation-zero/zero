from collections import deque
from collections.abc import Callable, Hashable, Iterator
from copy import deepcopy
from datetime import timedelta
from itertools import groupby
from math import ceil
from typing import Any, cast

from analysis.simulation_values import SimulationValues
from tests.helpers.collector import Collector
from thrs.classes.control import Control, ControlMode
from thrs.input_output.alarms import BaseAlarms
from thrs.input_output.base import CombinedValues, ThrsValues
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

    @property
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
        controller_state: CombinedValues,
    ) -> list[Any]:
        return [
            result
            for name, alarms in self._alarms.items()
            if (s := sensor_values.values.get(name)) is not None
            and (c := control_values.values.get(name)) is not None
            and (p := parameters.values.get(name)) is not None
            and (cs := controller_state.values.get(name)) is not None
            for result in alarms.check(s, c, p, cs)
        ]


class SimulationTestRunner[
    S: ThrsValues | CombinedValues,
    C: ThrsValues | CombinedValues,
    I: ThrsValues | SimulationValues,
    O: ThrsValues,
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
        simulation_inputs: I,
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
        self._simulation_inputs = simulation_inputs
        self._simulation_module = SimulationUnit(
            simulation, cast(SimulationChannels, None)
        )
        self._simulation = simulation
        self._modes: list[M] = [cast(M, self._control.mode)]
        self._simulation_outputs: O | None = None

    @property
    def simulation_outputs(self) -> O | None:
        return self._simulation_outputs

    def update_simulation_inputs(self, simulation_inputs: I):
        self._simulation_inputs = simulation_inputs

    def tick(self, collector: Collector | None = None) -> tuple[S, C, CS]:
        if isinstance(self._simulation_inputs, SimulationValues):
            simulation_inputs = self._simulation_inputs.get_values_at_time(
                self._simulation.time()
            )
        else:
            simulation_inputs = self._simulation_inputs
        self._simulation.update_simulation_inputs(simulation_inputs)

        result = self._simulation_module.execute_simulation_tick(self._control_values)
        self._simulation_outputs = result.simulation_outputs

        self._alarms.check(
            result.sensor_values,
            self._control_values,
            self._control.parameters,
            self._controller_state,
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
        self._modes.append(cast(M, self._control.mode))

        # Controls return their internal values; a copy keeps test mutations out of them.
        return (
            result.sensor_values,
            deepcopy(self._control_values),
            deepcopy(self._controller_state),
        )

    def run(
        self, n_ticks: int, collector: Collector | None = None
    ) -> tuple[S | None, C, CS]:
        result = (None, self._control_values, self._controller_state)
        for _ in range(n_ticks):
            result = self.tick(collector)
        return result

    def ticks_for(
        self, duration: timedelta, collector: Collector | None = None
    ) -> Iterator[tuple[S, C, CS]]:
        end = self._simulation.time() + duration
        while self._simulation.time() < end:
            yield self.tick(collector)

    def run_until(
        self,
        condition: Callable[[S, C, CS], bool],
        within: timedelta,
        check: Callable[[S, C, CS], None] | None = None,
        collector: Collector | None = None,
    ) -> tuple[S, C, CS]:
        """Runs until `condition` holds, calling `check` on every tick on the way."""
        start = self._simulation.time()
        while True:
            result = self.tick(collector)
            if check is not None:
                check(*result)
            if condition(*result):
                return result
            if self._simulation.time() - start >= within:
                raise AssertionError(
                    f"Condition not met within {within} (mode: {self._control.mode})"
                )

    def run_until_stable(
        self,
        condition: Callable[[S, C, CS], bool],
        stable_for: timedelta,
        within: timedelta,
        collector: Collector | None = None,
    ) -> tuple[S, C, CS]:
        """Runs until `condition` has held on every tick for `stable_for`."""
        window = deque(maxlen=ceil(stable_for / self._simulation.tick_duration))
        for result in self.ticks_for(within, collector):
            window.append(condition(*result))
            if len(window) == window.maxlen and all(window):
                return result
        raise AssertionError(
            f"Condition not stable for {stable_for} within {within} (mode: {self._control.mode})"
        )

    def mode_transitions[K: Hashable](self, key: Callable[[M], K]) -> list[K]:
        """The modes passed through so far, with consecutive repeats collapsed."""
        return [mode for mode, _ in groupby(key(mode) for mode in self._modes)]
