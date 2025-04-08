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
    # pvt_temperature_owners_supply: Annotated[
    #     sensor.TemperatureSensor, ComponentMeta("50001038-21")
    # ]
    # pvt_temperature_owners_return: Annotated[
    #     sensor.TemperatureSensor, ComponentMeta("50001038-04")]
    pvt_temperature_aft_supply: Annotated[
        sensor.TemperatureSensor, ComponentMeta("50001038-21")
    ] # TODO: replace after update FMU
    pvt_temperature_aft_return: Annotated[
        sensor.TemperatureSensor, ComponentMeta("50001038-04")
    ] # TODO: replace after update FMU
    pvt_mix_main_fwd: Annotated[sensor.Valve, ComponentMeta("50001044-01")]
    pvt_mix_main_aft: Annotated[sensor.Valve, ComponentMeta("50001044-02")]
    pvt_mix_owners: Annotated[sensor.Valve, ComponentMeta("50001043-01")]
    pvt_flow_main_fwd: Annotated[sensor.FlowSensor, ComponentMeta("50001058-12")]
    pvt_flow_main_aft: Annotated[sensor.FlowSensor, ComponentMeta("50001058-13")]
    pvt_flow_owners: Annotated[sensor.FlowSensor, ComponentMeta("50001057-03")]
    # pvt_pressure_main_fwd: Annotated[sensor.PressureSensor, ComponentMeta("50001097-03")]
    # pvt_pressure_main_aft: Annotated[sensor.PressureSensor, ComponentMeta("50001097-04")]
    # pvt_pressure_owners: Annotated[sensor.PressureSensor, ComponentMeta("50001097-05")] # TODO: replace after update FMU
    pvt_flowcontrol_main_fwd: Annotated[sensor.Valve, ComponentMeta("50001067-01")]
    pvt_flowcontrol_main_aft: Annotated[sensor.Valve, ComponentMeta("50001067-02")]
    pvt_flowcontrol_owners: Annotated[sensor.Valve, ComponentMeta("50001069-01")]
    pvt_mix_exchanger: Annotated[sensor.Valve, ComponentMeta("50001047-02")]
    pvt_temperature_exchanger: Annotated[sensor.TemperatureSensor, ComponentMeta("50001038-24")]


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
