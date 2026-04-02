from typing import Annotated
from thrs.input_output.base import (
    SimulationInputs,
    SimulationValues,
    ThrsValues,
    component_meta,
)
from thrs.input_output.definitions import control, sensor, simulation


class Lt1SensorValues(ThrsValues):
    lt1_pump1: Annotated[
        sensor.Pump, component_meta(yard_tag="50001028", component_type="pump")
    ]
    lt1_pump2: Annotated[
        sensor.Pump, component_meta(yard_tag="50001029", component_type="pump")
    ]
    lt1_temperature_shorepower_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-11", component_type="temperature_sensor"),
    ]
    lt1_temperature_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-14", component_type="temperature_sensor"),
    ]
    lt1_temperature_recovery: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-16", component_type="temperature_sensor"),
    ]
    lt1_temperature_recovery_mix: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-57", component_type="temperature_sensor"),
    ]
    lt1_temperature_recovery_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-59", component_type="temperature_sensor"),
    ]
    lt1_temperature_propdrive_aft1_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-32", component_type="temperature_sensor"),
    ]
    lt1_temperature_propdrive_fwd1_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-61", component_type="temperature_sensor"),
    ]
    lt1_temperature_propdrive_fwd_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-62", component_type="temperature_sensor"),
    ]
    lt1_temperature_propdrive_aft_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-63", component_type="temperature_sensor"),
    ]
    lt1_temperature_propdrive_aft2_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-64", component_type="temperature_sensor"),
    ]
    lt1_temperature_propdrive_fwd2_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-72", component_type="temperature_sensor"),
    ]
    lt1_mix_exchanger: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001046-01", component_type="valve", valve_type="mix"
        ),
    ]
    lt1_mix_recovery: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001046-03", component_type="valve", valve_type="mix"
        ),
    ]
    lt1_flow_shorepower: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001057-10", component_type="flow_sensor"),
    ]
    lt1_flow_propdrive_aft1: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001057-13", component_type="flow_sensor"),
    ]
    lt1_flow_propdrive_fwd2: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001057-14", component_type="flow_sensor"),
    ]
    lt1_flow_propdrive_fwd1: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001057-15", component_type="flow_sensor"),
    ]
    lt1_flow_propdrive_aft2: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001057-16", component_type="flow_sensor"),
    ]
    lt1_flow_recovery: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001058-03", component_type="flow_sensor"),
    ]
    lt1_switch_propdrive_aft: Annotated[  # TODO: rename lt1_flowcontrol_propdrives_aft
        sensor.Valve,
        component_meta(
            yard_tag="50001065-02", component_type="valve", valve_type="switch"
        ),
    ]
    lt1_switch_propdrive_fwd: Annotated[  # TODO: rename lt1_flowcontrol_propdrives_fwd
        sensor.Valve,
        component_meta(
            yard_tag="50001065-03", component_type="valve", valve_type="switch"
        ),
    ]
    lt1_switch_shorepower_supply: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001069-04", component_type="valve", valve_type="switch"
        ),
    ]
    lt1_switch_shorepower_return: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001069-05", component_type="valve", valve_type="switch"
        ),
    ]
    lt1_switch_propdrive_aft1: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001069-06", component_type="valve", valve_type="switch"
        ),
    ]
    lt1_switch_propdrive_aft2: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001069-09", component_type="valve", valve_type="switch"
        ),
    ]
    lt1_switch_propdrive_fwd1: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001069-07", component_type="valve", valve_type="switch"
        ),
    ]
    lt1_switch_propdrive_fwd2: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001069-08", component_type="valve", valve_type="switch"
        ),
    ]
    lt1_pressure: Annotated[
        sensor.PressureSensor,
        component_meta(yard_tag="50001097-10", component_type="pressure_sensor"),
    ]
    lt1_propdrive_aft1: Annotated[
        sensor.PropulsionDrive,
        component_meta(
            yard_tag="45002079",  # TODO: figure out correct yard tag. We do expect separate signal from each Aradex
            component_type="propulsion_drive",
            included_in_fmu=False,
        ),
    ]
    lt1_propdrive_aft2: Annotated[
        sensor.PropulsionDrive,
        component_meta(
            yard_tag="45002079",  # TODO: figure out correct yard tag. We do expect separate signal from each Aradex
            component_type="propulsion_drive",
            included_in_fmu=False,
        ),
    ]
    lt1_propdrive_fwd1: Annotated[
        sensor.PropulsionDrive,
        component_meta(
            yard_tag="45002080",  # TODO: figure out correct yard tag. We do expect separate signal from each Aradex
            component_type="propulsion_drive",
            included_in_fmu=False,
        ),
    ]
    lt1_propdrive_fwd2: Annotated[
        sensor.PropulsionDrive,
        component_meta(
            yard_tag="45002080",  # TODO: figure out correct yard tag. We do expect separate signal from each Aradex
            component_type="propulsion_drive",
            included_in_fmu=False,
        ),
    ]
    lt1_shorepower: Annotated[
        sensor.ShorePowerConverter,
        component_meta(
            yard_tag="45002001",
            component_type="shore_power_converter",
            included_in_fmu=False,
        ),
    ]


class Lt1ControlValues(ThrsValues):
    lt1_pump1: Annotated[
        control.Pump, component_meta(yard_tag="50001028", component_type="pump")
    ]
    lt1_pump2: Annotated[
        control.Pump, component_meta(yard_tag="50001029", component_type="pump")
    ]
    lt1_mix_exchanger: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001046-01", component_type="valve", valve_type="mix"
        ),
    ]
    lt1_mix_recovery: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001046-03", component_type="valve", valve_type="mix"
        ),
    ]
    lt1_switch_propdrive_aft: Annotated[  # TODO: Rename to flowcontrol valve
        control.Valve,
        component_meta(
            yard_tag="50001065-02", component_type="valve", valve_type="switch"
        ),
    ]
    lt1_switch_propdrive_fwd: Annotated[  # TODO: Rename to flowcontrol valve
        control.Valve,
        component_meta(
            yard_tag="50001065-03", component_type="valve", valve_type="switch"
        ),
    ]
    lt1_switch_shorepower_supply: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001069-04", component_type="valve", valve_type="switch"
        ),
    ]
    lt1_switch_shorepower_return: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001069-05", component_type="valve", valve_type="switch"
        ),
    ]
    lt1_switch_propdrive_aft1: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001069-06", component_type="valve", valve_type="switch"
        ),
    ]
    lt1_switch_propdrive_aft2: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001069-09", component_type="valve", valve_type="switch"
        ),
    ]
    lt1_switch_propdrive_fwd1: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001069-07", component_type="valve", valve_type="switch"
        ),
    ]
    lt1_switch_propdrive_fwd2: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001069-08", component_type="valve", valve_type="switch"
        ),
    ]


class Lt1SimulationInputs(SimulationInputs):
    lt1_oil_cooler_aft: simulation.HeatSource
    lt1_oil_cooler_fwd: simulation.HeatSource
    lt1_propdrive_aft1: simulation.PropulsionDrive
    lt1_propdrive_aft2: simulation.PropulsionDrive
    lt1_propdrive_fwd1: simulation.PropulsionDrive
    lt1_propdrive_fwd2: simulation.PropulsionDrive
    lt1_shorepower: simulation.Converter
    lt1_seawater_supply: simulation.Boundary
    lt1_boilers_supply: simulation.Boundary


class Lt1SimulationOutputs(SimulationValues):
    lt1_seawater_return: simulation.TemperatureBoundary
    lt1_boilers_return: simulation.TemperatureBoundary
