from typing import Annotated

from thrs.input_output.base import SimulationInputs, component_meta
from thrs.input_output.definitions import simulation
from thrs.input_output.modules.adsorption import (
    AdsorptionControlValues,
    AdsorptionSensorValues,
    AdsorptionSimulationInputs,
    AdsorptionSimulationOutputs,
)
from thrs.input_output.modules.consumers import (
    ConsumersControlValues,
    ConsumersSensorValues,
    ConsumersSimulationOutputs,
)
from thrs.input_output.modules.dc import (
    DcControlValues,
    DcSensorValues,
    DcSimulationInputs,
    DcSimulationOutputs,
)
from thrs.input_output.modules.dhw import (
    DhwControlValues,
    DhwSensorValues,
    DhwSimulationInputs,
    DhwSimulationOutputs,
)
from thrs.input_output.modules.drives import (
    DrivesControlValues,
    DrivesSensorValues,
    DrivesSimulationInputs,
    DrivesSimulationOutputs,
)
from thrs.input_output.modules.high_temperature import (
    HighTemperatureSimulationInputs,
    HighTemperatureSimulationOutputs,
)
from thrs.input_output.modules.pcm import (
    PcmControlValues,
    PcmSensorValues,
    PcmSimulationOutputs,
)
from thrs.input_output.modules.pvt import (
    PvtControlValues,
    PvtSensorValues,
    PvtSimulationOutputs,
)
from thrs.input_output.modules.thrusters import (
    ThrustersControlValues,
    ThrustersSensorValues,
    ThrustersSimulationOutputs,
)
from thrs.simulation.cosimulation import (
    CoSimulationMaster,
    CoSimulationParticipant,
    Coupling,
)
from thrs.simulation.fmu import Fmu
from thrs.simulation.models.fmu_paths import (
    adsorption_path,
    dc_path,
    dhw_path,
    drives_path,
    high_temperature_path,
)


class ThrsSimulationInputs(SimulationInputs):
    # thrusters
    thrusters_thruster_aft: simulation.Thruster
    thrusters_thruster_fwd: simulation.Thruster
    thrusters_seawater_supply: simulation.Boundary
    thrusters_pcs: simulation.Pcs
    # pvt
    pvt_main_fwd: simulation.HeatSource
    pvt_main_aft: simulation.HeatSource
    pvt_owners: simulation.HeatSource
    pvt_seawater_supply: simulation.Boundary
    # pcm
    pcm_freshwater_supply: simulation.Boundary
    # adsorption
    adsorption_cooling_supply: simulation.TemperatureBoundary
    adsorption_seawater_supply: simulation.Boundary
    adsorption_available_hot_temperature: Annotated[
        simulation.TemperatureBoundary, component_meta(included_in_fmu=False)
    ]
    adsorption_available_cold_temperature: Annotated[
        simulation.TemperatureBoundary, component_meta(included_in_fmu=False)
    ]
    adsorption_available_seawater_temperature: Annotated[
        simulation.TemperatureBoundary, component_meta(included_in_fmu=False)
    ]
    adsorption_chiller: Annotated[
        simulation.AdsorptionChiller, component_meta(included_in_fmu=False)
    ]
    # dhw
    dhw_freshwater_supply: simulation.OverpressureTemperatureBoundary
    dhw_hvac_exchanger: simulation.HvacExchanger
    dhw_seawater_supply: simulation.TemperatureBoundary
    dhw_hotwater_demand: simulation.FlowBoundary
    # dc
    dc_brightloop_fwd1: simulation.Converter
    dc_brightloop_fwd2: simulation.Converter
    dc_ugrid1: simulation.Converter
    dc_ugrid2: simulation.Converter
    dc_brightloop_aft1: simulation.Converter
    dc_brightloop_aft2: simulation.Converter
    dc_brightloop_aft3: simulation.Converter
    dc_brightloop_aft4: simulation.Converter
    dc_seawater_supply: simulation.Boundary
    # drives
    drives_oil_cooler_aft: simulation.HeatSource
    drives_oil_cooler_fwd: simulation.HeatSource
    drives_propdrive_aft1: simulation.PropulsionDrive
    drives_propdrive_aft2: simulation.PropulsionDrive
    drives_propdrive_fwd1: simulation.PropulsionDrive
    drives_propdrive_fwd2: simulation.PropulsionDrive
    drives_shorepower: simulation.Converter
    drives_seawater_supply: simulation.Boundary


class ThrsSimulationOutputs(
    ThrustersSimulationOutputs,
    PvtSimulationOutputs,
    PcmSimulationOutputs,
    ConsumersSimulationOutputs,
    AdsorptionSimulationOutputs,
    DhwSimulationOutputs,
    DcSimulationOutputs,
    DrivesSimulationOutputs,
):
    pass


participants = [
    CoSimulationParticipant(
        lambda: Fmu(high_temperature_path),
        [
            ThrustersSensorValues,
            PvtSensorValues,
            PcmSensorValues,
            ConsumersSensorValues,
        ],
        [
            ThrustersControlValues,
            PvtControlValues,
            PcmControlValues,
            ConsumersControlValues,
        ],
        HighTemperatureSimulationInputs,
        HighTemperatureSimulationOutputs,
        [
            # dhw to consumers
            Coupling(
                "dhw_consumers_exchanger", "flow", "consumers_dhw_supply", "flow", 0.0
            ),
            Coupling(
                "dhw_consumers_exchanger",
                "temperature_supply",
                "consumers_dhw_supply",
                "temperature",
                30.0,
            ),
            # adsorption to consumers
            Coupling(
                "adsorption_consumers_exchanger",
                "flow",
                "consumers_adsorption_supply",
                "flow",
                0.0,
            ),
            Coupling(
                "adsorption_consumers_exchanger",
                "temperature_supply",
                "consumers_adsorption_supply",
                "temperature",
                30.0,
            ),
        ],
    ),
    CoSimulationParticipant(
        lambda: Fmu(adsorption_path),
        [AdsorptionSensorValues],
        [AdsorptionControlValues],
        AdsorptionSimulationInputs,
        AdsorptionSimulationOutputs,
        [
            # consumers to adsorption
            Coupling(
                "consumers_adsorption_exchanger",
                "flow",
                "adsorption_consumers_supply",
                "flow",
                0.0,
            ),
            Coupling(
                "consumers_adsorption_exchanger",
                "temperature_supply",
                "adsorption_consumers_supply",
                "temperature",
                30.0,
            ),
            # dhw to adsorption
            Coupling(
                "dhw_adsorption_exchanger", "flow", "adsorption_dhw_supply", "flow", 0.0
            ),
            Coupling(
                "dhw_adsorption_exchanger",
                "temperature_supply",
                "adsorption_dhw_supply",
                "temperature",
                30.0,
            ),
        ],
    ),
    CoSimulationParticipant(
        lambda: Fmu(dhw_path),
        [DhwSensorValues],
        [DhwControlValues],
        DhwSimulationInputs,
        DhwSimulationOutputs,
        [
            # consumers to dhw
            Coupling(
                "consumers_dhw_exchanger", "flow", "dhw_consumers_supply", "flow", 0.0
            ),
            Coupling(
                "consumers_dhw_exchanger",
                "temperature_supply",
                "dhw_consumers_supply",
                "temperature",
                30.0,
            ),
            # adsorption to dhw
            Coupling(
                "adsorption_dhw_exchanger", "flow", "dhw_adsorption_supply", "flow", 0.0
            ),
            Coupling(
                "adsorption_dhw_exchanger",
                "temperature_supply",
                "dhw_adsorption_supply",
                "temperature",
                30.0,
            ),
            # dc to dhw
            Coupling("dc_dhw_exchanger", "flow", "dhw_dc_supply", "flow", 0.0),
            Coupling(
                "dc_dhw_exchanger",
                "temperature_supply",
                "dhw_dc_supply",
                "temperature",
                30.0,
            ),
            # drives to dhw
            Coupling("drives_dhw_exchanger", "flow", "dhw_drives_supply", "flow", 0.0),
            Coupling(
                "drives_dhw_exchanger",
                "temperature_supply",
                "dhw_drives_supply",
                "temperature",
                30.0,
            ),
        ],
    ),
    CoSimulationParticipant(
        lambda: Fmu(dc_path),
        [DcSensorValues],
        [DcControlValues],
        DcSimulationInputs,
        DcSimulationOutputs,
        [
            # dhw to dc
            Coupling("dhw_dc_exchanger", "flow", "dc_dhw_supply", "flow", 0.0),
            Coupling(
                "dhw_dc_exchanger",
                "temperature_supply",
                "dc_dhw_supply",
                "temperature",
                30.0,
            ),
        ],
    ),
    CoSimulationParticipant(
        lambda: Fmu(drives_path),
        [DrivesSensorValues],
        [DrivesControlValues],
        DrivesSimulationInputs,
        DrivesSimulationOutputs,
        [
            # dhw to drives
            Coupling("dhw_drives_exchanger", "flow", "drives_dhw_supply", "flow", 0.0),
            Coupling(
                "dhw_drives_exchanger",
                "temperature_supply",
                "drives_dhw_supply",
                "temperature",
                30.0,
            ),
        ],
    ),
]

thrs_cosimulation = CoSimulationMaster(participants)
