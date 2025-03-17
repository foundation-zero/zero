from typing import Annotated

import input_output.definitions.control as control
import input_output.definitions.sensor as sensor
from input_output.definitions import simulation
from input_output.base import Meta, SimulationInputs, ThrsModel


class ThrustersSensorValues(ThrsModel):
    thrusters_pump_1: Annotated[sensor.Pump, Meta("5001015")]
    thrusters_pump_2: Annotated[sensor.Pump, Meta("5001016")]
    thrusters_temperature_aft_return: Annotated[
        sensor.TemperatureSensor, Meta("5001038-01")
    ]
    thrusters_temperature_fwd_return: Annotated[
        sensor.TemperatureSensor, Meta("5001038-02")
    ]
    thrusters_temperature_supply: Annotated[
        sensor.TemperatureSensor, Meta("5001038-28")
    ]
    thrusters_temperature_fwd_supply: Annotated[
        sensor.TemperatureSensor, Meta("5001038-29")
    ]
    thrusters_temperature_aft_supply: Annotated[
        sensor.TemperatureSensor, Meta("5001038-30")
    ]
    thrusters_mix_aft: Annotated[sensor.Valve, Meta("5001042-01")]
    thrusters_mix_fwd: Annotated[sensor.Valve, Meta("5001042-02")]
    thrusters_mix_exchanger: Annotated[sensor.Valve, Meta("5001045-02")]
    thrusters_flow_fwd: Annotated[sensor.FlowSensor, Meta("50001057-22")]
    thrusters_flow_aft: Annotated[sensor.FlowSensor, Meta("50001057-23")]
    thrusters_flowcontrol_aft: Annotated[sensor.Valve, Meta("5001064-01")]
    thrusters_flowcontrol_fwd: Annotated[sensor.Valve, Meta("5001064-02")]
    thrusters_shutoff_recovery: Annotated[sensor.Valve, Meta("5001069-10")]
    thrusters_pressure_recovery: Annotated[sensor.PressureSensor, Meta("5001097-01")]
    thrusters_pressure_cooling: Annotated[sensor.PressureSensor, Meta("5001097-02")]


class ThrustersControlValues(ThrsModel):
    thrusters_pump_1: Annotated[control.Pump, Meta("5001015")]
    thrusters_pump_2: Annotated[control.Pump, Meta("5001016")]
    thrusters_mix_aft: Annotated[control.Valve, Meta("5001042-01")]
    thrusters_mix_fwd: Annotated[control.Valve, Meta("5001042-02")]
    thrusters_mix_exchanger: Annotated[control.Valve, Meta("5001045-02")]
    thrusters_flowcontrol_aft: Annotated[control.Valve, Meta("5001064-01")]
    thrusters_flowcontrol_fwd: Annotated[control.Valve, Meta("5001064-02")]
    thrusters_shutoff_recovery: Annotated[control.Valve, Meta("5001069-10")]
    thrusters_switch_aft: Annotated[control.Valve, Meta("5001091-01")]
    thrusters_switch_fwd: Annotated[control.Valve, Meta("5001091-02")]


class ThrustersSimulationInputs(SimulationInputs):
    aft: simulation.HeatSource
    fwd: simulation.HeatSource
    seawater_supply: simulation.Boundary
    module_supply: simulation.Boundary


class ThrustersSimulationOutputs(ThrsModel):
    seawater_supply: simulation.Boundary
    seawater_return: simulation.Boundary
    module_supply: simulation.Boundary
    module_return: simulation.Boundary
