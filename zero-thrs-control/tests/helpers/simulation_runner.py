from collections import deque
from collections.abc import Callable, Hashable, Iterator, Mapping
from copy import deepcopy
from datetime import timedelta
from functools import partial
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

# The collector also keeps what the FMU does not exchange.
_all_keys = partial(build_fmu_key_mapping, fmu_only=False)


def flatten_controller_state(state: ThrsValues | CombinedValues) -> dict[str, Any]:
    """A controller state as `__`-joined columns, a stamped value as its value.

    No controller state goes to the FMU, so it is flattened from its dump rather than
    with the FMU mapping; combined states are keyed by module first.
    """
    if isinstance(state, CombinedValues):
        return _flatten(
            {name: model.model_dump() for name, model in state.values.items()}
        )
    return _flatten(state.model_dump())


def _flatten(value: Any, key: str = "") -> dict[str, Any]:
    if isinstance(value, dict) and "timestamp" not in value:
        return {
            flat_key: flat_value
            for name, item in value.items()
            for flat_key, flat_value in _flatten(
                item, f"{key}__{name}" if key else name
            ).items()
        }
    return {key: value["value"] if isinstance(value, dict) else value}


class _CombinedControlAdapter[
    S: CombinedValues,
    C: CombinedValues,
    P,
    M,
    CS: CombinedValues,
]:
    def __init__(
        self,
        controls: Mapping[str, Control[ThrsValues, ThrsValues, P, M, ThrsValues]],
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
            else control.control(sensors)
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
    def __init__(self, alarms: Mapping[str, BaseAlarms]):
        self._alarms = alarms

    def check(
        self,
        sensor_values: CombinedValues,
        control_values: CombinedValues,
        controller_state: CombinedValues,
    ) -> list[Any]:
        return [
            result
            for name, alarms in self._alarms.items()
            if (s := sensor_values.values.get(name)) is not None
            and (c := control_values.values.get(name)) is not None
            and (cs := controller_state.values.get(name)) is not None
            for result in alarms.check(s, c, cs)
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
        | Mapping[str, Control[Any, Any, Any, Any, Any]],
        alarms: BaseAlarms | Mapping[str, BaseAlarms],
    ):
        if isinstance(control, Mapping):
            combined_control = cast(Control, _CombinedControlAdapter(control))
            combined_alarms = cast(
                BaseAlarms,
                _CombinedAlarmsAdapter(cast(Mapping[str, BaseAlarms], alarms)),
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
        sensor_values, control_values, controller_state = self._tick(collector)
        # Controls return their internal values; a copy keeps test mutations out of them.
        return sensor_values, deepcopy(control_values), deepcopy(controller_state)

    def _tick(self, collector: Collector | None) -> tuple[S, C, CS]:
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
            self._controller_state,
        )

        if collector is not None:
            collector.collect(
                {
                    **flatten_model_values(result.sensor_values, _all_keys),
                    **flatten_model_values(result.control_values, _all_keys),
                    **flatten_controller_state(self._controller_state),
                    **flatten_model_values(result.simulation_outputs, _all_keys),
                    **flatten_model_values(result.simulation_inputs, _all_keys),
                },
                str(self._control.mode),
                result.timestamp,
            )

        self._control_values, self._controller_state = self._control.control(
            result.sensor_values
        )
        self._modes.append(cast(M, self._control.mode))

        return result.sensor_values, self._control_values, self._controller_state

    def run(
        self, n_ticks: int, collector: Collector | None = None
    ) -> tuple[S | None, C, CS]:
        sensor_values = None
        for _ in range(n_ticks):
            sensor_values, *_ = self._tick(collector)
        # Only the last tick is returned, so copy once instead of on every tick.
        return (
            sensor_values,
            deepcopy(self._control_values),
            deepcopy(self._controller_state),
        )

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
