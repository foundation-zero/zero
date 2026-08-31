from typing import Annotated

from thrs.input_output.base import ThrsValues, component_meta
from thrs.input_output.definitions import simulation
from thrs.input_output.definitions.system import AmcsControlMode
from thrs.input_output.modules.consumers import (
    ConsumersSimulationOutputs,
)
from thrs.input_output.modules.pcm import (
    PcmSimulationOutputs,
)
from thrs.input_output.modules.pvt import (
    PvtSimulationOutputs,
)
from thrs.input_output.modules.thrusters import (
    ThrustersSimulationOutputs,
)


class HighTemperatureSimulationInputs(ThrsValues):
    thrusters_thruster_aft: simulation.Thruster
    thrusters_thruster_fwd: simulation.Thruster
    thrusters_seawater_supply: simulation.Boundary
    thrusters_pcs: simulation.Pcs
    pvt_main_fwd: simulation.HeatSource
    pvt_main_aft: simulation.HeatSource
    pvt_owners: simulation.HeatSource
    pvt_seawater_supply: simulation.Boundary
    pcm_freshwater_supply: simulation.Boundary
    consumers_dhw_supply: simulation.Boundary
    consumers_adsorption_supply: simulation.Boundary
    mode: Annotated[AmcsControlMode, component_meta(included_in_fmu=False)]


class HighTemperatureSimulationOutputs(
    PcmSimulationOutputs,
    ConsumersSimulationOutputs,
    PvtSimulationOutputs,
    ThrustersSimulationOutputs,
):
    pass
