from typing import Annotated

from pydantic import computed_field

from thrs.input_output.base import (
    SimulationInputs,
    SimulationValues,
    ThrsValues,
    component_meta,
)
from thrs.input_output.definitions import control, sensor, simulation


class PvtSensorValues(ThrsValues):
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
    pvt_pressure_supply: Annotated[
        sensor.PressureSensor,
        component_meta(yard_tag="50001097-06", component_type="pressure_sensor"),
    ]
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
    pvt_temperature_main_string_1_1_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-01", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string_1_2_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-02", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string_2_1_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-03", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string_2_2_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-04", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string_3_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-05", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string_4_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-06", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string_5_1_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-07", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string_5_2_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-08", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string_6_1_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-09", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string_6_2_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-10", component_type="temperature_sensor"),
    ]
    pvt_flow_main_string_1_1: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50009006-01", component_type="flow_sensor"),
    ]
    pvt_flow_main_string_1_2: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50009006-02", component_type="flow_sensor"),
    ]
    pvt_flow_main_string_2_1: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50009006-03", component_type="flow_sensor"),
    ]
    pvt_flow_main_string_2_2: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50009006-04", component_type="flow_sensor"),
    ]
    pvt_flow_main_string_3: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50009009-01", component_type="flow_sensor"),
    ]
    pvt_flow_main_string_4: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50009009-02", component_type="flow_sensor"),
    ]
    pvt_flow_main_string_5_1: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50009006-05", component_type="flow_sensor"),
    ]
    pvt_flow_main_string_5_2: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50009006-06", component_type="flow_sensor"),
    ]
    pvt_flow_main_string_6_1: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50009006-07", component_type="flow_sensor"),
    ]
    pvt_flow_main_string_6_2: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50009006-08", component_type="flow_sensor"),
    ]
    pvt_temperature_main_string_1_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-26", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string_2_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-25", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string_3_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-24", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string_4_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-23", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string_5_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-22", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string_6_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-21", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string_7_1_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-11", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string_7_2_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-12", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string_8_1_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-13", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string_8_2_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-14", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string_9_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-15", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string_10_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-16", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string_11_1_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-17", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string_11_2_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-18", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string_12_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-19", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string_13_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-20", component_type="temperature_sensor"),
    ]
    pvt_flow_main_string_7_1: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50009006-09", component_type="flow_sensor"),
    ]
    pvt_flow_main_string_7_2: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50009006-10", component_type="flow_sensor"),
    ]
    pvt_flow_main_string_8_1: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50009006-11", component_type="flow_sensor"),
    ]
    pvt_flow_main_string_8_2: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50009006-12", component_type="flow_sensor"),
    ]
    pvt_flow_main_string_9: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50009009-03", component_type="flow_sensor"),
    ]
    pvt_flow_main_string_10: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50009009-04", component_type="flow_sensor"),
    ]
    pvt_flow_main_string_11_1: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50009006-13", component_type="flow_sensor"),
    ]
    pvt_flow_main_string_11_2: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50009006-14", component_type="flow_sensor"),
    ]
    pvt_flow_main_string_12: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50009009-05", component_type="flow_sensor"),
    ]
    pvt_flow_main_string_13: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50009009-06", component_type="flow_sensor"),
    ]
    pvt_temperature_main_string_7_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-27", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string_8_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-28", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string_9_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-29", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string_10_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-30", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string_11_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-31", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string_12_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-32", component_type="temperature_sensor"),
    ]
    pvt_temperature_main_string_13_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-33", component_type="temperature_sensor"),
    ]
    pvt_temperature_owners_string_1_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-34", component_type="temperature_sensor"),
    ]
    pvt_temperature_owners_string_2_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-35", component_type="temperature_sensor"),
    ]
    pvt_temperature_owners_string_3_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-36", component_type="temperature_sensor"),
    ]
    pvt_temperature_owners_string_4_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-37", component_type="temperature_sensor"),
    ]
    pvt_temperature_owners_string_5_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-38", component_type="temperature_sensor"),
    ]
    pvt_temperature_owners_string_6_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-39", component_type="temperature_sensor"),
    ]
    pvt_flow_owners_string_1: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50009009-07", component_type="flow_sensor"),
    ]
    pvt_flow_owners_string_2: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50009009-08", component_type="flow_sensor"),
    ]
    pvt_flow_owners_string_3: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50009009-09", component_type="flow_sensor"),
    ]
    pvt_flow_owners_string_4: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50009009-10", component_type="flow_sensor"),
    ]
    pvt_flow_owners_string_5: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50009009-11", component_type="flow_sensor"),
    ]
    pvt_flow_owners_string_6: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50009009-12", component_type="flow_sensor"),
    ]
    pvt_temperature_owners_string_1_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-40", component_type="temperature_sensor"),
    ]
    pvt_temperature_owners_string_2_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-41", component_type="temperature_sensor"),
    ]
    pvt_temperature_owners_string_3_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-42", component_type="temperature_sensor"),
    ]
    pvt_temperature_owners_string_4_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-43", component_type="temperature_sensor"),
    ]
    pvt_temperature_owners_string_5_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-44", component_type="temperature_sensor"),
    ]
    pvt_temperature_owners_string_6_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50009005-45", component_type="temperature_sensor"),
    ]

    @computed_field(
        json_schema_extra=component_meta(
            component_type="calculated_temperature", included_in_fmu=False
        ).json_schema_extra
    )
    @property
    def pvt_max_temperature_main_fwd_strings(
        self,
    ) -> Annotated[sensor.CalculatedTemperature, component_meta(included_in_fmu=False)]:
        return sensor.CalculatedTemperature.from_max_temperature(
            [
                self.pvt_temperature_main_string_1_1_return,
                self.pvt_temperature_main_string_1_2_return,
                self.pvt_temperature_main_string_2_1_return,
                self.pvt_temperature_main_string_2_2_return,
                self.pvt_temperature_main_string_3_return,
                self.pvt_temperature_main_string_4_return,
                self.pvt_temperature_main_string_5_1_return,
                self.pvt_temperature_main_string_5_2_return,
                self.pvt_temperature_main_string_6_1_return,
                self.pvt_temperature_main_string_6_2_return,
                self.pvt_temperature_main_string_1_supply,
                self.pvt_temperature_main_string_2_supply,
                self.pvt_temperature_main_string_3_supply,
                self.pvt_temperature_main_string_4_supply,
                self.pvt_temperature_main_string_5_supply,
                self.pvt_temperature_main_string_6_supply,
            ]
        )

    @computed_field(
        json_schema_extra=component_meta(included_in_fmu=False).json_schema_extra
    )
    @property
    def pvt_max_temperature_main_aft_strings(
        self,
    ) -> Annotated[
        sensor.CalculatedTemperature,
        component_meta(component_type="calculated_temperature", included_in_fmu=False),
    ]:
        return sensor.CalculatedTemperature.from_max_temperature(
            [
                self.pvt_temperature_main_string_7_1_return,
                self.pvt_temperature_main_string_7_2_return,
                self.pvt_temperature_main_string_8_1_return,
                self.pvt_temperature_main_string_8_2_return,
                self.pvt_temperature_main_string_9_return,
                self.pvt_temperature_main_string_10_return,
                self.pvt_temperature_main_string_11_1_return,
                self.pvt_temperature_main_string_11_2_return,
                self.pvt_temperature_main_string_12_return,
                self.pvt_temperature_main_string_13_return,
                self.pvt_temperature_main_string_7_supply,
                self.pvt_temperature_main_string_8_supply,
                self.pvt_temperature_main_string_9_supply,
                self.pvt_temperature_main_string_10_supply,
                self.pvt_temperature_main_string_11_supply,
                self.pvt_temperature_main_string_12_supply,
                self.pvt_temperature_main_string_13_supply,
            ]
        )

    @computed_field(
        json_schema_extra=component_meta(included_in_fmu=False).json_schema_extra
    )
    @property
    def pvt_max_temperature_owners_strings(
        self,
    ) -> Annotated[
        sensor.CalculatedTemperature,
        component_meta(component_type="calculated_temperature", included_in_fmu=False),
    ]:
        return sensor.CalculatedTemperature.from_max_temperature(
            [
                self.pvt_temperature_owners_string_1_return,
                self.pvt_temperature_owners_string_2_return,
                self.pvt_temperature_owners_string_3_return,
                self.pvt_temperature_owners_string_4_return,
                self.pvt_temperature_owners_string_5_return,
                self.pvt_temperature_owners_string_6_return,
                self.pvt_temperature_owners_string_1_supply,
                self.pvt_temperature_owners_string_2_supply,
                self.pvt_temperature_owners_string_3_supply,
                self.pvt_temperature_owners_string_4_supply,
                self.pvt_temperature_owners_string_5_supply,
                self.pvt_temperature_owners_string_6_supply,
            ]
        )


class PvtControlValues(ThrsValues):
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


class PvtSimulationInputs(SimulationInputs):
    pvt_main_fwd: simulation.HeatSource
    pvt_main_aft: simulation.HeatSource
    pvt_owners: simulation.HeatSource
    pvt_module_supply: simulation.TemperatureBoundary
    pvt_seawater_supply: simulation.Boundary


class PvtSimulationOutputs(SimulationValues):
    pvt_module_return: simulation.Boundary
    pvt_module_supply: simulation.FlowBoundary
    pvt_seawater_return: simulation.TemperatureBoundary
