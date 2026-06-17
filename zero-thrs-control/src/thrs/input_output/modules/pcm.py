from typing import Annotated

from thrs.input_output.base import (
    SimulationInputs,
    SimulationValues,
    ThrsValues,
    component_meta,
)
from thrs.input_output.definitions import control, sensor, simulation


class PcmSensorValues(ThrsValues):
    pcm_pump: Annotated[
        sensor.Pump, component_meta(yard_tag="50001017", component_type="pump")
    ]
    pcm_temperature_producers_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-31", component_type="temperature_sensor"),
    ]
    pcm_temperature_producers_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-55", component_type="temperature_sensor"),
    ]
    pcm_temperature_module1: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-60", component_type="temperature_sensor"),
    ]
    pcm_temperature_module2: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-33", component_type="temperature_sensor"),
    ]
    pcm_temperature_module3: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-34", component_type="temperature_sensor"),
    ]
    pcm_temperature_module4: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-35", component_type="temperature_sensor"),
    ]
    pcm_module1: Annotated[
        sensor.Pcm, component_meta(yard_tag="50001049", component_type="pcm")
    ]
    pcm_module2: Annotated[
        sensor.Pcm, component_meta(yard_tag="50001050", component_type="pcm")
    ]
    pcm_module3: Annotated[
        sensor.Pcm, component_meta(yard_tag="50001051", component_type="pcm")
    ]
    pcm_module4: Annotated[
        sensor.Pcm, component_meta(yard_tag="50001052", component_type="pcm")
    ]
    pcm_flow_module1: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001057-18", component_type="flow_sensor"),
    ]
    pcm_flow_module2: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001057-19", component_type="flow_sensor"),
    ]
    pcm_flow_module3: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001057-20", component_type="flow_sensor"),
    ]
    pcm_flow_module4: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001057-21", component_type="flow_sensor"),
    ]
    pcm_switch_charging_return: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001062-02", component_type="valve", valve_type="switch"
        ),
    ]
    pcm_flowcontrol_module1: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001064-04", component_type="valve", valve_type="flowcontrol"
        ),
    ]
    pcm_flowcontrol_module2: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001064-05", component_type="valve", valve_type="flowcontrol"
        ),
    ]
    pcm_flowcontrol_module3: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001064-06", component_type="valve", valve_type="flowcontrol"
        ),
    ]
    pcm_flowcontrol_module4: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001064-07", component_type="valve", valve_type="flowcontrol"
        ),
    ]
    pcm_switch_discharging: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001066-01", component_type="valve", valve_type="switch"
        ),
    ]
    pcm_switch_charging_supply: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001190-01", component_type="valve", valve_type="switch"
        ),
    ]
    pcm_switch_consumers: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001071-02", component_type="valve", valve_type="switch"
        ),
    ]


class PcmControlValues(ThrsValues):
    pcm_pump: Annotated[
        control.Pump, component_meta(yard_tag="50001017", component_type="pump")
    ]
    pcm_switch_charging_return: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001062-02", component_type="valve", valve_type="switch"
        ),
    ]
    pcm_flowcontrol_module1: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001064-04", component_type="valve", valve_type="flowcontrol"
        ),
    ]
    pcm_flowcontrol_module2: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001064-05", component_type="valve", valve_type="flowcontrol"
        ),
    ]
    pcm_flowcontrol_module3: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001064-06", component_type="valve", valve_type="flowcontrol"
        ),
    ]
    pcm_flowcontrol_module4: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001064-07", component_type="valve", valve_type="flowcontrol"
        ),
    ]
    pcm_switch_discharging: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001066-01", component_type="valve", valve_type="switch"
        ),
    ]
    pcm_switch_charging_supply: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001190-01", component_type="valve", valve_type="switch"
        ),
    ]
    pcm_switch_consumers: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001071-02", component_type="valve", valve_type="switch"
        ),
    ]
    pcm_module1: Annotated[
        control.Pcm, component_meta(yard_tag="50001049", component_type="pcm")
    ]


class PcmSimulationInputs(SimulationInputs):
    # pcm_producers_supply: simulation.Boundary #TODO: make into pcm_pvt_supply
    pcm_thrusters_supply: simulation.Boundary
    pcm_freshwater_supply: simulation.Boundary
    pcm_consumers_supply: simulation.TemperatureBoundary


class PcmSimulationOutputs(SimulationValues):
    pcm_consumers_return: simulation.Boundary
    # pcm_thrusters_return: simulation.Boundary
    pcm_pvt_return: simulation.Boundary
    pcm_freshwater_return: simulation.Boundary
