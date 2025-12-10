from typing import Annotated
from thrs.input_output.base import (
    SimulationInputs,
    SimulationValues,
    ThrsValues,
    component_meta,
)
from thrs.input_output.definitions import control, sensor, simulation


class FahrenheitSensorValues(ThrsValues):
    fahrenheit_flowcontrol_waste: Annotated[
        sensor.Valve, component_meta(yard_tag="50001062-03", component_type="valve")
    ]
    fahrenheit_mix_hot: Annotated[
        sensor.Valve, component_meta(yard_tag="50001046-02", component_type="valve")
    ]
    fahrenheit_mix_waste: Annotated[
        sensor.Valve, component_meta(yard_tag="50001047-01", component_type="valve")
    ]
    fahrenheit_chiller: Annotated[
        sensor.Fahrenheit,
        component_meta(yard_tag="50001034", component_type="fahrenheit"),
    ]
    fahrenheit_flow_hot_exchanger: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001058-09", component_type="flow_sensor"),
    ]
    fahrenheit_flow_hot: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001058-02", component_type="flow_sensor"),
    ]
    fahrenheit_flow_waste: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001059", component_type="flow_sensor"),
    ]
    fahrenheit_flow_cold: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001058-05", component_type="flow_sensor"),
    ]
    fahrenheit_flow_boiler: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001058-10", component_type="flow_sensor"),
    ]
    fahrenheit_temperature_hot_exchanger_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-41", component_type="temperature_sensor"),
    ]
    fahrenheit_temperature_hot_exchanger_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-50", component_type="temperature_sensor"),
    ]
    fahrenheit_temperature_hot_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-36", component_type="temperature_sensor"),
    ]
    fahrenheit_temperature_hot_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-37", component_type="temperature_sensor"),
    ]
    fahrenheit_temperature_waste_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-38", component_type="temperature_sensor"),
    ]
    fahrenheit_temperature_waste_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-39", component_type="temperature_sensor"),
    ]
    fahrenheit_temperature_cold_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-42", component_type="temperature_sensor"),
    ]
    fahrenheit_temperature_cold_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-43", component_type="temperature_sensor"),
    ]
    fahrenheit_temperature_boiler_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-56", component_type="temperature_sensor"),
    ]


class FahrenheitControlValues(ThrsValues):
    fahrenheit_flowcontrol_waste: Annotated[
        control.Valve, component_meta(yard_tag="50001062-03", component_type="valve")
    ]
    fahrenheit_mix_hot: Annotated[
        control.Valve, component_meta(yard_tag="50001046-02", component_type="valve")
    ]
    fahrenheit_mix_waste: Annotated[
        control.Valve, component_meta(yard_tag="50001047-01", component_type="valve")
    ]
    fahrenheit_chiller: Annotated[
        control.Fahrenheit,
        component_meta(yard_tag="50001034", component_type="fahrenheit"),
    ]


class FahrenheitSimulationInputs(SimulationInputs):
    fahrenheit_hot_supply: simulation.FmuBoundary
    fahrenheit_waste_supply: simulation.FmuBoundary
    fahrenheit_cold_supply: simulation.TemperatureBoundary


class FahrenheitSimulationOutputs(SimulationValues):
    fahrenheit_hot_return: simulation.FmuBoundary
    fahrenheit_waste_return: simulation.FmuBoundary
