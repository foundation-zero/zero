from typing import Annotated

from thrs.input_output.base import (
    SimulationInputs,
    SimulationValues,
    ThrsValues,
    component_meta,
)
from thrs.input_output.definitions import control, sensor, simulation


class ConsumersSensorValues(ThrsValues):
    consumers_temperature_dhw_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-48", component_type="temperature_sensor"),
    ]
    consumers_temperature_adsorption_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-49", component_type="temperature_sensor"),
    ]
    consumers_temperature_dhw_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-53", component_type="temperature_sensor"),
    ]
    consumers_temperature_adsorption_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-54", component_type="temperature_sensor"),
    ]
    consumers_flow_dhw: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001058-07", component_type="flow_sensor"),
    ]
    consumers_flow_adsorption: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001058-08", component_type="flow_sensor"),
    ]
    consumers_flow_bypass: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001192", component_type="flow_sensor"),
    ]
    consumers_flowcontrol_adsorption: Annotated[
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
    consumers_flowcontrol_dhw: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001065-01", component_type="valve", valve_type="flowcontrol"
        ),
    ]
    consumers_switch_adsorption: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001066-02", component_type="valve", valve_type="switch"
        ),
    ]

    consumers_switch_dhw: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001067-15", component_type="valve", valve_type="switch"
        ),
    ]


class ConsumersControlValues(ThrsValues):
    consumers_flowcontrol_adsorption: Annotated[
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
    consumers_flowcontrol_dhw: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001065-01", component_type="valve", valve_type="flowcontrol"
        ),
    ]
    consumers_switch_adsorption: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001066-02", component_type="valve", valve_type="switch"
        ),
    ]

    consumers_switch_dhw: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001067-15", component_type="valve", valve_type="switch"
        ),
    ]


class ConsumersSimulationInputs(SimulationInputs):
    consumers_adsorption_supply: simulation.Boundary
    consumers_dhw_supply: simulation.Boundary
    consumers_pcm_supply: simulation.Boundary


class ConsumersSimulationOutputs(SimulationValues):
    consumers_adsorption_exchanger: simulation.ExchangerBoundary
    consumers_dhw_exchanger: simulation.ExchangerBoundary
    consumers_pcm_return: simulation.Boundary
