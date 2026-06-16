from typing import Annotated, cast

from pydantic import computed_field

from thrs.input_output.base import SimulationInputs, Stamped, component_meta
from thrs.input_output.definitions import sensor, simulation
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
    adsorption_ht_supply: simulation.Boundary  # TODO: change to consumers
    adsorption_dhw_supply: simulation.Boundary
    dhw_drives_supply: simulation.Boundary
    dhw_dc_supply: simulation.Boundary
    dhw_adsorption_supply: simulation.Boundary
    dhw_ht_supply: simulation.Boundary  # TODO: change to consumers
    dhw_freshwater_supply: simulation.OverpressureTemperatureBoundary
    dhw_hvac_exchanger: simulation.HvacExchanger
    dhw_seawater_supply: simulation.TemperatureBoundary
    dhw_hotwater_demand: simulation.FlowBoundary

    @computed_field(
        json_schema_extra=component_meta(included_in_fmu=False).json_schema_extra
    )
    @property
    def drives_flow_recovery(self) -> sensor.FlowSensor:
        return sensor.FlowSensor(
            flow=cast(Stamped, self.dhw_drives_supply.flow),
            temperature=cast(Stamped, self.dhw_drives_supply.temperature),
        )

    @computed_field(
        json_schema_extra=component_meta(
            included_in_fmu=False,
        ).json_schema_extra
    )
    @property
    def drives_temperature_recovery(self) -> sensor.TemperatureSensor:
        return sensor.TemperatureSensor(
            temperature=cast(Stamped, self.dhw_drives_supply.temperature)
        )

    @computed_field(
        json_schema_extra=component_meta(
            included_in_fmu=False,
        ).json_schema_extra
    )
    @property
    def dc_flow_recovery(self) -> sensor.FlowSensor:
        return sensor.FlowSensor(
            flow=cast(Stamped, self.dhw_dc_supply.flow),
            temperature=cast(Stamped, self.dhw_dc_supply.temperature),
        )

    @computed_field(
        json_schema_extra=component_meta(
            included_in_fmu=False,
        ).json_schema_extra
    )
    @property
    def dc_temperature_recovery(self) -> sensor.TemperatureSensor:
        return sensor.TemperatureSensor(
            temperature=cast(Stamped, self.dhw_dc_supply.temperature)
        )

    @computed_field(
        json_schema_extra=component_meta(
            included_in_fmu=False,
        ).json_schema_extra
    )
    @property
    def consumers_flow_dhw(self) -> sensor.FlowSensor:
        return sensor.FlowSensor(
            flow=cast(Stamped, self.dhw_ht_supply.flow),
            temperature=cast(Stamped, self.dhw_ht_supply.temperature),
        )

    @computed_field(
        json_schema_extra=component_meta(
            included_in_fmu=False,
            component_type="temperature_sensor",
        ).json_schema_extra
    )
    @property
    def consumers_temperature_dhw_supply(self) -> sensor.TemperatureSensor:
        return sensor.TemperatureSensor(
            temperature=cast(Stamped, self.dhw_ht_supply.temperature)
        )

    @computed_field(
        json_schema_extra=component_meta(
            included_in_fmu=False,
            component_type="flow_sensor",
        ).json_schema_extra
    )
    @property
    def adsorption_flow_dhw(self) -> sensor.FlowSensor:
        return sensor.FlowSensor(
            flow=cast(Stamped, self.dhw_adsorption_supply.flow),
            temperature=cast(Stamped, self.dhw_adsorption_supply.temperature),
        )

    @computed_field(
        json_schema_extra=component_meta(
            included_in_fmu=False,
            component_type="temperature_sensor",
        ).json_schema_extra
    )
    @property
    def adsorption_temperature_waste_return(self) -> sensor.TemperatureSensor:
        return sensor.TemperatureSensor(
            temperature=cast(Stamped, self.dhw_adsorption_supply.temperature)
        )

    dc_brightloop_fwd1: simulation.Converter
    dc_brightloop_fwd2: simulation.Converter
    dc_ugrid1: simulation.Converter
    dc_ugrid2: simulation.Converter
    dc_brightloop_aft1: simulation.Converter
    dc_brightloop_aft2: simulation.Converter
    dc_brightloop_aft3: simulation.Converter
    dc_brightloop_aft4: simulation.Converter
    dc_seawater_supply: simulation.Boundary
    dc_dhw_supply: simulation.Boundary
    drives_oil_cooler_aft: simulation.HeatSource
    drives_oil_cooler_fwd: simulation.HeatSource
    drives_propdrive_aft1: simulation.PropulsionDrive
    drives_propdrive_aft2: simulation.PropulsionDrive
    drives_propdrive_fwd1: simulation.PropulsionDrive
    drives_propdrive_fwd2: simulation.PropulsionDrive
    drives_shorepower: simulation.Converter
    drives_seawater_supply: simulation.Boundary
    drives_dhw_supply: simulation.Boundary


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


couplings = [
    # consumers to dhw
    Coupling("consumers_flow_dhw", "flow", "dhw_adsorption_supply", "flow", 0.0),
    Coupling(
        "consumers_temperature_dhw_supply",
        "temperature",
        "dhw_ht_supply",
        "temperature",
        30.0,
    ),
    # dhw to consumers
    Coupling(
        "dhw_ht_supply", "flow", "consumers_dhw_supply", "flow", 0.0
    ),  # no datapoint here - depends on valve positions  #rename to consumers?
    Coupling(
        "dhw_ht_supply", "temperature", "consumers_dhw_supply", "temperature", 30.0
    ),  # no datapoint here - depends on valve positions  #rename to consumers?
    # consumers to adsorption
    Coupling("consumers_flow_adsorption", "flow", "adsorption_ht_supply", "flow", 0.0),
    Coupling(
        "consumers_temperature_adsorption_supply",
        "temperature",
        "adsorption_ht_supply",
        "temperature",
        30.0,
    ),
    # adsorption to consumers
    Coupling(
        "adsorption_flow_ht", "flow", "consumers_adsorption_supply", "flow", 0.0
    ),  # rename to ht to consumers?
    Coupling(
        "adsorption_temperature_ht_supply",
        "temperature",
        "consumers_adsorption_supply",
        "temperature",
        30.0,
    ),  # rename ht to consumers?
    # dhw to adsorption
    Coupling("dhw_flow_dc", "flow", "adsorption_dhw_supply", "flow", 0.0),
    Coupling(
        "dhw_temperature_freshwater_supply",
        "temperature",
        "adsorption_dhw_supply",
        "temperature",
        30.0,
    ),
    # adsorption to dhw
    Coupling("adsorption_flow_dhw", "flow", "dhw_adsorption_supply", "flow", 0.0),
    Coupling(
        "adsorption_temperature_waste_return",
        "temperature",
        "dhw_adsorption_supply",
        "temperature",
        30.0,
    ),
    # dhw to dc
    Coupling("dhw_flow_dc", "flow", "dc_dhw_supply", "flow", 0.0),
    Coupling(
        "dhw_temperature_hvac_exchanger_return",
        "temperature",
        "dc_dhw_supply",
        "temperature",
        30.0,
    ),
    # dc to dhw
    Coupling("dc_flow_recovery", "flow", "dhw_dc_supply", "flow", 0.0),
    Coupling(
        "dc_temperature_recovery", "temperature", "dhw_dc_supply", "temperature", 30.0
    ),
    # dhw to drives
    Coupling(
        "dhw_flow_drives", "flow", "drives_dhw_supply", "flow", 0.0
    ),  # no datapoint here - depends on valve positions
    Coupling(
        "dhw_temperature_freshwater_supply",
        "temperature",
        "drives_dhw_supply",
        "temperature",
        30.0,
    ),  # no datapoint here - depends on valve positions
    # drives to dhw
    Coupling("drives_flow_recovery", "flow", "dhw_drives_supply", "flow", 0.0),
    Coupling(
        "drives_temperature_recovery",
        "temperature",
        "dhw_drives_supply",
        "temperature",
        30.0,
    ),
]

participants = [
    CoSimulationParticipant(
        Fmu(high_temperature_path),
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
            Coupling("dhw_ht_supply", "flow", "consumers_dhw_supply", "flow", 0.0),
            Coupling(
                "dhw_ht_supply",
                "temperature",
                "consumers_dhw_supply",
                "temperature",
                30.0,
            ),
            Coupling(
                "consumers_flow_adsorption", "flow", "adsorption_ht_supply", "flow", 0.0
            ),
            Coupling(
                "consumers_temperature_adsorption_supply",
                "temperature",
                "adsorption_ht_supply",
                "temperature",
                30.0,
            ),
            # adsorption to consumers
            Coupling(
                "adsorption_flow_ht", "flow", "consumers_adsorption_supply", "flow", 0.0
            ),
            Coupling(
                "adsorption_temperature_ht_supply",
                "temperature",
                "consumers_adsorption_supply",
                "temperature",
                30.0,
            ),
        ],
    ),
    CoSimulationParticipant(
        Fmu(adsorption_path),
        [AdsorptionSensorValues],
        [AdsorptionControlValues],
        AdsorptionSimulationInputs,
        AdsorptionSimulationOutputs,
        [
            # consumers to adsorption
            Coupling(
                "consumers_flow_adsorption", "flow", "adsorption_ht_supply", "flow", 0.0
            ),
            Coupling(
                "consumers_temperature_adsorption_supply",
                "temperature",
                "adsorption_ht_supply",
                "temperature",
                30.0,
            ),
            # dhw to adsorption
            Coupling("dhw_flow_dc", "flow", "adsorption_dhw_supply", "flow", 0.0),
            Coupling(
                "dhw_temperature_freshwater_supply",
                "temperature",
                "adsorption_dhw_supply",
                "temperature",
                30.0,
            ),
        ],
    ),
    CoSimulationParticipant(
        Fmu(dhw_path),
        [DhwSensorValues],
        [DhwControlValues],
        DhwSimulationInputs,
        DhwSimulationOutputs,
        [
            # consumers to dhw
            Coupling(
                "consumers_flow_dhw", "flow", "dhw_adsorption_supply", "flow", 0.0
            ),
            Coupling(
                "consumers_temperature_dhw_supply",
                "temperature",
                "dhw_ht_supply",
                "temperature",
                30.0,
            ),
            # adsorption to dhw
            Coupling(
                "adsorption_flow_dhw", "flow", "dhw_adsorption_supply", "flow", 0.0
            ),
            Coupling(
                "adsorption_temperature_waste_return",
                "temperature",
                "dhw_adsorption_supply",
                "temperature",
                30.0,
            ),
            # dc to dhw
            Coupling("dc_flow_recovery", "flow", "dhw_dc_supply", "flow", 0.0),
            Coupling(
                "dc_temperature_recovery",
                "temperature",
                "dhw_dc_supply",
                "temperature",
                30.0,
            ),
            # drives to dhw
            Coupling("drives_flow_recovery", "flow", "dhw_drives_supply", "flow", 0.0),
            Coupling(
                "drives_temperature_recovery",
                "temperature",
                "dhw_drives_supply",
                "temperature",
                30.0,
            ),
        ],
    ),
    CoSimulationParticipant(
        Fmu(dc_path),
        [DcSensorValues],
        [DcControlValues],
        DcSimulationInputs,
        DcSimulationOutputs,
        [
            # dhw to dc
            Coupling("dhw_flow_dc", "flow", "dc_dhw_supply", "flow", 0.0),
            Coupling(
                "dhw_temperature_hvac_exchanger_return",
                "temperature",
                "dc_dhw_supply",
                "temperature",
                30.0,
            ),
        ],
    ),
    CoSimulationParticipant(
        Fmu(drives_path),
        [DrivesSensorValues],
        [DrivesControlValues],
        DrivesSimulationInputs,
        DrivesSimulationOutputs,
        [  # dhw to drives
            Coupling("dhw_flow_drives", "flow", "drives_dhw_supply", "flow", 0.0),
            Coupling(
                "dhw_temperature_freshwater_supply",
                "temperature",
                "drives_dhw_supply",
                "temperature",
                30.0,
            ),
        ],
    ),
]

thrs_cosimulation = CoSimulationMaster(participants)

# need to pass relevant sensorvalues and controlvalues at master level? (high temp doesn't have high temp and low temp values.. )
# do we need couplings per participant? or just pass a long list to the master
# need to deal with combinedmodule input mapping..? look up how the flatten was done for HighTemperatureModule
# OR should we move the cosimulation master to the Simulation level, and deal with teh inputs in the IOmapping?
