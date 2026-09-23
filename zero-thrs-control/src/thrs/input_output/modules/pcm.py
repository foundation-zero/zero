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
from thrs.input_output.sensor_values import AmcsModeSensorValues


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
    ] = sensor.TemperatureSensor(  # TODO: Remove default when topic works
        temperature=Stamped(value=0.0, timestamp=datetime.fromtimestamp(0, UTC)),
    )

    freshwater_temperature_pcm_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(
            yard_tag="25001038-3",
            component_type="temperature_sensor",
            included_in_fmu=False,
            topic_override="250000-fresh-water/hot/hot-temperature-from-pcm",
        ),
    ] = sensor.TemperatureSensor(  # TODO: Remove default when topic works
        temperature=Stamped(value=0.0, timestamp=datetime.fromtimestamp(0, UTC)),
    )

    pcm_module1: Annotated[
        sensor.Pcm, component_meta(yard_tag="50001049", component_type="pcm_input")
    ] = sensor.Pcm(
        charged=Stamped(value=False, timestamp=datetime.fromtimestamp(0, UTC))
    )
    pcm_module2: Annotated[
        sensor.Pcm, component_meta(yard_tag="50001050", component_type="pcm_input")
    ] = sensor.Pcm(
        charged=Stamped(value=False, timestamp=datetime.fromtimestamp(0, UTC))
    )
    pcm_module3: Annotated[
        sensor.Pcm, component_meta(yard_tag="50001051", component_type="pcm_input")
    ] = sensor.Pcm(
        charged=Stamped(value=False, timestamp=datetime.fromtimestamp(0, UTC))
    )
    pcm_module4: Annotated[
        sensor.Pcm, component_meta(yard_tag="50001052", component_type="pcm_input")
    ] = sensor.Pcm(
        charged=Stamped(value=False, timestamp=datetime.fromtimestamp(0, UTC))
    )
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
        sensor.FlowSensor,
        component_meta(
            yard_tag="25001139",
            component_type="flow_sensor",
            included_in_fmu=False,
            topic_override="250000-fresh-water/tech/tech-flow-technical-room-energy-recovery",  # must be 250000-fresh-water/hot/hot-flow-technical-room-energy-recovery
        ),
    ] = sensor.FlowSensor(  # TODO: Remove default when topic is correct
        flow=Stamped(value=0.0, timestamp=datetime.fromtimestamp(0, UTC)),
        temperature=Stamped(value=0.0, timestamp=datetime.fromtimestamp(0, UTC)),
    )
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
    def _charging(self) -> bool:
        """Whether the modules are lined up on the producers header.

        Taken from the switch positions rather than the control mode so that the heat
        stays a function of the sensors alone.
        """
        return sensor.valves_open_closed(
            open_valves=[
                self.pcm_switch_charging_supply,
                self.pcm_switch_charging_return,
            ],
            tolerance=Valve.OPEN / 2,
        )

    @property
    def _module_inlet_temperature(self) -> Stamped[OptionalCelsius]:
        """The temperature of the water entering the modules.

        Flow through a module runs the same way in both directions of use, so only the
        source changes: the producers header while charging, and whatever the consumers
        send back otherwise.
        """
        if self._charging:
            return cast(
                Stamped[OptionalCelsius],
                self.pcm_temperature_producers_return.temperature,
            )
        return self.pcm_temperature_consumers_return.temperature

    @property
    def _module_inlet_source(self) -> str:
        return sensor.extract_source_yardtag(
            self, "pcm_temperature_producers_return" if self._charging else None
        )

    @computed_field(
        json_schema_extra=computed_meta(
            component_type="calculated_temperature", included_in_fmu=False
        )
    )
    @property
    def pcm_temperature_consumers_return(self) -> sensor.CalculatedTemperature:
        """What the consumers send back, which is what the modules see while supplying.

        The bypass carries the module outlet mix around, so it comes in at the flow
        weighted average of the module outlets.
        """
        bypass_temperature = sensor.CalculatedTemperature.from_weighted_sensors(
            [
                self.pcm_flow_module1.flow,
                self.pcm_flow_module2.flow,
                self.pcm_flow_module3.flow,
                self.pcm_flow_module4.flow,
            ],
            [
                self.pcm_temperature_module1,
                self.pcm_temperature_module2,
                self.pcm_temperature_module3,
                self.pcm_temperature_module4,
            ],
            default_if_zero_weight=None,
        )
        weights = [
            self.consumers_flow_dhw.flow,
            self.consumers_flow_adsorption.flow,
            self.consumers_flow_bypass.flow,
        ]
        temperatures: list[Stamped[OptionalCelsius]] = [
            cast(
                Stamped[OptionalCelsius],
                self.consumers_temperature_dhw_return.temperature,
            ),
            cast(
                Stamped[OptionalCelsius],
                self.consumers_temperature_adsorption_return.temperature,
            ),
            bypass_temperature.temperature,
        ]
        # A leg without flow or without a temperature is dropped rather than defaulted:
        # with no module flowing the bypass carries no temperature at all.
        known = [
            (weight, temperature)
            for weight, temperature in zip(weights, temperatures, strict=True)
            if temperature.value is not None and weight.value > 0
        ]
        total_flow = sum(weight.value for weight, _ in known)

        return sensor.CalculatedTemperature(
            temperature=Stamped.combine(
                *weights,
                *temperatures,
                value=(
                    sum(
                        weight.value * temperature.value
                        for weight, temperature in known
                        if temperature.value is not None
                    )
                    / total_flow
                    if total_flow > 0
                    else None
                ),
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
        """Module 1's second circuit, the HPC, which the freshwater system discharges.

        It can draw the module down with the thrs loop idle, so its energy counts too.
        """
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


class PcmControlValues(ThrsValues):
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
    # Drives module 1's electric element, the only one connected. Nothing commands it
    # yet: when to boost electrically is a separate decision from estimating the charge.
    pcm_module1: Annotated[
        control.Pcm, component_meta(yard_tag="50001049", component_type="pcm")
    ] = control.Pcm(on=Stamped(value=False, timestamp=datetime.fromtimestamp(0, UTC)))


class PcmSimulationInputs(ThrsValues):
    pcm_pvt_supply: simulation.Boundary
    pcm_thrusters_supply: simulation.Boundary
    pcm_freshwater_supply: simulation.Boundary
    pcm_consumers_supply: simulation.TemperatureBoundary
    mode: Annotated[AmcsControlMode, component_meta(included_in_fmu=False)]


class PcmSimulationOutputs(ThrsValues):
    pcm_consumers_return: simulation.Boundary
    pcm_thrusters_return: simulation.Boundary
    pcm_pvt_return: simulation.Boundary
    pcm_freshwater_return: simulation.Boundary
