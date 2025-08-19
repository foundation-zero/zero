from input_output.base import SimulationInputs
from input_output.definitions import simulation
from input_output.modules.consumers import (
    ConsumersSensorValues,
    ConsumersControlValues,
    ConsumersSimulationOutputs,
)
from input_output.modules.pcm import (
    PcmControlValues,
    PcmSensorValues,
    PcmSimulationOutputs,
)
from input_output.modules.pvt import (
    PvtControlValues,
    PvtSensorValues,
    PvtSimulationOutputs,
)
from input_output.modules.thrusters import (
    ThrustersControlValues,
    ThrustersSensorValues,
    ThrustersSimulationOutputs,
)


class HighTemperatureSensorValues(
    PcmSensorValues, ConsumersSensorValues, PvtSensorValues, ThrustersSensorValues
):
    pass


class HighTemperatureControlValues(
    PcmControlValues, ConsumersControlValues, PvtControlValues, ThrustersControlValues
):
    pass


class HighTemperatureSimulationInputs(SimulationInputs):
    thrusters_aft: simulation.Thruster
    thrusters_fwd: simulation.Thruster
    thrusters_seawater_supply: simulation.Boundary
    thrusters_pcs: simulation.Pcs
    pvt_main_fwd: simulation.HeatSource
    pvt_main_aft: simulation.HeatSource
    pvt_owners: simulation.HeatSource
    pvt_pump_failure_switch_main_fwd: simulation.ValvePosition
    pvt_pump_failure_switch_main_aft: simulation.ValvePosition
    pvt_pump_failure_switch_owners: simulation.ValvePosition
    pvt_seawater_supply: simulation.Boundary
    pcm_freshwater_supply: simulation.Boundary
    consumers_fahrenheit_supply: simulation.Boundary
    consumers_boosting_supply: simulation.Boundary


class HighTemperatureSimulationOutputs(
    PcmSimulationOutputs,
    ConsumersSimulationOutputs,
    PvtSimulationOutputs,
    ThrustersSimulationOutputs,
):
    pass
