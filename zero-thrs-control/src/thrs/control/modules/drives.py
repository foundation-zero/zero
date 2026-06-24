from datetime import datetime
from typing import Callable, Literal

from transitions import Machine, State

from thrs.classes.control import Control, ControlMode
from thrs.control.base import ModuleDescription
from thrs.control.controllers import FlowBalanceController, PidController
from thrs.input_output.alarms import BaseAlarms
from thrs.input_output.base import Stamped, ThrsValues
from thrs.input_output.definitions.control import Pump, Valve
from thrs.input_output.definitions.units import Celsius, LMin, Ratio, Tuning
from thrs.input_output.modules.drives import DrivesControlValues, DrivesSensorValues


class DrivesControlMode(ControlMode):
    mode: str

    @property
    def is_idle(self) -> bool:
        return self.mode == "idle"

    @property
    def is_shorepower(self) -> bool:
        return self.mode == "shorepower"

    @property
    def is_propulsion(self) -> bool:
        return self.mode == "propulsion"


class DrivesControllerValues(ThrsValues):
    control_mode: DrivesControlMode


class DrivesParameters(ThrsValues):
    shorepower_maximum_supply_temperature: Celsius = 35
    propulsion_maximum_supply_temperature: Celsius = 60
    recovery_temperature: Celsius = 50
    shorepower_flow_setpoint: LMin = 20
    propulsion_drives_flow_setpoint: LMin = 30
    pump_tuning: Tuning = (0.01, 0.001, 0)
    recovery_mix_tuning: Tuning = (-0.1, -0.0005, 0)
    heat_dump_tuning: Tuning = (0.05, 0.01, 0)
    aft_flow_balance_tuning: Tuning = (0.01, 0.001, 0)
    fwd_flow_balance_tuning: Tuning = (0.01, 0.001, 0)


def _INITIAL_CONTROL_VALUES(timestamp: datetime) -> DrivesControlValues:
    return DrivesControlValues(
        drives_pump1=Pump(
            dutypoint=Stamped(value=0.0, timestamp=timestamp),
            on=Stamped(value=False, timestamp=timestamp),
        ),
        drives_pump2=Pump(
            dutypoint=Stamped(value=0.0, timestamp=timestamp),
            on=Stamped(value=False, timestamp=timestamp),
        ),
        drives_mix_exchanger=Valve(
            setpoint=Stamped(value=Valve.MIXING_A_TO_AB, timestamp=timestamp)
        ),
        drives_mix_recovery=Valve(
            setpoint=Stamped(value=Valve.MIXING_B_TO_AB, timestamp=timestamp)
        ),
        drives_flowcontrol_propdrive_aft=Valve(
            setpoint=Stamped(value=Valve.OPEN, timestamp=timestamp)
        ),
        drives_flowcontrol_propdrive_fwd=Valve(
            setpoint=Stamped(value=Valve.OPEN, timestamp=timestamp)
        ),
        drives_switch_shorepower_supply=Valve(
            setpoint=Stamped(value=Valve.CLOSED, timestamp=timestamp)
        ),
        drives_switch_shorepower_return=Valve(
            setpoint=Stamped(value=Valve.CLOSED, timestamp=timestamp)
        ),
        drives_switch_propdrive_aft1=Valve(
            setpoint=Stamped(value=Valve.OPEN, timestamp=timestamp)
        ),
        drives_switch_propdrive_aft2=Valve(
            setpoint=Stamped(value=Valve.OPEN, timestamp=timestamp)
        ),
        drives_switch_propdrive_fwd1=Valve(
            setpoint=Stamped(value=Valve.OPEN, timestamp=timestamp)
        ),
        drives_switch_propdrive_fwd2=Valve(
            setpoint=Stamped(value=Valve.OPEN, timestamp=timestamp)
        ),
    )


class DrivesControl(
    Control[
        DrivesSensorValues,
        DrivesControlValues,
        DrivesParameters,
        DrivesControllerValues,
    ]
):
    def __init__(
        self, parameters: DrivesParameters, time_fn: Callable[[], datetime]
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
                    self._disable_heat_dump,
                    self._disable_recovery_mix,
                ],
                on_exit=[
                    self._activate_pump,
                    self._enable_heat_dump,
                    self._enable_recovery_mix,
                ],
            ),
            State(
                name="shorepower",
                on_enter=[
                    self._set_valves_to_shore_power,
                    self._enable_pump_control_shorepower,
                ],
                on_exit=[self._disable_pump_control_shorepower],
            ),
            State(
                name="propulsion",
                on_enter=[self._set_valves_to_propulsion, self._enable_flow_balancing],
                on_exit=[self._disable_flow_balancing],
            ),
        ]

        self._transitions = [
            {
                "trigger": "_check_shorepower",
                "source": "idle",
                "dest": "shorepower",
                "conditions": self._shorepower_on,
            },
            {
                "trigger": "_check_thrusters",
                "source": "idle",
                "dest": "propulsion",
                "conditions": self._propdrive_active,
            },
            {
                "trigger": "_check_shorepower",
                "source": "shorepower",
                "dest": "idle",
                "conditions": lambda sensor_values: (
                    not self._shorepower_on(sensor_values)
                ),
            },
            {
                "trigger": "_check_thrusters",
                "source": "propulsion",
                "dest": "idle",
                "conditions": lambda sensor_values: (
                    not self._propdrive_active(sensor_values)
                ),
            },
        ]

        self._state_machine = Machine(
            model=self,
            states=self._states,
            transitions=self._transitions,
            initial="idle",
        )

        self._heat_dump_controller = PidController[Ratio, Celsius](
            initial=self._current_values.drives_mix_exchanger.setpoint.value,
            setpoint=lambda: (
                self._parameters.propulsion_maximum_supply_temperature
                if self.state == "propulsion"  # type: ignore
                else self._parameters.shorepower_maximum_supply_temperature
            ),
            tuning=lambda: self._parameters.heat_dump_tuning,
            time_fn=self._time,
        )

        self._recovery_mix_controller = PidController[Ratio, Celsius](
            initial=self._current_values.drives_mix_recovery.setpoint.value,
            setpoint=lambda: self._parameters.recovery_temperature,
            tuning=lambda: self._parameters.recovery_mix_tuning,
            time_fn=self._time,
        )

        self._pump_controller_shorepower = PidController[Ratio, LMin](
            initial=self._current_values.drives_pump1.dutypoint.value,
            setpoint=lambda: self._parameters.shorepower_flow_setpoint,
            tuning=lambda: self._parameters.pump_tuning,
            time_fn=self._time,
        )

        self._pump_controller_propulsion = PidController[Ratio, LMin](
            initial=self._current_values.drives_pump1.dutypoint.value,
            setpoint=0,  # gets overriden by flow balance controller
            tuning=lambda: self._parameters.pump_tuning,
            time_fn=self._time,
        )

        self._aft_flow_controller = PidController[Ratio, LMin](
            initial=self._current_values.drives_flowcontrol_propdrive_aft.setpoint.value,
            setpoint=lambda: self._parameters.propulsion_drives_flow_setpoint,
            tuning=lambda: self._parameters.aft_flow_balance_tuning,
            time_fn=self._time,
        )

        self._fwd_flow_controller = PidController[Ratio, LMin](
            initial=self._current_values.drives_flowcontrol_propdrive_fwd.setpoint.value,
            setpoint=lambda: self._parameters.propulsion_drives_flow_setpoint,
            tuning=lambda: self._parameters.fwd_flow_balance_tuning,
            time_fn=self._time,
        )

        self._most_recently_active_pump: None | Literal["pump1", "pump2"] = None
        self._active_pump: None | Pump = None  # TODO: make into controller

        self._flow_balance_controller = FlowBalanceController(
            [
                self._current_values.drives_flowcontrol_propdrive_aft,
                self._current_values.drives_flowcontrol_propdrive_fwd,
            ],
            [self._aft_flow_controller, self._fwd_flow_controller],
            self._active_pump,
            self._pump_controller_propulsion,
            self._time,
        )

    @property
    def parameters(self) -> DrivesParameters:
        return self._parameters

    def update_parameters(self, parameters: DrivesParameters):
        self._parameters = parameters

    def modes(self) -> list[str]:
        return list(self._state_machine.states.keys())

    def initial(self) -> tuple[DrivesControlValues, DrivesControllerValues]:
        initial_mode: str = self._state_machine.initial  # type: ignore
        control_mode = DrivesControlMode(mode=initial_mode)

        return (
            _INITIAL_CONTROL_VALUES(self._time()),
            DrivesControllerValues(control_mode=control_mode),
        )

    def control(
        self, sensor_values: DrivesSensorValues
    ) -> tuple[DrivesControlValues, DrivesControllerValues]:
        if not DrivesControlMode(mode=self.state).is_propulsion:  # type: ignore
            self._check_shorepower(sensor_values)  # type: ignore
        if not DrivesControlMode(mode=self.state).is_shorepower:  # type: ignore
            self._check_thrusters(sensor_values)  # type: ignore
        self._control_heat_dump(sensor_values)
        self._control_flow_balance(sensor_values)
        self._control_pump_shorepower(sensor_values)
        self._control_recovery_mix(sensor_values)

        if DrivesControlMode(mode=self.state).is_shorepower:  # type: ignore
            self._control_pump_shorepower(sensor_values)
        elif DrivesControlMode(mode=self.state).is_propulsion:  # type: ignore
            self._control_flow_balance(sensor_values)

        mode: str = self.state  # type: ignore
        control_mode = DrivesControlMode(mode=mode)

        return (self._current_values, DrivesControllerValues(control_mode=control_mode))

    def _shorepower_on(self, sensor_values: DrivesSensorValues) -> bool:
        return sensor_values.drives_shorepower.active.value

    def _propdrive_active(self, sensor_values: DrivesSensorValues) -> bool:
        return (
            sensor_values.drives_propdrive_aft1.active.value
            or sensor_values.drives_propdrive_aft2.active.value
            or sensor_values.drives_propdrive_fwd1.active.value
            or sensor_values.drives_propdrive_fwd2.active.value
        )

    def _enable_recovery_mix(self, sensor_values: DrivesSensorValues):
        self._recovery_mix_controller.enable()

    def _disable_recovery_mix(self, sensor_values: DrivesSensorValues):
        self._recovery_mix_controller.disable()

    def _control_recovery_mix(self, sensor_values: DrivesSensorValues):
        if self._recovery_mix_controller.enabled():
            self._current_values.drives_mix_recovery.setpoint = Stamped(
                value=self._recovery_mix_controller(
                    sensor_values.drives_temperature_recovery.temperature.value
                ),
                timestamp=self._time(),
            )

    def _enable_heat_dump(self, sensor_values: DrivesSensorValues):
        self._heat_dump_controller.enable()

    def _disable_heat_dump(self, sensor_values: DrivesSensorValues):
        self._heat_dump_controller.disable()

    def _control_heat_dump(self, sensor_values: DrivesSensorValues):
        if self._heat_dump_controller.enabled():
            self._current_values.drives_mix_exchanger.setpoint = Stamped(
                value=self._heat_dump_controller(
                    sensor_values.drives_temperature_supply.temperature.value
                ),
                timestamp=self._time(),
            )

    def _enable_pump_control_propulsion(self, sensor_values: DrivesSensorValues):
        self._pump_controller_propulsion.enable()

    def _disable_pump_control_propulsion(self, sensor_values: DrivesSensorValues):
        self._pump_controller_propulsion.disable()

    def _enable_flow_balancing(self, sensor_values: DrivesSensorValues):
        self._flow_balance_controller.enable(
            [
                sensor_values.drives_propdrive_aft1.active.value
                or sensor_values.drives_propdrive_aft2.active.value,
                sensor_values.drives_propdrive_fwd1.active.value
                or sensor_values.drives_propdrive_fwd2.active.value,
            ]
        )

    def _disable_flow_balancing(self, sensor_values: DrivesSensorValues):
        self._flow_balance_controller.disable()

    def _control_flow_balance(self, sensor_values: DrivesSensorValues):
        if self._flow_balance_controller.enabled:
            self._flow_balance_controller.set_pump(self._active_pump)
            self._flow_balance_controller(
                [
                    sensor_values.drives_flow_propdrive_aft1.flow.value
                    + sensor_values.drives_flow_propdrive_aft2.flow.value,
                    sensor_values.drives_flow_propdrive_fwd1.flow.value
                    + sensor_values.drives_flow_propdrive_fwd2.flow.value,
                ]
            )

    def _enable_pump_control_shorepower(self, sensor_values: DrivesSensorValues):
        self._pump_controller_shorepower.enable()

    def _disable_pump_control_shorepower(self, sensor_values: DrivesSensorValues):
        self._pump_controller_shorepower.disable()

    def _control_pump_shorepower(self, sensor_values: DrivesSensorValues):
        if self._pump_controller_shorepower.enabled():
            self._current_values.drives_pump1.dutypoint = Stamped(
                value=self._pump_controller_shorepower(
                    sensor_values.drives_flow_shorepower.flow.value
                ),
                timestamp=self._time(),
            )
            self._current_values.drives_pump1.on = Stamped(
                value=True, timestamp=self._time()
            )

    def _activate_pump(self, sensor_values: DrivesSensorValues):
        if self._active_pump:
            raise Warning("A pump was already active upon selecting")
        else:
            if self._most_recently_active_pump == "pump1":
                self._most_recently_active_pump = "pump2"
                self._active_pump = self._current_values.drives_pump2

            else:
                self._most_recently_active_pump = "pump1"
                self._active_pump = self._current_values.drives_pump2

        self._active_pump.on = Stamped(value=True, timestamp=self._time())

    def _deactivate_pump(self, sensor_values: DrivesSensorValues):
        if not self._active_pump:
            raise Warning("No pump active when deactivating")

        self._active_pump.on = Stamped(value=False, timestamp=self._time())
        self._active_pump.dutypoint = Stamped(value=0, timestamp=self._time())
        self._active_pump = None

    def _set_valves_to_shore_power(self, sensor_values: DrivesSensorValues):
        self._current_values.drives_switch_shorepower_supply.setpoint = Stamped(
            value=Valve.OPEN, timestamp=self._time()
        )
        self._current_values.drives_switch_shorepower_return.setpoint = Stamped(
            value=Valve.OPEN, timestamp=self._time()
        )
        self._current_values.drives_switch_propdrive_aft1.setpoint = Stamped(
            value=Valve.CLOSED, timestamp=self._time()
        )

        self._current_values.drives_switch_propdrive_aft2.setpoint = Stamped(
            value=Valve.CLOSED, timestamp=self._time()
        )

        self._current_values.drives_switch_propdrive_fwd1.setpoint = Stamped(
            value=Valve.CLOSED, timestamp=self._time()
        )

        self._current_values.drives_switch_propdrive_fwd2.setpoint = Stamped(
            value=Valve.CLOSED, timestamp=self._time()
        )

    def _set_valves_to_propulsion(self, sensor_values: DrivesSensorValues):
        self._current_values.drives_switch_shorepower_supply.setpoint = Stamped(
            value=Valve.CLOSED, timestamp=self._time()
        )
        self._current_values.drives_switch_shorepower_return.setpoint = Stamped(
            value=Valve.CLOSED, timestamp=self._time()
        )
        self._current_values.drives_switch_propdrive_aft1.setpoint = Stamped(
            value=Valve.OPEN, timestamp=self._time()
        )

        self._current_values.drives_switch_propdrive_aft2.setpoint = Stamped(
            value=Valve.OPEN, timestamp=self._time()
        )

        self._current_values.drives_switch_propdrive_fwd1.setpoint = Stamped(
            value=Valve.OPEN, timestamp=self._time()
        )

        self._current_values.drives_switch_propdrive_fwd2.setpoint = Stamped(
            value=Valve.OPEN, timestamp=self._time()
        )


class DrivesAlarms(BaseAlarms):
    pass


DRIVES_MODULE_DESCRIPTION = ModuleDescription(
    DrivesSensorValues,
    DrivesControlValues,
    DrivesParameters,
    DrivesControl,
    DrivesControllerValues,
    DrivesAlarms,
)
