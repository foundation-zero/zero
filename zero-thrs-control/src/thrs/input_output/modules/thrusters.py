from typing import Annotated

from pydantic import computed_field

from thrs.input_output.base import (
    SimulationInputs,
    SimulationValues,
    Stamped,
    ThrsValues,
    component_meta,
    computed_meta,
)
from thrs.input_output.definitions import control, sensor, simulation


class ThrustersSensorValues(ThrsValues):
    thrusters_pump1: Annotated[
        sensor.Pump, component_meta(yard_tag="50001194", component_type="pump")
    ]
    thrusters_pump2: Annotated[
        sensor.Pump, component_meta(yard_tag="50001195", component_type="pump")
    ]
    thrusters_temperature_aft: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-01", component_type="temperature_sensor"),
    ]
    thrusters_temperature_fwd: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-02", component_type="temperature_sensor"),
    ]
    thrusters_temperature_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-28", component_type="temperature_sensor"),
    ]
    thrusters_temperature_recovery_mix: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-30", component_type="temperature_sensor"),
    ]
    thrusters_mix_recovery: Annotated[
        sensor.Valve,
        component_meta(yard_tag="50001074", component_type="valve", valve_type="mix"),
    ]
    thrusters_mix_exchanger: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001214-01", component_type="valve", valve_type="mix"
        ),
    ]
    thrusters_flow_fwd: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001057-22", component_type="flow_sensor"),
    ]
    thrusters_flow_aft: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001218-02", component_type="flow_sensor"),
    ]
    thrusters_flowcontrol_aft: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001215", component_type="valve", valve_type="flowcontrol"
        ),
    ]
    thrusters_flowcontrol_fwd: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001064-02", component_type="valve", valve_type="flowcontrol"
        ),
    ]
    thrusters_switch_recovery: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001066-03", component_type="valve", valve_type="switch"
        ),
    ]
    thrusters_switch_aft: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001091-01", component_type="valve", valve_type="switch"
        ),
    ]
    thrusters_switch_fwd: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001091-02", component_type="valve", valve_type="switch"
        ),
    ]
    thrusters_flow_recovery: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001218-01", component_type="flow_sensor"),
    ]
    thrusters_pressure_discharge: Annotated[
        sensor.PressureSensor,
        component_meta(yard_tag="50001097-01", component_type="pressure_sensor"),
    ]
    thrusters_pressure_system: Annotated[
        sensor.PressureSensor,
        component_meta(yard_tag="50001097-02", component_type="pressure_sensor"),
    ]
    thrusters_thruster_aft: Annotated[
        sensor.Thruster,
        component_meta(
            yard_tag="15001001",
            component_type="thruster",
            included_in_fmu=False,
            topic_override="dummy-pcs/thruster-aft-active",
        ),
    ]
    thrusters_thruster_fwd: Annotated[
        sensor.Thruster,
        component_meta(
            yard_tag="15001002",
            component_type="thruster",
            included_in_fmu=False,
            topic_override="dummy-pcs/thruster-fwd-active",
        ),
    ]
    thrusters_pcs: Annotated[
        sensor.Pcs,
        component_meta(
            yard_tag="1500",
            component_type="pcs",
            included_in_fmu=False,
            topic_override="dummy-pcs/pcs-mode",
        ),
    ]

    @computed_field(
        json_schema_extra=computed_meta(
            component_type="calculated_temperature", included_in_fmu=False
        )
    )
    @property
    def thrusters_temperature_recovery(self) -> sensor.CalculatedTemperature:
        total_flow = (
            self.thrusters_flow_aft.flow.value + self.thrusters_flow_fwd.flow.value
        )
        if (
            total_flow != 0.0
            and self.thrusters_temperature_aft.temperature.value is not None
            and self.thrusters_temperature_fwd.temperature.value is not None
        ):
            averaged_return_temperature = (
                self.thrusters_temperature_aft.temperature.value
                * self.thrusters_flow_aft.flow.value
                + self.thrusters_temperature_fwd.temperature.value
                * self.thrusters_flow_fwd.flow.value
            ) / total_flow
        else:
            averaged_return_temperature = None  # No flow, no temperature

        return sensor.CalculatedTemperature(
            temperature=Stamped(
                value=averaged_return_temperature,
                timestamp=min(
                    self.thrusters_temperature_aft.temperature.timestamp,
                    self.thrusters_temperature_fwd.temperature.timestamp,
                    self.thrusters_flow_aft.flow.timestamp,
                    self.thrusters_flow_fwd.flow.timestamp,
                ),
            )
        )

    @computed_field(
        json_schema_extra=computed_meta(
            yard_tag="50001001", component_type="heat_exchanger", included_in_fmu=False
        )
    )
    @property
    def thrusters_seawater_exchanger(self) -> sensor.HeatExchanger:
        return sensor.HeatExchanger(
            delta_t=Stamped.stamp(0), heat=Stamped.stamp(0)
        )  # TODO: Find where this should come from


class ThrustersControlValues(ThrsValues):
    thrusters_pump1: Annotated[
        control.Pump, component_meta(yard_tag="50001194", component_type="pump")
    ]
    thrusters_pump2: Annotated[
        control.Pump, component_meta(yard_tag="50001195", component_type="pump")
    ]
    thrusters_mix_recovery: Annotated[
        control.Valve,
        component_meta(yard_tag="50001074", component_type="valve", valve_type="mix"),
    ]
    thrusters_mix_exchanger: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001214-01", component_type="valve", valve_type="mix"
        ),
    ]
    thrusters_flowcontrol_aft: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001215", component_type="valve", valve_type="flowcontrol"
        ),
    ]
    thrusters_flowcontrol_fwd: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001064-02", component_type="valve", valve_type="flowcontrol"
        ),
    ]
    thrusters_switch_recovery: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001066-03", component_type="valve", valve_type="switch"
        ),
    ]
    thrusters_switch_aft: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001091-01", component_type="valve", valve_type="switch"
        ),
    ]
    thrusters_switch_fwd: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001091-02", component_type="valve", valve_type="switch"
        ),
    ]


class ThrustersSimulationInputs(SimulationInputs):
    thrusters_thruster_aft: simulation.Thruster
    thrusters_thruster_fwd: simulation.Thruster
    thrusters_seawater_supply: simulation.Boundary
    thrusters_pcm_supply: simulation.TemperatureBoundary
    thrusters_pcs: simulation.Pcs


class ThrustersSimulationOutputs(SimulationValues):
    thrusters_seawater_return: simulation.TemperatureBoundary
    thrusters_pcm_supply: simulation.FlowBoundary
    thrusters_pcm_return: simulation.Boundary
