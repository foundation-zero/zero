from datetime import UTC, datetime
from typing import Annotated, cast

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
from thrs.input_output.definitions.control import Valve
from thrs.input_output.definitions.system import AmcsControlMode
from thrs.input_output.definitions.units import (
    GLYCOL_20_HEAT_TRANSFER_CONVERSION,
    WATER_HEAT_TRANSFER_CONVERSION,
    OptionalCelsius,
)
from thrs.input_output.root_types import AmcsModeSensorValues, AmcsWatchdogControlValues


class PcmSensorValues(AmcsModeSensorValues):
    model_config = ConfigDict(
        alias_generator=to_snake,
        use_enum_values=True,
        validate_by_name=True,
    )

    pcm_pump: Annotated[
        sensor.Pump, component_meta(yard_tag="50001017", component_type="pump")
    ]
    pcm_temperature_producers_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-31", component_type="temperature_sensor"),
    ]
    pcm_temperature_producers_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-55", component_type="temperature_sensor"),
    ]
    pcm_temperature_module1: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-60", component_type="temperature_sensor"),
    ]
    pcm_temperature_module2: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-33", component_type="temperature_sensor"),
    ]
    pcm_temperature_module3: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-34", component_type="temperature_sensor"),
    ]
    pcm_temperature_module4: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-35", component_type="temperature_sensor"),
    ]
    freshwater_temperature_pcm_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(
            yard_tag="25001038-5",
            component_type="temperature_sensor",
            included_in_fmu=False,
            topic_override="250000-fresh-water/hot/hot-temperature-to-pcm",
        ),
    ]
    freshwater_temperature_pcm_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(
            yard_tag="25001038-3",
            component_type="temperature_sensor",
            included_in_fmu=False,
            topic_override="250000-fresh-water/hot/hot-temperature-from-pcm",
        ),
    ]
    pcm_flow_module1: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001057-18", component_type="flow_sensor"),
    ]
    pcm_flow_module2: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001057-19", component_type="flow_sensor"),
    ]
    pcm_flow_module3: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001057-20", component_type="flow_sensor"),
    ]
    pcm_flow_module4: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001057-21", component_type="flow_sensor"),
    ]
    freshwater_flow_pcm: Annotated[
        sensor.FlowOnlySensor,
        component_meta(
            yard_tag="25001139",
            component_type="flow_sensor",
            included_in_fmu=False,
            topic_override="250000-fresh-water/hot/hot-flow-to-pcm",
        ),
    ]
    pcm_switch_charging_return: Annotated[
        sensor.Valve,
        valve_meta(yard_tag="50001062-02", component_type="valve", valve_type="switch"),
    ]
    pcm_flowcontrol_module1: Annotated[
        sensor.Valve,
        valve_meta(
            yard_tag="50001064-04", component_type="valve", valve_type="flowcontrol"
        ),
    ]
    pcm_flowcontrol_module2: Annotated[
        sensor.Valve,
        valve_meta(
            yard_tag="50001064-05", component_type="valve", valve_type="flowcontrol"
        ),
    ]
    pcm_flowcontrol_module3: Annotated[
        sensor.Valve,
        valve_meta(
            yard_tag="50001064-06", component_type="valve", valve_type="flowcontrol"
        ),
    ]
    pcm_flowcontrol_module4: Annotated[
        sensor.Valve,
        valve_meta(
            yard_tag="50001064-07", component_type="valve", valve_type="flowcontrol"
        ),
    ]
    pcm_switch_discharging: Annotated[
        sensor.Valve,
        valve_meta(yard_tag="50001066-01", component_type="valve", valve_type="switch"),
    ]
    pcm_switch_charging_supply: Annotated[
        sensor.Valve,
        valve_meta(yard_tag="50001190-01", component_type="valve", valve_type="switch"),
    ]
    pcm_switch_consumers: Annotated[
        sensor.Valve,
        valve_meta(yard_tag="50001071-02", component_type="valve", valve_type="switch"),
    ]

    consumers_temperature_dhw_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(
            yard_tag="50001038-48",
            component_type="temperature_sensor",
            included_in_fmu=False,
            topic_override="500000-thrs/consumers/consumers-temperature-dhw-return",
        ),
    ]
    consumers_temperature_adsorption_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(
            yard_tag="50001038-49",
            component_type="temperature_sensor",
            included_in_fmu=False,
            topic_override="500000-thrs/consumers/consumers-temperature-adsorption-return",
        ),
    ]
    consumers_flow_dhw: Annotated[
        sensor.FlowSensor,
        component_meta(
            yard_tag="50001058-07",
            component_type="flow_sensor",
            included_in_fmu=False,
            topic_override="500000-thrs/consumers/consumers-flow-dhw",
        ),
    ]
    consumers_flow_adsorption: Annotated[
        sensor.FlowSensor,
        component_meta(
            yard_tag="50001058-08",
            component_type="flow_sensor",
            included_in_fmu=False,
            topic_override="500000-thrs/consumers/consumers-flow-adsorption",
        ),
    ]
    consumers_flow_bypass: Annotated[
        sensor.FlowSensor,
        component_meta(
            yard_tag="50001192",
            component_type="flow_sensor",
            included_in_fmu=False,
            topic_override="500000-thrs/consumers/consumers-flow-bypass",
        ),
    ]

    @property
    def _supply_from_producers(self) -> bool:
        return sensor.valves_open_closed(
            closed_valves=[self.pcm_switch_discharging],
            open_valves=[self.pcm_switch_charging_supply],
            tolerance=Valve.OPEN / 2,
        )

    @property
    def _supply_from_consumers(self) -> bool:
        return sensor.valves_open_closed(
            closed_valves=[
                self.pcm_switch_charging_supply,
                self.pcm_switch_charging_return,
            ],
            open_valves=[self.pcm_switch_discharging],
            tolerance=Valve.OPEN / 2,
        )

    @property
    def _module_inlet_temperature(self) -> Stamped[OptionalCelsius]:
        if self._supply_from_producers:
            return cast(
                Stamped[OptionalCelsius],
                self.pcm_temperature_producers_return.temperature,
            )
        if self._supply_from_consumers:
            return cast(
                Stamped[OptionalCelsius],
                self.pcm_temperature_consumers_return.temperature,
            )

        return sensor.stamped_by_valves(
            [
                self.pcm_switch_discharging,
                self.pcm_switch_charging_supply,
                self.pcm_switch_charging_return,
            ],
            None,
        )

    @property
    def _module_inlet_source(self) -> str:
        if self._supply_from_producers:
            return sensor.extract_source_yardtag(
                self, "pcm_temperature_producers_return"
            )
        if self._supply_from_consumers:
            return sensor.extract_source_yardtag(
                self, "pcm_temperature_consumers_return"
            )
        return "unknown"

    @computed_field(
        json_schema_extra=computed_meta(
            component_type="calculated_temperature", included_in_fmu=False
        )
    )
    @property
    def pcm_temperature_consumers_return(self) -> sensor.CalculatedTemperature:
        # What comes back from the consumers is a flow-weighted average of the dhw, absorption and bypass temperatures.
        return sensor.CalculatedTemperature(
            temperature=sensor.weighted_combined_measurement(
                weights=[
                    self.consumers_flow_dhw.flow,
                    self.consumers_flow_adsorption.flow,
                    self.consumers_flow_bypass.flow,
                ],
                measurements=[
                    self.consumers_temperature_dhw_return.temperature,
                    self.consumers_temperature_adsorption_return.temperature,
                    self.consumers_flow_bypass.temperature,  # Reading from flow sensor is inaccurate, but avoids a valve-dependent calculation
                ],
                default_if_zero_weight=None,
            )
        )

    @computed_field(
        json_schema_extra=computed_meta(
            yard_tag="50001049", component_type="pcm", included_in_fmu=False
        )
    )
    @property
    def pcm_heat_module1(self) -> sensor.HeatTransferDevice:
        return sensor.HeatTransferDevice.from_sensors(
            temperature_supply=self._module_inlet_temperature,
            temperature_return=self.pcm_temperature_module1.temperature,
            flow=self.pcm_flow_module1.flow,
            temperature_supply_source=self._module_inlet_source,
            temperature_return_source=sensor.extract_source_yardtag(
                self, "pcm_temperature_module1"
            ),
            flow_source=sensor.extract_source_yardtag(self, "pcm_flow_module1"),
            heat_transfer_conversion=GLYCOL_20_HEAT_TRANSFER_CONVERSION,
        )

    @computed_field(
        json_schema_extra=computed_meta(
            yard_tag="50001049", component_type="pcm", included_in_fmu=False
        )
    )
    @property
    def pcm_heat_module1_freshwater(self) -> sensor.HeatTransferDevice:
        """Module 1's A-D exchanger, discharged by the freshwater system."""
        return sensor.HeatTransferDevice.from_sensors(
            temperature_supply=self.freshwater_temperature_pcm_supply.temperature,
            temperature_return=self.freshwater_temperature_pcm_return.temperature,
            flow=self.freshwater_flow_pcm.flow,
            temperature_supply_source=sensor.extract_source_yardtag(
                self, "freshwater_temperature_pcm_supply"
            ),
            temperature_return_source=sensor.extract_source_yardtag(
                self, "freshwater_temperature_pcm_return"
            ),
            flow_source=sensor.extract_source_yardtag(self, "freshwater_flow_pcm"),
            heat_transfer_conversion=WATER_HEAT_TRANSFER_CONVERSION,
        )

    @computed_field(
        json_schema_extra=computed_meta(
            yard_tag="50001050", component_type="pcm", included_in_fmu=False
        )
    )
    @property
    def pcm_heat_module2(self) -> sensor.HeatTransferDevice:
        return sensor.HeatTransferDevice.from_sensors(
            temperature_supply=self._module_inlet_temperature,
            temperature_return=self.pcm_temperature_module2.temperature,
            flow=self.pcm_flow_module2.flow,
            temperature_supply_source=self._module_inlet_source,
            temperature_return_source=sensor.extract_source_yardtag(
                self, "pcm_temperature_module2"
            ),
            flow_source=sensor.extract_source_yardtag(self, "pcm_flow_module2"),
            heat_transfer_conversion=GLYCOL_20_HEAT_TRANSFER_CONVERSION,
        )

    @computed_field(
        json_schema_extra=computed_meta(
            yard_tag="50001051", component_type="pcm", included_in_fmu=False
        )
    )
    @property
    def pcm_heat_module3(self) -> sensor.HeatTransferDevice:
        return sensor.HeatTransferDevice.from_sensors(
            temperature_supply=self._module_inlet_temperature,
            temperature_return=self.pcm_temperature_module3.temperature,
            flow=self.pcm_flow_module3.flow,
            temperature_supply_source=self._module_inlet_source,
            temperature_return_source=sensor.extract_source_yardtag(
                self, "pcm_temperature_module3"
            ),
            flow_source=sensor.extract_source_yardtag(self, "pcm_flow_module3"),
            heat_transfer_conversion=GLYCOL_20_HEAT_TRANSFER_CONVERSION,
        )

    @computed_field(
        json_schema_extra=computed_meta(
            yard_tag="50001052", component_type="pcm", included_in_fmu=False
        )
    )
    @property
    def pcm_heat_module4(self) -> sensor.HeatTransferDevice:
        return sensor.HeatTransferDevice.from_sensors(
            temperature_supply=self._module_inlet_temperature,
            temperature_return=self.pcm_temperature_module4.temperature,
            flow=self.pcm_flow_module4.flow,
            temperature_supply_source=self._module_inlet_source,
            temperature_return_source=sensor.extract_source_yardtag(
                self, "pcm_temperature_module4"
            ),
            flow_source=sensor.extract_source_yardtag(self, "pcm_flow_module4"),
            heat_transfer_conversion=GLYCOL_20_HEAT_TRANSFER_CONVERSION,
        )

    @computed_field(
        json_schema_extra=computed_meta(
            component_type="heat_transfer", included_in_fmu=False
        )
    )
    @property
    def pcm_freshwater_heat(self) -> sensor.HeatTransferDevice:
        return sensor.HeatTransferDevice.from_sensors(
            temperature_supply=self.freshwater_temperature_pcm_supply.temperature,
            temperature_return=self.freshwater_temperature_pcm_return.temperature,
            flow=self.freshwater_flow_pcm.flow,
            temperature_supply_source=sensor.extract_source_yardtag(
                self, "freshwater_temperature_pcm_supply"
            ),
            temperature_return_source=sensor.extract_source_yardtag(
                self, "freshwater_temperature_pcm_return"
            ),
            flow_source=sensor.extract_source_yardtag(self, "freshwater_flow_pcm"),
            heat_transfer_conversion=WATER_HEAT_TRANSFER_CONVERSION,
        )


class PcmControlValues(AmcsWatchdogControlValues):
    model_config = ConfigDict(
        alias_generator=to_snake,
        use_enum_values=True,
        validate_by_name=True,
    )

    pcm_pump: Annotated[
        control.Pump, component_meta(yard_tag="50001017", component_type="pump")
    ]
    pcm_switch_charging_return: Annotated[
        control.Valve,
        valve_meta(yard_tag="50001062-02", component_type="valve", valve_type="switch"),
    ]
    pcm_flowcontrol_module1: Annotated[
        control.Valve,
        valve_meta(
            yard_tag="50001064-04", component_type="valve", valve_type="flowcontrol"
        ),
    ]
    pcm_flowcontrol_module2: Annotated[
        control.Valve,
        valve_meta(
            yard_tag="50001064-05", component_type="valve", valve_type="flowcontrol"
        ),
    ]
    pcm_flowcontrol_module3: Annotated[
        control.Valve,
        valve_meta(
            yard_tag="50001064-06", component_type="valve", valve_type="flowcontrol"
        ),
    ]
    pcm_flowcontrol_module4: Annotated[
        control.Valve,
        valve_meta(
            yard_tag="50001064-07", component_type="valve", valve_type="flowcontrol"
        ),
    ]
    pcm_switch_discharging: Annotated[
        control.Valve,
        valve_meta(yard_tag="50001066-01", component_type="valve", valve_type="switch"),
    ]
    pcm_switch_charging_supply: Annotated[
        control.Valve,
        valve_meta(yard_tag="50001190-01", component_type="valve", valve_type="switch"),
    ]
    pcm_switch_consumers: Annotated[
        control.Valve,
        valve_meta(yard_tag="50001071-02", component_type="valve", valve_type="switch"),
    ]
    pcm_module1: Annotated[
        control.Pcm, component_meta(yard_tag="50001049", component_type="pcm")
    ] = control.Pcm(on=Stamped(value=False, timestamp=datetime.fromtimestamp(0, UTC)))


class PcmSimulationInputs(ThrsValues):
    pcm_pvt_supply: simulation.Boundary
    pcm_thrusters_supply: simulation.Boundary
    pcm_freshwater_supply: simulation.Boundary
    pcm_consumers_supply: simulation.TemperatureBoundary
    mode: Annotated[AmcsControlMode, component_meta(included_in_fmu=False)]

    @computed_field(json_schema_extra=computed_meta(included_in_fmu=False))
    @property
    def freshwater_temperature_pcm_supply(self) -> sensor.TemperatureSensor:
        return sensor.TemperatureSensor(
            temperature=self.pcm_freshwater_supply.temperature
        )

    # The model has a single consumers stream, so every return reads its temperature.
    @computed_field(json_schema_extra=computed_meta(included_in_fmu=False))
    @property
    def consumers_temperature_dhw_return(self) -> sensor.TemperatureSensor:
        return sensor.TemperatureSensor(
            temperature=self.pcm_consumers_supply.temperature
        )

    @computed_field(json_schema_extra=computed_meta(included_in_fmu=False))
    @property
    def consumers_temperature_adsorption_return(self) -> sensor.TemperatureSensor:
        return sensor.TemperatureSensor(
            temperature=self.pcm_consumers_supply.temperature
        )


class PcmSimulationOutputs(ThrsValues):
    pcm_consumers_return: simulation.Boundary
    pcm_thrusters_return: simulation.Boundary
    pcm_pvt_return: simulation.Boundary
    pcm_freshwater_return: simulation.Boundary

    @computed_field(json_schema_extra=computed_meta(included_in_fmu=False))
    @property
    def freshwater_temperature_pcm_return(self) -> sensor.TemperatureSensor:
        return sensor.TemperatureSensor(
            temperature=self.pcm_freshwater_return.temperature
        )

    @computed_field(json_schema_extra=computed_meta(included_in_fmu=False))
    @property
    def freshwater_flow_pcm(self) -> sensor.FlowOnlySensor:
        return sensor.FlowOnlySensor(flow=self.pcm_freshwater_return.flow)

    # The model has a single consumers stream, so all of it goes past the dhw.
    @computed_field(json_schema_extra=computed_meta(included_in_fmu=False))
    @property
    def consumers_flow_dhw(self) -> sensor.FlowSensor:
        return sensor.FlowSensor(
            flow=self.pcm_consumers_return.flow,
            temperature=self.pcm_consumers_return.temperature,
        )

    @computed_field(json_schema_extra=computed_meta(included_in_fmu=False))
    @property
    def consumers_flow_adsorption(self) -> sensor.FlowSensor:
        return sensor.FlowSensor.zero()

    @computed_field(json_schema_extra=computed_meta(included_in_fmu=False))
    @property
    def consumers_flow_bypass(self) -> sensor.FlowSensor:
        return sensor.FlowSensor.zero()
