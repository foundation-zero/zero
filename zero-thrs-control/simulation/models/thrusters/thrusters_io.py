from input_output.units import Celsius, LMin, Watt
from simulation.input_output import SimulationInputs, SimulationOutputs


class ThrustersSimulationInputs(SimulationInputs):
    aft_heat_flow: Watt
    fwd_heat_flow: Watt
    seawater_supply_temperature: Celsius
    seawater_supply_flow: LMin
    module_supply_temperature: Celsius


class TrustersSimulationOutputs(SimulationOutputs):
    seawater_supply_temperature: Celsius
    seawater_supply_flow: LMin
    seawater_return_temperature: Celsius
    module_supply_flow: LMin
    module_return_temperature: Celsius
    module_return_flow: LMin
