from enum import StrEnum

from pydantic import BaseModel

from thrs.input_output.definitions.system import ControlMode


class MonitoringModule(StrEnum):
    DHW = "dhw"


class MonitoringMetric(StrEnum):
    TEMPERATURE = "temperature"
    LEVEL = "level"
    PRESSURE = "pressure"
    FLOW = "flow"
    FLOW_TEMPERATURE = "flow_temperature"
    FLOW_QUANTITY = "flow_quantity"
    PUMP_SPEED = "pump_speed"
    PUMP_FLOW = "pump_flow"
    PUMP_PRESSURE = "pump_pressure"
    PUMP_POWER_INPUT = "pump_power_input"
    PUMP_ENERGY_CONSUMPTION = "pump_energy_consumption"
    PUMP_OPERATION_TIME = "pump_operation_time"
    PUMP_DUTY_POINT = "pump_duty_point"
    PUMP_CONTROL_MODE = "pump_control_mode"
    PUMP_ON_OFF = "pump_on_off"
    VALVE_POSITION_ABSOLUTE = "valve_position_absolute"
    VALVE_POSITION_RELATIVE = "valve_position_relative"
    VALVE_SETPOINT = "valve_setpoint"
    MINIMUM_TANK_TEMPERATURE = "minimum_tank_temperature"
    MAXIMUM_TANK_TEMPERATURE = "maximum_tank_temperature"
    MINIMUM_TANK_LEVEL = "minimum_tank_level"
    MAXIMUM_TANK_LEVEL = "maximum_tank_level"
    HEAT = "heat"
    CALCULATED_FLOW = "calculated_flow"


class MonitoringSignal(StrEnum):
    AMCS_MODE = "amcs_mode"
    BOOSTING_MODE = "boosting_mode"
    FILLING_MODE = "filling_mode"
    TANK_1_STATE = "tank_1_state"
    TANK_2_STATE = "tank_2_state"
    TANK_3_STATE = "tank_3_state"


class Aggregate(StrEnum):
    AVERAGE = "AVG"
    MAXIMUM = "MAX"


class SensorSource(BaseModel, frozen=True):
    """A device column, binned per device like the Grafana Heat System trends."""

    table: str
    column: str
    unit: str | None
    aggregate: Aggregate = Aggregate.AVERAGE
    as_integer: bool = False
    # Pattern of the topics the module's devices publish on.
    topic: str = "marpower/500000-thrs/{module}/%"
    # Calculated values have no yard tag.
    has_yard_tag: bool = True
    # Multiplies the stored value, e.g. W to kW.
    scale: float | None = None

    def topic_prefix(self, module: MonitoringModule) -> str:
        return self.topic.format(module=module)


class ParameterSource(BaseModel, frozen=True):
    """A module parameter, returned as the steps where its value changed."""

    column: str
    unit: str | None

    def table(self, module: MonitoringModule) -> str:
        return f"thrs__controller__{module}__parameters"


class StateSource(BaseModel, frozen=True):
    table: str
    column: str
    technical_name: str | None = None
    null_state: str | None = None
    # Names for a numeric column, so segments carry readable states.
    labels: dict[int, str] | None = None

    def state(self, value: object) -> str | None:
        if value is None:
            return None
        if self.labels is not None:
            return self.labels.get(int(value), str(value))  # pyright: ignore[reportArgumentType]
        return str(value)


def _sensor(
    table: str,
    column: str,
    unit: str | None,
    aggregate: Aggregate = Aggregate.AVERAGE,
    as_integer: bool = False,
) -> SensorSource:
    return SensorSource(
        table=f"marpower__thrs__{table}",
        column=f"{column}__value",
        unit=unit,
        aggregate=aggregate,
        as_integer=as_integer,
    )


# Tables, columns, aggregates and units follow
# zero-dashboards/dashboards/Commissioning/heat-system-dashboard.json.
SERIES_SOURCES: dict[MonitoringMetric, SensorSource | ParameterSource] = {
    MonitoringMetric.TEMPERATURE: _sensor("temperatures", "temperature", "°C"),
    MonitoringMetric.LEVEL: _sensor("level_sensors", "level", "L"),
    MonitoringMetric.PRESSURE: _sensor("pressures", "pressure", "bar"),
    MonitoringMetric.FLOW: _sensor("flows", "flow", "L/min"),
    MonitoringMetric.FLOW_TEMPERATURE: _sensor("flows", "temperature", "°C"),
    MonitoringMetric.FLOW_QUANTITY: _sensor(
        "flows", "quantity", "L", Aggregate.MAXIMUM
    ),
    MonitoringMetric.PUMP_SPEED: _sensor("pumps", "speed", "Hz"),
    MonitoringMetric.PUMP_FLOW: _sensor("pumps", "flow", "L/min"),
    MonitoringMetric.PUMP_PRESSURE: _sensor("pumps", "pressure", "bar"),
    MonitoringMetric.PUMP_POWER_INPUT: _sensor("pumps", "power_input", "W"),
    MonitoringMetric.PUMP_ENERGY_CONSUMPTION: _sensor(
        "pumps", "energy_consumption", "J", Aggregate.MAXIMUM
    ),
    MonitoringMetric.PUMP_OPERATION_TIME: _sensor(
        "pumps", "op_time", "h", Aggregate.MAXIMUM
    ),
    MonitoringMetric.PUMP_DUTY_POINT: _sensor("pumps", "cc_duty_point", None),
    MonitoringMetric.PUMP_CONTROL_MODE: _sensor("pumps", "cc_control_mode", None),
    MonitoringMetric.PUMP_ON_OFF: _sensor("pumps", "cc_on_off", None, as_integer=True),
    MonitoringMetric.VALVE_POSITION_ABSOLUTE: _sensor("valves", "position_abs", "°"),
    MonitoringMetric.VALVE_POSITION_RELATIVE: _sensor("valves", "position_rel", None),
    MonitoringMetric.VALVE_SETPOINT: _sensor("valves", "cc_setpoint", None),
    # Heat the controller calculates per exchanger from its flow and delta T.
    MonitoringMetric.HEAT: SensorSource(
        table="marpower__thrs__heat_transfers",
        column="heat__value",
        unit="kW",
        topic="thrs/controller/{module}/%",
        has_yard_tag=False,
        scale=0.001,
    ),
    # Flows the controller adds up from meters, e.g. the fresh water into DHW.
    MonitoringMetric.CALCULATED_FLOW: SensorSource(
        table="marpower__thrs__calculated_flows",
        column="flow__value",
        unit="L/min",
        topic="thrs/controller/{module}/%",
        has_yard_tag=False,
    ),
    MonitoringMetric.MINIMUM_TANK_TEMPERATURE: ParameterSource(
        column="minimum_tank_temperature", unit="°C"
    ),
    MonitoringMetric.MAXIMUM_TANK_TEMPERATURE: ParameterSource(
        column="maximum_tank_temperature", unit="°C"
    ),
    MonitoringMetric.MINIMUM_TANK_LEVEL: ParameterSource(
        column="minimum_tank_level", unit="L"
    ),
    MonitoringMetric.MAXIMUM_TANK_LEVEL: ParameterSource(
        column="maximum_tank_level", unit="L"
    ),
}

# The control loop publishes no automatic mode while the module is in manual.
_MANUAL = "manual"

STATE_SOURCES: dict[MonitoringModule, dict[MonitoringSignal, StateSource]] = {
    MonitoringModule.DHW: {
        # Values follow thrs.input_output.definitions.system.ControlMode;
        # EXTERNAL is what the crew calls advisory mode.
        MonitoringSignal.AMCS_MODE: StateSource(
            table="marpower__thrs__amcs_modes",
            column="mode__value",
            technical_name="dhw-mode",
            labels={
                ControlMode.LOCAL.value: "amcs_local",
                ControlMode.MANUAL.value: "amcs_manual",
                ControlMode.AUTO.value: "amcs_auto",
                ControlMode.EXTERNAL.value: "advisory",
            },
        ),
        MonitoringSignal.BOOSTING_MODE: StateSource(
            table="thrs__controller__dhw__control_mode",
            column="automatic_mode__boosting_mode",
            null_state=_MANUAL,
        ),
        MonitoringSignal.FILLING_MODE: StateSource(
            table="thrs__controller__dhw__control_mode",
            column="automatic_mode__filling_mode",
            null_state=_MANUAL,
        ),
        **{
            signal: StateSource(
                table="marpower__thrs__tank_controllers",
                column=f"tank_{tank}_state__value",
                technical_name="dhw-tanks-controller",
            )
            for tank, signal in enumerate(
                (
                    MonitoringSignal.TANK_1_STATE,
                    MonitoringSignal.TANK_2_STATE,
                    MonitoringSignal.TANK_3_STATE,
                ),
                start=1,
            )
        },
    },
}


class UnsupportedSignalError(ValueError):
    pass


def state_source(module: MonitoringModule, signal: MonitoringSignal) -> StateSource:
    if (source := STATE_SOURCES.get(module, {}).get(signal)) is None:
        raise UnsupportedSignalError(f"{signal} is not monitored for {module}")
    return source
