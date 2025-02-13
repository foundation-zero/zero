from typing import Annotated
from simulation.io.base import ThrsModel, Meta
from simulation.io.sensor import (
    FlowSensor,
    PressureSensor,
    Pump,
    TemperatureSensor,
    Valve,
)


class ThrustersSensors(ThrsModel):
    thruster_pump_1: Annotated[Pump, Meta("5001015")]
    thruster_pump_2: Annotated[Pump, Meta("5001016")]
    thrusters_temperature_aft_return: Annotated[TemperatureSensor, Meta("5001038-01")]
    thrusters_temperature_fwd_return: Annotated[TemperatureSensor, Meta("5001038-02")]
    thrusters_temperature_supply: Annotated[TemperatureSensor, Meta("5001038-28")]
    thrusters_temperature_fwd_supply: Annotated[TemperatureSensor, Meta("5001038-29")]
    thrusters_temperature_aft_supply: Annotated[TemperatureSensor, Meta("5001038-30")]
    thrusters_mix_aft: Annotated[Valve, Meta("5001042-01")]
    thrusters_mix_fwd: Annotated[Valve, Meta("5001042-02")]
    thrusters_mix_exchanger: Annotated[Valve, Meta("5001045-03")]
    thrusters_flow_fwd: Annotated[FlowSensor, Meta("50001057-22")]
    thrusters_flow_aft: Annotated[FlowSensor, Meta("50001057-23")]
    thrusters_flowcontrol_aft: Annotated[Valve, Meta("5001064-01")]
    thrusters_flowcontrol_fwd: Annotated[Valve, Meta("5001064-02")]
    thrusters_shutoff_recovery: Annotated[Valve, Meta("5001069-10")]
    thrusters_pressure_recovery: Annotated[PressureSensor, Meta("5001097-01")]
    thrusters_pressure_cooling: Annotated[PressureSensor, Meta("5001097-02")]
