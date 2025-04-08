from typing import Annotated

import input_output.definitions.control as control
import input_output.definitions.sensor as sensor
from input_output.definitions import simulation
from input_output.base import ComponentMeta, SimulationInputs, ThrsModel


class ThrustersSensorValues(ThrsModel):
    thrusters_pump_1: Annotated[sensor.Pump, ComponentMeta("5001015")]
    thrusters_pump_2: Annotated[sensor.Pump, ComponentMeta("5001016")]
    thrusters_temperature_aft_return: Annotated[
        sensor.TemperatureSensor, ComponentMeta("5001038-01")
    ]
    thrusters_temperature_fwd_return: Annotated[
        sensor.TemperatureSensor, ComponentMeta("5001038-02")
    ]
    thrusters_temperature_supply: Annotated[
        sensor.TemperatureSensor, ComponentMeta("5001038-28")
    ]
    thrusters_temperature_fwd_mix: Annotated[
        sensor.TemperatureSensor, ComponentMeta("5001038-29")
    ]
    thrusters_temperature_aft_mix: Annotated[
        sensor.TemperatureSensor, ComponentMeta("5001038-30")
    ]
    thrusters_mix_aft: Annotated[sensor.Valve, ComponentMeta("5001042-01")]
    thrusters_mix_fwd: Annotated[sensor.Valve, ComponentMeta("5001042-02")]
    thrusters_mix_exchanger: Annotated[sensor.Valve, ComponentMeta("5001045-02")]
    thrusters_flow_fwd: Annotated[sensor.FlowSensor, ComponentMeta("50001057-22")]
    thrusters_flow_aft: Annotated[sensor.FlowSensor, ComponentMeta("50001057-23")]
    thrusters_flowcontrol_aft: Annotated[sensor.Valve, ComponentMeta("5001064-01")]
    thrusters_flowcontrol_fwd: Annotated[sensor.Valve, ComponentMeta("5001064-02")]
    thrusters_shutoff_recovery: Annotated[sensor.Valve, ComponentMeta("5001069-10")]
    thrusters_switch_aft: Annotated[sensor.Valve, ComponentMeta("50001091-01")]
    thrusters_switch_fwd: Annotated[sensor.Valve, ComponentMeta("50001091-02")]
    thrusters_flow_recovery_aft: Annotated[sensor.FlowSensor, ComponentMeta("5001093-01")]
    thrusters_flow_recovery_fwd: Annotated[sensor.FlowSensor, ComponentMeta("5001093-02")]
    thrusters_pressure_recovery: Annotated[sensor.PressureSensor, ComponentMeta("50001097-01")]
    thrusters_pressure_cooling: Annotated[sensor.PressureSensor, ComponentMeta("50001097-02")]

    thrusters_aft: Annotated[sensor.Thruster, ComponentMeta("15001001", included_in_fmu=False)]
    thrusters_fwd: Annotated[sensor.Thruster, ComponentMeta("15001002", included_in_fmu=False)]
    thrusters_pcs: Annotated[sensor.Pcs, ComponentMeta("1500", included_in_fmu=False)]


class ThrustersControlValues(ThrsModel):
    thrusters_pump_1: Annotated[control.Pump, ComponentMeta("5001015")]
    thrusters_pump_2: Annotated[control.Pump, ComponentMeta("5001016")]
    thrusters_mix_aft: Annotated[control.Valve, ComponentMeta("5001042-01")]
    thrusters_mix_fwd: Annotated[control.Valve, ComponentMeta("5001042-02")]
    thrusters_mix_exchanger: Annotated[control.Valve, ComponentMeta("5001045-02")]
    thrusters_flowcontrol_aft: Annotated[control.Valve, ComponentMeta("5001064-01")]
    thrusters_flowcontrol_fwd: Annotated[control.Valve, ComponentMeta("5001064-02")]
    thrusters_shutoff_recovery: Annotated[control.Valve, ComponentMeta("5001069-10")]
    thrusters_switch_aft: Annotated[control.Valve, ComponentMeta("5001091-01")]
    thrusters_switch_fwd: Annotated[control.Valve, ComponentMeta("5001091-02")]


class ThrustersSimulationInputs(SimulationInputs):
    thrusters_aft: simulation.Thruster
    thrusters_fwd: simulation.Thruster
    thrusters_seawater_supply: simulation.Boundary
    thrusters_module_supply: simulation.TemperatureBoundary
    thrusters_pcs: simulation.Pcs


class ThrustersSimulationOutputs(ThrsModel):
    thrusters_seawater_return: simulation.TemperatureBoundary
    thrusters_module_supply: simulation.FlowBoundary
    thrusters_module_return: simulation.Boundary
