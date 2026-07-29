from datetime import datetime
from typing import Annotated, Callable

from pydantic import Field, model_validator
from transitions import State

from thrs.classes.control import Control, ControlMode
from thrs.classes.machine_state_logger import (
    MachineStateLoggingServiceNoop,
    StateLogger,
)
from thrs.control.controllers import PidController
from thrs.input_output.alarms import BaseAlarms, Severity, alarm
from thrs.input_output.base import Stamped, ThrsValues, component_meta
from thrs.input_output.definitions import controllers
from thrs.input_output.definitions.control import HeatPump, Pump, Valve
from thrs.input_output.definitions.controllers import (
    PidControllerValues,
    TanksControllerValues,
)
from thrs.input_output.definitions.units import (
    Celsius,
    DeltaT,
    Liter,
    LMin,
    Ratio,
    Seconds,
    TankState,
    Tuning,
)
from thrs.input_output.modules.dhw import DhwControlValues, DhwSensorValues
from thrs.orchestration.module import ModuleDescription


class DhwControllerState(ThrsValues):
    dhw_tanks_controller: Annotated[
        controllers.TanksControllerValues,
        component_meta(component_type="tank_controller", included_in_fmu=False),
    ]
    dhw_pump_flow_controller: Annotated[
        controllers.PidControllerValues,
        component_meta(component_type="pid_controller", included_in_fmu=False),
    ]
    dhw_pump_temperature_controller: Annotated[
        controllers.PidControllerValues,
        component_meta(component_type="pid_controller", included_in_fmu=False),
    ]
    dhw_drives_flow_controller: Annotated[
        controllers.PidControllerValues,
        component_meta(component_type="pid_controller", included_in_fmu=False),
    ]
    dhw_dc_flow_controller: Annotated[
        controllers.PidControllerValues,
        component_meta(component_type="pid_controller", included_in_fmu=False),
    ]


class DhwParameters(ThrsValues):
    heatpump_boosting_enabled: bool = True
    ht_boosting_enabled: bool = True
    heatpump_flow_setpoint: LMin = 25
    heatpump_temperature_setpoint: Celsius = 65
    ht_boosting_temperature_setpoint: Celsius = 65
    minimum_tank_temperature: Celsius = 55
    maximum_tank_temperature: Celsius = 60
    boosting_delta: Annotated[
        DeltaT,
        Field(
            description="Required delta T between boosting source and tank temperature"
        ),
    ] = 2
    drives_flowcontrol_minimum_setpoint: Annotated[
        Ratio,
        Field(
            description="Minimum pump dutypoint to guarantee sufficient flow for a temperature measurement"
        ),
    ] = 0.1
    dc_flowcontrol_minimum_setpoint: Annotated[
        Ratio,
        Field(
            description="Minimum pump dutypoint to guarantee sufficient flow for a temperature measurement"
        ),
    ] = 0.1
    filling_temperature_setpoint: Celsius = 40
    minimum_tank_level: Liter = 30
    maximum_tank_level: Annotated[Liter, Field(le=275)] = 260
    tank1_disabled: bool = False
    tank2_disabled: bool = False
    tank3_disabled: bool = False
    pump_temperature_tuning: Tuning = (-0.01, -0.001, 0.0)
    pump_flow_tuning: Tuning = (0.01, 0.001, 0.0)
    dc_flow_tuning: Tuning = (-0.01, -0.001, 0.0)
    drives_flow_tuning: Tuning = (-0.01, -0.001, 0.0)

    @model_validator(mode="after")
    def check_tank_setpoints(self):
        if self.minimum_tank_temperature > self.maximum_tank_temperature:
            raise ValueError(
                "Maximum tank temperature must be greater than minimum tank temperature"
            )
        if self.minimum_tank_level > self.maximum_tank_level:
            raise ValueError(
                "Maximum tank level must be greater than minimum tank level"
            )
        return self


def _zero_pid(timestamp: datetime) -> PidControllerValues:
    return PidControllerValues(
        setpoint=Stamped(value=0.0, timestamp=timestamp),
        measurement=Stamped(value=None, timestamp=timestamp),
        output=Stamped(value=None, timestamp=timestamp),
        error=Stamped(value=None, timestamp=timestamp),
        enabled=Stamped(value=False, timestamp=timestamp),
        tuning=Stamped(value=(0.0, 0.0, 0.0), timestamp=timestamp),
        components=Stamped(value=(0.0, 0.0, 0.0), timestamp=timestamp),
    )


def _INITIAL_CONTROL_VALUES(timestamp: datetime) -> DhwControlValues:
    return DhwControlValues(
        dhw_pump=Pump(
            dutypoint=Stamped(value=0.0, timestamp=timestamp),
            on=Stamped(value=False, timestamp=timestamp),
        ),
        dhw_heatpump=HeatPump(
            on=Stamped(value=False, timestamp=timestamp),
            temperature_setpoint=Stamped(value=50.0, timestamp=timestamp),
        ),
        dhw_flowcontrol_dc=Valve(setpoint=Stamped(value=0.5, timestamp=timestamp)),
        dhw_flowcontrol_drives=Valve(setpoint=Stamped(value=0.5, timestamp=timestamp)),
        dhw_switch_tank3_inlet=Valve(setpoint=Stamped(value=0.0, timestamp=timestamp)),
        dhw_switch_tank3_boosting_return=Valve(
            setpoint=Stamped(value=0.0, timestamp=timestamp)
        ),
        dhw_switch_tank3_outlet=Valve(setpoint=Stamped(value=0.0, timestamp=timestamp)),
        dhw_switch_tank3_boosting_supply=Valve(
            setpoint=Stamped(value=0.0, timestamp=timestamp)
        ),
        dhw_switch_tank2_inlet=Valve(setpoint=Stamped(value=0.0, timestamp=timestamp)),
        dhw_switch_tank2_boosting_return=Valve(
            setpoint=Stamped(value=0.0, timestamp=timestamp)
        ),
        dhw_switch_tank2_outlet=Valve(setpoint=Stamped(value=0.0, timestamp=timestamp)),
        dhw_switch_tank2_boosting_supply=Valve(
            setpoint=Stamped(value=0.0, timestamp=timestamp)
        ),
        dhw_switch_tank1_inlet=Valve(setpoint=Stamped(value=0.0, timestamp=timestamp)),
        dhw_switch_tank1_boosting_return=Valve(
            setpoint=Stamped(value=0.0, timestamp=timestamp)
        ),
        dhw_switch_tank1_outlet=Valve(setpoint=Stamped(value=0.0, timestamp=timestamp)),
        dhw_switch_tank1_boosting_supply=Valve(
            setpoint=Stamped(value=0.0, timestamp=timestamp)
        ),
        dhw_switch_low_temperature=Valve(
            setpoint=Stamped(value=0.0, timestamp=timestamp)
        ),
        dhw_switch_heatpump=Valve(setpoint=Stamped(value=0.0, timestamp=timestamp)),
        dhw_switch_high_temperature=Valve(
            setpoint=Stamped(value=0.0, timestamp=timestamp)
        ),
    )


def _INITIAL_CONTROLLER_STATE(timestamp: datetime) -> DhwControllerState:
    return DhwControllerState(
        dhw_tanks_controller=TanksControllerValues(
            tank1_state=Stamped(value=TankState.NEEDS_FILL, timestamp=timestamp),
            tank2_state=Stamped(value=TankState.NEEDS_FILL, timestamp=timestamp),
            tank3_state=Stamped(value=TankState.NEEDS_FILL, timestamp=timestamp),
            time_to_fill=Stamped(value=None, timestamp=timestamp),
        ),
        dhw_drives_flow_controller=_zero_pid(timestamp),
        dhw_dc_flow_controller=_zero_pid(timestamp),
        dhw_pump_flow_controller=_zero_pid(timestamp),
        dhw_pump_temperature_controller=_zero_pid(timestamp),
    )


class Tank:
    def __init__(
        self,
        inlet: Valve,
        outlet: Valve,
        boosting_supply_valve: Valve,
        boosting_return_valve: Valve,
        disabled: bool,
    ):
        self._inlet = inlet
        self._outlet = outlet
        self._boosting_supply_valve = boosting_supply_valve
        self._boosting_return_valve = boosting_return_valve
        self._disabled = disabled
        self._temperature = None
        self._level = None
        self._full = False
        self._outlet_position = None

    @property
    def outlet_position(self) -> Ratio | None:
        return self._outlet_position

    @outlet_position.setter
    def outlet_position(self, value: Ratio | None):
        self._outlet_position = value

    @property
    def level(self) -> Liter | None:
        return self._level

    @level.setter
    def level(self, level: Liter):
        self._level = level

    @property
    def temperature(self) -> Celsius | None:
        return self._temperature

    @temperature.setter
    def temperature(self, temperature: Celsius):
        self._temperature = temperature

    @property
    def disabled(self) -> bool:
        return self._disabled

    @disabled.setter
    def disabled(self, value: bool):
        self._disabled = value

    def above_temperature_setpoint(self, parameters: DhwParameters) -> bool:
        if self._temperature is None:
            return False
        return self._temperature >= parameters.maximum_tank_temperature

    def below_temperature_setpoint(self, parameters: DhwParameters) -> bool:
        if self._temperature is None:
            return False
        return self._temperature < parameters.minimum_tank_temperature

    @property
    def full(self) -> bool:
        return self._full

    def empty(self, parameters: DhwParameters) -> bool:
        if self._level is None:
            return False
        return self._level < parameters.minimum_tank_level

    def standby(self, parameters: DhwParameters) -> bool:
        return (
            not self._disabled
            and self._full
            and not self.below_temperature_setpoint(parameters)
        )

    def boost(self, time: Callable[[], datetime]):
        for valve in [
            self._boosting_supply_valve,
            self._boosting_return_valve,
        ]:
            if valve.setpoint.value != Valve.OPEN:
                valve.setpoint = Stamped(value=Valve.OPEN, timestamp=time())

    def stop_boosting(self, time: Callable[[], datetime]):
        for valve in [self._boosting_supply_valve, self._boosting_return_valve]:
            if valve.setpoint.value != Valve.CLOSED:
                valve.setpoint = Stamped(value=Valve.CLOSED, timestamp=time())

    def boostable(self, parameters: DhwParameters) -> bool:
        return (
            not self.disabled
            and self._full
            and self.below_temperature_setpoint(parameters)
        )

    def fill(self, time: Callable[[], datetime]):
        if self._inlet.setpoint.value != Valve.OPEN:
            self._inlet.setpoint = Stamped(value=Valve.OPEN, timestamp=time())

    def stop_filling(self, time: Callable[[], datetime]):
        self._full = True
        if self._inlet.setpoint.value != Valve.CLOSED:
            self._inlet.setpoint = Stamped(value=Valve.CLOSED, timestamp=time())

    def fillable(self, parameters: DhwParameters) -> bool:
        return (not self._disabled) and (not self._full) and self.outlet_closed()

    def use(self, time: Callable[[], datetime]):
        self._full = False
        if self._outlet.setpoint.value != Valve.OPEN:
            self._outlet.setpoint = Stamped(value=Valve.OPEN, timestamp=time())

    def stop_use(self, time: Callable[[], datetime]):
        if self._outlet.setpoint.value != Valve.CLOSED:
            self._outlet.setpoint = Stamped(value=Valve.CLOSED, timestamp=time())

    def outlet_closed(self) -> bool:
        if self._outlet_position is None:
            return False
        return self._outlet_position < (Valve.CLOSED + 0.001)


class TanksController:
    def __init__(
        self, tank1: Tank, tank2: Tank, tank3: Tank, time_fn: Callable[[], datetime]
    ):
        self._time = time_fn
        self._tanks = [tank1, tank2, tank3]
        self._filling_tank: Tank | None = None
        self._boosting_tank: Tank | None = None
        self._tank_in_use: Tank | None = None

    @property
    def available_tanks(self):
        return [
            tank
            for tank in self._tanks
            if tank is not self._tank_in_use
            and tank is not self._filling_tank
            and tank is not self._boosting_tank
            and not tank.disabled
        ]

    def _update_tank_states(
        self, sensor_values: DhwSensorValues, parameters: DhwParameters
    ):
        temperatures = [
            sensor_values.dhw_temperature_tank1.temperature.value,
            sensor_values.dhw_temperature_tank2.temperature.value,
            sensor_values.dhw_temperature_tank3.temperature.value,
        ]

        levels = [
            sensor_values.dhw_level_tank1.level.value,
            sensor_values.dhw_level_tank2.level.value,
            sensor_values.dhw_level_tank3.level.value,
        ]

        disableds = [
            parameters.tank1_disabled,
            parameters.tank2_disabled,
            parameters.tank3_disabled,
        ]

        outlet_positions = [
            sensor_values.dhw_switch_tank1_outlet.position_rel.value,
            sensor_values.dhw_switch_tank2_outlet.position_rel.value,
            sensor_values.dhw_switch_tank3_outlet.position_rel.value,
        ]

        for tank, level, temperature, disabled, outlet_position in zip(
            self._tanks, levels, temperatures, disableds, outlet_positions
        ):
            tank.level = level
            tank.temperature = temperature
            tank.disabled = disabled
            tank.outlet_position = outlet_position

    def _select_tank_in_use(self, parameters: DhwParameters):
        if self._tank_in_use and self._tank_in_use.empty(parameters):
            self._tank_in_use.stop_use(self._time)
            self._tank_in_use = (
                None  # Don't wait for valve to close as we always need water available
            )

        if self._tank_in_use is None:
            self._tank_in_use = next(
                (tank for tank in self.available_tanks if tank.standby(parameters)),
                None,
            )
            if self._tank_in_use:
                self._tank_in_use.use(self._time)

    def _select_filling_tank(
        self, parameters: DhwParameters, sensor_values: DhwSensorValues
    ):
        if self._filling_tank:
            if not self._filling_tank.full:
                time_to_fill = self.time_to_fill(sensor_values, parameters)
                if (
                    time_to_fill and time_to_fill < 90
                ):  # It takes 90s to close a valve. Flow is decreasing as the tank is filling and as the valve is closing, so 90s should be safe
                    self._filling_tank.stop_filling(self._time)

            elif self._inlets_closed(
                sensor_values
            ):  # Filling is temperature controlled and will continue until the inlet valves is closed, so wait for the filling valves to close before deselecting tank.
                self._filling_tank = None

        else:
            self._filling_tank = next(
                (tank for tank in self.available_tanks if tank.fillable(parameters)),
                None,
            )
            self._filling_tank.fill(self._time) if self._filling_tank else None

    def _select_boosting_tank(
        self, parameters: DhwParameters, sensor_values: DhwSensorValues
    ):
        if (
            self._boosting_tank is not None
            and self._boosting_tank.above_temperature_setpoint(parameters)
        ):
            self._boosting_tank.stop_boosting(self._time)
            self._boosting_tank = None  # Don't wait for valves to close as we want boosting flow to stop when the valves are closing

        if self._boosting_tank is None and self._boosting_valves_closed(sensor_values):
            boostable_tanks = [
                tank for tank in self.available_tanks if tank.boostable(parameters)
            ]
            if boostable_tanks:
                self._boosting_tank = max(  # prioritize hottest tank for boosting #TODO this might not be want you want, as one tank might sit full for a long time (with the other two alternating)
                    boostable_tanks,
                    key=lambda tank: (
                        tank.temperature if tank.temperature is not None else 0
                    ),
                )
                self._boosting_tank.boost(self._time)

    @staticmethod
    def _boosting_valves_closed(sensor_values: DhwSensorValues) -> bool:
        return all(
            boosting_valve.position_rel.value < (Valve.CLOSED + 0.001)
            for boosting_valve in [
                sensor_values.dhw_switch_tank1_boosting_supply,
                sensor_values.dhw_switch_tank1_boosting_return,
                sensor_values.dhw_switch_tank2_boosting_supply,
                sensor_values.dhw_switch_tank2_boosting_return,
                sensor_values.dhw_switch_tank3_boosting_supply,
                sensor_values.dhw_switch_tank3_boosting_return,
            ]
        )

    @staticmethod
    def _inlets_closed(sensor_values: DhwSensorValues) -> bool:
        return all(
            filling_valve.position_rel.value < (Valve.CLOSED + 0.001)
            for filling_valve in [
                sensor_values.dhw_switch_tank1_inlet,
                sensor_values.dhw_switch_tank2_inlet,
                sensor_values.dhw_switch_tank3_inlet,
            ]
        )

    @property
    def filling(self) -> bool:
        return self._filling_tank is not None

    @property
    def boosting(self) -> bool:
        return self._boosting_tank is not None

    def time_to_fill(
        self, sensor_values: DhwSensorValues, parameters: DhwParameters
    ) -> Seconds | None:
        if (
            self._filling_tank is None
            or self._filling_tank.level is None
            or sensor_values.dhw_freshwater_flow_supply.flow.value == 0
        ):
            return None
        return (
            (parameters.maximum_tank_level - self._filling_tank.level)
            / sensor_values.dhw_freshwater_flow_supply.flow.value
            * 60
        )

    def __call__(self, sensor_values: DhwSensorValues, parameters: DhwParameters):
        self._update_tank_states(sensor_values, parameters)
        self._select_tank_in_use(parameters)
        self._select_filling_tank(parameters, sensor_values)
        self._select_boosting_tank(parameters, sensor_values)

    def tank_state(self, tank: Tank, parameters: DhwParameters) -> TankState:
        if tank is self._filling_tank:
            return TankState.FILLING
        if tank is self._boosting_tank:
            return TankState.BOOSTING
        if tank is self._tank_in_use:
            return TankState.IN_USE
        if tank.disabled:
            return TankState.DISABLED
        if tank.boostable(parameters):
            return TankState.NEEDS_BOOST
        if tank.fillable(parameters):
            return TankState.NEEDS_FILL
        return TankState.STANDBY

    def values(
        self, sensor_values: DhwSensorValues, parameters: DhwParameters
    ) -> TanksControllerValues:
        time = self._time()
        return TanksControllerValues(
            tank1_state=Stamped(
                value=self.tank_state(self._tanks[0], parameters), timestamp=time
            ),
            tank2_state=Stamped(
                value=self.tank_state(self._tanks[1], parameters), timestamp=time
            ),
            tank3_state=Stamped(
                value=self.tank_state(self._tanks[2], parameters), timestamp=time
            ),
            time_to_fill=Stamped(
                value=self.time_to_fill(sensor_values, parameters),
                timestamp=time,
            ),
        )


class DhwControlMode(ControlMode):
    boosting_mode: str
    filling_mode: str

    @property
    def is_boosting_idle(self) -> bool:
        return self.boosting_mode == "idle"

    @property
    def is_boosting_low_temperature(self) -> bool:
        return self.boosting_mode == "boosting_low_temperature"

    @property
    def is_boosting_high_temperature(self) -> bool:
        return self.boosting_mode == "boosting_high_temperature"

    @property
    def is_boosting_heatpump(self) -> bool:
        return self.boosting_mode == "boosting_heatpump"


class DhwControl(
    Control[
        DhwSensorValues,
        DhwControlValues,
        DhwParameters,
        DhwControlMode,
        DhwControllerState,
    ]
):
    state: str  # Value set by Machine transitions logic

    def __init__(
        self,
        parameters: DhwParameters,
        time_fn: Callable[[], datetime],
        state_logger: StateLogger | None = None,
    ) -> None:
        self._parameters = parameters
        self._time = time_fn
        self.state_logger = state_logger or MachineStateLoggingServiceNoop()
        self._current_values, self._current_controller_state = self.initial()

        self._init_state_machine_states()
        self._init_state_machine_transitions()
        self._state_machine = self.state_logger.create_logged_state_machine(
            self,
            transitions=self._transitions,
            states=self._states,
            initial="idle",
        )
        self._init_controllers()
        self.state_logger.log_parameters_initial_state(parameters)

    def _init_state_machine_states(self):
        self._states = [
            State(
                name="idle",
                on_enter=[
                    self._deactivate_pump,
                    self._close_boosting_valves,
                ],
                on_exit=[self._activate_pump],
            ),
            State(
                name="boosting_low_temperature",  # TODO: Low temperature boosting not implemented yet
                on_enter=[
                    self._set_valves_to_boosting_low_temperature,
                    self._enable_pump_temperature_control,
                ],
            ),
            State(
                name="boosting_high_temperature",
                on_enter=[
                    self._set_valves_to_boosting_high_temperature,
                    self._enable_pump_temperature_control,
                ],
                on_exit=[self._disable_pump_temperature_control],
            ),
            State(
                name="boosting_heatpump",
                on_enter=[
                    self._set_valves_to_boosting_heatpump,
                    self._activate_heatpump,
                    self._enable_pump_flow_control,
                ],
                on_exit=[self._deactivate_heatpump, self._disable_pump_flow_control],
            ),
        ]

    def _init_state_machine_transitions(self):
        self._transitions = [
            {
                "trigger": "_try_boosting",
                "source": ["idle", "boosting_heatpump"],
                "dest": "boosting_high_temperature",
                "conditions": lambda sensor_values: (
                    self._tanks_controller.boosting
                    and self._ht_sufficient_boosting_heat(sensor_values)
                    and self._parameters.heatpump_boosting_enabled
                ),
            },
            {
                "trigger": "_try_boosting",
                "source": ["idle", "boosting_high_temperature"],
                "dest": "boosting_heatpump",
                "conditions": lambda sensor_values: (
                    self._tanks_controller.boosting
                    and not self._ht_sufficient_boosting_heat(sensor_values)
                    and self._parameters.ht_boosting_enabled
                ),  # TODO: Should be extended with a assessment of whether using electricity for boosting is desireable. Alternatively, this should be controlled by a high-level controller that can enable or disable heatpump boosting.
            },
            {
                "trigger": "_try_boosting",
                "source": ["boosting_heatpump"],
                "dest": "idle",
                "conditions": lambda sensor_values: (
                    not self._tanks_controller.boosting
                    or not self._parameters.heatpump_boosting_enabled
                ),
            },
            {
                "trigger": "_try_boosting",
                "source": ["boosting_high_temperature"],
                "dest": "idle",
                "conditions": lambda sensor_values: (
                    not self._tanks_controller.boosting
                    or not self._parameters.ht_boosting_enabled
                ),
            },
        ]

    def _init_controllers(self):
        if not hasattr(self, "_state_machine") or self._state_machine is None:
            raise ValueError(
                "State machine must be initialized before creating control methods"
            )

        self._pump_temperature_controller = PidController[Ratio, Celsius](
            self._current_values.dhw_pump.dutypoint.value,
            0,
            lambda: self._parameters.pump_temperature_tuning,
            self._time,
        )

        self._pump_flow_controller = PidController[Ratio, LMin](
            self._current_values.dhw_pump.dutypoint.value,
            self._parameters.heatpump_flow_setpoint,
            lambda: self._parameters.pump_flow_tuning,
            self._time,
        )

        self._dhw_drives_flow_controller = PidController[Ratio, Celsius](
            self._current_values.dhw_flowcontrol_drives.setpoint.value,
            lambda: self._parameters.filling_temperature_setpoint,
            lambda: self._parameters.drives_flow_tuning,
            self._time,
            lambda: (self._parameters.drives_flowcontrol_minimum_setpoint, 1.0),
        )

        self._dhw_dc_flow_controller = PidController[Ratio, Celsius](
            self._current_values.dhw_flowcontrol_dc.setpoint.value,
            lambda: self._parameters.filling_temperature_setpoint,
            lambda: self._parameters.dc_flow_tuning,
            self._time,
            lambda: (self._parameters.dc_flowcontrol_minimum_setpoint, 1.0),
        )

        self._tanks_controller = TanksController(
            tank1=Tank(
                inlet=self._current_values.dhw_switch_tank1_inlet,
                outlet=self._current_values.dhw_switch_tank1_outlet,
                boosting_supply_valve=self._current_values.dhw_switch_tank1_boosting_supply,
                boosting_return_valve=self._current_values.dhw_switch_tank1_boosting_return,
                disabled=self._parameters.tank1_disabled,
            ),
            tank2=Tank(
                inlet=self._current_values.dhw_switch_tank2_inlet,
                outlet=self._current_values.dhw_switch_tank2_outlet,
                boosting_supply_valve=self._current_values.dhw_switch_tank2_boosting_supply,
                boosting_return_valve=self._current_values.dhw_switch_tank2_boosting_return,
                disabled=self._parameters.tank2_disabled,
            ),
            tank3=Tank(
                inlet=self._current_values.dhw_switch_tank3_inlet,
                outlet=self._current_values.dhw_switch_tank3_outlet,
                boosting_supply_valve=self._current_values.dhw_switch_tank3_boosting_supply,
                boosting_return_valve=self._current_values.dhw_switch_tank3_boosting_return,
                disabled=self._parameters.tank3_disabled,
            ),
            time_fn=self._time,
        )

    def update_controller_state(self, sensor_values: DhwSensorValues):
        self._current_controller_state.dhw_tanks_controller = (
            self._tanks_controller.values(
                sensor_values=sensor_values, parameters=self._parameters
            )
        )
        self._current_controller_state.dhw_drives_flow_controller = (
            self._dhw_drives_flow_controller.values()
        )
        self._current_controller_state.dhw_dc_flow_controller = (
            self._dhw_dc_flow_controller.values()
        )
        self._current_controller_state.dhw_pump_flow_controller = (
            self._pump_flow_controller.values()
        )
        self._current_controller_state.dhw_pump_temperature_controller = (
            self._pump_temperature_controller.values()
        )

    @property
    def parameters(self) -> DhwParameters:
        return self._parameters

    @StateLogger.log_parameters
    def update_parameters(self, parameters: DhwParameters):
        self._parameters = parameters

    def modes(self) -> list[str]:
        return list(self._state_machine.states.keys())

    @property
    def initial_mode(self) -> DhwControlMode:
        initial_mode: str = self._state_machine.initial  # type: ignore
        return DhwControlMode(boosting_mode=initial_mode, filling_mode="idle")

    @property
    def mode(self) -> DhwControlMode:
        mode: str = self.state  # type: ignore
        filling_mode: str = "idle" if not self._tanks_controller.filling else "filling"
        return DhwControlMode(boosting_mode=mode, filling_mode=filling_mode)

    def initial(self) -> tuple[DhwControlValues, DhwControllerState]:
        controller_state = _INITIAL_CONTROLLER_STATE(self._time())

        return (
            _INITIAL_CONTROL_VALUES(self._time()).model_copy(deep=True),
            controller_state.model_copy(deep=True),
        )

    @StateLogger.log_warnings
    def control(
        self, sensor_values: DhwSensorValues
    ) -> tuple[DhwControlValues, DhwControllerState]:
        self._tanks_controller(sensor_values, self._parameters)
        self._try_boosting(sensor_values)  # type: ignore
        self._enable_filling_flow_control(sensor_values)
        self._control_filling_flow(sensor_values)
        self._control_boosting_flow(sensor_values)

        self.update_controller_state(sensor_values)

        return (self._current_values, self._current_controller_state)

    def _drives_sufficient_boosting_heat(self, sensor_values: DhwSensorValues) -> bool:
        if self._tanks_controller._boosting_tank is None:
            return False

        delta = (
            sensor_values.drives_temperature_recovery.temperature.value
            - self._tanks_controller._boosting_tank.temperature
            if self._tanks_controller._boosting_tank.temperature is not None
            else False
        )

        return (
            delta > self._parameters.boosting_delta
            and sensor_values.drives_flow_recovery.flow.value > 0.1
        )

    def _ht_sufficient_boosting_heat(self, sensor_values: DhwSensorValues) -> bool:
        if self._tanks_controller._boosting_tank is None:
            return False

        delta = (
            sensor_values.consumers_temperature_dhw_supply.temperature.value
            - self._tanks_controller._boosting_tank.temperature
            if self._tanks_controller._boosting_tank.temperature is not None
            else False
        )

        return (
            delta > self._parameters.boosting_delta
            and sensor_values.consumers_flow_dhw.flow.value > 0.1
        )

    def _enable_filling_flow_control(self, sensor_values: DhwSensorValues):
        if self._tanks_controller.filling:
            for controller in [
                self._dhw_drives_flow_controller,
                self._dhw_dc_flow_controller,
            ]:
                if not controller.enabled():
                    controller.enable()

        if (
            not self._drives_heat_available(sensor_values)
            and self._dhw_drives_flow_controller.enabled()
        ):
            self._dhw_drives_flow_controller.disable()
            self._current_values.dhw_flowcontrol_drives.setpoint = Stamped(
                value=Valve.CLOSED, timestamp=self._time()
            )

        if not self._tanks_controller.filling:
            for controller in [
                self._dhw_drives_flow_controller,
                self._dhw_dc_flow_controller,
            ]:
                if controller.enabled():
                    controller.disable()
                self._current_values.dhw_flowcontrol_drives.setpoint = Stamped(
                    value=Valve.CLOSED, timestamp=self._time()
                )
                self._current_values.dhw_flowcontrol_dc.setpoint = Stamped(
                    value=Valve.CLOSED, timestamp=self._time()
                )

    def _control_filling_flow(self, sensor_values: DhwSensorValues):
        if self._dhw_drives_flow_controller.enabled():
            self._current_values.dhw_flowcontrol_drives.setpoint = Stamped(
                value=self._dhw_drives_flow_controller(
                    sensor_values.dhw_temperature_drives_return.temperature.value
                ),
                timestamp=self._time(),
            )
        if self._dhw_dc_flow_controller.enabled():
            self._current_values.dhw_flowcontrol_dc.setpoint = Stamped(
                value=self._dhw_dc_flow_controller(
                    sensor_values.dhw_temperature_dc_return.temperature.value
                ),
                timestamp=self._time(),
            )

    def _control_boosting_flow(self, sensor_values: DhwSensorValues):
        if (
            self._pump_temperature_controller.enabled()
            and self._pump_flow_controller.enabled()
        ):
            raise Exception(
                "Both pump temperature and flow controllers cannot be enabled at the same time"
            )

        elif self._pump_flow_controller.enabled():
            self._current_values.dhw_pump.dutypoint = Stamped(
                value=self._pump_flow_controller(
                    sensor_values.dhw_flow_boosting.flow.value
                ),
                timestamp=self._time(),
            )

        elif self._pump_temperature_controller.enabled():
            self._current_values.dhw_pump.dutypoint = Stamped(
                value=self._pump_temperature_controller(
                    sensor_values.dhw_temperature_boosting_return.temperature.value
                ),
                timestamp=self._time(),
            )

    def _drives_heat_available(self, sensor_values: DhwSensorValues) -> bool:
        return sensor_values.drives_flow_recovery.flow.value > 0.1

    def _set_valves_to_boosting_low_temperature(self, sensor_values: DhwSensorValues):
        self._current_values.dhw_switch_low_temperature.setpoint = Stamped(
            value=1.0, timestamp=self._time()
        )
        self._current_values.dhw_switch_high_temperature.setpoint = Stamped(
            value=0.0, timestamp=self._time()
        )
        self._current_values.dhw_switch_heatpump.setpoint = Stamped(
            value=0.0, timestamp=self._time()
        )

    def _set_valves_to_boosting_high_temperature(self, sensor_values: DhwSensorValues):
        self._current_values.dhw_switch_low_temperature.setpoint = Stamped(
            value=0.0, timestamp=self._time()
        )
        self._current_values.dhw_switch_high_temperature.setpoint = Stamped(
            value=1.0, timestamp=self._time()
        )
        self._current_values.dhw_switch_heatpump.setpoint = Stamped(
            value=0.0, timestamp=self._time()
        )

    def _set_valves_to_boosting_heatpump(self, sensor_values: DhwSensorValues):
        self._current_values.dhw_switch_low_temperature.setpoint = Stamped(
            value=0.0, timestamp=self._time()
        )
        self._current_values.dhw_switch_high_temperature.setpoint = Stamped(
            value=0.0, timestamp=self._time()
        )
        self._current_values.dhw_switch_heatpump.setpoint = Stamped(
            value=1.0, timestamp=self._time()
        )

    def _close_boosting_valves(self, sensor_values: DhwSensorValues):
        self._current_values.dhw_switch_low_temperature.setpoint = Stamped(
            value=0.0, timestamp=self._time()
        )
        self._current_values.dhw_switch_high_temperature.setpoint = Stamped(
            value=0.0, timestamp=self._time()
        )
        self._current_values.dhw_switch_heatpump.setpoint = Stamped(
            value=0.0, timestamp=self._time()
        )

    def _activate_pump(self, sensor_values: DhwSensorValues):
        self._current_values.dhw_pump.on = Stamped(value=True, timestamp=self._time())

    def _deactivate_pump(self, sensor_values: DhwSensorValues):
        self._current_values.dhw_pump.on = Stamped(value=False, timestamp=self._time())
        self._current_values.dhw_pump.dutypoint = Stamped(
            value=0.0, timestamp=self._time()
        )

    def _activate_heatpump(self, sensor_values: DhwSensorValues):
        self._current_values.dhw_heatpump.on = Stamped(
            value=True, timestamp=self._time()
        )
        self._current_values.dhw_heatpump.temperature_setpoint = Stamped(
            value=self._parameters.heatpump_temperature_setpoint, timestamp=self._time()
        )

    def _deactivate_heatpump(self, sensor_values: DhwSensorValues):
        self._current_values.dhw_heatpump.on = Stamped(
            value=False, timestamp=self._time()
        )

    def _enable_pump_temperature_control(self, sensor_values: DhwSensorValues):
        if not self._pump_temperature_controller.enabled():
            self._pump_temperature_controller.enable()

    def _disable_pump_temperature_control(self, sensor_values: DhwSensorValues):
        if self._pump_temperature_controller.enabled():
            self._pump_temperature_controller.disable()

    def _enable_pump_flow_control(self, sensor_values: DhwSensorValues):
        self._pump_flow_controller.enable()

    def _disable_pump_flow_control(self, sensor_values: DhwSensorValues):
        self._pump_flow_controller.disable()


class DhwAlarms(BaseAlarms):
    @staticmethod
    def _check_tank_temperature(
        tank_number: int,
        temperature: float,
        yard_tag: str,
        maximum: float,
        delta: float,
    ) -> str | None:
        if temperature > maximum + delta:
            return f"Tank {tank_number} temperature sensor {yard_tag} at {temperature:.1f}°C, above maximum {maximum}°C"
        return None

    @staticmethod
    def _check_tank_level(
        tank_number: int,
        level: float,
        yard_tag: str,
        maximum: float,
    ) -> str | None:
        if level > maximum:
            return f"Tank {tank_number} level sensor {yard_tag} at {level:.1f}L, above maximum {maximum}L"
        return None

    @alarm("Tank 1 high temperature warning", severity=Severity.WARNING)
    def check_tank1_temperature_warning(
        self,
        sensor_values: DhwSensorValues,
        control_values: DhwControlValues,
        parameters: DhwParameters,
    ) -> str | None:
        return self._check_tank_temperature(
            1,
            sensor_values.dhw_temperature_tank1.temperature.value,
            DhwSensorValues.yard_tag("dhw_temperature_tank1"),
            parameters.maximum_tank_temperature,
            2,
        )

    @alarm("Tank 2 high temperature warning", severity=Severity.WARNING)
    def check_tank2_temperature_warning(
        self,
        sensor_values: DhwSensorValues,
        control_values: DhwControlValues,
        parameters: DhwParameters,
    ) -> str | None:
        return self._check_tank_temperature(
            2,
            sensor_values.dhw_temperature_tank2.temperature.value,
            DhwSensorValues.yard_tag("dhw_temperature_tank2"),
            parameters.maximum_tank_temperature,
            2,
        )

    @alarm("Tank 3 high temperature warning", severity=Severity.WARNING)
    def check_tank3_temperature_warning(
        self,
        sensor_values: DhwSensorValues,
        control_values: DhwControlValues,
        parameters: DhwParameters,
    ) -> str | None:
        return self._check_tank_temperature(
            3,
            sensor_values.dhw_temperature_tank3.temperature.value,
            DhwSensorValues.yard_tag("dhw_temperature_tank3"),
            parameters.maximum_tank_temperature,
            2,
        )

    @alarm("Tank 1 high temperature alarm", severity=Severity.ALARM)
    def check_tank1_temperature_alarm(
        self,
        sensor_values: DhwSensorValues,
        control_values: DhwControlValues,
        parameters: DhwParameters,
    ) -> str | None:
        return self._check_tank_temperature(
            1,
            sensor_values.dhw_temperature_tank1.temperature.value,
            DhwSensorValues.yard_tag("dhw_temperature_tank1"),
            parameters.maximum_tank_temperature,
            5,
        )

    @alarm("Tank 2 high temperature alarm", severity=Severity.ALARM)
    def check_tank2_temperature_alarm(
        self,
        sensor_values: DhwSensorValues,
        control_values: DhwControlValues,
        parameters: DhwParameters,
    ) -> str | None:
        return self._check_tank_temperature(
            2,
            sensor_values.dhw_temperature_tank2.temperature.value,
            DhwSensorValues.yard_tag("dhw_temperature_tank2"),
            parameters.maximum_tank_temperature,
            5,
        )

    @alarm("Tank 3 high temperature alarm", severity=Severity.ALARM)
    def check_tank3_temperature_alarm(
        self,
        sensor_values: DhwSensorValues,
        control_values: DhwControlValues,
        parameters: DhwParameters,
    ) -> str | None:
        return self._check_tank_temperature(
            3,
            sensor_values.dhw_temperature_tank3.temperature.value,
            DhwSensorValues.yard_tag("dhw_temperature_tank3"),
            parameters.maximum_tank_temperature,
            5,
        )

    @alarm("Tank 1 high level warning", severity=Severity.WARNING)
    def check_tank1_level_warning(
        self,
        sensor_values: DhwSensorValues,
        control_values: DhwControlValues,
        parameters: DhwParameters,
    ) -> str | None:
        return self._check_tank_level(
            1,
            sensor_values.dhw_level_tank1.level.value,
            DhwSensorValues.yard_tag("dhw_level_tank1"),
            265,
        )

    @alarm("Tank 2 high level warning", severity=Severity.WARNING)
    def check_tank2_level_warning(
        self,
        sensor_values: DhwSensorValues,
        control_values: DhwControlValues,
        parameters: DhwParameters,
    ) -> str | None:
        return self._check_tank_level(
            2,
            sensor_values.dhw_level_tank2.level.value,
            DhwSensorValues.yard_tag("dhw_level_tank2"),
            265,
        )

    @alarm("Tank 3 high level warning", severity=Severity.WARNING)
    def check_tank3_level_warning(
        self,
        sensor_values: DhwSensorValues,
        control_values: DhwControlValues,
        parameters: DhwParameters,
    ) -> str | None:
        return self._check_tank_level(
            3,
            sensor_values.dhw_level_tank3.level.value,
            DhwSensorValues.yard_tag("dhw_level_tank3"),
            265,
        )

    @alarm("Tank 1 high level alarm", severity=Severity.ALARM)
    def check_tank1_level_alarm(
        self,
        sensor_values: DhwSensorValues,
        control_values: DhwControlValues,
        parameters: DhwParameters,
    ) -> str | None:
        return self._check_tank_level(
            1,
            sensor_values.dhw_level_tank1.level.value,
            DhwSensorValues.yard_tag("dhw_level_tank1"),
            270,
        )

    @alarm("Tank 2 high level alarm", severity=Severity.ALARM)
    def check_tank2_level_alarm(
        self,
        sensor_values: DhwSensorValues,
        control_values: DhwControlValues,
        parameters: DhwParameters,
    ) -> str | None:
        return self._check_tank_level(
            2,
            sensor_values.dhw_level_tank2.level.value,
            DhwSensorValues.yard_tag("dhw_level_tank2"),
            270,
        )

    @alarm("Tank 3 high level alarm", severity=Severity.ALARM)
    def check_tank3_level_alarm(
        self,
        sensor_values: DhwSensorValues,
        control_values: DhwControlValues,
        parameters: DhwParameters,
    ) -> str | None:
        return self._check_tank_level(
            3,
            sensor_values.dhw_level_tank3.level.value,
            DhwSensorValues.yard_tag("dhw_level_tank3"),
            270,
        )


DHW_MODULE_DESCRIPTION = ModuleDescription(
    DhwSensorValues,
    DhwControlValues,
    DhwParameters,
    DhwControl,
    DhwControlMode,
    DhwControllerState,
    DhwAlarms,
)
