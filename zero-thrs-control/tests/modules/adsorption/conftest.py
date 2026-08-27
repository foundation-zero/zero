from datetime import UTC, datetime, timedelta

from pytest import fixture

from thrs.classes.machine_state_logger import MachineStateLoggingServiceNoop
from thrs.control.modules.adsorption import AdsorptionControl, AdsorptionParameters
from thrs.input_output.base import Stamped
from thrs.input_output.definitions.simulation import (
    AdsorptionChiller,
    Boundary,
    TemperatureBoundary,
)
from thrs.input_output.definitions.system import AmcsControlMode, ControlMode
from thrs.input_output.modules.adsorption import (
    AdsorptionSensorValues,
    AdsorptionSimulationInputs,
    AdsorptionSimulationOutputs,
)
from thrs.orchestration.simulation import Simulation
from thrs.simulation.fmu import Fmu
from thrs.simulation.models.fmu_paths import adsorption_path


@fixture
def simulation_inputs():
    return AdsorptionSimulationInputs(
        adsorption_cooling_supply=TemperatureBoundary(temperature=Stamped.stamp(20.0)),
        adsorption_seawater_supply=Boundary(
            temperature=Stamped.stamp(32.0), flow=Stamped.stamp(64.0)
        ),
        adsorption_available_cold_temperature=TemperatureBoundary(
            temperature=Stamped.stamp(20.0)
        ),
        adsorption_available_hot_temperature=TemperatureBoundary(
            temperature=Stamped.stamp(65.0)
        ),
        adsorption_available_seawater_temperature=TemperatureBoundary(
            temperature=Stamped.stamp(30.0)
        ),
        adsorption_chiller=AdsorptionChiller(free_cooling=Stamped.stamp(False)),
        adsorption_consumers_supply=Boundary(
            temperature=Stamped.stamp(60.0), flow=Stamped.stamp(42.0)
        ),
        adsorption_dhw_supply=Boundary(
            temperature=Stamped.stamp(40.0), flow=Stamped.stamp(45.0)
        ),
        adsorption_mode=AmcsControlMode(mode=Stamped.stamp(ControlMode.EXTERNAL)),
    )


@fixture
def control(simulation):
    return AdsorptionControl(
        AdsorptionParameters(), simulation.time, MachineStateLoggingServiceNoop()
    )


@fixture
def simulation(simulation_inputs):
    with Fmu(adsorption_path) as fmu:
        yield Simulation(
            AdsorptionSensorValues,
            AdsorptionSimulationOutputs,
            fmu,
            simulation_inputs,
            datetime.now(UTC),
            timedelta(seconds=1),
        )
