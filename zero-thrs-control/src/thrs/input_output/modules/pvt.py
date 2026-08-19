from datetime import UTC, datetime
from typing import Annotated, cast

from pydantic import ConfigDict, computed_field
from pydantic.alias_generators import to_snake

from thrs.input_output.base import (
    Stamped,
    ThrsValues,
    component_meta,
    computed_meta,
)
from thrs.input_output.definitions import control, sensor, simulation
from thrs.input_output.definitions.units import WATER_HEAT_TRANSFER_CONVERSION, Celsius


class PvtSensorValues(ThrsValues):
    model_config = ConfigDict(
        alias_generator=to_snake,
        use_enum_values=True,
        validate_by_name=True,
    )

    pvt_pump_main_fwd: Annotated[
        sensor.Pump, component_meta(yard_tag="50001018", component_type="pump")
    ]
    pvt_pump_main_aft: Annotated[
        sensor.Pump, component_meta(yard_tag="50001019", component_type="pump")
    ]
    pvt_pump_owners: Annotated[
        sensor.Pump, component_meta(yard_tag="50001021", component_type="pump")
    ]
    pvt_temperature_main_fwd_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-03", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_fwd_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-23", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_aft_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-73", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_aft_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-22", component_type="temperature_sensor"),
    ]
    pvt_temperature_owners_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-21", component_type="temperature_sensor"),
    ]
    pvt_temperature_owners_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-04", component_type="temperature_sensor"),
    ]
    pvt_mix_main_fwd: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001044-01", component_type="valve", valve_type="mix"
        ),
    ]
    pvt_mix_main_aft: Annotated[
        sensor.Valve, component_meta(yard_tag="50001044-02", valve_type="mix")
    ]
    pvt_mix_owners: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001043-01", component_type="valve", valve_type="mix"
        ),
    ]
    pvt_flow_main_fwd_recovery: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001058-12", component_type="flow_sensor"),
    ]
    pvt_flow_main_aft_recovery: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001058-13", component_type="flow_sensor"),
    ]
    pvt_flow_owners_recovery: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001057-03", component_type="flow_sensor"),
    ]
    pvt_pressure_main_fwd: Annotated[
        sensor.PressureSensor,
        component_meta(yard_tag="50001097-03", component_type="pressure_sensor"),
    ]
    pvt_pressure_main_aft: Annotated[
        sensor.PressureSensor,
        component_meta(yard_tag="50001097-04", component_type="pressure_sensor"),
    ]
    pvt_pressure_owners: Annotated[
        sensor.PressureSensor,
        component_meta(yard_tag="50001097-05", component_type="pressure_sensor"),
    ]
    pvt_pressure_system: Annotated[
        sensor.PressureSensor,
        component_meta(yard_tag="50001097-06", component_type="pressure_sensor"),
    ]
    pvt_pressure_main_vacuum: Annotated[
        sensor.PressureSensor,
        component_meta(
            yard_tag="50009059-01",
            component_type="pressure_sensor",
            included_in_fmu=False,
        ),
    ] = sensor.PressureSensor(  # TODO: Remove default
        pressure=Stamped(value=0.0, timestamp=datetime.fromtimestamp(0, UTC))
    )
    pvt_pressure_owners_vacuum: Annotated[
        sensor.PressureSensor,
        component_meta(
            yard_tag="50009059-02",
            component_type="pressure_sensor",
            included_in_fmu=False,
        ),
    ] = sensor.PressureSensor(  # TODO: Remove default
        pressure=Stamped(value=0.0, timestamp=datetime.fromtimestamp(0, UTC))
    )
    pvt_switch_main_fwd: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001067-01", component_type="valve", valve_type="switch"
        ),
    ]
    pvt_switch_main_aft: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001067-02", component_type="valve", valve_type="switch"
        ),
    ]
    pvt_switch_owners: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001069-01", component_type="valve", valve_type="switch"
        ),
    ]
    pvt_mix_exchanger: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001047-02", component_type="valve", valve_type="mix"
        ),
    ]
    pvt_temperature_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-24", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string1_1_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-01", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string1_2_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-02", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string2_1_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-03", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string2_2_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-04", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string3_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-05", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string4_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-06", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string5_1_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-07", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string5_2_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-08", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string6_1_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-09", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string6_2_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-10", component_type="temperature_sensor"),
    ]
    pvt_flow_main_string1_1: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50009006-01", component_type="flow_sensor"),
    ]
    pvt_flow_main_string1_2: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50009006-02", component_type="flow_sensor"),
    ]
    pvt_flow_main_string2_1: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50009006-03", component_type="flow_sensor"),
    ]
    pvt_flow_main_string2_2: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50009006-04", component_type="flow_sensor"),
    ]
    pvt_flow_main_string3: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50009009-01", component_type="flow_sensor"),
    ]
    pvt_flow_main_string4: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50009009-02", component_type="flow_sensor"),
    ]
    pvt_flow_main_string5_1: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50009006-05", component_type="flow_sensor"),
    ]
    pvt_flow_main_string5_2: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50009006-06", component_type="flow_sensor"),
    ]
    pvt_flow_main_string6_1: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50009006-07", component_type="flow_sensor"),
    ]
    pvt_flow_main_string6_2: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50009006-08", component_type="flow_sensor"),
    ]
    pvt_temperature_main_string1_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-26", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string2_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-25", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string3_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-24", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string4_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-23", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string5_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-22", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string6_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-21", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string7_1_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-11", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string7_2_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-12", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string8_1_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-13", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string8_2_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-14", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string9_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-15", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string10_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-16", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string11_1_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-17", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string11_2_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-18", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string12_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-19", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string13_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-20", component_type="temperature_sensor"),
    ]
    pvt_flow_main_string7_1: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50009006-09", component_type="flow_sensor"),
    ]
    pvt_flow_main_string7_2: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50009006-10", component_type="flow_sensor"),
    ]
    pvt_flow_main_string8_1: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50009006-11", component_type="flow_sensor"),
    ]
    pvt_flow_main_string8_2: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50009006-12", component_type="flow_sensor"),
    ]
    pvt_flow_main_string9: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50009009-03", component_type="flow_sensor"),
    ]
    pvt_flow_main_string10: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50009009-04", component_type="flow_sensor"),
    ]
    pvt_flow_main_string11_1: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50009006-13", component_type="flow_sensor"),
    ]
    pvt_flow_main_string11_2: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50009006-14", component_type="flow_sensor"),
    ]
    pvt_flow_main_string12: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50009009-05", component_type="flow_sensor"),
    ]
    pvt_flow_main_string13: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50009009-06", component_type="flow_sensor"),
    ]
    pvt_temperature_main_string7_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-27", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string8_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-28", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string9_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-29", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string10_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-30", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string11_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-31", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string12_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-32", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string13_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-33", component_type="temperature_sensor"),
    ]
    pvt_temperature_owners_string1_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-34", component_type="temperature_sensor"),
    ]
    pvt_temperature_owners_string2_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-35", component_type="temperature_sensor"),
    ]
    pvt_temperature_owners_string3_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-36", component_type="temperature_sensor"),
    ]
    pvt_temperature_owners_string4_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-37", component_type="temperature_sensor"),
    ]
    pvt_temperature_owners_string5_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-38", component_type="temperature_sensor"),
    ]
    pvt_temperature_owners_string6_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-39", component_type="temperature_sensor"),
    ]
    pvt_flow_owners_string1: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50009009-07", component_type="flow_sensor"),
    ]
    pvt_flow_owners_string2: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50009009-08", component_type="flow_sensor"),
    ]
    pvt_flow_owners_string3: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50009009-09", component_type="flow_sensor"),
    ]
    pvt_flow_owners_string4: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50009009-10", component_type="flow_sensor"),
    ]
    pvt_flow_owners_string5: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50009009-11", component_type="flow_sensor"),
    ]
    pvt_flow_owners_string6: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50009009-12", component_type="flow_sensor"),
    ]
    pvt_temperature_owners_string1_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-40", component_type="temperature_sensor"),
    ]
    pvt_temperature_owners_string2_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-41", component_type="temperature_sensor"),
    ]
    pvt_temperature_owners_string3_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-42", component_type="temperature_sensor"),
    ]
    pvt_temperature_owners_string4_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-43", component_type="temperature_sensor"),
    ]
    pvt_temperature_owners_string5_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-44", component_type="temperature_sensor"),
    ]
    pvt_temperature_owners_string6_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-45", component_type="temperature_sensor"),
    ]

    pcm_temperature_producers_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(
            yard_tag="50001038-55",
            component_type="temperature_sensor",
            topic_override="500000-thrs/pcm/pcm-temperature-producers-supply",
            included_in_fmu=False,
        ),
    ]

    @computed_field(
        json_schema_extra=computed_meta(
            component_type="calculated_temperature", included_in_fmu=False
        )
    )
    @property
    def pvt_max_temperature_main_aft_strings(self) -> sensor.CalculatedTemperature:
        return sensor.CalculatedTemperature.from_max_temperature(
            [
                self.pvt_temperature_main_string1_1_return,
                self.pvt_temperature_main_string1_2_return,
                self.pvt_temperature_main_string2_1_return,
                self.pvt_temperature_main_string2_2_return,
                self.pvt_temperature_main_string3_return,
                self.pvt_temperature_main_string4_return,
                self.pvt_temperature_main_string5_1_return,
                self.pvt_temperature_main_string5_2_return,
                self.pvt_temperature_main_string6_1_return,
                self.pvt_temperature_main_string6_2_return,
                self.pvt_temperature_main_string1_supply,
                self.pvt_temperature_main_string2_supply,
                self.pvt_temperature_main_string3_supply,
                self.pvt_temperature_main_string4_supply,
                self.pvt_temperature_main_string5_supply,
                self.pvt_temperature_main_string6_supply,
            ]
        )

    @computed_field(
        json_schema_extra=computed_meta(
            component_type="calculated_temperature", included_in_fmu=False
        )
    )
    @property
    def pvt_max_temperature_main_fwd_strings(self) -> sensor.CalculatedTemperature:
        return sensor.CalculatedTemperature.from_max_temperature(
            [
                self.pvt_temperature_main_string7_1_return,
                self.pvt_temperature_main_string7_2_return,
                self.pvt_temperature_main_string8_1_return,
                self.pvt_temperature_main_string8_2_return,
                self.pvt_temperature_main_string9_return,
                self.pvt_temperature_main_string10_return,
                self.pvt_temperature_main_string11_1_return,
                self.pvt_temperature_main_string11_2_return,
                self.pvt_temperature_main_string12_return,
                self.pvt_temperature_main_string13_return,
                self.pvt_temperature_main_string7_supply,
                self.pvt_temperature_main_string8_supply,
                self.pvt_temperature_main_string9_supply,
                self.pvt_temperature_main_string10_supply,
                self.pvt_temperature_main_string11_supply,
                self.pvt_temperature_main_string12_supply,
                self.pvt_temperature_main_string13_supply,
            ]
        )

    @computed_field(
        json_schema_extra=computed_meta(
            component_type="calculated_temperature", included_in_fmu=False
        )
    )
    @property
    def pvt_max_temperature_owners_strings(self) -> sensor.CalculatedTemperature:
        return sensor.CalculatedTemperature.from_max_temperature(
            [
                self.pvt_temperature_owners_string1_return,
                self.pvt_temperature_owners_string2_return,
                self.pvt_temperature_owners_string3_return,
                self.pvt_temperature_owners_string4_return,
                self.pvt_temperature_owners_string5_return,
                self.pvt_temperature_owners_string6_return,
                self.pvt_temperature_owners_string1_supply,
                self.pvt_temperature_owners_string2_supply,
                self.pvt_temperature_owners_string3_supply,
                self.pvt_temperature_owners_string4_supply,
                self.pvt_temperature_owners_string5_supply,
                self.pvt_temperature_owners_string6_supply,
            ]
        )

    @computed_field(
        json_schema_extra=computed_meta(
            component_type="calculated_temperature", included_in_fmu=False
        )
    )
    @property
    def pvt_temperature_main_aft_strings_supply(self) -> sensor.CalculatedTemperature:
        return sensor.CalculatedTemperature.from_weighted_sensors(
            [
                self.pvt_flow_main_string1_1.flow,
                self.pvt_flow_main_string1_2.flow,
                self.pvt_flow_main_string2_1.flow,
                self.pvt_flow_main_string2_2.flow,
                self.pvt_flow_main_string3.flow,
                self.pvt_flow_main_string4.flow,
                self.pvt_flow_main_string5_1.flow,
                self.pvt_flow_main_string5_2.flow,
                self.pvt_flow_main_string6_1.flow,
                self.pvt_flow_main_string6_2.flow,
            ],
            [
                self.pvt_temperature_main_string1_supply,
                self.pvt_temperature_main_string1_supply,
                self.pvt_temperature_main_string2_supply,
                self.pvt_temperature_main_string2_supply,
                self.pvt_temperature_main_string3_supply,
                self.pvt_temperature_main_string4_supply,
                self.pvt_temperature_main_string5_supply,
                self.pvt_temperature_main_string5_supply,
                self.pvt_temperature_main_string6_supply,
                self.pvt_temperature_main_string6_supply,
            ],
            None,
        )

    @computed_field(
        json_schema_extra=computed_meta(
            component_type="calculated_temperature", included_in_fmu=False
        )
    )
    @property
    def pvt_temperature_main_fwd_strings_supply(self) -> sensor.CalculatedTemperature:
        return sensor.CalculatedTemperature.from_weighted_sensors(
            [
                self.pvt_flow_main_string7_1.flow,
                self.pvt_flow_main_string7_2.flow,
                self.pvt_flow_main_string8_1.flow,
                self.pvt_flow_main_string8_2.flow,
                self.pvt_flow_main_string9.flow,
                self.pvt_flow_main_string10.flow,
                self.pvt_flow_main_string11_1.flow,
                self.pvt_flow_main_string11_2.flow,
                self.pvt_flow_main_string12.flow,
                self.pvt_flow_main_string13.flow,
            ],
            [
                self.pvt_temperature_main_string7_supply,
                self.pvt_temperature_main_string7_supply,
                self.pvt_temperature_main_string8_supply,
                self.pvt_temperature_main_string8_supply,
                self.pvt_temperature_main_string9_supply,
                self.pvt_temperature_main_string10_supply,
                self.pvt_temperature_main_string11_supply,
                self.pvt_temperature_main_string11_supply,
                self.pvt_temperature_main_string12_supply,
                self.pvt_temperature_main_string13_supply,
            ],
            None,
        )

    @computed_field(
        json_schema_extra=computed_meta(
            component_type="calculated_temperature", included_in_fmu=False
        )
    )
    @property
    def pvt_temperature_owners_strings_supply(self) -> sensor.CalculatedTemperature:
        return sensor.CalculatedTemperature.from_weighted_sensors(
            [
                self.pvt_flow_owners_string1.flow,
                self.pvt_flow_owners_string2.flow,
                self.pvt_flow_owners_string3.flow,
                self.pvt_flow_owners_string4.flow,
                self.pvt_flow_owners_string5.flow,
                self.pvt_flow_owners_string6.flow,
            ],
            [
                self.pvt_temperature_owners_string1_supply,
                self.pvt_temperature_owners_string2_supply,
                self.pvt_temperature_owners_string3_supply,
                self.pvt_temperature_owners_string4_supply,
                self.pvt_temperature_owners_string5_supply,
                self.pvt_temperature_owners_string6_supply,
            ],
            None,
        )

    @computed_field(
        json_schema_extra=computed_meta(
            component_type="calculated_temperature", included_in_fmu=False
        )
    )
    @property
    def pvt_temperature_main_aft_strings_return(self) -> sensor.CalculatedTemperature:
        return sensor.CalculatedTemperature.from_weighted_sensors(
            [
                self.pvt_flow_main_string1_1.flow,
                self.pvt_flow_main_string1_2.flow,
                self.pvt_flow_main_string2_1.flow,
                self.pvt_flow_main_string2_2.flow,
                self.pvt_flow_main_string3.flow,
                self.pvt_flow_main_string4.flow,
                self.pvt_flow_main_string5_1.flow,
                self.pvt_flow_main_string5_2.flow,
                self.pvt_flow_main_string6_1.flow,
                self.pvt_flow_main_string6_2.flow,
            ],
            [
                self.pvt_temperature_main_string1_1_return,
                self.pvt_temperature_main_string1_2_return,
                self.pvt_temperature_main_string2_1_return,
                self.pvt_temperature_main_string2_2_return,
                self.pvt_temperature_main_string3_return,
                self.pvt_temperature_main_string4_return,
                self.pvt_temperature_main_string5_1_return,
                self.pvt_temperature_main_string5_2_return,
                self.pvt_temperature_main_string6_1_return,
                self.pvt_temperature_main_string6_2_return,
            ],
            None,
        )

    @computed_field(
        json_schema_extra=computed_meta(
            component_type="calculated_temperature", included_in_fmu=False
        )
    )
    @property
    def pvt_temperature_main_fwd_strings_return(self) -> sensor.CalculatedTemperature:
        return sensor.CalculatedTemperature.from_weighted_sensors(
            [
                self.pvt_flow_main_string7_1.flow,
                self.pvt_flow_main_string7_2.flow,
                self.pvt_flow_main_string8_1.flow,
                self.pvt_flow_main_string8_2.flow,
                self.pvt_flow_main_string9.flow,
                self.pvt_flow_main_string10.flow,
                self.pvt_flow_main_string11_1.flow,
                self.pvt_flow_main_string11_2.flow,
                self.pvt_flow_main_string12.flow,
                self.pvt_flow_main_string13.flow,
            ],
            [
                self.pvt_temperature_main_string7_1_return,
                self.pvt_temperature_main_string7_2_return,
                self.pvt_temperature_main_string8_1_return,
                self.pvt_temperature_main_string8_2_return,
                self.pvt_temperature_main_string9_return,
                self.pvt_temperature_main_string10_return,
                self.pvt_temperature_main_string11_1_return,
                self.pvt_temperature_main_string11_2_return,
                self.pvt_temperature_main_string12_return,
                self.pvt_temperature_main_string13_return,
            ],
            None,
        )

    @computed_field(
        json_schema_extra=computed_meta(
            component_type="calculated_temperature", included_in_fmu=False
        )
    )
    @property
    def pvt_temperature_owners_strings_return(self) -> sensor.CalculatedTemperature:
        return sensor.CalculatedTemperature.from_weighted_sensors(
            [
                self.pvt_flow_owners_string1.flow,
                self.pvt_flow_owners_string2.flow,
                self.pvt_flow_owners_string3.flow,
                self.pvt_flow_owners_string4.flow,
                self.pvt_flow_owners_string5.flow,
                self.pvt_flow_owners_string6.flow,
            ],
            [
                self.pvt_temperature_owners_string1_return,
                self.pvt_temperature_owners_string2_return,
                self.pvt_temperature_owners_string3_return,
                self.pvt_temperature_owners_string4_return,
                self.pvt_temperature_owners_string5_return,
                self.pvt_temperature_owners_string6_return,
            ],
            None,
        )

    @computed_field(
        json_schema_extra=computed_meta(
            component_type="calculated_temperature", included_in_fmu=False
        )
    )
    @property
    def pvt_flow_main_aft_strings(self) -> sensor.CalculatedFlow:
        return sensor.CalculatedFlow.from_sensors(
            [
                self.pvt_flow_main_string1_1,
                self.pvt_flow_main_string1_2,
                self.pvt_flow_main_string2_1,
                self.pvt_flow_main_string2_2,
                self.pvt_flow_main_string3,
                self.pvt_flow_main_string4,
                self.pvt_flow_main_string5_1,
                self.pvt_flow_main_string5_2,
                self.pvt_flow_main_string6_1,
                self.pvt_flow_main_string6_2,
            ],
        )

    @computed_field(
        json_schema_extra=computed_meta(
            component_type="calculated_temperature", included_in_fmu=False
        )
    )
    @property
    def pvt_flow_main_fwd_strings(self) -> sensor.CalculatedFlow:
        return sensor.CalculatedFlow.from_sensors(
            [
                self.pvt_flow_main_string7_1,
                self.pvt_flow_main_string7_2,
                self.pvt_flow_main_string8_1,
                self.pvt_flow_main_string8_2,
                self.pvt_flow_main_string9,
                self.pvt_flow_main_string10,
                self.pvt_flow_main_string11_1,
                self.pvt_flow_main_string11_2,
                self.pvt_flow_main_string12,
                self.pvt_flow_main_string13,
            ],
        )

    @computed_field(
        json_schema_extra=computed_meta(
            component_type="calculated_temperature", included_in_fmu=False
        )
    )
    @property
    def pvt_flow_owners_strings(self) -> sensor.CalculatedFlow:
        return sensor.CalculatedFlow.from_sensors(
            [
                self.pvt_flow_owners_string1,
                self.pvt_flow_owners_string2,
                self.pvt_flow_owners_string3,
                self.pvt_flow_owners_string4,
                self.pvt_flow_owners_string5,
                self.pvt_flow_owners_string6,
            ],
        )

    @computed_field(
        json_schema_extra=computed_meta(
            yard_tag="50009001-01",
            component_type="heat_exchanger",
            included_in_fmu=False,
        )
    )
    @property
    def pvt_pvt_main_fwd(self) -> sensor.Pvt:
        return sensor.Pvt.from_sensors(
            temperature_supply=self.pvt_temperature_main_fwd_strings_supply.temperature,
            temperature_return=self.pvt_temperature_main_fwd_strings_return.temperature,
            flow=self.pvt_flow_main_fwd_strings.flow,
            heat_transfer_conversion=WATER_HEAT_TRANSFER_CONVERSION,
        )

    @computed_field(
        json_schema_extra=computed_meta(
            yard_tag="50009002-01",
            component_type="heat_exchanger",
            included_in_fmu=False,
        )
    )
    @property
    def pvt_pvt_main_aft(self) -> sensor.Pvt:
        return sensor.Pvt.from_sensors(
            temperature_supply=self.pvt_temperature_main_aft_strings_supply.temperature,
            temperature_return=self.pvt_temperature_main_aft_strings_return.temperature,
            flow=self.pvt_flow_main_aft_strings.flow,
            heat_transfer_conversion=WATER_HEAT_TRANSFER_CONVERSION,
        )

    @computed_field(
        json_schema_extra=computed_meta(
            yard_tag="50009001-03",
            component_type="heat_exchanger",
            included_in_fmu=False,
        )
    )
    @property
    def pvt_pvt_owners(self) -> sensor.Pvt:
        return sensor.Pvt.from_sensors(
            temperature_supply=self.pvt_temperature_owners_strings_supply.temperature,
            temperature_return=self.pvt_temperature_owners_strings_return.temperature,
            flow=self.pvt_flow_owners_strings.flow,
            heat_transfer_conversion=WATER_HEAT_TRANSFER_CONVERSION,
        )

    @computed_field(
        json_schema_extra=computed_meta(
            component_type="calculated_flow", included_in_fmu=False
        )
    )
    @property
    def pvt_return_temperature(self) -> sensor.CalculatedTemperature:
        return sensor.CalculatedTemperature.from_weighted_sensors(
            [
                self.pvt_flow_main_aft_recovery.flow,
                self.pvt_flow_main_fwd_recovery.flow,
                self.pvt_flow_owners_recovery.flow,
            ],
            [
                self.pvt_temperature_main_aft_return,
                self.pvt_temperature_main_fwd_return,
                self.pvt_temperature_owners_return,
            ],
            None,
        )

    @computed_field(
        json_schema_extra=computed_meta(
            component_type="calculated_flow", included_in_fmu=False
        )
    )
    @property
    def pvt_total_flow(self) -> sensor.CalculatedFlow:
        return sensor.CalculatedFlow(
            flow=Stamped.combine(
                self.pvt_flow_main_aft_recovery.flow,
                self.pvt_flow_main_fwd_recovery.flow,
                self.pvt_flow_owners_recovery.flow,
                value=self.pvt_flow_main_aft_recovery.flow.value
                + self.pvt_flow_main_fwd_recovery.flow.value
                + self.pvt_flow_owners_recovery.flow.value,
            )
        )

    @computed_field(
        json_schema_extra=computed_meta(
            component_type="calculated_flow", included_in_fmu=False
        )
    )
    @property
    def pvt_seawater_exchanger_flow(self) -> sensor.CalculatedFlow:
        return sensor.CalculatedFlow(
            flow=Stamped.combine(
                self.pvt_mix_exchanger.position_rel,
                self.pvt_total_flow.flow,
                value=(1 - self.pvt_mix_exchanger.position_rel.value)
                * self.pvt_total_flow.flow.value,
            )
        )

    @computed_field(
        json_schema_extra=computed_meta(
            yard_tag="50001002", component_type="heat_exchanger", included_in_fmu=False
        )
    )
    @property
    def pvt_seawater_exchanger(self) -> sensor.HeatExchanger:
        return sensor.HeatExchanger.from_sensors(
            temperature_supply=self.pvt_temperature_supply.temperature,
            temperature_return=self.pcm_temperature_producers_supply.temperature,
            flow=self.pvt_seawater_exchanger_flow.flow,
            heat_transfer_conversion=WATER_HEAT_TRANSFER_CONVERSION,
        )


class PvtControlValues(ThrsValues):
    model_config = ConfigDict(
        alias_generator=to_snake,
        use_enum_values=True,
        validate_by_name=True,
    )

    pvt_pump_main_fwd: Annotated[
        control.Pump, component_meta(yard_tag="50001018", component_type="pump")
    ]
    pvt_pump_main_aft: Annotated[
        control.Pump, component_meta(yard_tag="50001019", component_type="pump")
    ]
    pvt_pump_owners: Annotated[
        control.Pump, component_meta(yard_tag="50001021", component_type="pump")
    ]
    pvt_mix_main_fwd: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001044-01", component_type="valve", valve_type="mix"
        ),
    ]
    pvt_mix_main_aft: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001044-02", component_type="valve", valve_type="mix"
        ),
    ]
    pvt_mix_owners: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001043-01", component_type="valve", valve_type="mix"
        ),
    ]
    pvt_switch_main_fwd: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001067-01", component_type="valve", valve_type="switch"
        ),
    ]
    pvt_switch_main_aft: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001067-02", component_type="valve", valve_type="switch"
        ),
    ]
    pvt_switch_owners: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001069-01", component_type="valve", valve_type="switch"
        ),
    ]
    pvt_mix_exchanger: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001047-02", component_type="valve", valve_type="mix"
        ),
    ]


class PvtSimulationInputs(ThrsValues):
    pvt_main_fwd: simulation.HeatSource
    pvt_main_aft: simulation.HeatSource
    pvt_owners: simulation.HeatSource
    pvt_pcm_supply: simulation.TemperatureBoundary
    pvt_seawater_supply: simulation.Boundary


class PvtSimulationOutputs(ThrsValues):
    pvt_pcm_return: simulation.Boundary
    pvt_pcm_supply: simulation.FlowBoundary
    pvt_seawater_return: simulation.TemperatureBoundary

    @computed_field(
        json_schema_extra=computed_meta(
            included_in_fmu=False, component_type="temperature_sensor"
        )
    )
    @property
    def pcm_temperature_producers_supply(self) -> sensor.TemperatureSensor:
        return sensor.TemperatureSensor(
            temperature=cast(Stamped[Celsius], self.pvt_pcm_return.temperature)
        )
