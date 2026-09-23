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
from thrs.input_output.definitions.units import (
    WATER_HEAT_TRANSFER_CONVERSION,
    AdsorptionChillerMode,
    FreeCoolingMode,
    TankControlMode,
)
from thrs.input_output.sensor_values import AmcsModeSensorValues


class AdsorptionSensorValues(AmcsModeSensorValues):
    model_config = ConfigDict(
        alias_generator=to_snake,
        use_enum_values=True,
        validate_by_name=True,
    )

    adsorption_flowcontrol_waste: Annotated[
        sensor.Valve,
        valve_meta(
            yard_tag="50001062-03", component_type="valve", valve_type="flowcontrol"
        ),
    ]
    adsorption_mix_hot: Annotated[
        sensor.Valve,
        valve_meta(yard_tag="50001046-02", component_type="valve", valve_type="mix"),
    ]
    adsorption_mix_waste: Annotated[
        sensor.Valve,
        valve_meta(yard_tag="50001047-01", component_type="valve", valve_type="mix"),
    ]
    adsorption_switch_dhw: Annotated[
        sensor.Valve,
        valve_meta(yard_tag="50001187-01", component_type="valve", valve_type="switch"),
    ]
    adsorption_chiller: Annotated[
        sensor.AdsorptionChiller,
        component_meta(yard_tag="50001034", component_type="adsorption_chiller"),
    ] = sensor.AdsorptionChiller(
        operating=Stamped(value=False, timestamp=datetime.fromtimestamp(0, UTC)),
        no_error=Stamped(value=False, timestamp=datetime.fromtimestamp(0, UTC)),
        free_cooling=Stamped(value=False, timestamp=datetime.fromtimestamp(0, UTC)),
        temperature_hot_in=Stamped(value=0.0, timestamp=datetime.fromtimestamp(0, UTC)),
        temperature_hot_out=Stamped(
            value=0.0, timestamp=datetime.fromtimestamp(0, UTC)
        ),
        temperature_waste_in=Stamped(
            value=0.0, timestamp=datetime.fromtimestamp(0, UTC)
        ),
        temperature_waste_out=Stamped(
            value=0.0, timestamp=datetime.fromtimestamp(0, UTC)
        ),
        temperature_cold_in=Stamped(
            value=0.0, timestamp=datetime.fromtimestamp(0, UTC)
        ),
        temperature_cold_out=Stamped(
            value=0.0, timestamp=datetime.fromtimestamp(0, UTC)
        ),
        pump_speed_hot=Stamped(value=0.0, timestamp=datetime.fromtimestamp(0, UTC)),
        pump_speed_cold=Stamped(value=0.0, timestamp=datetime.fromtimestamp(0, UTC)),
        pump_speed_waste=Stamped(value=0.0, timestamp=datetime.fromtimestamp(0, UTC)),
    )
    adsorption_flow_ht: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001058-09", component_type="flow_sensor"),
    ] = sensor.FlowSensor(
        flow=Stamped(value=0.0, timestamp=datetime.fromtimestamp(0, UTC)),
        temperature=Stamped(value=0.0, timestamp=datetime.fromtimestamp(0, UTC)),
    )
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
    ] = sensor.TemperatureSensor(
        temperature=Stamped(value=0.0, timestamp=datetime.fromtimestamp(0, UTC)),
    )
    adsorption_available_cold_temperature: Annotated[
        sensor.TemperatureSensor,
        component_meta(
            component_type="external_sensor", included_in_fmu=False
        ),  # TODO: figure out how to deal with Fahrenheit here. Is this a sensor value or should this be a parameter?
    ] = sensor.TemperatureSensor(
        temperature=Stamped(value=0.0, timestamp=datetime.fromtimestamp(0, UTC)),
    )
    adsorption_available_seawater_temperature: Annotated[
        sensor.TemperatureSensor,
        component_meta(
            component_type="external_sensor", included_in_fmu=False
        ),  # TODO: figure out how to deal with Fahrenheit here. Is this a sensor value or should this be a parameter?
    ] = sensor.TemperatureSensor(
        temperature=Stamped(value=0.0, timestamp=datetime.fromtimestamp(0, UTC)),
    )

    @computed_field(
        json_schema_extra=computed_meta(
            yard_tag="50001003",
            component_type="heat_transfer",
            included_in_fmu=False,
        )
    )
    @property
    def adsorption_ht_exchanger(self) -> sensor.HeatTransferDevice:
        return sensor.HeatTransferDevice.from_sensors(
            temperature_supply=self.adsorption_temperature_ht_supply.temperature,
            temperature_return=self.adsorption_temperature_ht_return.temperature,
            flow=self.adsorption_flow_ht.flow,
            heat_transfer_conversion=WATER_HEAT_TRANSFER_CONVERSION,
            temperature_supply_source=sensor.extract_source_yardtag(
                self, "adsorption_temperature_ht_supply"
            ),
            temperature_return_source=sensor.extract_source_yardtag(
                self, "adsorption_temperature_ht_return"
            ),
            flow_source=sensor.extract_source_yardtag(self, "adsorption_flow_ht"),
        )

    @computed_field(
        json_schema_extra=computed_meta(
            yard_tag="50001004",
            component_type="heat_transfer",
            included_in_fmu=False,
        )
    )
    @property
    def adsorption_dhw_exchanger(self) -> sensor.HeatTransferDevice:
        return sensor.HeatTransferDevice.from_sensors(
            temperature_supply=self.adsorption_temperature_waste_supply.temperature,
            temperature_return=self.adsorption_temperature_dhw_return.temperature,
            flow=self.adsorption_flow_dhw.flow,
            heat_transfer_conversion=WATER_HEAT_TRANSFER_CONVERSION,
            temperature_supply_source=sensor.extract_source_yardtag(
                self, "adsorption_temperature_waste_supply"
            ),
            temperature_return_source=sensor.extract_source_yardtag(
                self, "adsorption_temperature_dhw_return"
            ),
            flow_source=sensor.extract_source_yardtag(self, "adsorption_flow_dhw"),
        )


class AdsorptionControlValues(ThrsValues):
    model_config = ConfigDict(
        alias_generator=to_snake,
        use_enum_values=True,
        validate_by_name=True,
    )

    adsorption_flowcontrol_waste: Annotated[
        control.Valve,
        valve_meta(
            yard_tag="50001062-03", component_type="valve", valve_type="flowcontrol"
        ),
    ]
    adsorption_mix_hot: Annotated[
        control.Valve,
        valve_meta(yard_tag="50001046-02", component_type="valve", valve_type="mix"),
    ]
    adsorption_mix_waste: Annotated[
        control.Valve,
        valve_meta(yard_tag="50001047-01", component_type="valve", valve_type="mix"),
    ]
    adsorption_switch_dhw: Annotated[
        control.Valve,
        valve_meta(yard_tag="50001187-01", component_type="valve", valve_type="switch"),
    ]
    adsorption_chiller: Annotated[
        control.AdsorptionChiller,
        component_meta(yard_tag="50001034", component_type="adsorption_chiller"),
    ] = control.AdsorptionChiller(  # TODO: Remove once control readout from mqtt is finalized
        enable=Stamped(value=False, timestamp=datetime.fromtimestamp(0, UTC)),
        mode=Stamped(
            value=AdsorptionChillerMode.OFF, timestamp=datetime.fromtimestamp(0, UTC)
        ),
        cooling_setpoint=Stamped(value=17.0, timestamp=datetime.fromtimestamp(0, UTC)),
        free_cooling_mode=Stamped(
            value=FreeCoolingMode.AUTO, timestamp=datetime.fromtimestamp(0, UTC)
        ),
        available_seawater_temperature=Stamped(
            value=20.0, timestamp=datetime.fromtimestamp(0, UTC)
        ),
        available_hot_temperature=Stamped(
            value=20.0, timestamp=datetime.fromtimestamp(0, UTC)
        ),
        available_cold_temperature=Stamped(
            value=20.0, timestamp=datetime.fromtimestamp(0, UTC)
        ),
        cold_minimum=Stamped(value=15.0, timestamp=datetime.fromtimestamp(0, UTC)),
        hot_minimum=Stamped(value=53.0, timestamp=datetime.fromtimestamp(0, UTC)),
        cold_hysteresis=Stamped(value=2.0, timestamp=datetime.fromtimestamp(0, UTC)),
        hot_hysteresis=Stamped(value=2.0, timestamp=datetime.fromtimestamp(0, UTC)),
        tank_control_mode=Stamped(
            value=TankControlMode.BOTH, timestamp=datetime.fromtimestamp(0, UTC)
        ),
    )


class AdsorptionSimulationInputs(ThrsValues):
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
    mode: Annotated[AmcsControlMode, component_meta(included_in_fmu=False)]


class AdsorptionSimulationOutputs(ThrsValues):
    adsorption_cooling_return: simulation.Boundary
    adsorption_seawater_return: simulation.TemperatureBoundary
    adsorption_dhw_exchanger: simulation.ExchangerBoundary
    adsorption_dhw_return: simulation.TemperatureBoundary
    adsorption_consumers_exchanger: simulation.ExchangerBoundary
    adsorption_consumers_return: simulation.TemperatureBoundary
