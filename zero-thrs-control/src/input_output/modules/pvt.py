from typing import Annotated
from input_output.base import ComponentMeta, SimulationInputs, ThrsModel
from input_output.definitions import control, sensor, simulation


class PvtSensorValues(ThrsModel):
    pvt_pump_main_fwd: Annotated[sensor.Pump, ComponentMeta("50001018")]
    pvt_pump_main_aft: Annotated[sensor.Pump, ComponentMeta("50001019")]
    pvt_pump_owners: Annotated[sensor.Pump, ComponentMeta("50001021")]
    pvt_temperature_main_fwd_return: Annotated[
        sensor.TemperatureSensor, ComponentMeta("50001038-03")
    ]
    pvt_temperature_main_fwd_supply: Annotated[
        sensor.TemperatureSensor, ComponentMeta("50001038-23")
    ]
    pvt_temperature_main_aft_return: Annotated[
        sensor.TemperatureSensor, ComponentMeta("50001038-73")
    ]
    pvt_temperature_main_aft_supply: Annotated[
        sensor.TemperatureSensor, ComponentMeta("50001038-22")
    ]
    pvt_temperature_main_aft_return: Annotated[
        sensor.TemperatureSensor, ComponentMeta("50001038-04")
    ]
    pvt_temperature_owners_supply: Annotated[
        sensor.TemperatureSensor, ComponentMeta("50001038-21")
    ]
    pvt_temperature_owners_return: Annotated[
        sensor.TemperatureSensor, ComponentMeta("50001038-04")
    ]
    pvt_mix_main_fwd: Annotated[sensor.Valve, ComponentMeta("50001044-01")]
    pvt_mix_main_aft: Annotated[sensor.Valve, ComponentMeta("50001044-02")]
    pvt_mix_owners: Annotated[sensor.Valve, ComponentMeta("50001043-01")]
    pvt_flow_main_fwd: Annotated[sensor.FlowSensor, ComponentMeta("50001058-12")]
    pvt_flow_main_aft: Annotated[sensor.FlowSensor, ComponentMeta("50001058-13")]
    pvt_flow_owners: Annotated[sensor.FlowSensor, ComponentMeta("50001057-03")]
    pvt_pressure_main_fwd: Annotated[
        sensor.PressureSensor, ComponentMeta("50001097-03")
    ]
    pvt_pressure_main_aft: Annotated[
        sensor.PressureSensor, ComponentMeta("50001097-04")
    ]
    pvt_pressure_owners: Annotated[sensor.PressureSensor, ComponentMeta("50001097-05")]
    pvt_flowcontrol_main_fwd: Annotated[sensor.Valve, ComponentMeta("50001067-01")]
    pvt_flowcontrol_main_aft: Annotated[sensor.Valve, ComponentMeta("50001067-02")]
    pvt_flowcontrol_owners: Annotated[sensor.Valve, ComponentMeta("50001069-01")]
    pvt_mix_exchanger: Annotated[sensor.Valve, ComponentMeta("50001047-02")]
    pvt_temperature_exchanger: Annotated[
        sensor.TemperatureSensor, ComponentMeta("50001038-24")
    ]
    pvt_temperature_main_string_1_1_return: Annotated[
        sensor.TemperatureSensor, ComponentMeta("50009005-01")
    ]
    pvt_temperature_main_string_1_2_return: Annotated[
        sensor.TemperatureSensor, ComponentMeta("50009005-02")
    ]
    pvt_temperature_main_string_2_1_return: Annotated[
        sensor.TemperatureSensor, ComponentMeta("50009005-03")
    ]
    pvt_temperature_main_string_2_2_return: Annotated[
        sensor.TemperatureSensor, ComponentMeta("50009005-04")
    ]
    pvt_temperature_main_string_3_return: Annotated[
        sensor.TemperatureSensor, ComponentMeta("50009005-05")
    ]
    pvt_temperature_main_string_4_return: Annotated[
        sensor.TemperatureSensor, ComponentMeta("50009005-06")
    ]
    pvt_temperature_main_string_5_1_return: Annotated[
        sensor.TemperatureSensor, ComponentMeta("50009005-07")
    ]
    pvt_temperature_main_string_5_2_return: Annotated[
        sensor.TemperatureSensor, ComponentMeta("50009005-08")
    ]
    pvt_temperature_main_string_6_1_return: Annotated[
        sensor.TemperatureSensor, ComponentMeta("50009005-09")
    ]
    pvt_temperature_main_string_6_2_return: Annotated[
        sensor.TemperatureSensor, ComponentMeta("50009005-10")
    ]
    pvt_flow_main_string_1_1: Annotated[sensor.FlowSensor, ComponentMeta("50009006-01")]
    pvt_flow_main_string_1_2: Annotated[sensor.FlowSensor, ComponentMeta("50009006-02")]
    pvt_flow_main_string_2_1: Annotated[sensor.FlowSensor, ComponentMeta("50009006-03")]
    pvt_flow_main_string_2_2: Annotated[sensor.FlowSensor, ComponentMeta("50009006-04")]
    pvt_flow_main_string_3: Annotated[sensor.FlowSensor, ComponentMeta("50009009-01")]
    pvt_flow_main_string_4: Annotated[sensor.FlowSensor, ComponentMeta("50009009-02")]
    pvt_flow_main_string_5_1: Annotated[sensor.FlowSensor, ComponentMeta("50009006-05")]
    pvt_flow_main_string_5_2: Annotated[sensor.FlowSensor, ComponentMeta("50009006-06")]
    pvt_flow_main_string_6_1: Annotated[sensor.FlowSensor, ComponentMeta("50009006-07")]
    pvt_flow_main_string_6_2: Annotated[sensor.FlowSensor, ComponentMeta("50009006-08")]
    pvt_temperature_main_string_1_supply: Annotated[
        sensor.TemperatureSensor, ComponentMeta("50009005-26")
    ]
    pvt_temperature_main_string_2_supply: Annotated[
        sensor.TemperatureSensor, ComponentMeta("50009005-25")
    ]
    pvt_temperature_main_string_3_supply: Annotated[
        sensor.TemperatureSensor, ComponentMeta("50009005-24")
    ]
    pvt_temperature_main_string_4_supply: Annotated[
        sensor.TemperatureSensor, ComponentMeta("50009005-23")
    ]
    pvt_temperature_main_string_5_supply: Annotated[
        sensor.TemperatureSensor, ComponentMeta("50009005-22")
    ]
    pvt_temperature_main_string_6_supply: Annotated[
        sensor.TemperatureSensor, ComponentMeta("50009005-21")
    ]
    pvt_temperature_main_string_7_1_return: Annotated[
        sensor.TemperatureSensor, ComponentMeta("50009005-11")
    ]
    pvt_temperature_main_string_7_2_return: Annotated[
        sensor.TemperatureSensor, ComponentMeta("50009005-12")
    ]
    pvt_temperature_main_string_8_1_return: Annotated[
        sensor.TemperatureSensor, ComponentMeta("50009005-13")
    ]
    pvt_temperature_main_string_8_2_return: Annotated[
        sensor.TemperatureSensor, ComponentMeta("50009005-14")
    ]
    pvt_temperature_main_string_9_return: Annotated[
        sensor.TemperatureSensor, ComponentMeta("50009005-15")
    ]
    pvt_temperature_main_string_10_return: Annotated[
        sensor.TemperatureSensor, ComponentMeta("50009005-16")
    ]
    pvt_temperature_main_string_11_1_return: Annotated[
        sensor.TemperatureSensor, ComponentMeta("50009005-17")
    ]
    pvt_temperature_main_string_11_2_return: Annotated[
        sensor.TemperatureSensor, ComponentMeta("50009005-18")
    ]
    pvt_temperature_main_string_12_return: Annotated[
        sensor.TemperatureSensor, ComponentMeta("50009005-19")
    ]
    pvt_temperature_main_string_13_return: Annotated[
        sensor.TemperatureSensor, ComponentMeta("50009005-20")
    ]
    pvt_flow_main_string_7_1: Annotated[sensor.FlowSensor, ComponentMeta("50009006-09")]
    pvt_flow_main_string_7_2: Annotated[sensor.FlowSensor, ComponentMeta("50009006-10")]
    pvt_flow_main_string_8_1: Annotated[sensor.FlowSensor, ComponentMeta("50009006-11")]
    pvt_flow_main_string_8_2: Annotated[sensor.FlowSensor, ComponentMeta("50009006-12")]
    pvt_flow_main_string_9: Annotated[sensor.FlowSensor, ComponentMeta("50009009-03")]
    pvt_flow_main_string_10: Annotated[sensor.FlowSensor, ComponentMeta("50009009-04")]
    pvt_flow_main_string_11_1: Annotated[
        sensor.FlowSensor, ComponentMeta("50009006-13")
    ]
    pvt_flow_main_string_11_2: Annotated[
        sensor.FlowSensor, ComponentMeta("50009006-14")
    ]
    pvt_flow_main_string_12: Annotated[sensor.FlowSensor, ComponentMeta("50009009-05")]
    pvt_flow_main_string_13: Annotated[sensor.FlowSensor, ComponentMeta("50009009-06")]
    pvt_temperature_main_string_7_supply: Annotated[
        sensor.TemperatureSensor, ComponentMeta("50009005-27")
    ]
    pvt_temperature_main_string_8_supply: Annotated[
        sensor.TemperatureSensor, ComponentMeta("50009005-28")
    ]
    pvt_temperature_main_string_9_supply: Annotated[
        sensor.TemperatureSensor, ComponentMeta("50009005-29")
    ]
    pvt_temperature_main_string_10_supply: Annotated[
        sensor.TemperatureSensor, ComponentMeta("50009005-30")
    ]
    pvt_temperature_main_string_11_supply: Annotated[
        sensor.TemperatureSensor, ComponentMeta("50009005-31")
    ]
    pvt_temperature_main_string_12_supply: Annotated[
        sensor.TemperatureSensor, ComponentMeta("50009005-32")
    ]
    pvt_temperature_main_string_13_supply: Annotated[
        sensor.TemperatureSensor, ComponentMeta("50009005-33")
    ]
    pvt_temperature_owners_string_1_return: Annotated[
        sensor.TemperatureSensor, ComponentMeta("50009005-34")
    ]
    pvt_temperature_owners_string_2_return: Annotated[
        sensor.TemperatureSensor, ComponentMeta("50009005-35")
    ]
    pvt_temperature_owners_string_3_return: Annotated[
        sensor.TemperatureSensor, ComponentMeta("50009005-36")
    ]
    pvt_temperature_owners_string_4_return: Annotated[
        sensor.TemperatureSensor, ComponentMeta("50009005-37")
    ]
    pvt_temperature_owners_string_5_return: Annotated[
        sensor.TemperatureSensor, ComponentMeta("50009005-38")
    ]
    pvt_temperature_owners_string_6_return: Annotated[
        sensor.TemperatureSensor, ComponentMeta("50009005-39")
    ]
    pvt_flow_owners_string_1: Annotated[sensor.FlowSensor, ComponentMeta("50009009-07")]
    pvt_flow_owners_string_2: Annotated[sensor.FlowSensor, ComponentMeta("50009009-08")]
    pvt_flow_owners_string_3: Annotated[sensor.FlowSensor, ComponentMeta("50009009-09")]
    pvt_flow_owners_string_4: Annotated[sensor.FlowSensor, ComponentMeta("50009009-10")]
    pvt_flow_owners_string_5: Annotated[sensor.FlowSensor, ComponentMeta("50009009-11")]
    pvt_flow_owners_string_6: Annotated[sensor.FlowSensor, ComponentMeta("50009009-12")]
    pvt_temperature_owners_string_1_supply: Annotated[
        sensor.TemperatureSensor, ComponentMeta("50009005-40")
    ]
    pvt_temperature_owners_string_2_supply: Annotated[
        sensor.TemperatureSensor, ComponentMeta("50009005-41")
    ]
    pvt_temperature_owners_string_3_supply: Annotated[
        sensor.TemperatureSensor, ComponentMeta("50009005-42")
    ]
    pvt_temperature_owners_string_4_supply: Annotated[
        sensor.TemperatureSensor, ComponentMeta("50009005-43")
    ]
    pvt_temperature_owners_string_5_supply: Annotated[
        sensor.TemperatureSensor, ComponentMeta("50009005-44")
    ]
    pvt_temperature_owners_string_6_supply: Annotated[
        sensor.TemperatureSensor, ComponentMeta("50009005-45")
    ]


class PvtControlValues(ThrsModel):
    pvt_pump_main_fwd: Annotated[control.Pump, ComponentMeta("50001018")]
    pvt_pump_main_aft: Annotated[control.Pump, ComponentMeta("50001019")]
    pvt_pump_owners: Annotated[control.Pump, ComponentMeta("50001021")]
    pvt_mix_main_fwd: Annotated[control.Valve, ComponentMeta("50001044-01")]
    pvt_mix_main_aft: Annotated[control.Valve, ComponentMeta("50001044-02")]
    pvt_mix_owners: Annotated[control.Valve, ComponentMeta("50001043-01")]
    pvt_flowcontrol_main_fwd: Annotated[control.Valve, ComponentMeta("50001067-01")]
    pvt_flowcontrol_main_aft: Annotated[control.Valve, ComponentMeta("50001067-02")]
    pvt_flowcontrol_owners: Annotated[control.Valve, ComponentMeta("50001069-01")]
    pvt_mix_exchanger: Annotated[control.Valve, ComponentMeta("50001047-02")]


class PvtSimulationInputs(SimulationInputs):
    pvt_main_fwd: simulation.HeatSource
    pvt_main_aft: simulation.HeatSource
    pvt_owners: simulation.HeatSource
    pvt_pump_failure_switch_main_fwd: simulation.ValvePosition
    pvt_pump_failure_switch_main_aft: simulation.ValvePosition
    pvt_pump_failure_switch_owners: simulation.ValvePosition
    pvt_module_supply: simulation.TemperatureBoundary
    pvt_seawater_supply: simulation.Boundary


class PvtSimulationOutputs(ThrsModel):
    pvt_module_return: simulation.Boundary
    pvt_module_supply: simulation.FlowBoundary
    pvt_seawater_return: simulation.TemperatureBoundary
