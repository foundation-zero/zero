from datetime import UTC, datetime
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


class DrivesSensorValues(AmcsModeSensorValues):
    model_config = ConfigDict(
        alias_generator=to_snake,
        use_enum_values=True,
        validate_by_name=True,
    )

    drives_pump1: Annotated[
        sensor.Pump, component_meta(yard_tag="50001028", component_type="pump")
    ]
    drives_pump2: Annotated[
        sensor.Pump, component_meta(yard_tag="50001029", component_type="pump")
    ]
    drives_temperature_shorepower_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-11", component_type="temperature_sensor"),
    ]
    drives_temperature_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-14", component_type="temperature_sensor"),
    ]
    drives_temperature_recovery: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-16", component_type="temperature_sensor"),
    ]
    drives_temperature_recovery_mix: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-57", component_type="temperature_sensor"),
    ]
    drives_temperature_recovery_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-59", component_type="temperature_sensor"),
    ]
    drives_temperature_propdrive_aft1_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-32", component_type="temperature_sensor"),
    ]
    drives_temperature_propdrive_fwd1_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-61", component_type="temperature_sensor"),
    ]
    drives_temperature_propdrives_fwd_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-62", component_type="temperature_sensor"),
    ]
    drives_temperature_propdrives_aft_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-63", component_type="temperature_sensor"),
    ]
    drives_temperature_propdrive_aft2_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-64", component_type="temperature_sensor"),
    ]
    drives_temperature_propdrive_fwd2_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-72", component_type="temperature_sensor"),
    ]
    drives_mix_exchanger: Annotated[
        sensor.Valve,
        valve_meta(yard_tag="50001046-01", component_type="valve", valve_type="mix"),
    ]
    drives_mix_recovery: Annotated[
        sensor.Valve,
        valve_meta(yard_tag="50001046-03", component_type="valve", valve_type="mix"),
    ]
    drives_flow_shorepower: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001057-10", component_type="flow_sensor"),
    ]
    drives_flow_propdrive_aft1: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001057-13", component_type="flow_sensor"),
    ]
    drives_flow_propdrive_fwd2: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001057-14", component_type="flow_sensor"),
    ]
    drives_flow_propdrive_fwd1: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001057-15", component_type="flow_sensor"),
    ]
    drives_flow_propdrive_aft2: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001057-16", component_type="flow_sensor"),
    ]
    drives_flow_recovery: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001058-03", component_type="flow_sensor"),
    ]
    drives_flowcontrol_propdrive_aft: Annotated[
        sensor.Valve,
        valve_meta(
            yard_tag="50001065-02", component_type="valve", valve_type="flowcontrol"
        ),
    ]
    drives_flowcontrol_propdrive_fwd: Annotated[
        sensor.Valve,
        valve_meta(
            yard_tag="50001065-03", component_type="valve", valve_type="flowcontrol"
        ),
    ]
    drives_switch_shorepower_supply: Annotated[
        sensor.Valve,
        valve_meta(yard_tag="50001069-04", component_type="valve", valve_type="switch"),
    ]
    drives_switch_shorepower_return: Annotated[
        sensor.Valve,
        valve_meta(yard_tag="50001069-05", component_type="valve", valve_type="switch"),
    ]
    drives_switch_propdrive_aft1: Annotated[
        sensor.Valve,
        valve_meta(yard_tag="50001069-06", component_type="valve", valve_type="switch"),
    ]
    drives_switch_propdrive_aft2: Annotated[
        sensor.Valve,
        valve_meta(yard_tag="50001069-09", component_type="valve", valve_type="switch"),
    ]
    drives_switch_propdrive_fwd1: Annotated[
        sensor.Valve,
        valve_meta(yard_tag="50001069-07", component_type="valve", valve_type="switch"),
    ]
    drives_switch_propdrive_fwd2: Annotated[
        sensor.Valve,
        valve_meta(yard_tag="50001069-08", component_type="valve", valve_type="switch"),
    ]
    drives_pressure: Annotated[
        sensor.PressureSensor,
        component_meta(yard_tag="50001097-10", component_type="pressure_sensor"),
    ]
    drives_propdrive_aft1: Annotated[
        sensor.PropulsionDrive,
        component_meta(
            yard_tag="45002079",  # TODO: figure out correct yard tag. We do expect separate signal from each Aradex
            component_type="propulsion_drive",
            included_in_fmu=False,
            topic_override="dummy-pms/esi_active",
        ),
    ] = sensor.PropulsionDrive(
        active=Stamped(value=False, timestamp=datetime.fromtimestamp(0, UTC))
    )

    @computed_field(
        json_schema_extra=computed_meta(
            component_type="heat_transfer",
            included_in_fmu=False,
        )
    )
    @property
    def drives_propdrive_aft1_heat(self) -> sensor.HeatTransferDevice:
        return sensor.HeatTransferDevice.from_sensors(
            temperature_supply=self.drives_temperature_propdrives_aft_supply.temperature,
            temperature_return=self.drives_temperature_propdrive_aft1_return.temperature,
            flow=self.drives_flow_propdrive_aft1.flow,
            heat_transfer_conversion=GLYCOL_20_HEAT_TRANSFER_CONVERSION,
            temperature_supply_source=sensor.extract_source_yardtag(
                self, "drives_temperature_propdrives_aft_supply"
            ),
            temperature_return_source=sensor.extract_source_yardtag(
                self, "drives_temperature_propdrive_aft1_return"
            ),
            flow_source=sensor.extract_source_yardtag(
                self, "drives_flow_propdrive_aft1"
            ),
        )

    drives_propdrive_aft2: Annotated[
        sensor.PropulsionDrive,
        component_meta(
            yard_tag="45002079",  # TODO: figure out correct yard tag. We do expect separate signal from each Aradex
            component_type="propulsion_drive",
            included_in_fmu=False,
            topic_override="dummy-pcs/aradex-aft2-active",
        ),
    ] = sensor.PropulsionDrive(
        active=Stamped(value=False, timestamp=datetime.fromtimestamp(0, UTC))
    )

    @computed_field(
        json_schema_extra=computed_meta(
            component_type="heat_transfer",
            included_in_fmu=False,
        )
    )
    @property
    def drives_propdrive_aft2_heat(self) -> sensor.HeatTransferDevice:
        return sensor.HeatTransferDevice.from_sensors(
            temperature_supply=self.drives_temperature_propdrives_aft_supply.temperature,
            temperature_return=self.drives_temperature_propdrive_aft2_return.temperature,
            flow=self.drives_flow_propdrive_aft2.flow,
            heat_transfer_conversion=GLYCOL_20_HEAT_TRANSFER_CONVERSION,
            temperature_supply_source=sensor.extract_source_yardtag(
                self, "drives_temperature_propdrives_aft_supply"
            ),
            temperature_return_source=sensor.extract_source_yardtag(
                self, "drives_temperature_propdrive_aft2_return"
            ),
            flow_source=sensor.extract_source_yardtag(
                self, "drives_flow_propdrive_aft2"
            ),
        )

    # TODO: We need this for correct heatdump on the oil cooler
    # It currently does not work because we don't know the flow pas the bypass
    # @computed_field(
    #     json_schema_extra=computed_meta(
    #         component_type="calculated_flow", included_in_fmu=False
    #     )
    # )
    # @property
    # def drives_flow_propdrive_aft(self) -> sensor.CalculatedFlow:
    #     return sensor.CalculatedFlow(
    #         flow=Stamped.combine(
    #             self.drives_flow_propdrive_aft1.flow,
    #             self.drives_flow_propdrive_aft2.flow,
    #             value=self.drives_flow_propdrive_aft1.flow.value
    #             + self.drives_flow_propdrive_aft2.flow.value,
    #         )
    #     )

    @computed_field(
        json_schema_extra=computed_meta(
            yard_tag="50001012",
            component_type="heat_transfer",
            included_in_fmu=False,
        )
    )
    @property
    def drives_aft_oil_cooler_heat(self) -> sensor.HeatTransferDevice:
        return sensor.HeatTransferDevice.from_sensors(
            temperature_supply=self.drives_temperature_supply.temperature,
            temperature_return=self.drives_temperature_propdrives_aft_supply.temperature,
            flow=Stamped.combine(self.drives_flow_recovery.flow, value=None),
            heat_transfer_conversion=GLYCOL_20_HEAT_TRANSFER_CONVERSION,
            temperature_supply_source=sensor.extract_source_yardtag(
                self, "drives_temperature_supply"
            ),
            temperature_return_source=sensor.extract_source_yardtag(
                self, "drives_temperature_propdrives_aft_supply"
            ),
            flow_source="unknown",
        )

    drives_propdrive_fwd1: Annotated[
        sensor.PropulsionDrive,
        component_meta(
            yard_tag="45002080",  # TODO: figure out correct yard tag. We do expect separate signal from each Aradex
            component_type="propulsion_drive",
            included_in_fmu=False,
            topic_override="dummy-pcs/aradex-fwd1-active",
        ),
    ] = sensor.PropulsionDrive(
        active=Stamped(value=False, timestamp=datetime.fromtimestamp(0, UTC))
    )

    @computed_field(
        json_schema_extra=computed_meta(
            component_type="heat_transfer",
            included_in_fmu=False,
        )
    )
    @property
    def drives_propdrive_fwd1_heat(self) -> sensor.HeatTransferDevice:
        return sensor.HeatTransferDevice.from_sensors(
            temperature_supply=self.drives_temperature_propdrives_fwd_supply.temperature,
            temperature_return=self.drives_temperature_propdrive_fwd1_return.temperature,
            flow=self.drives_flow_propdrive_fwd1.flow,
            heat_transfer_conversion=GLYCOL_20_HEAT_TRANSFER_CONVERSION,
            temperature_supply_source=sensor.extract_source_yardtag(
                self, "drives_temperature_propdrives_fwd_supply"
            ),
            temperature_return_source=sensor.extract_source_yardtag(
                self, "drives_temperature_propdrive_fwd1_return"
            ),
            flow_source=sensor.extract_source_yardtag(
                self, "drives_flow_propdrive_fwd1"
            ),
        )

    drives_propdrive_fwd2: Annotated[
        sensor.PropulsionDrive,
        component_meta(
            yard_tag="45002080",  # TODO: figure out correct yard tag. We do expect separate signal from each Aradex
            component_type="propulsion_drive",
            included_in_fmu=False,
            topic_override="dummy-pcs/aradex-fwd2-active",
        ),
    ] = sensor.PropulsionDrive(
        active=Stamped(value=False, timestamp=datetime.fromtimestamp(0, UTC))
    )

    @computed_field(
        json_schema_extra=computed_meta(
            component_type="heat_transfer",
            included_in_fmu=False,
        )
    )
    @property
    def drives_propdrive_fwd2_heat(self) -> sensor.HeatTransferDevice:
        return sensor.HeatTransferDevice.from_sensors(
            temperature_supply=self.drives_temperature_propdrives_fwd_supply.temperature,
            temperature_return=self.drives_temperature_propdrive_fwd2_return.temperature,
            flow=self.drives_flow_propdrive_fwd2.flow,
            heat_transfer_conversion=GLYCOL_20_HEAT_TRANSFER_CONVERSION,
            temperature_supply_source=sensor.extract_source_yardtag(
                self, "drives_temperature_propdrives_fwd_supply"
            ),
            temperature_return_source=sensor.extract_source_yardtag(
                self, "drives_temperature_propdrive_fwd2_return"
            ),
            flow_source=sensor.extract_source_yardtag(
                self, "drives_flow_propdrive_fwd2"
            ),
        )

    # TODO: We need this for correct heatdump on the oil cooler
    # It currently does not work because we don't know the flow pas the bypass
    # @computed_field(
    #     json_schema_extra=computed_meta(
    #         component_type="calculated_flow", included_in_fmu=False
    #     )
    # )
    # @property
    # def drives_flow_propdrive_fwd(self) -> sensor.CalculatedFlow:
    #     return sensor.CalculatedFlow(
    #         flow=Stamped.combine(
    #             self.drives_flow_propdrive_fwd1.flow,
    #             self.drives_flow_propdrive_fwd2.flow,
    #             value=self.drives_flow_propdrive_fwd1.flow.value
    #             + self.drives_flow_propdrive_fwd2.flow.value,
    #         )
    #     )

    @computed_field(
        json_schema_extra=computed_meta(
            yard_tag="50001013",
            component_type="heat_transfer",
            included_in_fmu=False,
        )
    )
    @property
    def drives_fwd_oil_cooler_heat(self) -> sensor.HeatTransferDevice:
        return sensor.HeatTransferDevice.from_sensors(
            temperature_supply=self.drives_temperature_supply.temperature,
            temperature_return=self.drives_temperature_propdrives_fwd_supply.temperature,
            flow=Stamped.combine(self.drives_flow_recovery.flow, value=None),
            heat_transfer_conversion=GLYCOL_20_HEAT_TRANSFER_CONVERSION,
            temperature_supply_source=sensor.extract_source_yardtag(
                self, "drives_temperature_supply"
            ),
            temperature_return_source=sensor.extract_source_yardtag(
                self, "drives_temperature_propdrives_fwd_supply"
            ),
            flow_source="unknown",
        )

    drives_shorepower: Annotated[
        sensor.ShorePowerConverter,
        component_meta(
            yard_tag="45002001",
            component_type="shore_power_converter",
            included_in_fmu=False,
            topic_override="dummy-pcs/shorepower-active",  # TODO
        ),
    ] = sensor.ShorePowerConverter(
        active=Stamped(value=False, timestamp=datetime.fromtimestamp(0, UTC))
    )

    @computed_field(
        json_schema_extra=computed_meta(
            component_type="heat_transfer",
            included_in_fmu=False,
        )
    )
    @property
    def drives_shorepower_heat(self) -> sensor.HeatTransferDevice:
        return sensor.HeatTransferDevice.from_sensors(
            temperature_supply=self.drives_temperature_supply.temperature,
            temperature_return=self.drives_temperature_shorepower_return.temperature,
            flow=self.drives_flow_shorepower.flow,
            heat_transfer_conversion=GLYCOL_20_HEAT_TRANSFER_CONVERSION,
            temperature_supply_source=sensor.extract_source_yardtag(
                self, "drives_temperature_supply"
            ),
            temperature_return_source=sensor.extract_source_yardtag(
                self, "drives_temperature_shorepower_return"
            ),
            flow_source=sensor.extract_source_yardtag(self, "drives_flow_shorepower"),
        )

    @computed_field(
        json_schema_extra=computed_meta(
            yard_tag="50001009",
            component_type="heat_transfer",
            included_in_fmu=False,
        )
    )
    @property
    def drives_dhw_exchanger(self) -> sensor.HeatTransferDevice:
        return sensor.HeatTransferDevice.from_sensors(
            temperature_supply=self.drives_temperature_recovery.temperature,
            temperature_return=self.drives_temperature_recovery_return.temperature,
            flow=self.drives_flow_recovery.flow,
            heat_transfer_conversion=GLYCOL_20_HEAT_TRANSFER_CONVERSION,
            temperature_supply_source=sensor.extract_source_yardtag(
                self, "drives_temperature_recovery"
            ),
            temperature_return_source=sensor.extract_source_yardtag(
                self, "drives_temperature_recovery_return"
            ),
            flow_source=sensor.extract_source_yardtag(self, "drives_flow_recovery"),
        )

    # TODO: We need this for correct heatdump to the seawater if dhw bypass is active
    # @computed_field(
    #     json_schema_extra=computed_meta(
    #         component_type="calculated_flow", included_in_fmu=False
    #     )
    # )
    # @property
    # def drives_total_flow(self) -> sensor.CalculatedFlow:
    #     return sensor.CalculatedFlow(
    #         flow=Stamped.combine(
    #             self.drives_flow_propdrive_aft.flow,
    #             self.drives_flow_propdrive_fwd.flow,
    #             self.drives_flow_shorepower.flow,
    #             value=self.drives_flow_propdrive_aft.flow.value
    #             + self.drives_flow_propdrive_fwd.flow.value
    #             + self.drives_flow_shorepower.flow.value,
    #         )
    #     )

    @computed_field(
        json_schema_extra=computed_meta(
            yard_tag="50001011",
            component_type="heat_transfer",
            included_in_fmu=False,
        )
    )
    @property
    def drives_seawater_exchanger(self) -> sensor.HeatTransferDevice:
        if sensor.valves_open_closed(open_valves=[self.drives_mix_recovery]):
            flow = self.drives_flow_recovery.flow
            flow_source = sensor.extract_source_yardtag(self, "drives_flow_recovery")
        else:
            flow = Stamped.combine(self.drives_flow_recovery.flow, value=None)
            flow_source = "unknown"

        return sensor.HeatTransferDevice.from_sensors_with_mix_valve(
            temperature_supply=self.drives_temperature_recovery_mix.temperature,
            temperature_return=self.drives_temperature_supply.temperature,
            flow=flow,  # type: ignore
            mix_valve=self.drives_mix_exchanger,
            heat_transfer_conversion=GLYCOL_20_HEAT_TRANSFER_CONVERSION,
            temperature_supply_source=sensor.extract_source_yardtag(
                self, "drives_temperature_recovery_mix"
            ),
            temperature_return_source=flow_source,
        )


class DrivesControlValues(AmcsWatchdogControlValues):
    model_config = ConfigDict(
        alias_generator=to_snake,
        use_enum_values=True,
        validate_by_name=True,
    )

    drives_pump1: Annotated[
        control.Pump, component_meta(yard_tag="50001028", component_type="pump")
    ]
    drives_pump2: Annotated[
        control.Pump, component_meta(yard_tag="50001029", component_type="pump")
    ]
    drives_mix_exchanger: Annotated[
        control.Valve,
        valve_meta(yard_tag="50001046-01", component_type="valve", valve_type="mix"),
    ]
    drives_mix_recovery: Annotated[
        control.Valve,
        valve_meta(yard_tag="50001046-03", component_type="valve", valve_type="mix"),
    ]
    drives_flowcontrol_propdrive_aft: Annotated[
        control.Valve,
        valve_meta(
            yard_tag="50001065-02", component_type="valve", valve_type="flowcontrol"
        ),
    ]
    drives_flowcontrol_propdrive_fwd: Annotated[
        control.Valve,
        valve_meta(
            yard_tag="50001065-03", component_type="valve", valve_type="flowcontrol"
        ),
    ]
    drives_switch_shorepower_supply: Annotated[
        control.Valve,
        valve_meta(yard_tag="50001069-04", component_type="valve", valve_type="switch"),
    ]
    drives_switch_shorepower_return: Annotated[
        control.Valve,
        valve_meta(yard_tag="50001069-05", component_type="valve", valve_type="switch"),
    ]
    drives_switch_propdrive_aft1: Annotated[
        control.Valve,
        valve_meta(yard_tag="50001069-06", component_type="valve", valve_type="switch"),
    ]
    drives_switch_propdrive_aft2: Annotated[
        control.Valve,
        valve_meta(yard_tag="50001069-09", component_type="valve", valve_type="switch"),
    ]
    drives_switch_propdrive_fwd1: Annotated[
        control.Valve,
        valve_meta(yard_tag="50001069-07", component_type="valve", valve_type="switch"),
    ]
    drives_switch_propdrive_fwd2: Annotated[
        control.Valve,
        valve_meta(yard_tag="50001069-08", component_type="valve", valve_type="switch"),
    ]


class DrivesSimulationInputs(ThrsValues):
    drives_oil_cooler_aft: simulation.HeatSource
    drives_oil_cooler_fwd: simulation.HeatSource
    drives_propdrive_aft1: simulation.PropulsionDrive
    drives_propdrive_aft2: simulation.PropulsionDrive
    drives_propdrive_fwd1: simulation.PropulsionDrive
    drives_propdrive_fwd2: simulation.PropulsionDrive
    drives_shorepower: simulation.Converter
    drives_seawater_supply: simulation.Boundary
    drives_dhw_supply: simulation.Boundary
    mode: Annotated[AmcsControlMode, component_meta(included_in_fmu=False)]


class DrivesSimulationOutputs(ThrsValues):
    drives_seawater_return: simulation.TemperatureBoundary
    drives_dhw_exchanger: simulation.ExchangerBoundary
    drives_dhw_return: simulation.TemperatureBoundary
