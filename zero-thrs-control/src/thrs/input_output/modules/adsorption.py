from typing import Annotated

from thrs.input_output.base import (
    SimulationInputs,
    SimulationValues,
    ThrsValues,
    component_meta,
)
from thrs.input_output.definitions import control, sensor, simulation


class AdsorptionSensorValues(ThrsValues):
    adsorption_flowcontrol_waste: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001062-03", component_type="valve", valve_type="flowcontrol"
        ),
    ]
    adsorption_mix_hot: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001046-02", component_type="valve", valve_type="mix"
        ),
    ]
    adsorption_mix_waste: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001047-01", component_type="valve", valve_type="mix"
        ),
    ]
    adsorption_switch_dhw: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001187-01", component_type="valve", valve_type="switch"
        ),
    ]
    adsorption_chiller: Annotated[
        sensor.AdsorptionChiller,
        component_meta(yard_tag="50001034", component_type="adsorption_chiller"),
    ]
    adsorption_flow_ht: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001058-09", component_type="flow_sensor"),
    ]
    adsorption_flow_hot: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001058-02", component_type="flow_sensor"),
    ]
    adsorption_flow_waste: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001059", component_type="flow_sensor"),
    ]
    adsorption_flow_dhw: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001058-10", component_type="flow_sensor"),
    ]
    adsorption_temperature_ht_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-41", component_type="temperature_sensor"),
    ]
    adsorption_temperature_ht_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-50", component_type="temperature_sensor"),
    ]
    adsorption_temperature_hot_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-36", component_type="temperature_sensor"),
    ]
    adsorption_temperature_hot_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-37", component_type="temperature_sensor"),
    ]
    adsorption_temperature_waste_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-38", component_type="temperature_sensor"),
    ]
    adsorption_temperature_waste_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-39", component_type="temperature_sensor"),
    ]
    adsorption_temperature_dhw_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-56", component_type="temperature_sensor"),
    ]
    adsorption_available_hot_temperature: Annotated[
        sensor.TemperatureSensor,
        component_meta(
            component_type="external_sensor", included_in_fmu=False
        ),  # TODO: figure out how to deal with Fahrenheit here. Is this a sensor value or should this be a parameter?
    ]
    adsorption_available_cold_temperature: Annotated[
        sensor.TemperatureSensor,
        component_meta(
            component_type="external_sensor", included_in_fmu=False
        ),  # TODO: figure out how to deal with Fahrenheit here. Is this a sensor value or should this be a parameter?
    ]
    adsorption_available_seawater_temperature: Annotated[
        sensor.TemperatureSensor,
        component_meta(
            component_type="external_sensor", included_in_fmu=False
        ),  # TODO: figure out how to deal with Fahrenheit here. Is this a sensor value or should this be a parameter?
    ]


class AdsorptionControlValues(ThrsValues):
    adsorption_flowcontrol_waste: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001062-03", component_type="valve", valve_type="flowcontrol"
        ),
    ]
    adsorption_mix_hot: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001046-02", component_type="valve", valve_type="mix"
        ),
    ]
    adsorption_mix_waste: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001047-01", component_type="valve", valve_type="mix"
        ),
    ]
    adsorption_switch_dhw: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001187-01", component_type="valve", valve_type="switch"
        ),
    ]
    adsorption_chiller: Annotated[
        control.AdsorptionChiller,
        component_meta(yard_tag="50001034", component_type="adsorption_chiller"),
    ]


class AdsorptionSimulationInputs(SimulationInputs):
    adsorption_cooling_supply: simulation.TemperatureBoundary
    adsorption_seawater_supply: simulation.Boundary
    adsorption_available_hot_temperature: Annotated[
        simulation.TemperatureBoundary, component_meta(included_in_fmu=False)
    ]
    adsorption_available_cold_temperature: Annotated[
        simulation.TemperatureBoundary, component_meta(included_in_fmu=False)
    ]
    adsorption_available_seawater_temperature: Annotated[
        simulation.TemperatureBoundary, component_meta(included_in_fmu=False)
    ]
    adsorption_chiller: Annotated[
        simulation.AdsorptionChiller, component_meta(included_in_fmu=False)
    ]
    adsorption_consumers_supply: simulation.Boundary
    adsorption_dhw_supply: simulation.Boundary


class AdsorptionSimulationOutputs(SimulationValues):
    adsorption_cooling_return: simulation.Boundary
    adsorption_seawater_return: simulation.TemperatureBoundary
    adsorption_dhw_exchanger: simulation.ExchangerBoundary
    adsorption_dhw_return: simulation.TemperatureBoundary
    adsorption_consumers_exchanger: simulation.ExchangerBoundary
    adsorption_consumers_return: simulation.TemperatureBoundary
