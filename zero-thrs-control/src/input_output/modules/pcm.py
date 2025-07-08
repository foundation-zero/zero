from typing import Annotated
from input_output.base import ParameterMeta, SimulationInputs, ThrsModel
from input_output.definitions import control, sensor, simulation


class PcmSensorValues(ThrsModel):
    pcm_pump: Annotated[sensor.Pump, ParameterMeta("50001017")]
    pcm_temperature_producers_return: Annotated[
        sensor.TemperatureSensor, ParameterMeta("50001038-31")
    ]
    pcm_temperature_producers_supply: Annotated[
        sensor.TemperatureSensor, ParameterMeta("50001038-55")
    ]
    pcm_temperature_module_1_out: Annotated[sensor.TemperatureSensor, ParameterMeta("50001038-32")]
    pcm_temperature_module_2_out: Annotated[sensor.TemperatureSensor, ParameterMeta("50001038-33")]
    pcm_temperature_module_3_out: Annotated[sensor.TemperatureSensor, ParameterMeta("50001038-34")]
    pcm_temperature_module_4_out: Annotated[sensor.TemperatureSensor, ParameterMeta("50001038-35")]
    pcm_module_1: Annotated[sensor.Pcm, ParameterMeta("50001049")]
    pcm_module_2: Annotated[sensor.Pcm, ParameterMeta("50001050")]
    pcm_module_3: Annotated[sensor.Pcm, ParameterMeta("50001051")]
    pcm_module_4: Annotated[sensor.Pcm, ParameterMeta("50001052")]
    pcm_flow_module_1: Annotated[sensor.FlowSensor, ParameterMeta("50001057-18")]
    pcm_flow_module_2: Annotated[sensor.FlowSensor, ParameterMeta("50001057-19")]
    pcm_flow_module_3: Annotated[sensor.FlowSensor, ParameterMeta("50001057-20")]
    pcm_flow_module_4: Annotated[sensor.FlowSensor, ParameterMeta("50001057-21")]
    pcm_switch_charging_return: Annotated[sensor.Valve, ParameterMeta("50001062-02")]
    pcm_flowcontrol_module_1: Annotated[sensor.Valve, ParameterMeta("50001064-04")]
    pcm_flowcontrol_module_2: Annotated[sensor.Valve, ParameterMeta("50001064-05")]
    pcm_flowcontrol_module_3: Annotated[sensor.Valve, ParameterMeta("50001064-06")]
    pcm_flowcontrol_module_4: Annotated[sensor.Valve, ParameterMeta("50001064-07")]
    pcm_switch_discharging: Annotated[sensor.Valve, ParameterMeta("50001066-01")]
    pcm_switch_charging_supply: Annotated[sensor.Valve, ParameterMeta("50001090-01")]
    pcm_switch_consumers: Annotated[sensor.Valve, ParameterMeta("50001071-02")]

class PcmControlValues(ThrsModel):
    pcm_pump: Annotated[control.Pump, ParameterMeta("50001017")]
    pcm_switch_charging_return: Annotated[control.Valve, ParameterMeta("50001062-02")]
    pcm_flowcontrol_module_1: Annotated[control.Valve, ParameterMeta("50001064-04")]
    pcm_flowcontrol_module_2: Annotated[control.Valve, ParameterMeta("50001064-05")]
    pcm_flowcontrol_module_3: Annotated[control.Valve, ParameterMeta("50001064-06")]
    pcm_flowcontrol_module_4: Annotated[control.Valve, ParameterMeta("50001064-07")]
    pcm_switch_discharging: Annotated[control.Valve, ParameterMeta("50001066-01")]
    pcm_switch_charging_supply: Annotated[control.Valve, ParameterMeta("50001090-01")]
    pcm_switch_consumers: Annotated[control.Valve, ParameterMeta("50001071-02")]
    pcm_module_1: Annotated[control.Pcm, ParameterMeta("50001049")]

class PcmSimulationInputs(SimulationInputs):
    pcm_producers_supply: simulation.Boundary
    pcm_consumers_supply: simulation.TemperatureBoundary
    pcm_freshwater_supply: simulation.Boundary

class PcmSimulationOutputs(ThrsModel):
    pcm_consumers_return: simulation.Boundary
    pcm_producers_return: simulation.Boundary
    pcm_freshwater_return: simulation.Boundary
