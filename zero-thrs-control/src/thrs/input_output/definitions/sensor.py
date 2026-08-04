from typing import Annotated, Self

from pydantic import ConfigDict, Field, computed_field
from pydantic.alias_generators import to_pascal

from thrs.input_output.base import Stamped, ThrsValues
from thrs.input_output.definitions import control
from thrs.input_output.definitions.units import (
    Bar,
    Celsius,
    Charged,
    DeltaT,
    Empty,
    Hz,
    Liter,
    LMin,
    NoError,
    OnOff,
    Operating,
    OptionalCelsius,
    PcsMode,
    Ratio,
    Seconds,
    Watt,
)
from thrs.utils.string import hyphenize


class FlowSensor(ThrsValues):
    flow: Stamped[LMin]
    temperature: Stamped[Celsius]


class Pump(ThrsValues):
    speed: Stamped[Hz]
    op_time: Stamped[Seconds]
    flow: Stamped[LMin]


class TemperatureSensor(ThrsValues):
    temperature: Stamped[Celsius]


class LevelSensor(ThrsValues):
    level: Stamped[Liter]


class CalculatedTemperature(ThrsValues):
    temperature: Stamped[OptionalCelsius]

    @classmethod
    def from_max_temperature(cls, sensors: list[TemperatureSensor]):
        max_sensor = max(sensors, key=lambda sensor: sensor.temperature.value)

        return CalculatedTemperature(
            temperature=Stamped(
                value=max_sensor.temperature.value,
                timestamp=max_sensor.temperature.timestamp,
            )
        )


class CalculatedFlow(ThrsValues):
    flow: Stamped[LMin]


class TemperatureDelta(ThrsValues):
    delta_t: Stamped[DeltaT]

    @classmethod
    def from_temperature_sensors(
        cls, temperature_supply: Stamped[Celsius], temperature_return: Stamped[Celsius]
    ) -> Self:
        delta_t = Stamped.combine(
            temperature_supply,
            temperature_return,
            value=temperature_return.value - temperature_supply.value,
        )
        return cls(delta_t=delta_t)


class HeatTransferDevice(ThrsValues):
    delta_t: Stamped[DeltaT]
    heat: Stamped[Watt]

    @classmethod
    def from_sensors(
        cls,
        temperature_supply: Stamped[Celsius],
        temperature_return: Stamped[Celsius],
        flow: Stamped[LMin],
        heat_transfer_conversion: float,
    ) -> Self:
        delta_t = Stamped.combine(
            temperature_supply,
            temperature_return,
            value=temperature_return.value - temperature_supply.value,
        )
        heat = Stamped.combine(
            delta_t, flow, value=flow.value * delta_t.value * heat_transfer_conversion
        )
        return cls(delta_t=delta_t, heat=heat)


class HvacExchanger(HeatTransferDevice):
    pass


class HeatPump(HeatTransferDevice):
    pass


class HeatExchanger(HeatTransferDevice):
    pass


class Valve(ThrsValues):
    model_config = ConfigDict(
        alias_generator=hyphenize,
        use_enum_values=True,
        validate_by_name=True,
    )

    position_rel: Stamped[Ratio]


def valves_open_closed(open_valves: list[Valve], closed_valves: list[Valve]) -> bool:
    return all(
        valve.position_rel.value == control.Valve.OPEN for valve in open_valves
    ) and all(
        valve.position_rel.value < (control.Valve.CLOSED + 0.01)
        for valve in closed_valves
    )


class PressureSensor(ThrsValues):
    pressure: Stamped[Bar]


class Thruster(ThrsValues):
    active: Annotated[Stamped[OnOff], Field(alias="LeverNotInZero")]


class PropulsionDrive(ThrsValues):
    active: Stamped[OnOff]


class ShorePowerConverter(ThrsValues):
    active: Stamped[OnOff]


class Brightloop(ThrsValues):
    active: Stamped[OnOff]


class Ugrid(ThrsValues):
    active: Annotated[Stamped[OnOff], Field(alias="ENABLE")]


class Pcs(ThrsValues):
    model_config = ConfigDict(
        alias_generator=to_pascal,
        use_enum_values=True,
        validate_by_name=True,
    )

    prop_mode_select_aft_thruster: Stamped[bool]
    man_mode_select_aft_thruster: Stamped[bool]
    reg_mode_select_aft_thruster: Stamped[bool]
    prop_mode_select_fwd_thruster: Stamped[bool]
    man_mode_select_fwd_thruster: Stamped[bool]
    reg_mode_select_fwd_thruster: Stamped[bool]

    @computed_field()
    @property
    def mode(self) -> Stamped[PcsMode]:

        return Stamped.combine(
            self.man_mode_select_aft_thruster,
            self.reg_mode_select_aft_thruster,
            self.prop_mode_select_aft_thruster,
            self.man_mode_select_fwd_thruster,
            self.reg_mode_select_fwd_thruster,
            self.prop_mode_select_fwd_thruster,
            value=(
                PcsMode.MANEUVERING
                if self.man_mode_select_aft_thruster.value
                or self.man_mode_select_fwd_thruster.value
                else (
                    PcsMode.REGENERATION
                    if self.reg_mode_select_aft_thruster.value
                    or self.reg_mode_select_fwd_thruster.value
                    else (
                        PcsMode.PROPULSION
                        if self.prop_mode_select_aft_thruster.value
                        or self.prop_mode_select_fwd_thruster.value
                        else PcsMode.OFF
                    )
                )
            ),
        )


class Pcm(ThrsValues):
    charged: Stamped[Charged]


class LevelSwitch(ThrsValues):
    empty: Annotated[Stamped[Empty], Field(alias="HIGHLEV")]


# Leaving in commented fields as we might need these IOs in the future, but need to accomodate for them in the SimulationInputs or in the FMU first as they are currently not part of the FMU. For now, they are to be used as reference for the IOs that we might want to add in the future.
class AdsorptionChiller(ThrsValues):
    operating: Stamped[Operating]
    no_error: Stamped[NoError]
    free_cooling: Stamped[OnOff]
    # cooler_ventilator_speed: Annotated[
    #    Stamped[Ratio], field_meta(included_in_fmu=False)
    # ]
    # fault_cooler: Annotated[Stamped[Error], field_meta(included_in_fmu=False)]
    temperature_hot_in: Stamped[Celsius]
    temperature_hot_out: Stamped[Celsius]
    temperature_waste_in: Stamped[Celsius]
    temperature_waste_out: Stamped[Celsius]
    temperature_cold_in: Stamped[Celsius]
    temperature_cold_out: Stamped[Celsius]
    # temperature_seawater: Annotated[Stamped[Celsius], field_meta(included_in_fmu=False)]
    # available_temperature_hot: Annotated[
    #    Stamped[Celsius], field_meta(included_in_fmu=False)
    # ]
    # available_temperature_cold: Annotated[
    #    Stamped[Celsius], field_meta(included_in_fmu=False)
    # ]
    # available_temperature_waste: Annotated[Stamped[Celsius], field_meta(included_in_fmu=False)]
    # operating_hours_adsorption: Annotated[
    #    Stamped[Seconds], field_meta(included_in_fmu=False)
    # ]
    # operating_hours_free_cooling: Annotated[
    #    Stamped[Seconds], field_meta(included_in_fmu=False)
    # ]
    # cooling_energy: Annotated[Stamped[Joule], field_meta(included_in_fmu=False)]
    pump_speed_hot: Stamped[Ratio]
    pump_speed_cold: Stamped[Ratio]
    pump_speed_waste: Stamped[Ratio]
    # no_cold_flow: Annotated[Stamped[Error], field_meta(included_in_fmu=False)]
    # freeze_protection: Annotated[Stamped[Error], field_meta(included_in_fmu=False)]
    # low_cooling_capacity: Annotated[Stamped[Error], field_meta(included_in_fmu=False)]
    # collective_fault_temperature_sensors: Annotated[
    #    Stamped[Error], field_meta(included_in_fmu=False)
    # ]
    # collective_fault_pumps: Annotated[Stamped[Error], field_meta(included_in_fmu=False)]
    # power_last_half_cycle: Annotated[Stamped[Watt], field_meta(included_in_fmu=False)]


class TankageSystem(ThrsValues):
    model_config = ConfigDict(
        alias_generator=lambda s: s.upper(),
        use_enum_values=True,
        validate_by_name=True,
    )

    hotwater11_level: Stamped[Liter]
    hotwater13_level: Stamped[Liter]
    hotwater15_level: Stamped[Liter]


class FreshwaterSystem(ThrsValues):
    model_config = ConfigDict(
        alias_generator=lambda s: s.upper(),
        use_enum_values=True,
        validate_by_name=True,
    )

    # mak1_alarm
    # mak2_alarm
    # chlorine_unit_alarm
    # circ_pump_running
    # coldwater_lower_saloon_flow
    # coldwater_dayhead_flow
    # hotwater_guest_cabin_sb_flow
    # coldwater_guest_cabin_sb_flow
    # hotwater_guest_cabin_ps_fwd_flow
    # coldwater_guest_cabin_ps_fwd_flow
    # hotwater_guest_cabin_ps_aft_flow
    # coldwater_guest_cabin_ps_aft_flow
    # hotwater_master_cabin_sb_flow
    # coldwater_master_cabin_sb_flow
    # hotwater_master_cabin_ps_flow
    # coldwater_master_cabin_ps_flow
    # hotwater_lazaret_flow
    # coldwater_lazaret_flow
    # coldwater_water_softner_flow
    hotwater_main_tech_space_fr45_flow: Stamped[LMin]
    # coldwater_main_tech_space_flow
    coldwater_main_tech_space_fr45_flow: Stamped[LMin]
    # tank_1_fr_45_ps_level
    # tank_2_fr_45_sb_level
    # hotwater_dayhead_flow
    # technical_room_energ_rec_flow
    # flow_sensor_25001137_c1
    # coldwater_owners_deckhouse_flow
    # hotwater_owners_deckhouse_flow
    energy_rec_system_temp7: Stamped[Celsius]
    energy_rec_system_temp4: Stamped[Celsius]
    energy_rec_system_temp5: Stamped[Celsius]
    energy_rec_system_temp8: Stamped[Celsius]
    energy_rec_system_temp6: Stamped[Celsius]
    # circ_pump_onoff
    # hotwater_crew_mess_flow
    # coldwater_crew_mess_flow
    # hotwater_galley_2_flow
    # coldwater_galley_2_flow
    # hotwater_guest_bathr_ps_fwd_flow
    # coldwater_guest_bathr_ps_fwd_flow
    # hotwater_laundry_ps_1_flow
    # coldwater_laundry_ps_flow
    # hotwater_captains_cabin_flow
    # coldwater_captains_cabin_flow
    # hotwater_crew_cabin_sb_aft_flow
    # coldwater_crew_cabin_sb_aft_flow
    # hotwater_crew_cabin_sb_mid_flow
    # coldwater_crew_cabin_sb_mid_flow
    # hotwater_crew_cabin_ps_mid_flow
    # coldwater_crew_cabin_ps_mid_flow
    # hotwater_crew_cabin_sb_fwd_flow
    # coldwater_crew_cabin_sb_fwd_flow
    # hotwater_crew_cabin_ps_fwd_flow
    # coldwater_crew_cabin_ps_fwd_flow
    # hotwater_deckhouse_flow
    # coldwater_deckhouse_flow
    # hotwater_deck_fr48_sb_tech_cor_flow
    # coldwater_deck_fr48_sb_tech_cor_flow
    # fr_46_system_beh_pres_pumps_press


class PowerSensor(ThrsValues):
    flow: Stamped[LMin]
    power: Stamped[Watt]
    delta_t: Stamped[DeltaT]
    temperature_warm: Stamped[Celsius]
    temperature_cold: Stamped[Celsius]


__all__ = [
    "AdsorptionChiller",
    "Brightloop",
    "CalculatedFlow",
    "CalculatedTemperature",
    "FlowSensor",
    "FreshwaterSystem",
    "HeatExchanger",
    "HeatPump",
    "HeatTransferDevice",
    "HvacExchanger",
    "LevelSensor",
    "LevelSwitch",
    "Pcm",
    "Pcs",
    "PowerSensor",
    "PressureSensor",
    "PropulsionDrive",
    "Pump",
    "ShorePowerConverter",
    "TankageSystem",
    "TemperatureDelta",
    "TemperatureSensor",
    "Thruster",
    "Ugrid",
    "Valve",
]
