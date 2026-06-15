from typing import Annotated, cast

from pydantic import computed_field

from thrs.input_output.base import (
    SimulationInputs,
    SimulationValues,
    Stamped,
    ThrsValues,
    component_meta,
)
from thrs.input_output.definitions import control, controllers, sensor, simulation
from thrs.input_output.definitions.units import WATER_HEAT_TRANSFER_CONVERSION


class BoilersSensorValues(ThrsValues):
    boilers_pump: Annotated[
        sensor.Pump, component_meta(yard_tag="50001022", component_type="pump")
    ]
    boilers_temperature_hvac_exchanger_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-25", component_type="temperature_sensor"),
    ]
    boilers_temperature_lt2_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-26", component_type="temperature_sensor"),
    ]
    boilers_temperature_tank3: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-27", component_type="temperature_sensor"),
    ]
    boilers_temperature_tank2: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-44", component_type="temperature_sensor"),
    ]
    boilers_temperature_tank1: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-45", component_type="temperature_sensor"),
    ]
    boilers_temperature_lt1_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-46", component_type="temperature_sensor"),
    ]
    boilers_temperature_freshwater_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-47", component_type="temperature_sensor"),
    ]
    boilers_temperature_fahrenheit_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-51", component_type="temperature_sensor"),
    ]
    boilers_temperature_boosting_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-65", component_type="temperature_sensor"),
    ]
    boilers_temperature_boosting_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-66", component_type="temperature_sensor"),
    ]
    boilers_level_tank1: Annotated[
        sensor.LevelSensor,
        component_meta(yard_tag="50001056-01", component_type="level_sensor"),
    ]
    boilers_level_tank2: Annotated[
        sensor.LevelSensor,
        component_meta(yard_tag="50001056-02", component_type="level_sensor"),
    ]
    boilers_level_tank3: Annotated[
        sensor.LevelSensor,
        component_meta(yard_tag="50001056-03", component_type="level_sensor"),
    ]
    boilers_flow_lt2: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001057-17", component_type="flow_sensor"),
    ]
    boilers_flow_lt1: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001057-24", component_type="flow_sensor"),
    ]
    boilers_flow_boosting: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001058-11", component_type="flow_sensor"),
    ]
    boilers_flowcontrol_lt2: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001064-03", component_type="valve", valve_type="flowcontrol"
        ),
    ]
    boilers_flowcontrol_lt1: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001064-08", component_type="valve", valve_type="flowcontrol"
        ),
    ]
    boilers_switch_tank3_fill: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001067-03", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_switch_tank3_boosting_return: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001067-04", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_switch_tank3_empty: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001067-05", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_switch_tank3_boosting_supply: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001067-06", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_switch_tank2_fill: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001067-07", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_switch_tank2_boosting_return: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001067-08", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_switch_tank2_empty: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001067-09", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_switch_tank2_boosting_supply: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001067-10", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_switch_tank1_fill: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001067-11", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_switch_tank1_boosting_return: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001067-12", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_switch_tank1_empty: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001067-13", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_switch_tank1_boosting_supply: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001067-14", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_switch_low_temperature: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001067-16", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_switch_heatpump: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001067-17", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_switch_high_temperature: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001067-18", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_pressure_boosting: Annotated[
        sensor.PressureSensor,
        component_meta(yard_tag="50001097-11", component_type="pressure_sensor"),
    ]
    lt1_flow_recovery: Annotated[
        sensor.FlowSensor,
        component_meta(
            yard_tag="50001058-03",
            component_type="flow_sensor",
            included_in_fmu=False,
            topic="lt1/lt1_flow_recovery",
        ),
    ]
    lt1_temperature_recovery: Annotated[
        sensor.TemperatureSensor,
        component_meta(
            yard_tag="50001038-16",
            component_type="temperature_sensor",
            included_in_fmu=False,
            topic="lt1/lt1_temperature_recovery",
        ),
    ]
    lt1_temperature_recovery_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(
            yard_tag="50001038-59",
            component_type="temperature_sensor",
            included_in_fmu=False,
            topic="lt1/lt1_temperature_recovery_return",
        ),
    ]

    @computed_field(
        json_schema_extra=component_meta(
            component_type="delta_t",
            included_in_fmu=False,
            topic="control/boilers/lt1_delta",
        ).json_schema_extra
    )
    @property
    def lt1_delta(
        self,
    ) -> Annotated[
        sensor.TemperatureDelta,
        component_meta(
            component_type="delta_t",
            included_in_fmu=False,
            topic="control/boilers/lt1_delta",
        ),
    ]:
        return sensor.TemperatureDelta.from_temperature_sensors(
            temperature_supply=self.lt1_temperature_recovery.temperature,
            temperature_return=self.lt1_temperature_recovery_return.temperature,
        )

    lt2_flow_recovery: Annotated[
        sensor.FlowSensor,
        component_meta(
            yard_tag="50001058-04",
            component_type="flow_sensor",
            included_in_fmu=False,
            topic="lt2/lt2_flow_recovery",
        ),
    ]
    lt2_temperature_recovery: Annotated[
        sensor.TemperatureSensor,
        component_meta(
            yard_tag="50001038-52",
            component_type="temperature_sensor",
            included_in_fmu=False,
            topic="lt2/lt2_temperature_recovery",
        ),
    ]
    lt2_temperature_recovery_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(
            yard_tag="50001038-58",
            component_type="temperature_sensor",
            included_in_fmu=False,
            topic="lt2/lt2_temperature_recovery_return",
        ),
    ]

    @computed_field(
        json_schema_extra=component_meta(
            component_type="delta_t",
            included_in_fmu=False,
            topic="control/boilers/lt2_delta",
        ).json_schema_extra
    )
    @property
    def lt2_delta(self) -> sensor.TemperatureDelta:
        return sensor.TemperatureDelta.from_temperature_sensors(
            temperature_supply=self.lt2_temperature_recovery.temperature,
            temperature_return=self.lt2_temperature_recovery_return.temperature,
        )

    consumers_flow_boosting: Annotated[
        sensor.FlowSensor,
        component_meta(
            yard_tag="50001058-07",
            component_type="flow_sensor",
            included_in_fmu=False,
            topic="consumers/consumers_flow_boosting",
        ),
    ]
    consumers_temperature_boosting_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(
            yard_tag="50001038-53",
            component_type="temperature_sensor",
            included_in_fmu=False,
            topic="consumers/consumers_temperature_boosting_supply",
        ),
    ]

    consumers_temperature_boosting_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(
            yard_tag="50001038-48",
            component_type="temperature_sensor",
            included_in_fmu=False,
            topic="consumers/consumers_temperature_boosting_return",
        ),
    ]

    @computed_field(
        json_schema_extra=component_meta(
            component_type="delta_t",
            included_in_fmu=False,
            topic="control/boilers/consumers_delta",
        ).json_schema_extra
    )
    @property
    def consumers_delta(self) -> sensor.TemperatureDelta:
        return sensor.TemperatureDelta.from_temperature_sensors(
            temperature_supply=self.consumers_temperature_boosting_supply.temperature,
            temperature_return=self.consumers_temperature_boosting_return.temperature,
        )

    fahrenheit_flow_boilers: Annotated[
        sensor.FlowSensor,
        component_meta(
            yard_tag="50001058-10",
            component_type="flow_sensor",
            included_in_fmu=False,
            topic="fahrenheit/fahrenheit_flow_boilers",
        ),
    ]
    fahrenheit_temperature_waste_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(
            yard_tag="50001038-38",
            component_type="temperature_sensor",
            included_in_fmu=False,
            topic="fahrenheit/fahrenheit_temperature_waste_return",
        ),
    ]

    fahrenheit_temperature_boilers_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(
            yard_tag="50001038-56",
            component_type="temperature_sensor",
            included_in_fmu=False,
            topic="fahrenheit/fahrenheit_temperature_boilers_return",
        ),
    ]

    @computed_field(
        json_schema_extra=component_meta(
            component_type="delta_t",
            included_in_fmu=False,
            topic="control/boilers/fahrenheit_delta",
        ).json_schema_extra
    )
    @property
    def fahrenheit_delta(self) -> sensor.TemperatureDelta:
        return sensor.TemperatureDelta.from_temperature_sensors(
            temperature_supply=self.fahrenheit_temperature_waste_return.temperature,
            temperature_return=self.fahrenheit_temperature_boilers_return.temperature,
        )

    freshwater_hotwater_flow: Annotated[
        sensor.FlowSensor,
        component_meta(
            yard_tag="25001123-1",
            included_in_fmu=False,
            topic="freshwater/freshwater_hotwater_flow",
        ),
    ]
    freshwater_hotwater_temperature: Annotated[
        sensor.TemperatureSensor,
        component_meta(
            yard_tag="25001038-1",
            included_in_fmu=False,
            topic="freshwater/freshwater_hotwater_temperature",
        ),
    ]

    @computed_field(
        json_schema_extra=component_meta(included_in_fmu=False).json_schema_extra
    )
    @property
    def freshwater_flow_supply(self) -> sensor.CalculatedFlow:
        return sensor.CalculatedFlow(
            flow=Stamped.combine(
                self.boilers_flow_lt1.flow,
                self.boilers_flow_lt2.flow,
                value=self.boilers_flow_lt1.flow.value
                + self.boilers_flow_lt2.flow.value,
            )
        )

    @computed_field(
        json_schema_extra=component_meta(
            yard_tag="41001001",
            component_type="hvac_exchanger",
            included_in_fmu=False,
            topic="control/boilers/boilers_hvac_exchanger",
        ).json_schema_extra
    )
    @property
    def boilers_hvac_exchanger(self) -> sensor.HvacExchanger:
        return sensor.HvacExchanger.from_sensors(
            temperature_supply=self.boilers_temperature_hvac_exchanger_return.temperature,
            temperature_return=self.boilers_temperature_fahrenheit_return.temperature,
            flow=self.boilers_flow_lt2.flow,
            heat_transfer_conversion=WATER_HEAT_TRANSFER_CONVERSION,
        )

    @computed_field(
        json_schema_extra=component_meta(
            yard_tag="50001035",
            component_type="heatpump",
            included_in_fmu=False,
            topic="control/boilers/boilers_heatpump",
        ).json_schema_extra
    )
    @property
    def boilers_heatpump(self) -> sensor.HeatPump:
        return sensor.HeatPump.from_sensors(
            temperature_supply=self.boilers_temperature_boosting_supply.temperature,
            temperature_return=self.boilers_temperature_boosting_return.temperature,
            flow=self.boilers_flow_boosting.flow,
            heat_transfer_conversion=WATER_HEAT_TRANSFER_CONVERSION,
        )

    @computed_field(
        json_schema_extra=component_meta(
            yard_tag="50001004",
            component_type="heat_exchanger",
            included_in_fmu=False,
            topic="control/boilers/boilers_fahrenheit_exchanger",
        ).json_schema_extra
    )
    @property
    def boilers_fahrenheit_exchanger(self) -> sensor.HeatExchanger:
        return sensor.HeatExchanger.from_sensors(
            temperature_supply=self.boilers_temperature_freshwater_supply.temperature,
            temperature_return=self.boilers_temperature_fahrenheit_return.temperature,
            flow=self.boilers_flow_lt2.flow,
            heat_transfer_conversion=WATER_HEAT_TRANSFER_CONVERSION,
        )

    @computed_field(
        json_schema_extra=component_meta(
            yard_tag="50001007",
            component_type="heat_exchanger",
            included_in_fmu=False,
            topic="control/boilers/boilers_consumers_exchanger",
        ).json_schema_extra
    )
    @property
    def boilers_consumers_exchanger(self) -> sensor.HeatExchanger:
        return sensor.HeatExchanger.from_sensors(
            temperature_supply=self.boilers_temperature_boosting_supply.temperature,
            temperature_return=self.boilers_temperature_boosting_return.temperature,
            flow=self.boilers_flow_boosting.flow,
            heat_transfer_conversion=WATER_HEAT_TRANSFER_CONVERSION,
        )

    @computed_field(
        json_schema_extra=component_meta(
            yard_tag="50001008",
            component_type="heat_exchanger",
            included_in_fmu=False,
            topic="control/boilers/boilers_lt2_exchanger",
        ).json_schema_extra
    )
    @property
    def boilers_lt2_exchanger(self) -> sensor.HeatExchanger:
        return sensor.HeatExchanger.from_sensors(
            temperature_supply=self.boilers_temperature_hvac_exchanger_return.temperature,
            temperature_return=self.boilers_temperature_lt2_return.temperature,
            flow=self.boilers_flow_lt2.flow,
            heat_transfer_conversion=WATER_HEAT_TRANSFER_CONVERSION,
        )

    @computed_field(
        json_schema_extra=component_meta(
            yard_tag="50001009",
            component_type="heat_exchanger",
            included_in_fmu=False,
            topic="control/boilers/boilers_lt1_exchanger",
        ).json_schema_extra
    )
    @property
    def boilers_lt1_exchanger(self) -> sensor.HeatExchanger:
        return sensor.HeatExchanger.from_sensors(
            temperature_supply=self.boilers_temperature_hvac_exchanger_return.temperature,
            temperature_return=self.boilers_temperature_lt1_return.temperature,
            flow=self.boilers_flow_lt1.flow,
            heat_transfer_conversion=WATER_HEAT_TRANSFER_CONVERSION,
        )


class BoilersControlValues(ThrsValues):
    boilers_pump: Annotated[
        control.Pump, component_meta(yard_tag="50001022", component_type="pump")
    ]
    boilers_heatpump: Annotated[
        control.HeatPump, component_meta(yard_tag="50001035", component_type="heatpump")
    ]
    boilers_flowcontrol_lt2: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001064-03", component_type="valve", valve_type="flowcontrol"
        ),
    ]
    boilers_flowcontrol_lt1: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001064-08", component_type="valve", valve_type="flowcontrol"
        ),
    ]
    boilers_switch_tank3_fill: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001067-03", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_switch_tank3_boosting_return: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001067-04", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_switch_tank3_empty: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001067-05", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_switch_tank3_boosting_supply: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001067-06", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_switch_tank2_fill: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001067-07", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_switch_tank2_boosting_return: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001067-08", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_switch_tank2_empty: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001067-09", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_switch_tank2_boosting_supply: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001067-10", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_switch_tank1_fill: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001067-11", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_switch_tank1_boosting_return: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001067-12", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_switch_tank1_empty: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001067-13", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_switch_tank1_boosting_supply: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001067-14", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_switch_low_temperature: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001067-16", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_switch_heatpump: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001067-17", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_switch_high_temperature: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001067-18", component_type="valve", valve_type="switch"
        ),
    ]
    boilers_tanks_controller: Annotated[
        controllers.TanksControllerValues,
        component_meta(
            included_in_fmu=False, topic="control/boilers/boilers_tanks_controller"
        ),
    ]
    boilers_pump_flow_controller: Annotated[
        controllers.PidControllerValues,
        component_meta(
            included_in_fmu=False, topic="control/boilers/boilers_pump_flow_controller"
        ),
    ]
    boilers_pump_temperature_controller: Annotated[
        controllers.PidControllerValues,
        component_meta(
            included_in_fmu=False,
            topic="control/boilers/boilers_pump_temperature_controller",
        ),
    ]
    boilers_lt1_flow_controller: Annotated[
        controllers.PidControllerValues,
        component_meta(
            included_in_fmu=False, topic="control/boilers/boilers_lt1_flow_controller"
        ),
    ]
    boilers_lt2_flow_controller: Annotated[
        controllers.PidControllerValues,
        component_meta(
            included_in_fmu=False, topic="control/boilers/boilers_lt2_flow_controller"
        ),
    ]


class BoilersSimulationInputs(SimulationInputs):
    boilers_lt1_supply: simulation.Boundary
    boilers_lt2_supply: simulation.Boundary
    boilers_fahrenheit_supply: simulation.Boundary
    boilers_ht_supply: simulation.Boundary
    boilers_freshwater_supply: simulation.OverpressureTemperatureBoundary
    boilers_hvac_exchanger: simulation.HvacExchanger
    boilers_seawater_supply: simulation.TemperatureBoundary
    boilers_hotwater_demand: simulation.FlowBoundary

    @computed_field(
        json_schema_extra=component_meta(included_in_fmu=False).json_schema_extra
    )
    @property
    def lt1_flow_recovery(self) -> sensor.FlowSensor:
        return sensor.FlowSensor(
            flow=cast(Stamped, self.boilers_lt1_supply.flow),
            temperature=cast(Stamped, self.boilers_lt1_supply.temperature),
        )

    @computed_field(
        json_schema_extra=component_meta(
            included_in_fmu=False,
        ).json_schema_extra
    )
    @property
    def lt1_temperature_recovery(self) -> sensor.TemperatureSensor:
        return sensor.TemperatureSensor(
            temperature=cast(Stamped, self.boilers_lt1_supply.temperature)
        )

    @computed_field(
        json_schema_extra=component_meta(
            included_in_fmu=False,
        ).json_schema_extra
    )
    @property
    def lt2_flow_recovery(self) -> sensor.FlowSensor:
        return sensor.FlowSensor(
            flow=cast(Stamped, self.boilers_lt2_supply.flow),
            temperature=cast(Stamped, self.boilers_lt2_supply.temperature),
        )

    @computed_field(
        json_schema_extra=component_meta(
            included_in_fmu=False,
        ).json_schema_extra
    )
    @property
    def lt2_temperature_recovery(self) -> sensor.TemperatureSensor:
        return sensor.TemperatureSensor(
            temperature=cast(Stamped, self.boilers_lt2_supply.temperature)
        )

    @computed_field(
        json_schema_extra=component_meta(
            included_in_fmu=False,
        ).json_schema_extra
    )
    @property
    def consumers_flow_boosting(self) -> sensor.FlowSensor:
        return sensor.FlowSensor(
            flow=cast(Stamped, self.boilers_ht_supply.flow),
            temperature=cast(Stamped, self.boilers_ht_supply.temperature),
        )

    @computed_field(
        json_schema_extra=component_meta(
            included_in_fmu=False,
            component_type="temperature_sensor",
        ).json_schema_extra
    )
    @property
    def consumers_temperature_boosting_supply(self) -> sensor.TemperatureSensor:
        return sensor.TemperatureSensor(
            temperature=cast(Stamped, self.boilers_ht_supply.temperature)
        )

    @computed_field(
        json_schema_extra=component_meta(
            included_in_fmu=False,
            component_type="flow_sensor",
        ).json_schema_extra
    )
    @property
    def fahrenheit_flow_boilers(self) -> sensor.FlowSensor:
        return sensor.FlowSensor(
            flow=cast(Stamped, self.boilers_fahrenheit_supply.flow),
            temperature=cast(Stamped, self.boilers_fahrenheit_supply.temperature),
        )

    @computed_field(
        json_schema_extra=component_meta(
            included_in_fmu=False,
            component_type="temperature_sensor",
        ).json_schema_extra
    )
    @property
    def fahrenheit_temperature_waste_return(self) -> sensor.TemperatureSensor:
        return sensor.TemperatureSensor(
            temperature=cast(Stamped, self.boilers_fahrenheit_supply.temperature)
        )


class BoilersSimulationOutputs(SimulationValues):
    boilers_lt1_return: simulation.TemperatureBoundary
    boilers_lt2_return: simulation.TemperatureBoundary
    boilers_fahrenheit_return: simulation.TemperatureBoundary
    boilers_ht_return: simulation.TemperatureBoundary
    boilers_seawater_return: simulation.TemperatureBoundary
    boilers_seawater_supply: simulation.FlowBoundary
    boilers_freshwater_return: simulation.FlowBoundary

    @computed_field(
        json_schema_extra=component_meta(
            included_in_fmu=False,
            component_type="temperature_sensor",
        ).json_schema_extra
    )
    @property
    def lt1_temperature_recovery_return(self) -> sensor.TemperatureSensor:
        return sensor.TemperatureSensor(
            temperature=cast(Stamped, self.boilers_lt1_return.temperature)
        )

    @computed_field(
        json_schema_extra=component_meta(
            included_in_fmu=False,
            component_type="temperature_sensor",
        ).json_schema_extra
    )
    @property
    def lt2_temperature_recovery_return(self) -> sensor.TemperatureSensor:
        return sensor.TemperatureSensor(
            temperature=cast(Stamped, self.boilers_lt2_return.temperature)
        )

    @computed_field(
        json_schema_extra=component_meta(
            included_in_fmu=False,
            component_type="temperature_sensor",
        ).json_schema_extra
    )
    @property
    def fahrenheit_temperature_boilers_return(self) -> sensor.TemperatureSensor:
        return sensor.TemperatureSensor(
            temperature=cast(Stamped, self.boilers_fahrenheit_return.temperature)
        )

    @computed_field(
        json_schema_extra=component_meta(
            included_in_fmu=False,
            component_type="temperature_sensor",
        ).json_schema_extra
    )
    @property
    def consumers_temperature_boosting_return(self) -> sensor.TemperatureSensor:
        return sensor.TemperatureSensor(
            temperature=cast(Stamped, self.boilers_ht_return.temperature)
        )

    @computed_field(
        json_schema_extra=component_meta(
            included_in_fmu=False,
            component_type="flow_sensor",
        ).json_schema_extra
    )
    @property
    def freshwater_hotwater_flow(self) -> sensor.FlowSensor:
        return sensor.FlowSensor(
            flow=cast(Stamped, self.boilers_freshwater_return.flow),
            temperature=Stamped.stamp(
                0
            ),  # TODO: Add hot water temperature as output to the FMU
        )

    @computed_field(
        json_schema_extra=component_meta(
            included_in_fmu=False,
        ).json_schema_extra
    )
    @property
    def freshwater_hotwater_temperature(self) -> sensor.TemperatureSensor:
        return sensor.TemperatureSensor(
            temperature=Stamped.stamp(
                0
            )  # TODO: Add hot water temperature as output to the FMU
        )
