from typing import Annotated

from thrs.input_output.base import (
    SimulationInputs,
    SimulationValues,
    ThrsValues,
    component_meta,
)
from thrs.input_output.definitions import control, sensor, simulation


class BoilersSensorValues(ThrsValues):
    boilers_pump: Annotated[
        sensor.Pump, component_meta(yard_tag="50001022", component_type="pump")
    ]
    boilers_temperature_chiller_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-25", component_type="temperature_sensor"),
    ]
    boilers_temperature_converters_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-26", component_type="temperature_sensor"),
    ]
    boilers_temperature_tank3: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-27", component_type="temperature_sensor"),
    ]
    boilers_temperature_tank2: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-44", component_type="temperature_sensor"),
    ]
    boilers_temperature_tank1: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-45", component_type="temperature_sensor"),
    ]
    boilers_temperature_propdrive_shore_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-46", component_type="temperature_sensor"),
    ]
    boilers_temperature_freshwater_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-47", component_type="temperature_sensor"),
    ]
    boilers_temperature_fahrenheit_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-51", component_type="temperature_sensor"),
    ]
    boilers_temperature_boosting_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-65", component_type="temperature_sensor"),
    ]
    boilers_temperature_boosting_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-66", component_type="temperature_sensor"),
    ]
    boilers_level_tank1: Annotated[
        sensor.LevelSensor,
        component_meta(yard_tag="50001056-01", component_type="pressure_sensor"),
    ]
    boilers_level_tank2: Annotated[
        sensor.LevelSensor,
        component_meta(yard_tag="50001056-02", component_type="pressure_sensor"),
    ]
    boilers_level_tank3: Annotated[
        sensor.LevelSensor,
        component_meta(yard_tag="50001056-03", component_type="pressure_sensor"),
    ]
    boilers_flow_converters: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001057-17", component_type="flow_sensor"),
    ]
    boilers_flow_propdrive_shore: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001057-24", component_type="flow_sensor"),
    ]
    boilers_flow_boosting: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001058-11", component_type="flow_sensor"),
    ]
    boilers_flowcontrol_converters: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001064-03", component_type="valve", valve_type="flowcontrol"
        ),
    ]
    boilers_flowcontrol_propdrive_shore: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001064-08", component_type="valve", valve_type="flowcontrol"
        ),
    ]
    boilers_switch_tank3_fill: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001067-03", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_switch_tank3_boosting_return: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001067-04", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_switch_tank3_empty: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001067-05", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_switch_tank3_boosting_supply: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001067-06", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_switch_tank2_fill: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001067-07", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_switch_tank2_boosting_return: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001067-08", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_switch_tank2_empty: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001067-09", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_switch_tank2_boosting_supply: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001067-10", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_switch_tank1_fill: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001067-11", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_switch_tank1_boosting_return: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001067-12", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_switch_tank1_empty: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001067-13", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_switch_tank1_boosting_supply: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001067-14", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_switch_low_temperature: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001067-16", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_switch_heatpump: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001067-17", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_switch_high_temperature: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001067-18", component_type="valve", valve_type="switch"
        ),
    ]


class BoilersControlValues(ThrsValues):
    boilers_pump: Annotated[
        control.Pump, component_meta(yard_tag="50001022", component_type="pump")
    ]
    boilers_heatpump: Annotated[
        control.HeatPump, component_meta(yard_tag="50001035", component_type="heatpump")
    ]
    boilers_flowcontrol_converters: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001064-03", component_type="valve", valve_type="flowcontrol"
        ),
    ]
    boilers_flowcontrol_propdrive_shore: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001064-08", component_type="valve", valve_type="flowcontrol"
        ),
    ]
    boilers_switch_tank3_fill: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001067-03", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_switch_tank3_boosting_return: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001067-04", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_switch_tank3_empty: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001067-05", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_switch_tank3_boosting_supply: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001067-06", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_switch_tank2_fill: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001067-07", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_switch_tank2_boosting_return: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001067-08", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_switch_tank2_empty: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001067-09", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_switch_tank2_boosting_supply: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001067-10", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_switch_tank1_fill: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001067-11", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_switch_tank1_boosting_return: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001067-12", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_switch_tank1_empty: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001067-13", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_switch_tank1_boosting_supply: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001067-14", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_switch_low_temperature: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001067-16", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_switch_heatpump: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001067-17", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_switch_high_temperature: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001067-18", component_type="valve", valve_type="switch"
        ),
    ]


class BoilersSimulationInputs(SimulationInputs):
    boilers_propdrive_shore_supply: simulation.FmuBoundary
    boilers_fahrenheit_supply: simulation.FmuBoundary
    boilers_converters_supply: simulation.FmuBoundary
    boilers_high_temperature_supply: simulation.FmuBoundary
    boilers_freshwater_supply: simulation.TemperatureBoundary
    boilers_freshwater_pressure: simulation.PressureBoundary


class BoilersSimulationOutputs(SimulationValues):
    boilers_propdrive_shore_return: simulation.FmuBoundary
    boilers_fahrenheit_return: simulation.FmuBoundary
    boilers_converters_return: simulation.FmuBoundary
    boilers_high_temperature_return: simulation.FmuBoundary
    boilers_freshwater_return: simulation.FmuBoundary
