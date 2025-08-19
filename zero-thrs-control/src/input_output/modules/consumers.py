from typing import Annotated
from input_output.base import ParameterMeta, SimulationInputs, ThrsModel
from input_output.definitions import control, sensor, simulation


class ConsumersSensorValues(ThrsModel):
    consumers_switch_fahrenheit_direct_supply: Annotated[
        sensor.Valve, ParameterMeta("50001074")
    ]
    consumers_temperature_boosting_return: Annotated[
        sensor.TemperatureSensor, ParameterMeta("50001038-48")
    ]
    consumers_temperature_fahrenheit_return: Annotated[
        sensor.TemperatureSensor, ParameterMeta("50001038-49")
    ]
    consumers_temperature_boosting_supply: Annotated[
        sensor.TemperatureSensor, ParameterMeta("50001038-53")
    ]
    consumers_temperature_fahrenheit_supply: Annotated[
        sensor.TemperatureSensor, ParameterMeta("50001038-54")
    ]
    consumers_flow_boosting: Annotated[sensor.FlowSensor, ParameterMeta("50001058-07")]
    consumers_flow_fahrenheit: Annotated[
        sensor.FlowSensor, ParameterMeta("50001058-08")
    ]
    consumers_flow_bypass: Annotated[sensor.FlowSensor, ParameterMeta("50001060-01")]
    consumers_flowcontrol_fahrenheit: Annotated[sensor.Valve, ParameterMeta("50001061")]
    consumers_flowcontrol_bypass: Annotated[sensor.Valve, ParameterMeta("50001062-01")]
    consumers_flowcontrol_boosting: Annotated[
        sensor.Valve, ParameterMeta("50001065-01")
    ]
    consumers_switch_fahrenheit_exchanger: Annotated[
        sensor.Valve, ParameterMeta("50001066-02")
    ]
    consumers_switch_fahrenheit_direct_return: Annotated[
        sensor.Valve, ParameterMeta("50001066-03")
    ]
    consumers_switch_boosting: Annotated[sensor.Valve, ParameterMeta("50001067-15")]


class ConsumersControlValues(ThrsModel):
    consumers_switch_fahrenheit_direct_supply: Annotated[
        control.Valve, ParameterMeta("50001074")
    ]
    consumers_flowcontrol_fahrenheit: Annotated[
        control.Valve, ParameterMeta("50001061")
    ]
    consumers_flowcontrol_bypass: Annotated[control.Valve, ParameterMeta("50001062-01")]
    consumers_flowcontrol_boosting: Annotated[
        control.Valve, ParameterMeta("50001065-01")
    ]
    consumers_switch_fahrenheit_exchanger: Annotated[
        control.Valve, ParameterMeta("50001066-02")
    ]
    consumers_switch_fahrenheit_direct_return: Annotated[
        control.Valve, ParameterMeta("50001066-03")
    ]
    consumers_switch_boosting: Annotated[control.Valve, ParameterMeta("50001067-15")]


class ConsumersSimulationInputs(SimulationInputs):
    consumers_fahrenheit_supply: simulation.Boundary
    consumers_module_supply: simulation.Boundary
    consumers_boosting_supply: simulation.Boundary


class ConsumersSimulationOutputs(ThrsModel):
    consumers_fahrenheit_return: simulation.Boundary
    consumers_boosting_return: simulation.Boundary
    consumers_module_return: simulation.Boundary
