from collections.abc import Callable
from datetime import UTC, datetime
from typing import Annotated

from thrs.classes.control import Control
from thrs.control.state import ControlState
from thrs.input_output.alarms import BaseAlarms
from thrs.input_output.base import Stamped, ThrsValues, component_meta
from thrs.input_output.definitions.sensor import FlowSensor
from thrs.input_output.definitions.system import AmcsControlMode, ControlMode
from thrs.input_output.root_types import AmcsModeSensorValues, AmcsWatchdogControlValues
from thrs.orchestration.simulation import Simulation, SimulationResult


class SimpleInOut(AmcsModeSensorValues, AmcsWatchdogControlValues):
    go_with_the: FlowSensor

    mode: Annotated[AmcsControlMode, component_meta(included_in_fmu=False)] = (
        AmcsControlMode(mode=Stamped.stamp(ControlMode.EXTERNAL))
    )


class SimpleSimulationInputs(ThrsValues):
    pass


class SimpleSimulationOutputs(ThrsValues):
    pass


class SimpleSimulation(
    Simulation[
        SimpleInOut, SimpleInOut, SimpleSimulationInputs, SimpleSimulationOutputs
    ]
):
    def __init__(self, start_time):
        self.controls = []
        self._start_time = start_time

    async def start(self):
        pass

    def tick(
        self, control_values: SimpleInOut
    ) -> SimulationResult[
        SimpleInOut, SimpleInOut, SimpleSimulationInputs, SimpleSimulationOutputs
    ]:
        self.controls.append(control_values)
        return SimulationResult(
            timestamp=datetime.now(UTC),
            sensor_values=control_values,
            control_values=control_values,
            simulation_outputs=SimpleSimulationOutputs(),
            simulation_inputs=SimpleSimulationInputs(),
            raw={},
        )

    @property
    def start_time(self):
        return self._start_time

    def time(self):
        return datetime.now(UTC)


class SimpleParameters(ThrsValues):
    pass


class SimpleMode(ThrsValues):
    pass


class SimpleControllerState(ControlState[SimpleInOut, SimpleParameters, SimpleMode]):
    pass


class SimpleControl(
    Control[
        SimpleInOut, SimpleInOut, SimpleParameters, SimpleMode, SimpleControllerState
    ]
):
    def __init__(
        self,
        parameters: SimpleParameters,
        time_fn: Callable[[], datetime],
    ):
        self._parameters = parameters
        self._time = time_fn
        self._current_values: SimpleInOut = SimpleInOut.zero()

    def initial(self) -> tuple[SimpleInOut, SimpleControllerState]:
        return (
            SimpleInOut.zero(),
            SimpleControllerState(parameters=SimpleParameters()),
        )

    def control(
        self, sensor_values: SimpleInOut
    ) -> tuple[SimpleInOut, SimpleControllerState]:
        return (
            sensor_values,
            SimpleControllerState(parameters=self._parameters, control_mode=self.mode),
        )

    @staticmethod
    def modes() -> list[str]:
        return []

    @staticmethod
    def initial_mode() -> str:
        return ""

    @property
    def mode(self) -> SimpleMode | None:
        return SimpleMode()

    @property
    def parameters(self) -> SimpleParameters:
        return self._parameters

    def update_parameters(self, parameters: SimpleParameters):
        self._parameters = parameters

    def update_controls(self, control_values: SimpleInOut) -> None:
        self._current_values.update_in_place(control_values)

    def reset(self) -> None:
        self._current_values = SimpleInOut.zero()


def simple_controller_state() -> SimpleControllerState:
    return SimpleControllerState(parameters=SimpleParameters())


def simple_advisory_values(flow: float) -> SimpleInOut:
    return SimpleInOut(
        go_with_the=FlowSensor(
            flow=Stamped.stamp(flow), temperature=Stamped.stamp(20.0)
        ),
        mode=AmcsControlMode(mode=Stamped.stamp(ControlMode.EXTERNAL)),
    )


def simple_non_advisory_values(
    flow: float, mode: ControlMode = ControlMode.MANUAL
) -> SimpleInOut:
    return SimpleInOut(
        go_with_the=FlowSensor(
            flow=Stamped.stamp(flow), temperature=Stamped.stamp(20.0)
        ),
        mode=AmcsControlMode(mode=Stamped.stamp(mode)),
    )


def simple_control_values(flow: float) -> SimpleInOut:
    return SimpleInOut(
        go_with_the=FlowSensor(
            flow=Stamped.stamp(flow), temperature=Stamped.stamp(20.0)
        )
    )


class SimpleAlarms(BaseAlarms[SimpleInOut, SimpleInOut, SimpleControllerState]):
    pass
