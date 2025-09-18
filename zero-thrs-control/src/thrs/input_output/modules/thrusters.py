from typing import Annotated

import thrs.input_output.definitions.control as control
import thrs.input_output.definitions.sensor as sensor
from thrs.input_output.definitions import simulation
from thrs.input_output.base import (
    SimulationInputs,
    ThrsModel,
    component_meta,
)


class ThrustersSensorValues(ThrsModel):
    thrusters_pump_1: Annotated[sensor.Pump, component_meta(yard_tag="5001015")]
    thrusters_pump_2: Annotated[sensor.Pump, component_meta(yard_tag="5001016")]
    thrusters_temperature_aft_return: Annotated[
        sensor.TemperatureSensor, component_meta(yard_tag="5001038-01")
    ]
    thrusters_temperature_fwd_return: Annotated[
        sensor.TemperatureSensor, component_meta(yard_tag="5001038-02")
    ]
    thrusters_temperature_supply: Annotated[
        sensor.TemperatureSensor, component_meta(yard_tag="5001038-28")
    ]
    thrusters_temperature_fwd_mix: Annotated[
        sensor.TemperatureSensor, component_meta(yard_tag="5001038-29")
    ]
    thrusters_temperature_aft_mix: Annotated[
        sensor.TemperatureSensor, component_meta(yard_tag="5001038-30")
    ]
    thrusters_mix_aft: Annotated[
        sensor.Valve, component_meta(yard_tag="5001042-01", valve_type="mix")
    ]
    thrusters_mix_fwd: Annotated[
        sensor.Valve, component_meta(yard_tag="5001042-02", valve_type="mix")
    ]
    thrusters_mix_exchanger: Annotated[
        sensor.Valve, component_meta(yard_tag="5001045-02", valve_type="mix")
    ]
    thrusters_flow_fwd: Annotated[
        sensor.FlowSensor, component_meta(yard_tag="50001057-22")
    ]
    thrusters_flow_aft: Annotated[
        sensor.FlowSensor, component_meta(yard_tag="50001057-23")
    ]
    thrusters_flowcontrol_aft: Annotated[
        sensor.Valve, component_meta(yard_tag="5001064-01", valve_type="flowcontrol")
    ]
    thrusters_flowcontrol_fwd: Annotated[
        sensor.Valve, component_meta(yard_tag="5001064-02", valve_type="flowcontrol")
    ]
    thrusters_shutoff_recovery: Annotated[
        sensor.Valve, component_meta(yard_tag="5001069-10", valve_type="shutoff")
    ]
    thrusters_switch_aft: Annotated[
        sensor.Valve, component_meta(yard_tag="50001091-01", valve_type="switch")
    ]
    thrusters_switch_fwd: Annotated[
        sensor.Valve, component_meta(yard_tag="50001091-02", valve_type="switch")
    ]
    thrusters_flow_recovery_aft: Annotated[
        sensor.FlowSensor, component_meta(yard_tag="5001093-01")
    ]
    thrusters_flow_recovery_fwd: Annotated[
        sensor.FlowSensor, component_meta(yard_tag="5001093-02")
    ]
    thrusters_pressure_recovery: Annotated[
        sensor.PressureSensor, component_meta(yard_tag="50001097-01")
    ]
    thrusters_pressure_cooling: Annotated[
        sensor.PressureSensor, component_meta(yard_tag="50001097-02")
    ]

    thrusters_aft: Annotated[
        sensor.Thruster, component_meta(yard_tag="15001001", included_in_fmu=False)
    ]
    thrusters_fwd: Annotated[
        sensor.Thruster, component_meta(yard_tag="15001002", included_in_fmu=False)
    ]
    thrusters_pcs: Annotated[
        sensor.Pcs, component_meta(yard_tag="1500", included_in_fmu=False)
    ]


class ThrustersControlValues(ThrsModel):
    thrusters_pump_1: Annotated[
        control.Pump, component_meta(yard_tag="5001015", component_type="pump")
    ]
    thrusters_pump_2: Annotated[
        control.Pump, component_meta(yard_tag="5001016", component_type="pump")
    ]
    thrusters_mix_aft: Annotated[
        control.Valve,
        component_meta(yard_tag="5001042-01", component_type="valve", valve_type="mix"),
    ]
    thrusters_mix_fwd: Annotated[
        control.Valve,
        component_meta(yard_tag="5001042-02", component_type="valve", valve_type="mix"),
    ]
    thrusters_mix_exchanger: Annotated[
        control.Valve,
        component_meta(yard_tag="5001045-02", component_type="valve", valve_type="mix"),
    ]
    thrusters_flowcontrol_aft: Annotated[
        control.Valve,
        component_meta(
            yard_tag="5001064-01", component_type="valve", valve_type="flowcontrol"
        ),
    ]
    thrusters_flowcontrol_fwd: Annotated[
        control.Valve,
        component_meta(
            yard_tag="5001064-02", component_type="valve", valve_type="flowcontrol"
        ),
    ]
    thrusters_shutoff_recovery: Annotated[
        control.Valve,
        component_meta(
            yard_tag="5001069-10", component_type="valve", valve_type="shutoff"
        ),
    ]
    thrusters_switch_aft: Annotated[
        control.Valve,
        component_meta(
            yard_tag="5001091-01", component_type="valve", valve_type="switch"
        ),
    ]
    thrusters_switch_fwd: Annotated[
        control.Valve,
        component_meta(
            yard_tag="5001091-02", component_type="valve", valve_type="switch"
        ),
    ]


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
