from datetime import UTC, datetime, timedelta
from types import TracebackType
from typing import Any, Self

from pytest import fixture

from tests.helpers.simulation_runner import SimulationTestRunner
from thrs.classes.machine_state_logger import MachineStateLoggingServiceNoop
from thrs.control.modules.pcm import (
    PcmAlarms,
    PcmControl,
    PcmControllerState,
    PcmControlMode,
    PcmParameters,
)
from thrs.input_output.base import Stamped
from thrs.input_output.definitions.control import Valve
from thrs.input_output.definitions.simulation import Boundary, TemperatureBoundary
from thrs.input_output.definitions.system import AmcsControlMode, ControlMode
from thrs.input_output.modules.pcm import (
    PcmControlValues,
    PcmSensorValues,
    PcmSimulationInputs,
    PcmSimulationOutputs,
)
from thrs.orchestration.simulation import Simulation
from thrs.simulation.fmu import Fmu, FmuLike
from thrs.simulation.models.fmu_paths import pcm_path

type PcmSimulation = Simulation[
    PcmSensorValues,
    PcmControlValues,
    PcmSimulationInputs,
    PcmSimulationOutputs,
]

type PcmRunner = SimulationTestRunner[
    PcmSensorValues,
    PcmControlValues,
    PcmSimulationInputs,
    PcmSimulationOutputs,
    PcmParameters,
    PcmControlMode,
    PcmControllerState,
]


class _ThrottledConsumersSwitch:
    """Limits the consumers switch opening the FMU sees while charging.

    The FMU has no counterpressure on the consumers side, so with the switch open the
    producers' flow bypasses the modules. Throttling it stands in for that
    counterpressure, while the control values keep what the control commanded.
    """

    _OPENING: float = 0.2

    def __init__(self, fmu: FmuLike) -> None:
        self._fmu = fmu

    def tick(self, inputs: dict[str, Any], duration: timedelta) -> dict[str, Any]:
        charging = inputs["pcm_switch_charging_supply__setpoint__ratio"] == Valve.OPEN
        throttled_inputs = (
            inputs
            | {
                "pcm_switch_consumers__setpoint__ratio": min(
                    inputs["pcm_switch_consumers__setpoint__ratio"], self._OPENING
                )
            }
            if charging
            else inputs
        )
        return self._fmu.tick(throttled_inputs, duration)

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        type_: type[BaseException] | None,
        value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        return self._fmu.__exit__(type_, value, traceback)

    @property
    def solver_time(self) -> float:
        return self._fmu.solver_time


@fixture
def control(simulation):
    return PcmControl(
        PcmParameters(), simulation.time, MachineStateLoggingServiceNoop()
    )


@fixture
def simulation_inputs():
    return PcmSimulationInputs(
        pcm_thrusters_supply=Boundary(
            temperature=Stamped.stamp(70), flow=Stamped.stamp(15)
        ),
        pcm_consumers_supply=TemperatureBoundary(temperature=Stamped.stamp(60)),
        pcm_freshwater_supply=Boundary(
            temperature=Stamped.stamp(40), flow=Stamped.stamp(0)
        ),
        pcm_pvt_supply=Boundary(temperature=Stamped.stamp(70), flow=Stamped.stamp(30)),
        mode=AmcsControlMode(mode=Stamped.stamp(ControlMode.EXTERNAL)),
    )


@fixture
def simulation(simulation_inputs):
    with Fmu(pcm_path) as fmu:
        yield Simulation(
            PcmSensorValues,
            PcmSimulationOutputs,
            _ThrottledConsumersSwitch(fmu),
            simulation_inputs,
            datetime.now(UTC),
            timedelta(seconds=1),
        )


@fixture
def alarms() -> PcmAlarms:
    return PcmAlarms()


@fixture
def runner(
    control: PcmControl,
    simulation: PcmSimulation,
    simulation_inputs: PcmSimulationInputs,
    alarms: PcmAlarms,
) -> PcmRunner:
    return SimulationTestRunner(simulation, simulation_inputs, control, alarms)
