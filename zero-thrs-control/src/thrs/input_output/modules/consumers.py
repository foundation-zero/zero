from typing import Annotated
from thrs.input_output.base import (
    SimulationInputs,
    SimulationValues,
    ThrsModel,
    component_meta,
)
from thrs.input_output.definitions import control, sensor, simulation


class ConsumersSensorValues(ThrsModel):
    consumers_temperature_boosting_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-48", component_type="temperature_sensor"),
    ]
    consumers_temperature_fahrenheit_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-49", component_type="temperature_sensor"),
    ]
    consumers_temperature_boosting_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-53", component_type="temperature_sensor"),
    ]
    consumers_temperature_fahrenheit_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-54", component_type="temperature_sensor"),
    ]
    consumers_flow_boosting: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001058-07", component_type="flow_sensor"),
    ]
    consumers_flow_fahrenheit: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001058-08", component_type="flow_sensor"),
    ]
    consumers_flow_bypass: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001060-01", component_type="flow_sensor"),
    ]
    consumers_flowcontrol_fahrenheit: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001061", component_type="valve", valve_type="flowcontrol"
        ),
    ]
    consumers_flowcontrol_bypass: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001062-01", component_type="valve", valve_type="flowcontrol"
        ),
    ]
    consumers_flowcontrol_boosting: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001065-01", component_type="valve", valve_type="flowcontrol"
        ),
    ]
    consumers_switch_fahrenheit_exchanger: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001066-02", component_type="valve", valve_type="switch"
        ),
    ]

    consumers_switch_boosting: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001067-15", component_type="valve", valve_type="switch"
        ),
    ]


class ConsumersControlValues(ThrsModel):
    consumers_flowcontrol_fahrenheit: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001061", component_type="valve", valve_type="flowcontrol"
        ),
    ]
    consumers_flowcontrol_bypass: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001062-01", component_type="valve", valve_type="flowcontrol"
        ),
    ]
    consumers_flowcontrol_boosting: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001065-01", component_type="valve", valve_type="flowcontrol"
        ),
    ]
    consumers_switch_fahrenheit_exchanger: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001066-02", component_type="valve", valve_type="switch"
        ),
    ]

    consumers_switch_boosting: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001067-15", component_type="valve", valve_type="switch"
        ),
    ]


class ConsumersSimulationInputs(SimulationInputs):
    consumers_fahrenheit_supply: simulation.FmuBoundary
    consumers_boosting_supply: simulation.FmuBoundary
    consumers_module_supply: simulation.Boundary


class ConsumersSimulationOutputs(SimulationValues):
    consumers_fahrenheit_return: simulation.FmuBoundary
    consumers_boosting_return: simulation.FmuBoundary
    consumers_module_return: simulation.Boundary
