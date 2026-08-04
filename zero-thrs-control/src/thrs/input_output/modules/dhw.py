from typing import Annotated

from pydantic import ConfigDict, computed_field
from pydantic.alias_generators import to_snake

from thrs.input_output.base import (
    Stamped,
    ThrsValues,
    component_meta,
    computed_meta,
)
from thrs.input_output.definitions import control, sensor, simulation
from thrs.input_output.definitions.units import WATER_HEAT_TRANSFER_CONVERSION


class DhwSensorValues(ThrsValues):
    model_config = ConfigDict(
        alias_generator=to_snake,
        use_enum_values=True,
        validate_by_name=True,
    )

    dhw_pump: Annotated[
        sensor.Pump, component_meta(yard_tag="50001022", component_type="pump")
    ]
    dhw_temperature_hvac_exchanger_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-25", component_type="temperature_sensor"),
    ]
    dhw_temperature_dc_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-26", component_type="temperature_sensor"),
    ]
    dhw_temperature_tank3: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-27", component_type="temperature_sensor"),
    ]
    dhw_temperature_tank2: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-44", component_type="temperature_sensor"),
    ]
    dhw_temperature_tank1: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-45", component_type="temperature_sensor"),
    ]
    dhw_temperature_drives_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-46", component_type="temperature_sensor"),
    ]
    dhw_temperature_freshwater_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-47", component_type="temperature_sensor"),
    ]
    dhw_temperature_adsorption_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-51", component_type="temperature_sensor"),
    ]
    dhw_temperature_boosting_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-65", component_type="temperature_sensor"),
    ]
    dhw_temperature_boosting_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-66", component_type="temperature_sensor"),
    ]
    dhw_level_tank1: Annotated[
        sensor.LevelSensor,
        component_meta(yard_tag="50001056-01", component_type="level_sensor"),
    ]
    dhw_level_tank2: Annotated[
        sensor.LevelSensor,
        component_meta(yard_tag="50001056-02", component_type="level_sensor"),
    ]
    dhw_level_tank3: Annotated[
        sensor.LevelSensor,
        component_meta(yard_tag="50001056-03", component_type="level_sensor"),
    ]
    dhw_flow_dc: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001057-17", component_type="flow_sensor"),
    ]
    dhw_flow_drives: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001057-24", component_type="flow_sensor"),
    ]
    dhw_flow_boosting: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001058-11", component_type="flow_sensor"),
    ]
    dhw_flowcontrol_dc: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001064-03", component_type="valve", valve_type="flowcontrol"
        ),
    ]
    dhw_flowcontrol_drives: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001064-08", component_type="valve", valve_type="flowcontrol"
        ),
    ]
    dhw_switch_tank3_inlet: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001067-03", component_type="valve", valve_type="switch"
        ),
    ]
    dhw_switch_tank3_boosting_return: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001067-04", component_type="valve", valve_type="switch"
        ),
    ]
    dhw_switch_tank3_outlet: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001067-05", component_type="valve", valve_type="switch"
        ),
    ]
    dhw_switch_tank3_boosting_supply: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001067-06", component_type="valve", valve_type="switch"
        ),
    ]
    dhw_switch_tank2_inlet: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001067-07", component_type="valve", valve_type="switch"
        ),
    ]
    dhw_switch_tank2_boosting_return: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001067-08", component_type="valve", valve_type="switch"
        ),
    ]
    dhw_switch_tank2_outlet: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001067-09", component_type="valve", valve_type="switch"
        ),
    ]
    dhw_switch_tank2_boosting_supply: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001067-10", component_type="valve", valve_type="switch"
        ),
    ]
    dhw_switch_tank1_inlet: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001067-11", component_type="valve", valve_type="switch"
        ),
    ]
    dhw_switch_tank1_boosting_return: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001067-12", component_type="valve", valve_type="switch"
        ),
    ]
    dhw_switch_tank1_outlet: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001067-13", component_type="valve", valve_type="switch"
        ),
    ]
    dhw_switch_tank1_boosting_supply: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001067-14", component_type="valve", valve_type="switch"
        ),
    ]
    dhw_switch_low_temperature: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001067-16", component_type="valve", valve_type="switch"
        ),
    ]
    dhw_switch_heatpump: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001067-17", component_type="valve", valve_type="switch"
        ),
    ]
    dhw_switch_high_temperature: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001067-18", component_type="valve", valve_type="switch"
        ),
    ]
    dhw_level_switch_tank1: Annotated[
        sensor.LevelSwitch,
        component_meta(yard_tag="50001098-01", component_type="level_switch"),
    ]
    dhw_level_switch_tank2: Annotated[
        sensor.LevelSwitch,
        component_meta(yard_tag="50001098-02", component_type="level_switch"),
    ]
    dhw_level_switch_tank3: Annotated[
        sensor.LevelSwitch,
        component_meta(yard_tag="50001098-03", component_type="level_switch"),
    ]
    dhw_pressure: Annotated[
        sensor.PressureSensor,
        component_meta(yard_tag="50001097-11", component_type="pressure_sensor"),
    ]
    drives_flow_recovery: Annotated[
        sensor.FlowSensor,
        component_meta(
            yard_tag="50001058-03",
            component_type="flow_sensor",
            included_in_fmu=False,
            topic_override="drives/drives-flow-recovery",
        ),
    ]
    drives_temperature_recovery: Annotated[
        sensor.TemperatureSensor,
        component_meta(
            yard_tag="50001038-16",
            component_type="temperature_sensor",
            included_in_fmu=False,
            topic_override="drives/drives-temperature-recovery-supply",
        ),
    ]
    drives_temperature_recovery_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(
            yard_tag="50001038-59",
            component_type="temperature_sensor",
            included_in_fmu=False,
            topic_override="drives/drives-temperature-recovery-return",
        ),
    ]

    @computed_field(
        json_schema_extra=computed_meta(component_type="delta_t", included_in_fmu=False)
    )
    @property
    def drives_delta(self) -> sensor.TemperatureDelta:
        return sensor.TemperatureDelta.from_temperature_sensors(
            temperature_supply=self.drives_temperature_recovery.temperature,
            temperature_return=self.drives_temperature_recovery_return.temperature,
        )

    dc_flow_recovery: Annotated[
        sensor.FlowSensor,
        component_meta(
            yard_tag="50001058-04",
            component_type="flow_sensor",
            included_in_fmu=False,
            topic_override="dc/dc-flow-recovery",
        ),
    ]
    dc_temperature_recovery: Annotated[
        sensor.TemperatureSensor,
        component_meta(
            yard_tag="50001038-52",
            component_type="temperature_sensor",
            included_in_fmu=False,
            topic_override="dc/dc-temperature-recovery-supply",
        ),
    ]
    dc_temperature_recovery_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(
            yard_tag="50001038-58",
            component_type="temperature_sensor",
            included_in_fmu=False,
            topic_override="dc/dc-temperature-recovery-return",
        ),
    ]

    @computed_field(
        json_schema_extra=computed_meta(component_type="delta_t", included_in_fmu=False)
    )
    @property
    def dc_delta(self) -> sensor.TemperatureDelta:
        return sensor.TemperatureDelta.from_temperature_sensors(
            temperature_supply=self.dc_temperature_recovery.temperature,
            temperature_return=self.dc_temperature_recovery_return.temperature,
        )

    consumers_flow_dhw: Annotated[
        sensor.FlowSensor,
        component_meta(
            yard_tag="50001058-07",
            component_type="flow_sensor",
            included_in_fmu=False,
            topic_override="consumers/consumers-flow-dhw",
        ),
    ]
    consumers_temperature_dhw_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(
            yard_tag="50001038-53",
            component_type="temperature_sensor",
            included_in_fmu=False,
            topic_override="consumers/consumers-temperature-dhw-supply",
        ),
    ]

    consumers_temperature_dhw_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(
            yard_tag="50001038-48",
            component_type="temperature_sensor",
            included_in_fmu=False,
            topic_override="consumers/consumers-temperature-dhw-return",
        ),
    ]

    @computed_field(
        json_schema_extra=computed_meta(component_type="delta_t", included_in_fmu=False)
    )
    @property
    def consumers_delta(self) -> sensor.TemperatureDelta:
        return sensor.TemperatureDelta.from_temperature_sensors(
            temperature_supply=self.consumers_temperature_dhw_supply.temperature,
            temperature_return=self.consumers_temperature_dhw_return.temperature,
        )

    adsorption_flow_dhw: Annotated[
        sensor.FlowSensor,
        component_meta(
            yard_tag="50001058-10",
            component_type="flow_sensor",
            included_in_fmu=False,
            topic_override="adsorption/adsorption-flow-dhw",
        ),
    ]
    adsorption_temperature_waste_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(
            yard_tag="50001038-38",
            component_type="temperature_sensor",
            included_in_fmu=False,
            topic_override="adsorption/adsorption-temperature-waste-return",
        ),
    ]

    adsorption_temperature_dhw_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(
            yard_tag="50001038-56",
            component_type="temperature_sensor",
            included_in_fmu=False,
            topic_override="adsorption/adsorption-temperature-dhw-return",
        ),
    ]

    @computed_field(
        json_schema_extra=computed_meta(component_type="delta_t", included_in_fmu=False)
    )
    @property
    def adsorption_delta(self) -> sensor.TemperatureDelta:
        return sensor.TemperatureDelta.from_temperature_sensors(
            temperature_supply=self.adsorption_temperature_waste_return.temperature,
            temperature_return=self.adsorption_temperature_dhw_return.temperature,
        )

    freshwater_hotwater_flow: Annotated[
        sensor.FlowSensor, component_meta(yard_tag="25001123-1", included_in_fmu=False)
    ]
    freshwater_hotwater_temperature: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="25001038-1", included_in_fmu=False),
    ]

    @computed_field(
        json_schema_extra=computed_meta(
            component_type="calculated_flow", included_in_fmu=False
        )
    )
    @property
    def dhw_freshwater_flow_supply(self) -> sensor.CalculatedFlow:
        return sensor.CalculatedFlow(
            flow=Stamped.combine(
                self.dhw_flow_drives.flow,
                self.dhw_flow_dc.flow,
                value=self.dhw_flow_drives.flow.value + self.dhw_flow_dc.flow.value,
            )
        )

    @computed_field(
        json_schema_extra=computed_meta(
            yard_tag="41001001", component_type="hvac_exchanger", included_in_fmu=False
        )
    )
    @property
    def dhw_hvac_exchanger(self) -> sensor.HvacExchanger:
        return sensor.HvacExchanger.from_sensors(
            temperature_supply=self.dhw_temperature_adsorption_return.temperature,
            temperature_return=self.dhw_temperature_hvac_exchanger_return.temperature,
            flow=self.dhw_flow_dc.flow,
            heat_transfer_conversion=WATER_HEAT_TRANSFER_CONVERSION,
        )

    @computed_field(
        json_schema_extra=computed_meta(
            yard_tag="50001035", component_type="heatpump", included_in_fmu=False
        )
    )
    @property
    def dhw_heatpump(self) -> sensor.HeatPump:
        if sensor.valves_open_closed(
            open_valves=[self.dhw_switch_heatpump],
            closed_valves=[
                self.dhw_switch_high_temperature,
                self.dhw_switch_low_temperature,
            ],
        ):
            return sensor.HeatPump.from_sensors(
                temperature_supply=self.dhw_temperature_boosting_supply.temperature,
                temperature_return=self.dhw_temperature_boosting_return.temperature,
                flow=self.dhw_flow_boosting.flow,
                heat_transfer_conversion=WATER_HEAT_TRANSFER_CONVERSION,
            )
        return sensor.HeatPump(delta_t=Stamped.stamp(0), heat=Stamped.stamp(0))

    @computed_field(
        json_schema_extra=computed_meta(
            yard_tag="50001004", component_type="heat_exchanger", included_in_fmu=False
        )
    )
    @property
    def dhw_adsorption_exchanger(self) -> sensor.HeatExchanger:
        return sensor.HeatExchanger.from_sensors(
            temperature_supply=self.dhw_temperature_freshwater_supply.temperature,
            temperature_return=self.dhw_temperature_adsorption_return.temperature,
            flow=self.dhw_flow_dc.flow,
            heat_transfer_conversion=WATER_HEAT_TRANSFER_CONVERSION,
        )

    @computed_field(
        json_schema_extra=computed_meta(
            yard_tag="50001007", component_type="heat_exchanger", included_in_fmu=False
        )
    )
    @property
    def dhw_consumers_exchanger(self) -> sensor.HeatExchanger:
        if sensor.valves_open_closed(
            open_valves=[self.dhw_switch_high_temperature],
            closed_valves=[
                self.dhw_switch_heatpump,
                self.dhw_switch_low_temperature,
            ],
        ):
            return sensor.HeatExchanger.from_sensors(
                temperature_supply=self.dhw_temperature_boosting_supply.temperature,
                temperature_return=self.dhw_temperature_boosting_return.temperature,
                flow=self.dhw_flow_boosting.flow,
                heat_transfer_conversion=WATER_HEAT_TRANSFER_CONVERSION,
            )
        return sensor.HeatExchanger(delta_t=Stamped.stamp(0), heat=Stamped.stamp(0))

    @computed_field(
        json_schema_extra=computed_meta(
            yard_tag="50001008", component_type="heat_exchanger", included_in_fmu=False
        )
    )
    @property
    def dhw_dc_exchanger(self) -> sensor.HeatExchanger:
        return sensor.HeatExchanger.from_sensors(
            temperature_supply=self.dhw_temperature_hvac_exchanger_return.temperature,
            temperature_return=self.dhw_temperature_dc_return.temperature,
            flow=self.dhw_flow_dc.flow,
            heat_transfer_conversion=WATER_HEAT_TRANSFER_CONVERSION,
        )

    @computed_field(
        json_schema_extra=computed_meta(
            yard_tag="50001009", component_type="heat_exchanger", included_in_fmu=False
        )
    )
    @property
    def dhw_drives_exchanger(self) -> sensor.HeatExchanger:
        if sensor.valves_open_closed(
            open_valves=[], closed_valves=[self.dhw_switch_low_temperature]
        ):
            return sensor.HeatExchanger.from_sensors(
                temperature_supply=self.dhw_temperature_freshwater_supply.temperature,
                temperature_return=self.dhw_temperature_drives_return.temperature,
                flow=self.dhw_flow_drives.flow,
                heat_transfer_conversion=WATER_HEAT_TRANSFER_CONVERSION,
            )
        if sensor.valves_open_closed(
            open_valves=[self.dhw_switch_low_temperature],
            closed_valves=[
                self.dhw_switch_heatpump,
                self.dhw_switch_high_temperature,
                self.dhw_flowcontrol_drives,
            ],
        ):
            return sensor.HeatExchanger.from_sensors(
                temperature_supply=self.dhw_temperature_boosting_supply.temperature,
                temperature_return=self.dhw_temperature_drives_return.temperature,
                flow=self.dhw_flow_boosting.flow,
                heat_transfer_conversion=WATER_HEAT_TRANSFER_CONVERSION,
            )
        return sensor.HeatExchanger(delta_t=Stamped.stamp(0), heat=Stamped.stamp(0))


class DhwControlValues(ThrsValues):
    model_config = ConfigDict(
        alias_generator=to_snake,
        use_enum_values=True,
        validate_by_name=True,
    )

    dhw_pump: Annotated[
        control.Pump, component_meta(yard_tag="50001022", component_type="pump")
    ]
    dhw_heatpump: Annotated[
        control.HeatPump, component_meta(yard_tag="50001035", component_type="heatpump")
    ]
    dhw_flowcontrol_dc: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001064-03", component_type="valve", valve_type="flowcontrol"
        ),
    ]
    dhw_flowcontrol_drives: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001064-08", component_type="valve", valve_type="flowcontrol"
        ),
    ]
    dhw_switch_tank3_inlet: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001067-03", component_type="valve", valve_type="switch"
        ),
    ]
    dhw_switch_tank3_boosting_return: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001067-04", component_type="valve", valve_type="switch"
        ),
    ]
    dhw_switch_tank3_outlet: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001067-05", component_type="valve", valve_type="switch"
        ),
    ]
    dhw_switch_tank3_boosting_supply: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001067-06", component_type="valve", valve_type="switch"
        ),
    ]
    dhw_switch_tank2_inlet: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001067-07", component_type="valve", valve_type="switch"
        ),
    ]
    dhw_switch_tank2_boosting_return: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001067-08", component_type="valve", valve_type="switch"
        ),
    ]
    dhw_switch_tank2_outlet: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001067-09", component_type="valve", valve_type="switch"
        ),
    ]
    dhw_switch_tank2_boosting_supply: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001067-10", component_type="valve", valve_type="switch"
        ),
    ]
    dhw_switch_tank1_inlet: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001067-11", component_type="valve", valve_type="switch"
        ),
    ]
    dhw_switch_tank1_boosting_return: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001067-12", component_type="valve", valve_type="switch"
        ),
    ]
    dhw_switch_tank1_outlet: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001067-13", component_type="valve", valve_type="switch"
        ),
    ]
    dhw_switch_tank1_boosting_supply: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001067-14", component_type="valve", valve_type="switch"
        ),
    ]
    dhw_switch_low_temperature: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001067-16", component_type="valve", valve_type="switch"
        ),
    ]
    dhw_switch_heatpump: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001067-17", component_type="valve", valve_type="switch"
        ),
    ]
    dhw_switch_high_temperature: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001067-18", component_type="valve", valve_type="switch"
        ),
    ]


class DhwSimulationInputs(ThrsValues):
    dhw_drives_supply: simulation.Boundary
    dhw_dc_supply: simulation.Boundary
    dhw_adsorption_supply: simulation.Boundary
    dhw_consumers_supply: simulation.Boundary
    dhw_freshwater_supply: simulation.OverpressureTemperatureBoundary
    dhw_hvac_exchanger: simulation.HvacExchanger
    dhw_seawater_supply: simulation.TemperatureBoundary
    dhw_hotwater_demand: simulation.FlowBoundary

    @computed_field(json_schema_extra=computed_meta(included_in_fmu=False))
    @property
    def drives_flow_recovery(self) -> sensor.FlowSensor:
        return sensor.FlowSensor(
            flow=self.dhw_drives_supply.flow,
            temperature=self.dhw_drives_supply.temperature,
        )

    @computed_field(json_schema_extra=computed_meta(included_in_fmu=False))
    @property
    def drives_temperature_recovery(self) -> sensor.TemperatureSensor:
        return sensor.TemperatureSensor(temperature=self.dhw_drives_supply.temperature)

    @computed_field(json_schema_extra=computed_meta(included_in_fmu=False))
    @property
    def dc_flow_recovery(self) -> sensor.FlowSensor:
        return sensor.FlowSensor(
            flow=self.dhw_dc_supply.flow,
            temperature=self.dhw_dc_supply.temperature,
        )

    @computed_field(json_schema_extra=computed_meta(included_in_fmu=False))
    @property
    def dc_temperature_recovery(self) -> sensor.TemperatureSensor:
        return sensor.TemperatureSensor(temperature=self.dhw_dc_supply.temperature)

    @computed_field(json_schema_extra=computed_meta(included_in_fmu=False))
    @property
    def consumers_flow_dhw(self) -> sensor.FlowSensor:
        return sensor.FlowSensor(
            flow=self.dhw_consumers_supply.flow,
            temperature=self.dhw_consumers_supply.temperature,
        )

    @computed_field(
        json_schema_extra=computed_meta(
            included_in_fmu=False, component_type="temperature_sensor"
        )
    )
    @property
    def consumers_temperature_dhw_supply(self) -> sensor.TemperatureSensor:
        return sensor.TemperatureSensor(
            temperature=self.dhw_consumers_supply.temperature
        )

    @computed_field(
        json_schema_extra=computed_meta(
            included_in_fmu=False, component_type="flow_sensor"
        )
    )
    @property
    def adsorption_flow_dhw(self) -> sensor.FlowSensor:
        return sensor.FlowSensor(
            flow=self.dhw_adsorption_supply.flow,
            temperature=self.dhw_adsorption_supply.temperature,
        )

    @computed_field(
        json_schema_extra=computed_meta(
            included_in_fmu=False, component_type="temperature_sensor"
        )
    )
    @property
    def adsorption_temperature_waste_return(self) -> sensor.TemperatureSensor:
        return sensor.TemperatureSensor(
            temperature=self.dhw_adsorption_supply.temperature
        )


class DhwSimulationOutputs(ThrsValues):
    dhw_drives_exchanger: simulation.ExchangerBoundary
    dhw_drives_return: simulation.TemperatureBoundary
    dhw_dc_exchanger: simulation.ExchangerBoundary
    dhw_dc_return: simulation.TemperatureBoundary
    dhw_adsorption_exchanger: simulation.ExchangerBoundary
    dhw_adsorption_return: simulation.TemperatureBoundary
    dhw_consumers_exchanger: simulation.ExchangerBoundary
    dhw_consumers_return: simulation.TemperatureBoundary
    dhw_seawater_return: simulation.TemperatureBoundary
    dhw_seawater_supply: simulation.FlowBoundary
    dhw_freshwater_return: simulation.Boundary

    @computed_field(
        json_schema_extra=computed_meta(
            included_in_fmu=False, component_type="temperature_sensor"
        )
    )
    @property
    def drives_temperature_recovery_return(self) -> sensor.TemperatureSensor:
        return sensor.TemperatureSensor(
            temperature=self.dhw_drives_exchanger.temperature_return
        )

    @computed_field(
        json_schema_extra=computed_meta(
            included_in_fmu=False, component_type="temperature_sensor"
        )
    )
    @property
    def dc_temperature_recovery_return(self) -> sensor.TemperatureSensor:
        return sensor.TemperatureSensor(
            temperature=self.dhw_dc_exchanger.temperature_return
        )

    @computed_field(
        json_schema_extra=computed_meta(
            included_in_fmu=False, component_type="temperature_sensor"
        )
    )
    @property
    def adsorption_temperature_dhw_return(self) -> sensor.TemperatureSensor:
        return sensor.TemperatureSensor(
            temperature=self.dhw_adsorption_exchanger.temperature_return
        )

    @computed_field(
        json_schema_extra=computed_meta(
            included_in_fmu=False, component_type="temperature_sensor"
        )
    )
    @property
    def consumers_temperature_dhw_return(self) -> sensor.TemperatureSensor:
        return sensor.TemperatureSensor(
            temperature=self.dhw_consumers_exchanger.temperature_return
        )

    @computed_field(
        json_schema_extra=computed_meta(
            included_in_fmu=False, component_type="flow_sensor"
        )
    )
    @property
    def freshwater_hotwater_flow(self) -> sensor.FlowSensor:
        return sensor.FlowSensor(
            flow=self.dhw_freshwater_return.flow,
            temperature=self.dhw_freshwater_return.temperature,
        )

    @computed_field(json_schema_extra=computed_meta(included_in_fmu=False))
    @property
    def freshwater_hotwater_temperature(self) -> sensor.TemperatureSensor:
        return sensor.TemperatureSensor(
            temperature=self.dhw_freshwater_return.temperature
        )
