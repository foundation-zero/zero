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
    fahrenheit_switch_waste: Annotated[
        sensor.Valve, component_meta(yard_tag="50001187-01", component_type="valve")
    ]
    fahrenheit_chiller: Annotated[
        sensor.Fahrenheit,
        component_meta(yard_tag="50001034", component_type="fahrenheit"),
    ]
    fahrenheit_flow_ht: Annotated[
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
    fahrenheit_flow_boilers: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001058-10", component_type="flow_sensor"),
    ]
    fahrenheit_temperature_ht_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-41", component_type="temperature_sensor"),
    ]
    fahrenheit_temperature_ht_supply: Annotated[
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
    fahrenheit_temperature_boilers_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-56", component_type="temperature_sensor"),
    ]
    fahrenheit_available_hot_temperature: Annotated[
        sensor.TemperatureSensor,
        component_meta(component_type="external_sensor", included_in_fmu=False),
    ]
    fahrenheit_available_cold_temperature: Annotated[
        sensor.TemperatureSensor,
        component_meta(component_type="external_sensor", included_in_fmu=False),
    ]
    fahrenheit_available_seawater_temperature: Annotated[
        sensor.TemperatureSensor,
        component_meta(component_type="external_sensor", included_in_fmu=False),
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
    fahrenheit_switch_waste: Annotated[
        control.Valve, component_meta(yard_tag="50001187-01", component_type="valve")
    ]
    fahrenheit_chiller: Annotated[
        control.Fahrenheit,
        component_meta(yard_tag="50001034", component_type="fahrenheit"),
    ]


class FahrenheitSimulationInputs(SimulationInputs):
    fahrenheit_cold_supply: simulation.TemperatureBoundary
    fahrenheit_seawater_supply: simulation.Boundary
    fahrenheit_available_hot_temperature: Annotated[
        simulation.TemperatureBoundary, component_meta(included_in_fmu=False)
    ]
    fahrenheit_available_cold_temperature: Annotated[
        simulation.TemperatureBoundary, component_meta(included_in_fmu=False)
    ]
    fahrenheit_available_seawater_temperature: Annotated[
        simulation.TemperatureBoundary, component_meta(included_in_fmu=False)
    ]
    fahrenheit_chiller: Annotated[
        simulation.Fahrenheit, component_meta(included_in_fmu=False)
    ]
    fahrenheit_ht_supply: simulation.Boundary
    fahrenheit_boilers_supply: simulation.Boundary


class FahrenheitSimulationOutputs(SimulationValues):
    fahrenheit_cold_return: simulation.Boundary
    fahrenheit_seawater_return: simulation.TemperatureBoundary
    fahrenheit_boilers_return: simulation.TemperatureBoundary
    fahrenheit_ht_return: simulation.TemperatureBoundary
