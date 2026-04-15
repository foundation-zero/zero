from datetime import datetime
from typing import Callable

from transitions import Machine, State
from thrs.classes.control import Control, ControlMode, ControlResult
from thrs.control.controllers import Controller
from thrs.input_output.alarms import BaseAlarms
from thrs.input_output.base import Stamped, ThrsValues
from thrs.input_output.definitions.control import HeatPump, Pump, Valve
from thrs.input_output.definitions.units import (
    Celsius,
    Kelvin,
    LMin,
    Liter,
    Ratio,
    Tuning,
)
from thrs.input_output.modules.boilers import BoilersControlValues, BoilersSensorValues


class BoilersParameters(ThrsValues):
    heatpump_flow_setpoint: LMin = 25
    heatpump_temperature_setpoint: Celsius = 65
    minimum_tank_temperature: Celsius = 55
    maximum_tank_temperature: Celsius = 60
    boosting_delta: Kelvin = (
        2  # required delta T between boosting source and tank temperature
    )
    tank_temperature_setpoint: Celsius = 50
    lt1_flowcontrol_minimum_setpoint: Ratio = 0.3  # need flow to have temp measurement available, and these minima are needed to control the minimum filling flow
    lt2_flowcontrol_minimum_setpoint: Ratio = 0.3
    filling_temperature_setpoint: Celsius = 40
    minimum_tank_level: Liter = 30
    maximum_tank_level: Liter = 260
    tank1_disabled: bool = False
    tank2_disabled: bool = False
    tank3_disabled: bool = False
    pump_temperature_tuning: Tuning = (-0.01, -0.001, 0.0)
    pump_flow_tuning: Tuning = (0.01, 0.001, 0.0)
    lt2_flow_tuning: Tuning = (-0.01, -0.001, 0.0)
    lt1_flow_tuning: Tuning = (-0.01, -0.001, 0.0)


def _INITIAL_CONTROL_VALUES(timestamp: datetime) -> BoilersControlValues:
    return BoilersControlValues(
        boilers_pump=Pump(
            dutypoint=Stamped(value=0.0, timestamp=timestamp),
            on=Stamped(value=False, timestamp=timestamp),
        ),
        boilers_heatpump=HeatPump(
            on=Stamped(value=False, timestamp=timestamp),
            temperature_setpoint=Stamped(value=50.0, timestamp=timestamp),
        ),
        boilers_flowcontrol_lt2=Valve(setpoint=Stamped(value=0.5, timestamp=timestamp)),
        boilers_flowcontrol_lt1=Valve(setpoint=Stamped(value=0.5, timestamp=timestamp)),
        boilers_switch_tank3_fill=Valve(
            setpoint=Stamped(value=0.0, timestamp=timestamp)
        ),
        boilers_switch_tank3_boosting_return=Valve(
            setpoint=Stamped(value=0.0, timestamp=timestamp)
        ),
        boilers_switch_tank3_empty=Valve(
            setpoint=Stamped(value=0.0, timestamp=timestamp)
        ),
        boilers_switch_tank3_boosting_supply=Valve(
            setpoint=Stamped(value=0.0, timestamp=timestamp)
        ),
        boilers_switch_tank2_fill=Valve(
            setpoint=Stamped(value=0.0, timestamp=timestamp)
        ),
        boilers_switch_tank2_boosting_return=Valve(
            setpoint=Stamped(value=0.0, timestamp=timestamp)
        ),
        boilers_switch_tank2_empty=Valve(
            setpoint=Stamped(value=0.0, timestamp=timestamp)
        ),
        boilers_switch_tank2_boosting_supply=Valve(
            setpoint=Stamped(value=0.0, timestamp=timestamp)
        ),
        boilers_switch_tank1_fill=Valve(
            setpoint=Stamped(value=0.0, timestamp=timestamp)
        ),
        boilers_switch_tank1_boosting_return=Valve(
            setpoint=Stamped(value=0.0, timestamp=timestamp)
        ),
        boilers_switch_tank1_empty=Valve(
            setpoint=Stamped(value=0.0, timestamp=timestamp)
        ),
        boilers_switch_tank1_boosting_supply=Valve(
            setpoint=Stamped(value=0.0, timestamp=timestamp)
        ),
        boilers_switch_low_temperature=Valve(
            setpoint=Stamped(value=0.0, timestamp=timestamp)
        ),
        boilers_switch_heatpump=Valve(setpoint=Stamped(value=0.0, timestamp=timestamp)),
        boilers_switch_high_temperature=Valve(
            setpoint=Stamped(value=0.0, timestamp=timestamp)
        ),
    )


class Tank:
    def __init__(
        self,
        fill_valve: Valve,
        empty_valve: Valve,
        boosting_supply_valve: Valve,
        boosting_return_valve: Valve,
        disabled: bool,
    ):
        self._fill_valve = fill_valve
        self._empty_valve = empty_valve
        self._boosting_supply_valve = boosting_supply_valve
        self._boosting_return_valve = boosting_return_valve
        self._disabled = disabled
        self._temperature = None
        self._level = None

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

    def above_temperature_setpoint(self, parameters: BoilersParameters) -> bool:
        if self._temperature is None:
            return False
        return self._temperature >= parameters.maximum_tank_temperature

    def below_temperature_setpoint(self, parameters: BoilersParameters) -> bool:
        if self._temperature is None:
            return False
        return self._temperature < parameters.minimum_tank_temperature

    def full(self, parameters: BoilersParameters) -> bool:
        if self._level is None:
            return False
        return self._level > parameters.maximum_tank_level

    def empty(self, parameters: BoilersParameters) -> bool:
        if self._level is None:
            return False
        return self._level < parameters.minimum_tank_level

    def standby(self, parameters: BoilersParameters) -> bool:
        if self.full is None:
            return False
        return (
            not self.disabled
            and self.full(parameters)
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

    def boostable(self, parameters: BoilersParameters) -> bool:
        return (
            not self.disabled
            and self.full(parameters)
            and self.below_temperature_setpoint(parameters)
        )

    def fill(self, time: Callable[[], datetime]):
        if self._fill_valve.setpoint.value != Valve.OPEN:
            self._fill_valve.setpoint = Stamped(value=Valve.OPEN, timestamp=time())

    def stop_filling(self, time: Callable[[], datetime]):
        if self._fill_valve.setpoint.value != Valve.CLOSED:
            self._fill_valve.setpoint = Stamped(value=Valve.CLOSED, timestamp=time())

    def fillable(self, parameters: BoilersParameters) -> bool:
        return not self.disabled and not self.full(parameters)

    def use(self, time: Callable[[], datetime]):
        if self._empty_valve.setpoint.value != Valve.OPEN:
            self._empty_valve.setpoint = Stamped(value=Valve.OPEN, timestamp=time())

    def stop_use(self, time: Callable[[], datetime]):
        if self._empty_valve.setpoint.value != Valve.CLOSED:
            self._empty_valve.setpoint = Stamped(value=Valve.CLOSED, timestamp=time())


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
        self, sensor_values: BoilersSensorValues, parameters: BoilersParameters
    ):
        temperatures = [
            sensor_values.boilers_temperature_tank1.temperature.value,
            sensor_values.boilers_temperature_tank2.temperature.value,
            sensor_values.boilers_temperature_tank3.temperature.value,
        ]

        levels = [
            sensor_values.boilers_level_tank1.level.value,
            sensor_values.boilers_level_tank2.level.value,
            sensor_values.boilers_level_tank3.level.value,
        ]

        disableds = [
            parameters.tank1_disabled,
            parameters.tank2_disabled,
            parameters.tank3_disabled,
        ]

        for tank, level, temperature, disabled in zip(
            self._tanks, levels, temperatures, disableds
        ):
            tank.level = level
            tank.temperature = temperature
            tank.disabled = disabled

    def _select_tank_in_use(self, parameters: BoilersParameters):
        if self._tank_in_use is not None and self._tank_in_use.empty(parameters):
            self._tank_in_use.stop_use(self._time)
            self._tank_in_use = (
                None  # Don't wait for valve to close as we always want tank in use
            )

        if self._tank_in_use is None:
            self._tank_in_use = next(
                (tank for tank in self.available_tanks if tank.standby(parameters)),
                None,
            )
            if self._tank_in_use is not None:
                self._tank_in_use.use(self._time)

    def _select_filling_tank(
        self, parameters: BoilersParameters, sensor_values: BoilersSensorValues
    ):
        if self._filling_tank is not None and self._filling_tank.full(parameters):
            self._filling_tank.stop_filling(self._time)

            if all(
                filling_valve.position_rel.value < (Valve.CLOSED + 0.001)
                for filling_valve in [
                    sensor_values.boilers_switch_tank1_fill,
                    sensor_values.boilers_switch_tank2_fill,
                    sensor_values.boilers_switch_tank3_fill,
                ]
            ):
                self._filling_tank = None

        if self._filling_tank is None:
            self._filling_tank = next(
                (tank for tank in self.available_tanks if tank.fillable(parameters)),
                None,
            )
            if self._filling_tank is not None:
                self._filling_tank.fill(self._time)

    def _select_boosting_tank(
        self, parameters: BoilersParameters, sensor_values: BoilersSensorValues
    ):
        if (
            self._boosting_tank is not None
            and self._boosting_tank.above_temperature_setpoint(parameters)
        ):
            self._boosting_tank.stop_boosting(self._time)
            if all(
                boosting_valve.position_rel.value < (Valve.CLOSED + 0.001)
                for boosting_valve in [
                    sensor_values.boilers_switch_tank1_boosting_supply,
                    sensor_values.boilers_switch_tank1_boosting_return,
                    sensor_values.boilers_switch_tank2_boosting_supply,
                    sensor_values.boilers_switch_tank2_boosting_return,
                    sensor_values.boilers_switch_tank3_boosting_supply,
                    sensor_values.boilers_switch_tank3_boosting_return,
                ]
            ):
                self._boosting_tank = None

        if self._boosting_tank is None:
            boostable_tanks = [
                tank for tank in self.available_tanks if tank.boostable(parameters)
            ]
            if boostable_tanks:
                self._boosting_tank = max(  # prioritize hottest tank for boosting
                    boostable_tanks,
                    key=lambda tank: tank.temperature
                    if tank.temperature is not None
                    else 0,
                )
                self._boosting_tank.boost(self._time)

    @property
    def filling(self) -> bool:
        return self._filling_tank is not None

    @property
    def boosting(self) -> bool:
        return self._boosting_tank is not None

    def __call__(
        self, sensor_values: BoilersSensorValues, parameters: BoilersParameters
    ):
        self._update_tank_states(sensor_values, parameters)
        self._select_tank_in_use(parameters)
        self._select_filling_tank(parameters, sensor_values)
        self._select_boosting_tank(parameters, sensor_values)


class BoilersControlMode(ControlMode):
    mode: str

    @property
    def is_idle(self) -> bool:
        return self.mode == "idle"

    @property
    def is_boosting_low_temperature(self) -> bool:
        return self.mode == "boosting_low_temperature"

    @property
    def is_boosting_high_temperature(self) -> bool:
        return self.mode == "boosting_high_temperature"

    @property
    def is_boosting_heatpump(self) -> bool:
        return self.mode == "boosting_heatpump"


class BoilersControl(
    Control[
        BoilersSensorValues, BoilersControlValues, BoilersParameters, BoilersControlMode
    ]
):
    def __init__(
        self, parameters: BoilersParameters, time_fn: Callable[[], datetime]
    ) -> None:
        self._parameters = parameters
        self._time = time_fn
        self._current_values = _INITIAL_CONTROL_VALUES(self._time()).model_copy(
            deep=True
        )

        self._states = [
            State(
                name="idle",
                on_enter=[
                    self._deactivate_pump,
                    self._disable_pump_flow_control,
                    self._close_boosting_valves,
                ],
                on_exit=[self._activate_pump],
            ),
            # State(
            #     name="boosting_low_temperature",  # TODO: Need separate valve settings for Low temperature boosting since it uses filling valves..
            #     on_enter=[
            #         self._set_valves_to_boosting_low_temperature,
            #         self._enable_pump_temperature_control,
            #     ],
            # ),
            State(
                name="boosting_high_temperature",
                on_enter=[
                    self._set_valves_to_boosting_high_temperature,
                    self._enable_pump_temperature_control,
                ],
            ),
            State(
                name="boosting_heatpump",
                on_enter=[
                    self._set_valves_to_boosting_heatpump,
                    self._activate_heatpump,
                    self._enable_pump_flow_control,
                ],
                on_exit=[self._deactivate_heatpump],
            ),
        ]

        self._transitions = [
            {
                "trigger": "_try_boosting",
                "source": ["idle", "boosting_heatpump"],
                "dest": "boosting_high_temperature",
                "conditions": lambda sensor_values: self._tanks_controller.boosting
                and self._ht_sufficient_boosting_heat(sensor_values),
            },
            {
                "trigger": "_try_boosting",
                "source": ["idle", "boosting_high_temperature"],
                "dest": "boosting_heatpump",
                "conditions": lambda sensor_values: self._tanks_controller.boosting
                and not self._ht_sufficient_boosting_heat(
                    sensor_values
                ),  # TODO: using electricity is worth it. <- maybe use a heatpump_boosting_enabled parameter. Or let it depend on whether there is a tank standby or not...
            },
            {
                "trigger": "_try_boosting",
                "source": ["boosting_heatpump", "boosting_high_temperature"],
                "dest": "idle",
                "conditions": lambda sensor_values: not self._tanks_controller.boosting,
            },
        ]

        self._state_machine = Machine(
            model=self,
            states=self._states,
            transitions=self._transitions,
            initial="idle",
        )

        self._pump_temperature_controller = Controller[Ratio, Celsius](
            self._current_values.boilers_pump.dutypoint.value,
            0,
            lambda: self._parameters.pump_temperature_tuning,
            self._time,
        )

        self._pump_flow_controller = Controller[Ratio, LMin](
            self._current_values.boilers_pump.dutypoint.value,
            0,
            lambda: self._parameters.pump_flow_tuning,
            self._time,
        )

        self._lt1_flow_controller = Controller[Ratio, Celsius](
            self._current_values.boilers_flowcontrol_lt1.setpoint.value,
            lambda: self._parameters.filling_temperature_setpoint,
            lambda: self._parameters.lt1_flow_tuning,
            self._time,
            lambda: (self._parameters.lt1_flowcontrol_minimum_setpoint, 1.0),
        )

        self._lt2_flow_controller = Controller[Ratio, Celsius](
            self._current_values.boilers_flowcontrol_lt2.setpoint.value,
            lambda: self._parameters.filling_temperature_setpoint,
            lambda: self._parameters.lt2_flow_tuning,
            self._time,
            lambda: (self._parameters.lt2_flowcontrol_minimum_setpoint, 1.0),
        )

        self._tanks_controller = TanksController(
            tank1=Tank(
                fill_valve=self._current_values.boilers_switch_tank1_fill,
                empty_valve=self._current_values.boilers_switch_tank1_empty,
                boosting_supply_valve=self._current_values.boilers_switch_tank1_boosting_supply,
                boosting_return_valve=self._current_values.boilers_switch_tank1_boosting_return,
                disabled=self._parameters.tank1_disabled,
            ),
            tank2=Tank(
                fill_valve=self._current_values.boilers_switch_tank2_fill,
                empty_valve=self._current_values.boilers_switch_tank2_empty,
                boosting_supply_valve=self._current_values.boilers_switch_tank2_boosting_supply,
                boosting_return_valve=self._current_values.boilers_switch_tank2_boosting_return,
                disabled=self._parameters.tank2_disabled,
            ),
            tank3=Tank(
                fill_valve=self._current_values.boilers_switch_tank3_fill,
                empty_valve=self._current_values.boilers_switch_tank3_empty,
                boosting_supply_valve=self._current_values.boilers_switch_tank3_boosting_supply,
                boosting_return_valve=self._current_values.boilers_switch_tank3_boosting_return,
                disabled=self._parameters.tank3_disabled,
            ),
            time_fn=self._time,
        )

    @property
    def parameters(self) -> BoilersParameters:
        return self._parameters

    def update_parameters(self, parameters: BoilersParameters):
        self._parameters = parameters

    def modes(self) -> list[str]:
        return list(self._state_machine.states.keys())

    @property
    def initial_mode(self) -> BoilersControlMode:
        initial_mode: str = self._state_machine.initial  # type: ignore
        return BoilersControlMode(mode=initial_mode)

    @property
    def mode(self) -> BoilersControlMode:
        mode: str = self.state  # type: ignore
        return BoilersControlMode(mode=mode)

    def initial(self) -> ControlResult[BoilersControlValues]:
        return ControlResult(self._time(), _INITIAL_CONTROL_VALUES(self._time()))

    def control(
        self, sensor_values: BoilersSensorValues
    ) -> ControlResult[BoilersControlValues]:
        self._tanks_controller(sensor_values, self._parameters)
        self._try_boosting(sensor_values)  # type: ignore
        self._enable_filling_flow_control(sensor_values)
        self._control_filling_flow(sensor_values)

        return ControlResult(self._time(), self._current_values)

    def _lt1_sufficient_boosting_heat(self, sensor_values: BoilersSensorValues) -> bool:
        if self._tanks_controller._boosting_tank is None:
            return False

        delta = (
            sensor_values.lt1_temperature_recovery.temperature.value
            - self._tanks_controller._boosting_tank.temperature
            if self._tanks_controller._boosting_tank.temperature is not None
            else False
        )

        return (
            delta > self._parameters.boosting_delta
            and sensor_values.lt1_flow_recovery.flow.value > 0.1
        )

    def _ht_sufficient_boosting_heat(self, sensor_values: BoilersSensorValues) -> bool:
        if self._tanks_controller._boosting_tank is None:
            return False

        delta = (
            sensor_values.consumers_temperature_boosting_supply.temperature.value
            - self._tanks_controller._boosting_tank.temperature
            if self._tanks_controller._boosting_tank.temperature is not None
            else False
        )

        return (
            delta > self._parameters.boosting_delta
            and sensor_values.consumers_flow_boosting.flow.value > 0.1
        )

    def _enable_filling_flow_control(self, sensor_values: BoilersSensorValues):
        if self._tanks_controller.filling:
            for controller in [self._lt1_flow_controller, self._lt2_flow_controller]:
                if not controller.enabled():
                    controller.enable()

        if not self._lt1_heat_available(sensor_values):
            if self._lt1_flow_controller.enabled():
                self._lt1_flow_controller.disable()
                self._current_values.boilers_flowcontrol_lt1.setpoint = Stamped(
                    value=Valve.CLOSED, timestamp=self._time()
                )

        if not self._tanks_controller.filling:
            for controller in [self._lt1_flow_controller, self._lt2_flow_controller]:
                if controller.enabled():
                    controller.disable()
                self._current_values.boilers_flowcontrol_lt1.setpoint = Stamped(
                    value=Valve.CLOSED, timestamp=self._time()
                )
                self._current_values.boilers_flowcontrol_lt2.setpoint = Stamped(
                    value=Valve.CLOSED, timestamp=self._time()
                )

    def _control_filling_flow(self, sensor_values: BoilersSensorValues):
        if self._lt1_flow_controller.enabled():
            self._current_values.boilers_flowcontrol_lt1.setpoint = Stamped(
                value=self._lt1_flow_controller(
                    sensor_values.boilers_temperature_lt1_return.temperature.value
                ),
                timestamp=self._time(),
            )
        if self._lt2_flow_controller.enabled():
            self._current_values.boilers_flowcontrol_lt2.setpoint = Stamped(
                value=self._lt2_flow_controller(
                    sensor_values.boilers_temperature_lt2_return.temperature.value
                ),
                timestamp=self._time(),
            )

    def _lt1_heat_available(self, sensor_values: BoilersSensorValues) -> bool:
        return sensor_values.lt1_flow_recovery.flow.value > 0.1

    def _set_valves_to_boosting_low_temperature(
        self, sensor_values: BoilersSensorValues
    ):
        self._current_values.boilers_switch_low_temperature.setpoint = Stamped(
            value=1.0, timestamp=self._time()
        )
        self._current_values.boilers_switch_high_temperature.setpoint = Stamped(
            value=0.0, timestamp=self._time()
        )
        self._current_values.boilers_switch_heatpump.setpoint = Stamped(
            value=0.0, timestamp=self._time()
        )

    def _set_valves_to_boosting_high_temperature(
        self, sensor_values: BoilersSensorValues
    ):
        self._current_values.boilers_switch_low_temperature.setpoint = Stamped(
            value=0.0, timestamp=self._time()
        )
        self._current_values.boilers_switch_high_temperature.setpoint = Stamped(
            value=1.0, timestamp=self._time()
        )
        self._current_values.boilers_switch_heatpump.setpoint = Stamped(
            value=0.0, timestamp=self._time()
        )

    def _set_valves_to_boosting_heatpump(self, sensor_values: BoilersSensorValues):
        self._current_values.boilers_switch_low_temperature.setpoint = Stamped(
            value=0.0, timestamp=self._time()
        )
        self._current_values.boilers_switch_high_temperature.setpoint = Stamped(
            value=0.0, timestamp=self._time()
        )
        self._current_values.boilers_switch_heatpump.setpoint = Stamped(
            value=1.0, timestamp=self._time()
        )

    def _close_boosting_valves(self, sensor_values: BoilersSensorValues):
        self._current_values.boilers_switch_low_temperature.setpoint = Stamped(
            value=0.0, timestamp=self._time()
        )
        self._current_values.boilers_switch_high_temperature.setpoint = Stamped(
            value=0.0, timestamp=self._time()
        )
        self._current_values.boilers_switch_heatpump.setpoint = Stamped(
            value=0.0, timestamp=self._time()
        )

    def _activate_pump(self, sensor_values: BoilersSensorValues):
        self._current_values.boilers_pump.on = Stamped(
            value=True, timestamp=self._time()
        )

    def _deactivate_pump(self, sensor_values: BoilersSensorValues):
        self._current_values.boilers_pump.on = Stamped(
            value=False, timestamp=self._time()
        )

    def _activate_heatpump(self, sensor_values: BoilersSensorValues):
        self._current_values.boilers_heatpump.on = Stamped(
            value=True, timestamp=self._time()
        )
        self._current_values.boilers_heatpump.temperature_setpoint = Stamped(
            value=self._parameters.heatpump_temperature_setpoint, timestamp=self._time()
        )

    def _deactivate_heatpump(self, sensor_values: BoilersSensorValues):
        self._current_values.boilers_heatpump.on = Stamped(
            value=False, timestamp=self._time()
        )

    def _enable_pump_temperature_control(self, sensor_values: BoilersSensorValues):
        if not self._pump_temperature_controller.enabled():
            self._pump_temperature_controller.enable()

    def _disable_pump_temperature_control(self, sensor_values: BoilersSensorValues):
        if self._pump_temperature_controller.enabled():
            self._pump_temperature_controller.disable()

    def _enable_pump_flow_control(self, sensor_values: BoilersSensorValues):
        self._pump_flow_controller.enable()

    def _disable_pump_flow_control(self, sensor_values: BoilersSensorValues):
        self._pump_flow_controller.disable()


class BoilersAlarms(BaseAlarms):
    pass
