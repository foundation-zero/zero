from typing import Annotated
from thrs.input_output.base import SimulationInputs, ThrsModel, component_meta
from thrs.input_output.definitions import control, sensor, simulation


class FahrenheitSensorValues(ThrsModel):
    fahrenheit_flowcontrol_waste: Annotated[
        sensor.Valve, component_meta(yard_tag="50001062-03")
    ]
    fahrenheit_mix_hot: Annotated[sensor.Valve, component_meta(yard_tag="50001046-02")]
    fahrenheit_mix_waste: Annotated[
        sensor.Valve, component_meta(yard_tag="50001047-01")
    ]
    fahrenheit_chiller: Annotated[
        sensor.Fahrenheit, component_meta(yard_tag="50001034")
    ]
    fahrenheit_flow_hot_exchanger: Annotated[
        sensor.FlowSensor, component_meta(yard_tag="50001058-09")
    ]
    fahrenheit_flow_hot: Annotated[
        sensor.FlowSensor, component_meta(yard_tag="50001058-02")
    ]
    fahrenheit_flow_waste: Annotated[
        sensor.FlowSensor, component_meta(yard_tag="50001059")
    ]
    fahrenheit_flow_cold: Annotated[
        sensor.FlowSensor, component_meta(yard_tag="50001058-05")
    ]
    fahrenheit_flow_boiler: Annotated[
        sensor.FlowSensor, component_meta(yard_tag="50001058-10")
    ]
    fahrenheit_temperature_hot_exchanger_return: Annotated[
        sensor.TemperatureSensor, component_meta(yard_tag="50001038-41")
    ]
    fahrenheit_temperature_hot_exchanger_supply: Annotated[
        sensor.TemperatureSensor, component_meta(yard_tag="50001038-50")
    ]
    fahrenheit_temperature_hot_return: Annotated[
        sensor.TemperatureSensor, component_meta(yard_tag="50001038-36")
    ]
    fahrenheit_temperature_hot_supply: Annotated[
        sensor.TemperatureSensor, component_meta(yard_tag="50001038-37")
    ]
    fahrenheit_temperature_waste_return: Annotated[
        sensor.TemperatureSensor, component_meta(yard_tag="50001038-38")
    ]
    fahrenheit_temperature_waste_supply: Annotated[
        sensor.TemperatureSensor, component_meta(yard_tag="50001038-39")
    ]
    fahrenheit_temperature_cold_return: Annotated[
        sensor.TemperatureSensor, component_meta(yard_tag="50001038-42")
    ]
    fahrenheit_temperature_cold_supply: Annotated[
        sensor.TemperatureSensor, component_meta(yard_tag="50001038-43")
    ]
    fahrenheit_temperature_boiler_return: Annotated[
        sensor.TemperatureSensor, component_meta(yard_tag="50001038-56")
    ]


class FahrenheitControlValues(ThrsModel):
    fahrenheit_flowcontrol_waste: Annotated[
        control.Valve, component_meta(yard_tag="50001062-03")
    ]
    fahrenheit_mix_hot: Annotated[control.Valve, component_meta(yard_tag="50001046-02")]
    fahrenheit_mix_waste: Annotated[
        control.Valve, component_meta(yard_tag="50001047-01")
    ]
    fahrenheit_chiller: Annotated[
        control.Fahrenheit, component_meta(yard_tag="50001034")
    ]


class FahrenheitSimulationInputs(SimulationInputs):
    fahrenheit_hot_supply: simulation.Boundary
    fahrenheit_waste_supply: simulation.TemperatureBoundary
    fahrenheit_cold_supply: simulation.TemperatureBoundary
