from typing import Annotated

from pydantic import computed_field

from thrs.input_output.base import Stamped, ThrsValues, component_meta, computed_meta
from thrs.input_output.definitions import sensor, simulation
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

    @computed_field(json_schema_extra=computed_meta(included_in_fmu=False))
    @property
    def freshwater_temperature_pcm_supply(self) -> sensor.TemperatureSensor:
        return sensor.TemperatureSensor(
            temperature=self.pcm_freshwater_supply.temperature
        )

    @computed_field(
        json_schema_extra=computed_meta(
            included_in_fmu=False, component_type="pyranometer"
        )
    )
    @property
    def pvt_pyranometer_ps(self) -> sensor.Pyranometer:
        return sensor.Pyranometer(irradiance=Stamped.stamp(0))

    @computed_field(
        json_schema_extra=computed_meta(
            included_in_fmu=False, component_type="pyranometer"
        )
    )
    @property
    def pvt_pyranometer_sb(self) -> sensor.Pyranometer:
        return sensor.Pyranometer(irradiance=Stamped.stamp(0))

    @computed_field(json_schema_extra=computed_meta(included_in_fmu=False))
    @property
    def pcm_temperature_dhw_supply(self) -> sensor.TemperatureSensor:
        return sensor.TemperatureSensor(temperature=Stamped.stamp(0))  # TODO Fix this


class HighTemperatureSimulationOutputs(
    PcmSimulationOutputs,
    ConsumersSimulationOutputs,
    PvtSimulationOutputs,
    ThrustersSimulationOutputs,
):
    pass
