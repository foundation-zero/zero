from input_output.units import Celsius, LMin, Watt
from simulation.environmentals import Environmentals


class ThrustersEnvironmentals(Environmentals):
    aft_heat_flow: Watt
    fwd_heat_flow: Watt
    seawater_temperature: Celsius
    seawater_flow: LMin
    module_inflow_temperature: Celsius
