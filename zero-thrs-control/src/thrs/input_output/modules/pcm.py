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
        sensor.PcmInput, component_meta(yard_tag="50001049", component_type="pcm_input")
    ] = sensor.PcmInput(
        charged=Stamped(value=False, timestamp=datetime.fromtimestamp(0, UTC))
    )
    pcm_module2: Annotated[
        sensor.PcmInput, component_meta(yard_tag="50001050", component_type="pcm_input")
    ] = sensor.PcmInput(
        charged=Stamped(value=False, timestamp=datetime.fromtimestamp(0, UTC))
    )
    pcm_module3: Annotated[
        sensor.PcmInput, component_meta(yard_tag="50001051", component_type="pcm_input")
    ] = sensor.PcmInput(
        charged=Stamped(value=False, timestamp=datetime.fromtimestamp(0, UTC))
    )
    pcm_module4: Annotated[
        sensor.PcmInput, component_meta(yard_tag="50001052", component_type="pcm_input")
    ] = sensor.PcmInput(
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

    @computed_field(
        json_schema_extra=computed_meta(
            yard_tag="50001049", component_type="pcm", included_in_fmu=False
        )
    )
    @property
    def pcm_heat_module1(self) -> sensor.Pcm:
        return sensor.Pcm.from_sensors(
            temperature_supply=self.pcm_temperature_producers_return.temperature,
            temperature_return=self.pcm_temperature_module1.temperature,
            flow=self.pcm_flow_module1.flow,
            charged=self.pcm_module1.charged,
        )

    @computed_field(
        json_schema_extra=computed_meta(
            yard_tag="50001050", component_type="pcm", included_in_fmu=False
        )
    )
    @property
    def pcm_heat_module2(self) -> sensor.Pcm:
        return sensor.Pcm.from_sensors(
            temperature_supply=self.pcm_temperature_producers_return.temperature,
            temperature_return=self.pcm_temperature_module2.temperature,
            flow=self.pcm_flow_module2.flow,
            charged=self.pcm_module2.charged,
        )

    @computed_field(
        json_schema_extra=computed_meta(
            yard_tag="50001051", component_type="pcm", included_in_fmu=False
        )
    )
    @property
    def pcm_heat_module3(self) -> sensor.Pcm:
        return sensor.Pcm.from_sensors(
            temperature_supply=self.pcm_temperature_producers_return.temperature,
            temperature_return=self.pcm_temperature_module3.temperature,
            flow=self.pcm_flow_module3.flow,
            charged=self.pcm_module3.charged,
        )

    @computed_field(
        json_schema_extra=computed_meta(
            yard_tag="50001052", component_type="pcm", included_in_fmu=False
        )
    )
    @property
    def pcm_heat_module4(self) -> sensor.Pcm:
        return sensor.Pcm.from_sensors(
            temperature_supply=self.pcm_temperature_producers_return.temperature,
            temperature_return=self.pcm_temperature_module4.temperature,
            flow=self.pcm_flow_module4.flow,
            charged=self.pcm_module4.charged,
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
    ] = control.Pcm(  # TODO: Remove
        on=Stamped(value=False, timestamp=datetime.fromtimestamp(0, UTC))
    )


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
