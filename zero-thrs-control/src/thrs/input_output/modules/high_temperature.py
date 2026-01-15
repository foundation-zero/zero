from thrs.input_output.base import SimulationInputs
from thrs.input_output.definitions import simulation
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


class HighTemperatureSimulationInputs(SimulationInputs):
    thrusters_aft: simulation.Thruster
    thrusters_fwd: simulation.Thruster
    thrusters_seawater_supply: simulation.Boundary
    thrusters_pcs: simulation.Pcs
    pvt_main_fwd: simulation.HeatSource
    pvt_main_aft: simulation.HeatSource
    pvt_owners: simulation.HeatSource
    pvt_seawater_supply: simulation.Boundary
    pcm_freshwater_supply: simulation.Boundary
    consumers_fahrenheit_supply: simulation.ExchangerBoundary
    consumers_boosting_supply: simulation.ExchangerBoundary


class HighTemperatureSimulationOutputs(
    PcmSimulationOutputs,
    ConsumersSimulationOutputs,
    PvtSimulationOutputs,
    ThrustersSimulationOutputs,
):
    pass
