from datetime import datetime
from typing import Callable

from transitions import Machine, State
from thrs.classes.control import Control, ControlResult
from thrs.control.controllers import Controller, FlowDistributionController
from thrs.input_output.base import Stamped, ThrsModel
from thrs.input_output.definitions.units import Celsius, Full, LMin, Ratio, Tuning
from thrs.input_output.modules.boilers import BoilersControlValues, BoilersSensorValues

from thrs.input_output.definitions import control


class BoilersParameters(ThrsModel):
    heatpump_flow_setpoint: LMin = 25
    boosting_temperature_setpoint: Celsius = 55
    tank_temperature_setpoint: Celsius = 50
    propdrive_shore_flow_ratio_setpoint: Ratio = 0.5
    converters_flow_ratio_setpoint: Ratio = 0.5
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
        self._boosting = False
        self._filling = False
        self._in_use = False
        self._full = None
        self._temperature = None

    @property
    def full(self) -> Full | None:
        return self._full

    @full.setter
    def full(self, full: Full):
        self._full = full

    @property
    def temperature(self) -> Celsius | None:
        return self._temperature

    @temperature.setter
    def temperature(self, temperature: Celsius):
        self._temperature = temperature

    def above_boosting_setpoint(self, parameters: BoilersParameters) -> bool:
        if self._temperature is None:
            return False
        return self._temperature >= parameters.boosting_temperature_setpoint

    def below_tank_setpoint(self, parameters: BoilersParameters) -> bool:
        if self._temperature is None:
            return False
        return self._temperature < parameters.tank_temperature_setpoint

    def standby(self, parameters: BoilersParameters) -> bool:
        if self._full is None:
            return False
        return (
            not self._disabled
            and not self._in_use
            and not self._boosting
            and not self._filling
            and self._full
            and not self.below_tank_setpoint(parameters)
        )

    @property
    def disabled(self) -> bool:
        return self._disabled

    @disabled.setter
    def disabled(self, value: bool):
        self._disabled = value

    def enable(self):
        self._disabled = False

    @property
    def boosting(self) -> bool:
        return self._boosting

    def boost(self, time: Callable[[], datetime]):
        self._boosting = True
        self._boosting_supply_valve.setpoint = Stamped(value=1.0, timestamp=time())
        self._boosting_return_valve.setpoint = Stamped(value=1.0, timestamp=time())

    def stop_boosting(self, time: Callable[[], datetime]):
        self._boosting = False
        self._boosting_supply_valve.setpoint = Stamped(value=0.0, timestamp=time())
        self._boosting_return_valve.setpoint = Stamped(value=0.0, timestamp=time())

    def boostable(self, parameters: BoilersParameters) -> bool:
        if self._in_use or self._full is None:
            return False
        return (
            not self._disabled
            and not self._in_use
            and self._full
            and self.below_tank_setpoint(parameters)
        )

    @property
    def filling(self) -> bool:
        return self._filling

    def fill(self, time: Callable[[], datetime]):
        self._filling = True
        self._fill_valve.setpoint = Stamped(value=1.0, timestamp=time())

    def stop_filling(self, time: Callable[[], datetime]):
        self._filling = False
        self._fill_valve.setpoint = Stamped(value=0.0, timestamp=time())

    def fillable(self) -> bool:
        return not self._disabled and not self._in_use and not self._full

    @property
    def in_use(self) -> bool:
        return self._in_use

    def use(self, time: Callable[[], datetime]):
        self._in_use = True
        self._empty_valve.setpoint = Stamped(value=1.0, timestamp=time())

    def stop_use(self, time: Callable[[], datetime]):
        self._in_use = False
        self._empty_valve.setpoint = Stamped(value=0.0, timestamp=time())


class TanksController:
    def __init__(
        self, tank1: Tank, tank2: Tank, tank3: Tank, time_fn: Callable[[], datetime]
    ):
        self._time = time_fn
        self._tank1 = tank1
        self._tank2 = tank2
        self._tank3 = tank3
        self._tanks = [self._tank1, self._tank2, self._tank3]
        self._filling_tank: Tank | None = None
        self._boosting_tank: Tank | None = None
        self._tank_in_use: Tank | None = None

        # always 1 tank in use, two left
        # case 1: none full -> fill one of them
        # case 2: one full -> fill the other, possible boost the one
        # case 3: two full -> boost the lowest temperatur one..

        # if one is disabled:
        # case 1: full -> possibly boost
        # case 2: not full -> fill it

    def _update_tank_states(
        self, sensor_values: BoilersSensorValues, parameters: BoilersParameters
    ):
        self._tank1.full = sensor_values.boilers_level_tank1.full.value
        self._tank1.temperature = (
            sensor_values.boilers_temperature_tank1.temperature.value
        )
        self._tank1.disabled = parameters.tank1_disabled
        self._tank2.full = sensor_values.boilers_level_tank2.full.value
        self._tank2.temperature = (
            sensor_values.boilers_temperature_tank2.temperature.value
        )
        self._tank2.disabled = parameters.tank2_disabled
        self._tank3.full = sensor_values.boilers_level_tank3.full.value
        self._tank3.temperature = (
            sensor_values.boilers_temperature_tank3.temperature.value
        )
        self._tank3.disabled = parameters.tank3_disabled

    def _select_tank_in_use(self, parameters: BoilersParameters):
        # TODO: when to switch to other tank? how do we know when it's empty
        if self._tank_in_use is None:
            self._tank_in_use = next(
                (tank for tank in self._tanks if tank.standby(parameters)), None
            )
            if self._tank_in_use is not None:
                self._tank_in_use.use(self._time)

    def _select_filling_tank(self):
        # stop filling when full
        if self._filling_tank is not None and self._filling_tank.full:
            self._filling_tank.stop_filling(self._time)
            self._filling_tank = None

        # choose new tank to fill
        if self._filling_tank is None:
            self._filling_tank = next(
                (tank for tank in self._tanks if tank.fillable()),
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
                for tank in self._tanks
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
        self._select_filling_tank()
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

        self._propdrive_shore_flow_controller = Controller[Ratio, LMin](
            _INITIAL_CONTROL_VALUES.boilers_flowcontrol_propdrive_shore.setpoint.value,
            0,
            parameters.propdrive_shore_flow_tuning,
            self._time,
        )

        self._converters_flow_controller = Controller[Ratio, LMin](
            _INITIAL_CONTROL_VALUES.boilers_flowcontrol_converters.setpoint.value,
            0,
            parameters.converters_flow_tuning,
            self._time,
        )
        self._flow_distribution_controller = FlowDistributionController(
            [
                self._current_values.boilers_flowcontrol_propdrive_shore,
                self._current_values.boilers_flowcontrol_converters,
            ],
            [
                self._propdrive_shore_flow_controller,
                self._converters_flow_controller,
            ],
        )
        self._flow_distribution_controller.set_active_valves([True, True])

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
        self._control_flow_distribution(sensor_values)

        return ControlResult(self._time(), self._current_values)

    def _control_flow_distribution(self, sensor_values: BoilersSensorValues):
        self._flow_distribution_controller.set_ratios(
            [
                self._parameters.propdrive_shore_flow_ratio_setpoint,
                self._parameters.converters_flow_ratio_setpoint,
            ]
        )
        self._flow_distribution_controller(
            [
                sensor_values.boilers_flow_propdrive_shore.flow.value,
                sensor_values.boilers_flow_converters.flow.value,
            ]
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
