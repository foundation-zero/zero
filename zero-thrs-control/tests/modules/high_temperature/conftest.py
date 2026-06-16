from datetime import datetime, timedelta

from pytest import fixture

from thrs.control.modules.consumers import (
    CONSUMERS_MODULE_DESCRIPTION,
    ConsumersParameters,
)
from thrs.control.modules.pcm import PCM_MODULE_DESCRIPTION, PcmParameters
from thrs.control.modules.pvt import PVT_MODULE_DESCRIPTION, PvtParameters
from thrs.control.modules.thrusters import (
    THRUSTERS_MODULE_DESCRIPTION,
    ThrustersParameters,
)
from thrs.input_output.base import CombinedValues, Stamped
from thrs.input_output.definitions.simulation import (
    Boundary,
    HeatSource,
    Pcs,
    Thruster,
)
from thrs.input_output.definitions.units import PcsMode
from thrs.input_output.modules.high_temperature import (
    HighTemperatureSimulationInputs,
    HighTemperatureSimulationOutputs,
)
from thrs.orchestration.module import CombinedModule
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
    )


@fixture
def module():
    return CombinedModule(
        {
            "thrusters": THRUSTERS_MODULE_DESCRIPTION,
            "pvt": PVT_MODULE_DESCRIPTION,
            "pcm": PCM_MODULE_DESCRIPTION,
            "consumers": CONSUMERS_MODULE_DESCRIPTION,
        },
        HighTemperatureSimulationInputs,
        HighTemperatureSimulationOutputs,
    )


@fixture
def control(module, simulation):
    return module.control(
        CombinedValues(
            {
                "thrusters": ThrustersParameters(),
                "pvt": PvtParameters(),
                "pcm": PcmParameters(),
                "consumers": ConsumersParameters(),
            }
        ),
        simulation.time,
    )


@fixture
def simulation(module, simulation_inputs):
    with Fmu(high_temperature_path) as fmu:
        yield Simulation(
            module.sensor_values_clss,
            module.simulation_outputs_cls,
            fmu,
            simulation_inputs,
            datetime.now(),
            timedelta(seconds=1),
        )
