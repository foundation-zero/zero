from datetime import datetime
from typing import Callable

from transitions import Machine, State
from thrs.classes.control import Control, ControlResult
from thrs.control.controllers import Controller
from thrs.input_output.base import Stamped, ThrsModel
from thrs.input_output.definitions.units import Celsius, LMin, Liter, Ratio, Tuning
from thrs.input_output.modules.boilers import BoilersControlValues, BoilersSensorValues

from thrs.input_output.definitions import control


class BoilersParameters(ThrsModel):
    heatpump_flow_setpoint: LMin = 25
    boosting_temperature_setpoint: Celsius = 55
    tank_temperature_setpoint: Celsius = 50
    propdrive_shore_flowcontrol_minimum_setpoint: Ratio = 0.1  # need flow to have temp measurement available, and need these minima are needed to control the minimum filling flow
    converters_flowcontrol_minimum_setpoint: Ratio = 0.1
    filling_temperature_setpoint: Celsius = 40
    minimum_tank_level: Liter = 30
    maximum_tank_level: Liter = 260
    tank1_disabled: bool = False
    tank2_disabled: bool = False
    tank3_disabled: bool = False
    pump_temperature_tuning: Tuning = (-0.01, -0.001, 0.0)
    pump_flow_tuning: Tuning = (0.01, 0.001, 0.0)
    converters_flow_tuning: Tuning = (0.01, 0.001, 0.0)
    propdrive_shore_flow_tuning: Tuning = (0.01, 0.001, 0.0)


_ZERO_TIME = datetime.fromtimestamp(0)
_INITIAL_CONTROL_VALUES = BoilersControlValues(
    boilers_pump=control.Pump(
        dutypoint=Stamped(value=0.0, timestamp=_ZERO_TIME),
        on=Stamped(value=False, timestamp=_ZERO_TIME),
    ),
    boilers_heatpump=control.HeatPump(),
    boilers_flowcontrol_converters=control.Valve(
        setpoint=Stamped(value=0.5, timestamp=_ZERO_TIME)
    ),
    boilers_flowcontrol_propdrive_shore=control.Valve(
        setpoint=Stamped(value=0.5, timestamp=_ZERO_TIME)
    ),
    boilers_switch_tank3_fill=control.Valve(
        setpoint=Stamped(value=0.0, timestamp=_ZERO_TIME)
    ),
    boilers_switch_tank3_boosting_return=control.Valve(
        setpoint=Stamped(value=0.0, timestamp=_ZERO_TIME)
    ),
    boilers_switch_tank3_empty=control.Valve(
        setpoint=Stamped(value=0.0, timestamp=_ZERO_TIME)
    ),
    boilers_switch_tank3_boosting_supply=control.Valve(
        setpoint=Stamped(value=0.0, timestamp=_ZERO_TIME)
    ),
    boilers_switch_tank2_fill=control.Valve(
        setpoint=Stamped(value=0.0, timestamp=_ZERO_TIME)
    ),
    boilers_switch_tank2_boosting_return=control.Valve(
        setpoint=Stamped(value=0.0, timestamp=_ZERO_TIME)
    ),
    boilers_switch_tank2_empty=control.Valve(
        setpoint=Stamped(value=0.0, timestamp=_ZERO_TIME)
    ),
    boilers_switch_tank2_boosting_supply=control.Valve(
        setpoint=Stamped(value=0.0, timestamp=_ZERO_TIME)
    ),
    boilers_switch_tank1_fill=control.Valve(
        setpoint=Stamped(value=0.0, timestamp=_ZERO_TIME)
    ),
    boilers_switch_tank1_boosting_return=control.Valve(
        setpoint=Stamped(value=0.0, timestamp=_ZERO_TIME)
    ),
    boilers_switch_tank1_empty=control.Valve(
        setpoint=Stamped(value=0.0, timestamp=_ZERO_TIME)
    ),
    boilers_switch_tank1_boosting_supply=control.Valve(
        setpoint=Stamped(value=0.0, timestamp=_ZERO_TIME)
    ),
    boilers_switch_low_temperature=control.Valve(
        setpoint=Stamped(value=0.0, timestamp=_ZERO_TIME)
    ),
    boilers_switch_heatpump=control.Valve(
        setpoint=Stamped(value=0.0, timestamp=_ZERO_TIME)
    ),
    boilers_switch_high_temperature=control.Valve(
        setpoint=Stamped(value=0.0, timestamp=_ZERO_TIME)
    ),
)


class Tank:
    def __init__(
        self,
        fill_valve: control.Valve,
        empty_valve: control.Valve,
        boosting_supply_valve: control.Valve,
        boosting_return_valve: control.Valve,
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

    def above_boosting_setpoint(self, parameters: BoilersParameters) -> bool:
        if self._temperature is None:
            return False
        return self._temperature >= parameters.boosting_temperature_setpoint

    def below_tank_setpoint(self, parameters: BoilersParameters) -> bool:
        if self._temperature is None:
            return False
        return self._temperature < parameters.tank_temperature_setpoint

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
            and not self.below_tank_setpoint(parameters)
        )

    def boost(self, time: Callable[[], datetime]):
        self._boosting_supply_valve.setpoint = Stamped(value=1.0, timestamp=time())
        self._boosting_return_valve.setpoint = Stamped(value=1.0, timestamp=time())

    def stop_boosting(self, time: Callable[[], datetime]):
        self._boosting_supply_valve.setpoint = Stamped(value=0.0, timestamp=time())
        self._boosting_return_valve.setpoint = Stamped(value=0.0, timestamp=time())

    def boostable(self, parameters: BoilersParameters) -> bool:
        return (
            not self.disabled
            and self.full(parameters)
            and self.below_tank_setpoint(parameters)
        )

    def fill(self, time: Callable[[], datetime]):
        self._fill_valve.setpoint = Stamped(value=1.0, timestamp=time())

    def stop_filling(self, time: Callable[[], datetime]):
        self._fill_valve.setpoint = Stamped(value=0.0, timestamp=time())

    def fillable(self, parameters: BoilersParameters) -> bool:
        return not self.disabled and not self.full(parameters)

    def use(self, time: Callable[[], datetime]):
        self._empty_valve.setpoint = Stamped(value=1.0, timestamp=time())

    def stop_use(self, time: Callable[[], datetime]):
        self._empty_valve.setpoint = Stamped(value=0.0, timestamp=time())


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
        # zip with boilers levels and temperatures
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
        # stop using when empty
        if self._tank_in_use is not None and self._tank_in_use.empty(parameters):
            self._tank_in_use.stop_use(self._time)
            self._tank_in_use = None

        if self._tank_in_use is None:
            self._tank_in_use = next(
                (tank for tank in self.available_tanks if tank.standby(parameters)),
                None,
            )
            if self._tank_in_use is not None:
                self._tank_in_use.use(self._time)

    def _select_filling_tank(self, parameters: BoilersParameters):
        # stop filling when full
        if self._filling_tank is not None and self._filling_tank.full(parameters):
            self._filling_tank.stop_filling(self._time)
            self._filling_tank = None

        # choose new tank to fill
        if self._filling_tank is None:
            self._filling_tank = next(
                (tank for tank in self.available_tanks if tank.fillable(parameters)),
                None,
            )
            if self._filling_tank is not None:
                self._filling_tank.fill(self._time)

    def _select_boosting_tank(self, parameters: BoilersParameters):
        # stop boosting when temp reached
        if (
            self._boosting_tank is not None
            and self._boosting_tank.above_boosting_setpoint(parameters)
        ):
            self._boosting_tank.stop_boosting(self._time)
            self._boosting_tank = None

        # choose new tank to boost
        # TODO: add logic for stopping boost based on deltaT? how to deal with temperature supply..switch to another tank to boost with lower temperature? depends on the boosting temp available in each loop..for now, we assume to be able to get to 55 for all..
        # TODO: should we be choosing the highest temperature tank that is below setpoint? this depends on available temperature...
        # TODO: boosting depends on state machine...should we open the valves when boosting is inactive? Maybe only open boost valves of the boosting tank when mode is engaged?
        if self._boosting_tank is None:
            boostable_tanks = [
                tank
                for tank in self.available_tanks
                if tank.boostable(
                    parameters
                )  # start boosting if below tank temperature setpoint, stop boosting if above boosting temperature setpoint
            ]  # TODO: this depends on available supply temperature vs current tank temperature
            if boostable_tanks:
                self._boosting_tank = max(
                    boostable_tanks,
                    key=lambda tank: tank.temperature
                    if tank.temperature is not None
                    else 0,  # select hottest tank or coldest tank?
                )
                self._boosting_tank.boost(self._time)

    def __call__(
        self, sensor_values: BoilersSensorValues, parameters: BoilersParameters
    ):
        self._update_tank_states(sensor_values, parameters)
        self._select_tank_in_use(parameters)
        self._select_filling_tank(parameters)
        self._select_boosting_tank(parameters)


class BoilersControl(
    Control[BoilersSensorValues, BoilersControlValues, BoilersParameters]
):
    def __init__(
        self, parameters: BoilersParameters, time_fn: Callable[[], datetime]
    ) -> None:
        self._parameters = parameters
        self._time = time_fn
        self._current_values = _INITIAL_CONTROL_VALUES.model_copy(deep=True)

        self.states = [
            State(
                name="idle",
                on_enter=[self._deactivate_pump],
                on_exit=[self._activate_pump],
            ),
            State(
                name="boosting_low_temperature",
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
            ),
            State(
                name="boosting_heatpump",
                on_enter=[
                    self._set_valves_to_boosting_heatpump,
                    self._enable_pump_flow_control,
                ],
            ),
        ]
        # TODO: we want to prioritize low temp boosting, then high temp boosting, then heatpump boosting
        # TODO: when should heat pump boosting be used? when there is demand and no other heat available? or wait for heat? <- maybe use a heatpump_boosting_enabled parameter. Or let it depend on whether there is a tank standby or not...
        # TODO: should the choosing between boosting sources logic be in the high over control? we need info on the availability of HT and LT heat..
        # We let the 'demand' logic be handled by the tank selection...if a boosting_tank is selected, then the state machine should handle the 'supply'
        self.transitions = [
            {
                "trigger": "_try_boosting",
                "source": "idle",
                "dest": "boosting_low_temperature",
                "conditions": [
                    lambda sensor_values: self._tanks_controller._filling_tank is None,
                    lambda sensor_values: self._tanks_controller._boosting_tank
                    is not None,
                ],
            },  # TODO: low level heat must be available
            {
                "trigger": "_try_boosting",
                "source": "idle",
                "dest": "boosting_high_temperature",
                "conditions": lambda sensor_values: self._tanks_controller._boosting_tank
                is not None,
            },  # high temp is available
            {
                "trigger": "_try_boosting",
                "source": "idle",
                "dest": "boosting_heatpump",
                "conditions": lambda sensor_values: self._tanks_controller._boosting_tank
                is not None,
            },  # using electricity is worth it
            {
                "trigger": "_try_boosting",
                "source": [
                    "boosting_low_temperature",
                    "boosting_high_temperature",
                    "boosting_heatpump",
                ],
                "dest": "idle",
                "conditions": lambda sensor_values: self._tanks_controller._boosting_tank
                is None,
            },
        ]
        self.state_machine = Machine(
            model=self,
            states=self.states,
            transitions=self.transitions,
            initial="idle",
        )

        self._pump_temperature_controller = Controller[Ratio, Celsius](
            _INITIAL_CONTROL_VALUES.boilers_pump.dutypoint.value,
            0,
            parameters.pump_temperature_tuning,
            self._time,
        )

        self._pump_flow_controller = Controller[Ratio, LMin](
            _INITIAL_CONTROL_VALUES.boilers_pump.dutypoint.value,
            0,
            parameters.pump_flow_tuning,
            self._time,
        )

        self._propdrive_shore_flow_controller = Controller[Ratio, Celsius](
            _INITIAL_CONTROL_VALUES.boilers_flowcontrol_propdrive_shore.setpoint.value,
            parameters.filling_temperature_setpoint,
            parameters.propdrive_shore_flow_tuning,
            self._time,
            (parameters.propdrive_shore_flowcontrol_minimum_setpoint, 1.0),
        )

        self._propdrive_shore_flow_controller.enable()

        self._converters_flow_controller = Controller[Ratio, Celsius](
            _INITIAL_CONTROL_VALUES.boilers_flowcontrol_converters.setpoint.value,
            parameters.filling_temperature_setpoint,
            parameters.converters_flow_tuning,
            self._time,
            (parameters.converters_flowcontrol_minimum_setpoint, 1.0),
        )

        self._converters_flow_controller.enable()

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

    def initial(self) -> ControlResult[BoilersControlValues]:
        return ControlResult(self._time(), self._current_values)

    def control(
        self, sensor_values: BoilersSensorValues
    ) -> ControlResult[BoilersControlValues]:
        self._tanks_controller(sensor_values, self._parameters)
        self._try_boosting(sensor_values)  # type: ignore
        self._control_filling_flow(sensor_values)

        return ControlResult(self._time(), self._current_values)

    def _control_filling_flow(self, sensor_values: BoilersSensorValues):
        self._propdrive_shore_flow_controller(
            sensor_values.boilers_temperature_propdrive_shore_return.temperature.value
        )
        self._converters_flow_controller(
            sensor_values.boilers_temperature_converters_return.temperature.value
        )

    def _set_valves_to_boosting_low_temperature(self):
        self._current_values.boilers_switch_low_temperature.setpoint = Stamped(
            value=1.0, timestamp=self._time()
        )
        self._current_values.boilers_switch_high_temperature.setpoint = Stamped(
            value=0.0, timestamp=self._time()
        )
        self._current_values.boilers_switch_heatpump.setpoint = Stamped(
            value=0.0, timestamp=self._time()
        )

    def _set_valves_to_boosting_high_temperature(self):
        self._current_values.boilers_switch_low_temperature.setpoint = Stamped(
            value=0.0, timestamp=self._time()
        )
        self._current_values.boilers_switch_high_temperature.setpoint = Stamped(
            value=1.0, timestamp=self._time()
        )
        self._current_values.boilers_switch_heatpump.setpoint = Stamped(
            value=0.0, timestamp=self._time()
        )

    def _set_valves_to_boosting_heatpump(self):
        self._current_values.boilers_switch_low_temperature.setpoint = Stamped(
            value=0.0, timestamp=self._time()
        )
        self._current_values.boilers_switch_high_temperature.setpoint = Stamped(
            value=0.0, timestamp=self._time()
        )
        self._current_values.boilers_switch_heatpump.setpoint = Stamped(
            value=1.0, timestamp=self._time()
        )

    def _activate_pump(self):
        self._current_values.boilers_pump.on = Stamped(
            value=True, timestamp=self._time()
        )

    def _deactivate_pump(self):
        self._current_values.boilers_pump.on = Stamped(
            value=False, timestamp=self._time()
        )

    def _enable_pump_temperature_control(self):
        self._pump_temperature_controller.enable()

    def _disable_pump_temperature_control(self):
        self._pump_temperature_controller.disable()

    def _enable_pump_flow_control(self):
        self._pump_flow_controller.enable()

    def _disable_pump_flow_control(self):
        self._pump_flow_controller.disable()
