from datetime import UTC, datetime, timedelta

from pytest import fixture

from thrs.control.modules.consumers import (
    CONSUMERS_MODULE_DESCRIPTION,
)
from thrs.control.modules.pcm import PCM_MODULE_DESCRIPTION
from thrs.control.modules.pvt import PVT_MODULE_DESCRIPTION
from thrs.control.modules.thrusters import (
    THRUSTERS_MODULE_DESCRIPTION,
)
from thrs.input_output.base import Stamped
from thrs.input_output.definitions.simulation import (
    Boundary,
    HeatSource,
    Pcs,
    Thruster,
)
from thrs.input_output.definitions.system import AmcsControlMode, ControlMode
from thrs.input_output.definitions.units import PcsMode
from thrs.input_output.modules.consumers import ConsumersSensorValues
from thrs.input_output.modules.high_temperature import (
    HighTemperatureSimulationInputs,
    HighTemperatureSimulationOutputs,
)
from thrs.input_output.modules.pcm import PcmSensorValues
from thrs.input_output.modules.pvt import PvtSensorValues
from thrs.input_output.modules.thrusters import ThrustersSensorValues
from thrs.orchestration.module import ModuleDescription
from thrs.orchestration.simulation import Simulation
from thrs.simulation.fmu import Fmu
from thrs.simulation.models.fmu_paths import high_temperature_path


@fixture
def simulation_inputs():
    return HighTemperatureSimulationInputs(
        thrusters_thruster_aft=Thruster(
            heat_flow=Stamped.stamp(9000), active=Stamped.stamp(True)
        ),
        thrusters_thruster_fwd=Thruster(
            heat_flow=Stamped.stamp(4300), active=Stamped.stamp(True)
        ),
        thrusters_seawater_supply=Boundary(
            temperature=Stamped.stamp(32), flow=Stamped.stamp(64)
        ),
        thrusters_pcs=Pcs(mode=Stamped.stamp(PcsMode.PROPULSION)),
        pvt_main_fwd=HeatSource(heat_flow=Stamped.stamp(16000)),
        pvt_main_aft=HeatSource(heat_flow=Stamped.stamp(16000)),
        pvt_owners=HeatSource(heat_flow=Stamped.stamp(8000)),
        pvt_seawater_supply=Boundary(
            temperature=Stamped.stamp(32), flow=Stamped.stamp(64)
        ),
        pcm_freshwater_supply=Boundary(
            temperature=Stamped.stamp(40), flow=Stamped.stamp(0)
        ),
        consumers_adsorption_supply=Boundary(
            temperature=Stamped.stamp(60),
            flow=Stamped.stamp(42),
        ),
        consumers_dhw_supply=Boundary(
            temperature=Stamped.stamp(40),
            flow=Stamped.stamp(29),
        ),
        consumers_mode=AmcsControlMode(mode=Stamped.stamp(ControlMode.EXTERNAL)),
        pcm_mode=AmcsControlMode(mode=Stamped.stamp(ControlMode.EXTERNAL)),
        pvt_mode=AmcsControlMode(mode=Stamped.stamp(ControlMode.EXTERNAL)),
        thrusters_mode=AmcsControlMode(mode=Stamped.stamp(ControlMode.EXTERNAL)),
    )


@fixture
def modules() -> dict[str, ModuleDescription]:
    return {
        "thrusters": THRUSTERS_MODULE_DESCRIPTION,
        "pvt": PVT_MODULE_DESCRIPTION,
        "pcm": PCM_MODULE_DESCRIPTION,
        "consumers": CONSUMERS_MODULE_DESCRIPTION,
    }


@fixture
def simulation(simulation_inputs):
    with Fmu(high_temperature_path) as fmu:
        yield Simulation(
            {
                "thrusters": ThrustersSensorValues,
                "pvt": PvtSensorValues,
                "pcm": PcmSensorValues,
                "consumers": ConsumersSensorValues,
            },
            HighTemperatureSimulationOutputs,
            fmu,
            simulation_inputs,
            datetime.now(UTC),
            timedelta(seconds=1),
        )
