from typing import Annotated, cast

from pydantic import ConfigDict, computed_field
from pydantic.alias_generators import to_snake

from thrs.input_output.base import Stamped, ThrsValues, component_meta, computed_meta
from thrs.input_output.definitions import control, sensor, simulation
from thrs.input_output.definitions.units import (
    WATER_HEAT_TRANSFER_CONVERSION,
    OptionalCelsius,
)


class ThrustersSensorValues(ThrsValues):
    model_config = ConfigDict(
        alias_generator=to_snake,
        use_enum_values=True,
        validate_by_name=True,
    )

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
        """The average temperature after thrusters before optional mix with pcm."""
        return sensor.CalculatedTemperature.from_weighted_sensors(
            [self.thrusters_flow_aft.flow, self.thrusters_flow_fwd.flow],
            [self.thrusters_temperature_aft, self.thrusters_temperature_fwd],
            None,  # No flow, no temperature
        )

    @computed_field(
        json_schema_extra=computed_meta(
            component_type="calculated_temperature", included_in_fmu=False
        )
    )
    @property
    def thrusters_temperature_pre_cooler(self) -> sensor.CalculatedTemperature:
        """
        The temperature after the thrusters and mix with pcm.

        If this was an actual sensor it would have been located just before the inlet to the seawater exchanger.
        """
        if sensor.valves_open_closed(
            open_valves=[self.thrusters_switch_fwd, self.thrusters_switch_aft]
        ):
            # If switches to A we can return a real sensor
            return self.thrusters_temperature_recovery

        if sensor.valves_open_closed(
            closed_valves=[self.thrusters_switch_fwd, self.thrusters_switch_aft]
        ):
            # If switches to B we need to calculate
            return sensor.CalculatedTemperature(
                temperature=cast(
                    Stamped[OptionalCelsius],
                    self.thrusters_temperature_recovery_mix.temperature,
                )
            )

        # If valves are not both completely closed or opened, we don't know the temp
        return sensor.CalculatedTemperature(
            temperature=Stamped.combine(
                self.thrusters_switch_fwd.position_rel,
                self.thrusters_switch_aft.position_rel,
                value=None,
            )
        )

    @computed_field(
        json_schema_extra=computed_meta(
            component_type="calculated_flow", included_in_fmu=False
        )
    )
    @property
    def thrusters_flow(self) -> sensor.CalculatedFlow:
        return sensor.CalculatedFlow.from_summed_sensors(
            self.thrusters_flow_aft, self.thrusters_flow_fwd
        )

    @computed_field(
        json_schema_extra=computed_meta(
            yard_tag="50001001", component_type="heat_exchanger", included_in_fmu=False
        )
    )
    @property
    def thrusters_seawater_exchanger(self) -> sensor.HeatExchanger:
        temperature_supply = self.thrusters_temperature_pre_cooler.temperature
        temperature_return = self.thrusters_temperature_supply.temperature
        flow = self.thrusters_flow.flow
        exchange_mix_ration = self.thrusters_mix_exchanger.position_rel

        # DeltaT is slightly more difficult since we need to account for the part that does not flow past the exchanger
        delta_t = Stamped.combine(
            temperature_supply,
            temperature_return,
            value=(
                (
                    1
                    / exchange_mix_ration.value
                    * (temperature_return.value - temperature_supply.value)
                )
                if exchange_mix_ration.value > 0
                else 0.0
            )
            if temperature_supply.value
            else 0.0,
        )

        # We don't use above delta_t because its too complicated and we can assume that the part that does not flow past the exchanger does no heat dump.
        heat = Stamped.combine(
            temperature_return,
            temperature_supply,
            flow,
            value=flow.value
            * (
                (temperature_return.value - temperature_supply.value)
                if temperature_supply.value
                else 0.0
            )
            * WATER_HEAT_TRANSFER_CONVERSION,
        )

        return sensor.HeatExchanger(delta_t=delta_t, heat=heat)


class ThrustersControlValues(ThrsValues):
    model_config = ConfigDict(
        alias_generator=to_snake,
        use_enum_values=True,
        validate_by_name=True,
    )

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


class ThrustersSimulationInputs(ThrsValues):
    thrusters_thruster_aft: simulation.Thruster
    thrusters_thruster_fwd: simulation.Thruster
    thrusters_seawater_supply: simulation.Boundary
    thrusters_pcm_supply: simulation.TemperatureBoundary
    thrusters_pcs: simulation.Pcs


class ThrustersSimulationOutputs(ThrsValues):
    thrusters_seawater_return: simulation.TemperatureBoundary
    thrusters_pcm_supply: simulation.FlowBoundary
    thrusters_pcm_return: simulation.Boundary
