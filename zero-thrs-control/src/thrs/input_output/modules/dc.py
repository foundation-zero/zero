from typing import Annotated

from pydantic import ConfigDict, computed_field
from pydantic.alias_generators import to_snake

from thrs.input_output.base import (
    Stamped,
    ThrsValues,
    component_meta,
    computed_meta,
    valve_meta,
)
from thrs.input_output.definitions import control, sensor, simulation
from thrs.input_output.definitions.system import AmcsControlMode
from thrs.input_output.definitions.units import GLYCOL_20_HEAT_TRANSFER_CONVERSION
from thrs.input_output.root_types import AmcsModeSensorValues, AmcsWatchdogControlValues


class DcSensorValues(AmcsModeSensorValues):
    model_config = ConfigDict(
        alias_generator=to_snake,
        use_enum_values=True,
        validate_by_name=True,
    )

    dc_pump_aft: Annotated[
        sensor.Pump, component_meta(yard_tag="50001020", component_type="pump")
    ]
    dc_pump_ugrid: Annotated[
        sensor.Pump, component_meta(yard_tag="50001023", component_type="pump")
    ]
    dc_pump_fwd: Annotated[
        sensor.Pump, component_meta(yard_tag="50001025", component_type="pump")
    ]
    dc_temperature_aft4_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-05", component_type="temperature_sensor"),
    ]
    dc_temperature_aft3_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-06", component_type="temperature_sensor"),
    ]
    dc_temperature_aft2_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-07", component_type="temperature_sensor"),
    ]
    dc_temperature_aft1_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-08", component_type="temperature_sensor"),
    ]
    dc_temperature_ugrid2_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-09", component_type="temperature_sensor"),
    ]
    dc_temperature_ugrid1_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-10", component_type="temperature_sensor"),
    ]
    dc_temperature_fwd2_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-12", component_type="temperature_sensor"),
    ]
    dc_temperature_fwd1_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-13", component_type="temperature_sensor"),
    ]
    dc_temperature_aft_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-15", component_type="temperature_sensor"),
    ]
    dc_temperature_recovery_mix: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-17", component_type="temperature_sensor"),
    ]
    dc_temperature_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-18", component_type="temperature_sensor"),
    ]
    dc_temperature_fwd_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-19", component_type="temperature_sensor"),
    ]
    dc_temperature_aft_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-20", component_type="temperature_sensor"),
    ]
    dc_temperature_recovery: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-52", component_type="temperature_sensor"),
    ]
    dc_temperature_recovery_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-58", component_type="temperature_sensor"),
    ]
    dc_temperature_fwd_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-69", component_type="temperature_sensor"),
    ]
    dc_temperature_ugrid_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-70", component_type="temperature_sensor"),
    ]
    dc_temperature_ugrid_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-71", component_type="temperature_sensor"),
    ]
    dc_mix_fwd: Annotated[
        sensor.Valve,
        valve_meta(yard_tag="50001042-03", component_type="valve", valve_type="mix"),
    ]
    dc_mix_aft: Annotated[
        sensor.Valve,
        valve_meta(yard_tag="50001043-02", component_type="valve", valve_type="mix"),
    ]
    dc_mix_ugrid: Annotated[
        sensor.Valve,
        valve_meta(yard_tag="50001045-01", component_type="valve", valve_type="mix"),
    ]
    dc_mix_recovery: Annotated[
        sensor.Valve,
        valve_meta(yard_tag="50001046-04", component_type="valve", valve_type="mix"),
    ]
    dc_mix_exchanger: Annotated[
        sensor.Valve,
        valve_meta(yard_tag="50001046-05", component_type="valve", valve_type="mix"),
    ]
    dc_flow_aft4: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001057-04", component_type="flow_sensor"),
    ]
    dc_flow_aft3: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001057-05", component_type="flow_sensor"),
    ]
    dc_flow_aft2: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001057-06", component_type="flow_sensor"),
    ]
    dc_flow_aft1: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001057-07", component_type="flow_sensor"),
    ]
    dc_flow_ugrid2: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001057-08", component_type="flow_sensor"),
    ]
    dc_flow_ugrid1: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001057-09", component_type="flow_sensor"),
    ]
    dc_flow_fwd2: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001057-11", component_type="flow_sensor"),
    ]
    dc_flow_fwd1: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001057-12", component_type="flow_sensor"),
    ]
    dc_flow_aft_return: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001057-25", component_type="flow_sensor"),
    ]
    dc_flow_fwd_return: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001057-26", component_type="flow_sensor"),
    ]
    dc_flow_recovery: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001058-04", component_type="flow_sensor"),
    ]
    dc_flow_ugrid_return: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001058-06", component_type="flow_sensor"),
    ]
    dc_switch_aft4: Annotated[
        sensor.Valve,
        valve_meta(yard_tag="50001068-01", component_type="valve", valve_type="switch"),
    ]
    dc_switch_aft3: Annotated[
        sensor.Valve,
        valve_meta(yard_tag="50001068-02", component_type="valve", valve_type="switch"),
    ]
    dc_switch_aft2: Annotated[
        sensor.Valve,
        valve_meta(yard_tag="50001068-03", component_type="valve", valve_type="switch"),
    ]
    dc_switch_aft1: Annotated[
        sensor.Valve,
        valve_meta(yard_tag="50001068-04", component_type="valve", valve_type="switch"),
    ]
    dc_switch_fwd2: Annotated[
        sensor.Valve,
        valve_meta(yard_tag="50001068-05", component_type="valve", valve_type="switch"),
    ]
    dc_switch_fwd1: Annotated[
        sensor.Valve,
        valve_meta(yard_tag="50001068-06", component_type="valve", valve_type="switch"),
    ]
    dc_switch_ugrid2: Annotated[
        sensor.Valve,
        valve_meta(yard_tag="50001069-02", component_type="valve", valve_type="switch"),
    ]
    dc_switch_ugrid1: Annotated[
        sensor.Valve,
        valve_meta(yard_tag="50001069-03", component_type="valve", valve_type="switch"),
    ]
    dc_pressure_aft: Annotated[
        sensor.PressureSensor,
        component_meta(yard_tag="50001097-07", component_type="pressure_sensor"),
    ]
    dc_pressure_ugrid: Annotated[
        sensor.PressureSensor,
        component_meta(yard_tag="50001097-08", component_type="pressure_sensor"),
    ]
    dc_pressure_fwd: Annotated[
        sensor.PressureSensor,
        component_meta(yard_tag="50001097-09", component_type="pressure_sensor"),
    ]
    # TODO: confirm that yard tag and battery system both ascend (45002073 is 05_41)
    dc_brightloop_aft1_converter1: Annotated[
        sensor.BrightloopConverter,
        component_meta(
            yard_tag="45002076",
            component_type="brightloop_converter",
            included_in_fmu=False,
            topic_override="450000-main-power-storage-errors/5-44-1",
        ),
    ]
    dc_brightloop_aft1_converter2: Annotated[
        sensor.BrightloopConverter,
        component_meta(
            yard_tag="45002076",
            component_type="brightloop_converter",
            included_in_fmu=False,
            topic_override="450000-main-power-storage-errors/5-44-2",
        ),
    ]
    dc_brightloop_aft1_converter3: Annotated[
        sensor.BrightloopConverter,
        component_meta(
            yard_tag="45002076",
            component_type="brightloop_converter",
            included_in_fmu=False,
            topic_override="450000-main-power-storage-errors/5-44-3",
        ),
    ]
    dc_brightloop_aft1_converter4: Annotated[
        sensor.BrightloopConverter,
        component_meta(
            yard_tag="45002076",
            component_type="brightloop_converter",
            included_in_fmu=False,
            topic_override="450000-main-power-storage-errors/5-44-4",
        ),
    ]
    dc_brightloop_aft2_converter1: Annotated[
        sensor.BrightloopConverter,
        component_meta(
            yard_tag="45002075",
            component_type="brightloop_converter",
            included_in_fmu=False,
            topic_override="450000-main-power-storage-errors/5-43-1",
        ),
    ]
    dc_brightloop_aft2_converter2: Annotated[
        sensor.BrightloopConverter,
        component_meta(
            yard_tag="45002075",
            component_type="brightloop_converter",
            included_in_fmu=False,
            topic_override="450000-main-power-storage-errors/5-43-2",
        ),
    ]
    dc_brightloop_aft2_converter3: Annotated[
        sensor.BrightloopConverter,
        component_meta(
            yard_tag="45002075",
            component_type="brightloop_converter",
            included_in_fmu=False,
            topic_override="450000-main-power-storage-errors/5-43-3",
        ),
    ]
    dc_brightloop_aft3_converter1: Annotated[
        sensor.BrightloopConverter,
        component_meta(
            yard_tag="45002074",
            component_type="brightloop_converter",
            included_in_fmu=False,
            topic_override="450000-main-power-storage-errors/5-42-1",
        ),
    ]
    dc_brightloop_aft3_converter2: Annotated[
        sensor.BrightloopConverter,
        component_meta(
            yard_tag="45002074",
            component_type="brightloop_converter",
            included_in_fmu=False,
            topic_override="450000-main-power-storage-errors/5-42-2",
        ),
    ]
    dc_brightloop_aft3_converter3: Annotated[
        sensor.BrightloopConverter,
        component_meta(
            yard_tag="45002074",
            component_type="brightloop_converter",
            included_in_fmu=False,
            topic_override="450000-main-power-storage-errors/5-42-3",
        ),
    ]
    dc_brightloop_aft4_converter1: Annotated[
        sensor.BrightloopConverter,
        component_meta(
            yard_tag="45002073",
            component_type="brightloop_converter",
            included_in_fmu=False,
            topic_override="450000-main-power-storage-errors/5-41-1",
        ),
    ]
    dc_brightloop_aft4_converter2: Annotated[
        sensor.BrightloopConverter,
        component_meta(
            yard_tag="45002073",
            component_type="brightloop_converter",
            included_in_fmu=False,
            topic_override="450000-main-power-storage-errors/5-41-2",
        ),
    ]
    dc_brightloop_aft4_converter3: Annotated[
        sensor.BrightloopConverter,
        component_meta(
            yard_tag="45002073",
            component_type="brightloop_converter",
            included_in_fmu=False,
            topic_override="450000-main-power-storage-errors/5-41-3",
        ),
    ]
    dc_brightloop_aft4_converter4: Annotated[
        sensor.BrightloopConverter,
        component_meta(
            yard_tag="45002073",
            component_type="brightloop_converter",
            included_in_fmu=False,
            topic_override="450000-main-power-storage-errors/5-41-4",
        ),
    ]
    dc_brightloop_fwd1_converter1: Annotated[
        sensor.BrightloopConverter,
        component_meta(
            yard_tag="45002078",
            component_type="brightloop_converter",
            included_in_fmu=False,
            topic_override="450000-main-power-storage-errors/5-46-1",
        ),
    ]
    dc_brightloop_fwd1_converter2: Annotated[
        sensor.BrightloopConverter,
        component_meta(
            yard_tag="45002078",
            component_type="brightloop_converter",
            included_in_fmu=False,
            topic_override="450000-main-power-storage-errors/5-46-2",
        ),
    ]
    dc_brightloop_fwd1_converter3: Annotated[
        sensor.BrightloopConverter,
        component_meta(
            yard_tag="45002078",
            component_type="brightloop_converter",
            included_in_fmu=False,
            topic_override="450000-main-power-storage-errors/5-46-3",
        ),
    ]
    dc_brightloop_fwd1_converter4: Annotated[
        sensor.BrightloopConverter,
        component_meta(
            yard_tag="45002078",
            component_type="brightloop_converter",
            included_in_fmu=False,
            topic_override="450000-main-power-storage-errors/5-46-4",
        ),
    ]
    dc_brightloop_fwd2_converter1: Annotated[
        sensor.BrightloopConverter,
        component_meta(
            yard_tag="45002077",
            component_type="brightloop_converter",
            included_in_fmu=False,
            topic_override="450000-main-power-storage-errors/5-45-1",
        ),
    ]
    dc_brightloop_fwd2_converter2: Annotated[
        sensor.BrightloopConverter,
        component_meta(
            yard_tag="45002077",
            component_type="brightloop_converter",
            included_in_fmu=False,
            topic_override="450000-main-power-storage-errors/5-45-2",
        ),
    ]
    dc_brightloop_fwd2_converter3: Annotated[
        sensor.BrightloopConverter,
        component_meta(
            yard_tag="45002077",
            component_type="brightloop_converter",
            included_in_fmu=False,
            topic_override="450000-main-power-storage-errors/5-45-3",
        ),
    ]
    dc_brightloop_fwd2_converter4: Annotated[
        sensor.BrightloopConverter,
        component_meta(
            yard_tag="45002077",
            component_type="brightloop_converter",
            included_in_fmu=False,
            topic_override="450000-main-power-storage-errors/5-45-4",
        ),
    ]

    @computed_field(
        json_schema_extra=computed_meta(
            yard_tag="45002076",
            component_type="brightloop",
            included_in_fmu=False,
        )
    )
    @property
    def dc_brightloop_aft1(self) -> sensor.Brightloop:
        return sensor.Brightloop.from_converters(
            (
                self.dc_brightloop_aft1_converter1,
                self.dc_brightloop_aft1_converter2,
                self.dc_brightloop_aft1_converter3,
                self.dc_brightloop_aft1_converter4,
            )
        )

    @computed_field(
        json_schema_extra=computed_meta(
            yard_tag="45002075",
            component_type="brightloop",
            included_in_fmu=False,
        )
    )
    @property
    def dc_brightloop_aft2(self) -> sensor.Brightloop:
        return sensor.Brightloop.from_converters(
            (
                self.dc_brightloop_aft2_converter1,
                self.dc_brightloop_aft2_converter2,
                self.dc_brightloop_aft2_converter3,
            )
        )

    @computed_field(
        json_schema_extra=computed_meta(
            yard_tag="45002074",
            component_type="brightloop",
            included_in_fmu=False,
        )
    )
    @property
    def dc_brightloop_aft3(self) -> sensor.Brightloop:
        return sensor.Brightloop.from_converters(
            (
                self.dc_brightloop_aft3_converter1,
                self.dc_brightloop_aft3_converter2,
                self.dc_brightloop_aft3_converter3,
            )
        )

    @computed_field(
        json_schema_extra=computed_meta(
            yard_tag="45002073",
            component_type="brightloop",
            included_in_fmu=False,
        )
    )
    @property
    def dc_brightloop_aft4(self) -> sensor.Brightloop:
        return sensor.Brightloop.from_converters(
            (
                self.dc_brightloop_aft4_converter1,
                self.dc_brightloop_aft4_converter2,
                self.dc_brightloop_aft4_converter3,
                self.dc_brightloop_aft4_converter4,
            )
        )

    @computed_field(
        json_schema_extra=computed_meta(
            yard_tag="45002078",
            component_type="brightloop",
            included_in_fmu=False,
        )
    )
    @property
    def dc_brightloop_fwd1(self) -> sensor.Brightloop:
        return sensor.Brightloop.from_converters(
            (
                self.dc_brightloop_fwd1_converter1,
                self.dc_brightloop_fwd1_converter2,
                self.dc_brightloop_fwd1_converter3,
                self.dc_brightloop_fwd1_converter4,
            )
        )

    @computed_field(
        json_schema_extra=computed_meta(
            yard_tag="45002077",
            component_type="brightloop",
            included_in_fmu=False,
        )
    )
    @property
    def dc_brightloop_fwd2(self) -> sensor.Brightloop:
        return sensor.Brightloop.from_converters(
            (
                self.dc_brightloop_fwd2_converter1,
                self.dc_brightloop_fwd2_converter2,
                self.dc_brightloop_fwd2_converter3,
                self.dc_brightloop_fwd2_converter4,
            )
        )

    dc_ugrid1: Annotated[
        sensor.Ugrid,
        component_meta(
            yard_tag="45002082",
            component_type="ugrid",
            included_in_fmu=False,
            topic_override="450000-dynamic-conv-ps-ara/5-11-u101",
        ),
    ]
    dc_ugrid2: Annotated[
        sensor.Ugrid,
        component_meta(
            yard_tag="45002081",
            component_type="ugrid",
            included_in_fmu=False,
            topic_override="450000-dynamic-conv-sb/ara-5/12/u101",
        ),
    ]

    @computed_field(
        json_schema_extra=computed_meta(
            component_type="brightloop_group",
            included_in_fmu=False,
        )
    )
    @property
    def dc_aft_brightloops(self) -> sensor.BrightloopGroup:
        return sensor.BrightloopGroup.from_brightloops(
            (
                self.dc_brightloop_aft1,
                self.dc_brightloop_aft2,
                self.dc_brightloop_aft3,
                self.dc_brightloop_aft4,
            )
        )

    @computed_field(
        json_schema_extra=computed_meta(
            component_type="brightloop_group",
            included_in_fmu=False,
        )
    )
    @property
    def dc_fwd_brightloops(self) -> sensor.BrightloopGroup:
        return sensor.BrightloopGroup.from_brightloops(
            (self.dc_brightloop_fwd1, self.dc_brightloop_fwd2)
        )

    @computed_field(
        json_schema_extra=computed_meta(
            component_type="ugrid_group",
            included_in_fmu=False,
        )
    )
    @property
    def dc_ugrids(self) -> sensor.UgridGroup:
        return sensor.UgridGroup.from_ugrids((self.dc_ugrid1, self.dc_ugrid2))

    @computed_field(
        json_schema_extra=computed_meta(
            yard_tag="50001008",
            component_type="heat_transfer",
            included_in_fmu=False,
        )
    )
    @property
    def dc_dhw_exchanger(self) -> sensor.HeatTransferDevice:
        return sensor.HeatTransferDevice.from_sensors(
            temperature_supply=self.dc_temperature_recovery.temperature,
            temperature_return=self.dc_temperature_recovery_return.temperature,
            flow=self.dc_flow_recovery.flow,
            heat_transfer_conversion=GLYCOL_20_HEAT_TRANSFER_CONVERSION,
            temperature_supply_source=sensor.extract_source_yardtag(
                self, "dc_temperature_recovery"
            ),
            temperature_return_source=sensor.extract_source_yardtag(
                self, "dc_temperature_recovery_return"
            ),
            flow_source=sensor.extract_source_yardtag(self, "dc_flow_recovery"),
        )

    @computed_field(
        json_schema_extra=computed_meta(
            component_type="calculated_flow", included_in_fmu=False
        )
    )
    @property
    def dc_total_flow(self) -> sensor.CalculatedFlow:
        return sensor.CalculatedFlow(
            flow=Stamped.combine(
                self.dc_flow_aft_return.flow,
                self.dc_flow_fwd_return.flow,
                self.dc_flow_ugrid_return.flow,
                value=self.dc_flow_aft_return.flow.value
                + self.dc_flow_fwd_return.flow.value
                + self.dc_flow_ugrid_return.flow.value,
            )
        )

    @computed_field(
        json_schema_extra=computed_meta(
            yard_tag="50001006",
            component_type="heat_transfer",
            included_in_fmu=False,
        )
    )
    @property
    def dc_seawater_exchanger(self) -> sensor.HeatTransferDevice:
        return sensor.HeatTransferDevice.from_sensors_with_mix_valve(
            temperature_supply=self.dc_temperature_recovery_mix.temperature,
            temperature_return=self.dc_temperature_supply.temperature,
            flow=self.dc_total_flow.flow,
            mix_valve=self.dc_mix_exchanger,
            heat_transfer_conversion=GLYCOL_20_HEAT_TRANSFER_CONVERSION,
            temperature_supply_source=sensor.extract_source_yardtag(
                self, "dc_temperature_recovery_mix"
            ),
            temperature_return_source=sensor.extract_source_yardtag(
                self, "dc_temperature_supply"
            ),
        )

    @computed_field(
        json_schema_extra=computed_meta(
            component_type="calculated_flow", included_in_fmu=False
        )
    )
    @property
    def dc_aft_flow(self) -> sensor.CalculatedFlow:
        return sensor.CalculatedFlow(
            flow=Stamped.combine(
                self.dc_flow_aft1.flow,
                self.dc_flow_aft2.flow,
                self.dc_flow_aft3.flow,
                self.dc_flow_aft4.flow,
                value=self.dc_flow_aft1.flow.value
                + self.dc_flow_aft2.flow.value
                + self.dc_flow_aft3.flow.value
                + self.dc_flow_aft4.flow.value,
            )
        )

    @computed_field(
        json_schema_extra=computed_meta(
            component_type="heat_transfer",
            included_in_fmu=False,
        )
    )
    @property
    def dc_aft_heat(self) -> sensor.HeatTransferDevice:
        return sensor.HeatTransferDevice.from_sensors(
            temperature_supply=self.dc_temperature_aft_supply.temperature,
            temperature_return=self.dc_temperature_aft_return.temperature,
            flow=self.dc_aft_flow.flow,
            heat_transfer_conversion=GLYCOL_20_HEAT_TRANSFER_CONVERSION,
            temperature_supply_source=sensor.extract_source_yardtag(
                self, "dc_temperature_aft_supply"
            ),
            temperature_return_source=sensor.extract_source_yardtag(
                self, "dc_temperature_aft_return"
            ),
            flow_source=sensor.extract_source_yardtag(self, "dc_aft_flow"),
        )

    @computed_field(
        json_schema_extra=computed_meta(
            component_type="calculated_flow", included_in_fmu=False
        )
    )
    @property
    def dc_ugrid_flow(self) -> sensor.CalculatedFlow:
        return sensor.CalculatedFlow(
            flow=Stamped.combine(
                self.dc_flow_ugrid1.flow,
                self.dc_flow_ugrid2.flow,
                value=self.dc_flow_ugrid1.flow.value + self.dc_flow_ugrid2.flow.value,
            )
        )

    @computed_field(
        json_schema_extra=computed_meta(
            component_type="heat_transfer",
            included_in_fmu=False,
        )
    )
    @property
    def dc_ugrid_heat(self) -> sensor.HeatTransferDevice:
        return sensor.HeatTransferDevice.from_sensors(
            temperature_supply=self.dc_temperature_ugrid_supply.temperature,
            temperature_return=self.dc_temperature_ugrid_return.temperature,
            flow=self.dc_ugrid_flow.flow,
            heat_transfer_conversion=GLYCOL_20_HEAT_TRANSFER_CONVERSION,
            temperature_supply_source=sensor.extract_source_yardtag(
                self, "dc_temperature_ugrid_supply"
            ),
            temperature_return_source=sensor.extract_source_yardtag(
                self, "dc_temperature_ugrid_return"
            ),
            flow_source=sensor.extract_source_yardtag(self, "dc_ugrid_flow"),
        )

    @computed_field(
        json_schema_extra=computed_meta(
            component_type="calculated_flow", included_in_fmu=False
        )
    )
    @property
    def dc_fwd_flow(self) -> sensor.CalculatedFlow:
        return sensor.CalculatedFlow(
            flow=Stamped.combine(
                self.dc_flow_fwd1.flow,
                self.dc_flow_fwd2.flow,
                value=self.dc_flow_fwd1.flow.value + self.dc_flow_fwd2.flow.value,
            )
        )

    @computed_field(
        json_schema_extra=computed_meta(
            component_type="heat_transfer",
            included_in_fmu=False,
        )
    )
    @property
    def dc_fwd_heat(self) -> sensor.HeatTransferDevice:
        return sensor.HeatTransferDevice.from_sensors(
            temperature_supply=self.dc_temperature_fwd_supply.temperature,
            temperature_return=self.dc_temperature_fwd_return.temperature,
            flow=self.dc_fwd_flow.flow,
            heat_transfer_conversion=GLYCOL_20_HEAT_TRANSFER_CONVERSION,
            temperature_supply_source=sensor.extract_source_yardtag(
                self, "dc_temperature_fwd_supply"
            ),
            temperature_return_source=sensor.extract_source_yardtag(
                self, "dc_temperature_fwd_return"
            ),
            flow_source=sensor.extract_source_yardtag(self, "dc_fwd_flow"),
        )


class DcControlValues(AmcsWatchdogControlValues):
    model_config = ConfigDict(
        alias_generator=to_snake,
        use_enum_values=True,
        validate_by_name=True,
    )

    dc_pump_aft: Annotated[
        control.Pump, component_meta(yard_tag="50001020", component_type="pump")
    ]
    dc_pump_fwd: Annotated[
        control.Pump, component_meta(yard_tag="50001025", component_type="pump")
    ]
    dc_pump_ugrid: Annotated[
        control.Pump, component_meta(yard_tag="50001023", component_type="pump")
    ]
    dc_mix_aft: Annotated[
        control.Valve,
        valve_meta(yard_tag="50001043-02", component_type="valve", valve_type="mix"),
    ]
    dc_mix_fwd: Annotated[
        control.Valve,
        valve_meta(yard_tag="50001042-03", component_type="valve", valve_type="mix"),
    ]
    dc_mix_ugrid: Annotated[
        control.Valve,
        valve_meta(yard_tag="50001045-01", component_type="valve", valve_type="mix"),
    ]
    dc_mix_recovery: Annotated[
        control.Valve,
        valve_meta(yard_tag="50001046-04", component_type="valve", valve_type="mix"),
    ]
    dc_mix_exchanger: Annotated[
        control.Valve,
        valve_meta(yard_tag="50001046-05", component_type="valve", valve_type="mix"),
    ]
    dc_switch_aft4: Annotated[
        control.Valve,
        valve_meta(yard_tag="50001068-01", component_type="valve", valve_type="switch"),
    ]
    dc_switch_aft3: Annotated[
        control.Valve,
        valve_meta(yard_tag="50001068-02", component_type="valve", valve_type="switch"),
    ]
    dc_switch_aft2: Annotated[
        control.Valve,
        valve_meta(yard_tag="50001068-03", component_type="valve", valve_type="switch"),
    ]
    dc_switch_aft1: Annotated[
        control.Valve,
        valve_meta(yard_tag="50001068-04", component_type="valve", valve_type="switch"),
    ]
    dc_switch_fwd2: Annotated[
        control.Valve,
        valve_meta(yard_tag="50001068-05", component_type="valve", valve_type="switch"),
    ]
    dc_switch_fwd1: Annotated[
        control.Valve,
        valve_meta(yard_tag="50001068-06", component_type="valve", valve_type="switch"),
    ]
    dc_switch_ugrid2: Annotated[
        control.Valve,
        valve_meta(yard_tag="50001069-02", component_type="valve", valve_type="switch"),
    ]
    dc_switch_ugrid1: Annotated[
        control.Valve,
        valve_meta(yard_tag="50001069-03", component_type="valve", valve_type="switch"),
    ]


class DcSimulationInputs(ThrsValues):
    dc_brightloop_fwd1_converter1: Annotated[
        simulation.BrightloopConverter, component_meta(included_in_fmu=False)
    ]
    dc_brightloop_fwd1_converter2: Annotated[
        simulation.BrightloopConverter, component_meta(included_in_fmu=False)
    ]
    dc_brightloop_fwd1_converter3: Annotated[
        simulation.BrightloopConverter, component_meta(included_in_fmu=False)
    ]
    dc_brightloop_fwd1_converter4: Annotated[
        simulation.BrightloopConverter, component_meta(included_in_fmu=False)
    ]
    dc_brightloop_fwd2_converter1: Annotated[
        simulation.BrightloopConverter, component_meta(included_in_fmu=False)
    ]
    dc_brightloop_fwd2_converter2: Annotated[
        simulation.BrightloopConverter, component_meta(included_in_fmu=False)
    ]
    dc_brightloop_fwd2_converter3: Annotated[
        simulation.BrightloopConverter, component_meta(included_in_fmu=False)
    ]
    dc_brightloop_fwd2_converter4: Annotated[
        simulation.BrightloopConverter, component_meta(included_in_fmu=False)
    ]
    dc_ugrid1: simulation.Ugrid
    dc_ugrid2: simulation.Ugrid
    dc_brightloop_aft1_converter1: Annotated[
        simulation.BrightloopConverter, component_meta(included_in_fmu=False)
    ]
    dc_brightloop_aft1_converter2: Annotated[
        simulation.BrightloopConverter, component_meta(included_in_fmu=False)
    ]
    dc_brightloop_aft1_converter3: Annotated[
        simulation.BrightloopConverter, component_meta(included_in_fmu=False)
    ]
    dc_brightloop_aft1_converter4: Annotated[
        simulation.BrightloopConverter, component_meta(included_in_fmu=False)
    ]
    dc_brightloop_aft2_converter1: Annotated[
        simulation.BrightloopConverter, component_meta(included_in_fmu=False)
    ]
    dc_brightloop_aft2_converter2: Annotated[
        simulation.BrightloopConverter, component_meta(included_in_fmu=False)
    ]
    dc_brightloop_aft2_converter3: Annotated[
        simulation.BrightloopConverter, component_meta(included_in_fmu=False)
    ]
    dc_brightloop_aft3_converter1: Annotated[
        simulation.BrightloopConverter, component_meta(included_in_fmu=False)
    ]
    dc_brightloop_aft3_converter2: Annotated[
        simulation.BrightloopConverter, component_meta(included_in_fmu=False)
    ]
    dc_brightloop_aft3_converter3: Annotated[
        simulation.BrightloopConverter, component_meta(included_in_fmu=False)
    ]
    dc_brightloop_aft4_converter1: Annotated[
        simulation.BrightloopConverter, component_meta(included_in_fmu=False)
    ]
    dc_brightloop_aft4_converter2: Annotated[
        simulation.BrightloopConverter, component_meta(included_in_fmu=False)
    ]
    dc_brightloop_aft4_converter3: Annotated[
        simulation.BrightloopConverter, component_meta(included_in_fmu=False)
    ]
    dc_brightloop_aft4_converter4: Annotated[
        simulation.BrightloopConverter, component_meta(included_in_fmu=False)
    ]
    dc_seawater_supply: simulation.Boundary
    dc_dhw_supply: simulation.Boundary
    mode: Annotated[AmcsControlMode, component_meta(included_in_fmu=False)]
    dc_brightloop_fwd1: simulation.HeatSource
    dc_brightloop_fwd2: simulation.HeatSource
    dc_brightloop_aft1: simulation.HeatSource
    dc_brightloop_aft2: simulation.HeatSource
    dc_brightloop_aft3: simulation.HeatSource
    dc_brightloop_aft4: simulation.HeatSource


class DcSimulationOutputs(ThrsValues):
    dc_seawater_return: simulation.TemperatureBoundary
    dc_dhw_exchanger: simulation.ExchangerBoundary
    dc_dhw_return: simulation.TemperatureBoundary
