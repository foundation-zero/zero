from typing import Annotated

import thrs.input_output.definitions.control as control
import thrs.input_output.definitions.sensor as sensor
from thrs.input_output.definitions import simulation
from thrs.input_output.base import (
    ComponentMeta,
    SimulationInputs,
    ThrsModel,
)


class ThrustersSensorValues(ThrsModel):
    thrusters_pump_1: Annotated[sensor.Pump, ComponentMeta(yard_tag="50001194")]
    thrusters_pump_2: Annotated[sensor.Pump, ComponentMeta(yard_tag="50001195")]
    thrusters_temperature_aft_return: Annotated[
        sensor.TemperatureSensor, ComponentMeta(yard_tag="50001038-01")
    ]
    thrusters_temperature_fwd_return: Annotated[
        sensor.TemperatureSensor, ComponentMeta(yard_tag="50001038-02")
    ]
    thrusters_temperature_supply: Annotated[
        sensor.TemperatureSensor, ComponentMeta(yard_tag="50001038-28")
    ]
    thrusters_temperature_recovery_mix: Annotated[
        sensor.TemperatureSensor, ComponentMeta(yard_tag="50001038-30")
    ]
    thrusters_mix_recovery: Annotated[sensor.Valve, ComponentMeta(yard_tag="50001074")]
    thrusters_mix_exchanger: Annotated[sensor.Valve, ComponentMeta(yard_tag="50001214-01")]
    thrusters_flow_fwd: Annotated[sensor.FlowSensor, ComponentMeta(yard_tag="50001057-22")]
    thrusters_flow_aft: Annotated[sensor.FlowSensor, ComponentMeta(yard_tag="50001057-23")]
    thrusters_flowcontrol_aft: Annotated[sensor.Valve, ComponentMeta(yard_tag="50001215")]
    thrusters_flowcontrol_fwd: Annotated[sensor.Valve, ComponentMeta(yard_tag="50001064-02")]
    thrusters_shutoff_recovery: Annotated[sensor.Valve, ComponentMeta(yard_tag="50001066-03")]
    thrusters_switch_aft: Annotated[sensor.Valve, ComponentMeta(yard_tag="50001091-01")]
    thrusters_switch_fwd: Annotated[sensor.Valve, ComponentMeta(yard_tag="50001091-02")]
    thrusters_flow_recovery: Annotated[sensor.FlowSensor, ComponentMeta(yard_tag="50001093-01")]
    thrusters_pressure_pump: Annotated[
        sensor.PressureSensor, ComponentMeta(yard_tag="50001097-01")
    ]
    thrusters_pressure_relief: Annotated[
        sensor.PressureSensor, ComponentMeta(yard_tag="50001097-02")
    ]
    thrusters_aft: Annotated[
        sensor.Thruster, ComponentMeta(yard_tag="150001001", included_in_fmu=False)
    ]
    thrusters_fwd: Annotated[
        sensor.Thruster, ComponentMeta(yard_tag="150001002", included_in_fmu=False)
    ]
    thrusters_pcs: Annotated[sensor.Pcs, ComponentMeta(yard_tag="1500", included_in_fmu=False)]


class ThrustersControlValues(ThrsModel):
    thrusters_pump_1: Annotated[control.Pump, ComponentMeta(yard_tag="50001194")]
    thrusters_pump_2: Annotated[control.Pump, ComponentMeta(yard_tag="50001195")]
    thrusters_mix_recovery: Annotated[control.Valve, ComponentMeta(yard_tag="50001074")]
    thrusters_mix_exchanger: Annotated[control.Valve, ComponentMeta(yard_tag="50001214-01")]
    thrusters_flowcontrol_aft: Annotated[control.Valve, ComponentMeta(yard_tag="50001215")]
    thrusters_flowcontrol_fwd: Annotated[control.Valve, ComponentMeta(yard_tag="50001064-02")]
    thrusters_shutoff_recovery: Annotated[control.Valve, ComponentMeta(yard_tag="50001066-03")]
    thrusters_switch_aft: Annotated[control.Valve, ComponentMeta(yard_tag="50001091-01")]
    thrusters_switch_fwd: Annotated[control.Valve, ComponentMeta(yard_tag="50001091-02")]


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
