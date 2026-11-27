from collections.abc import Callable
from datetime import datetime
from typing import Literal

from statemachine import State, StateChart

from thrs.classes.control import Control
from thrs.control.controllers import FlowBalanceController, PidController
from thrs.control.modules.drives.io import DrivesControlValues, DrivesSensorValues
from thrs.control.modules.drives.state import (
    DrivesControllerState,
    DrivesControlMode,
    DrivesParameters,
)
from thrs.input_output.alarms import BaseAlarms
from thrs.input_output.base import Stamped
from thrs.input_output.definitions.control import Pump, Valve
from thrs.input_output.definitions.units import Celsius, LMin, Ratio
from thrs.orchestration.module import ModuleDescription


class _DrivesStateMachine(StateChart["DrivesControl"]):
    """Each event takes the first of its transitions whose condition holds."""

    # An error in a guard or action raises instead of becoming an unhandled event.
    catch_errors_as_events = False

    idle = State(
        initial=True,
        enter=["_deactivate_pump", "_disable_heat_dump", "_disable_recovery_mix"],
        exit=["_activate_pump", "_enable_heat_dump", "_enable_recovery_mix"],
    )
    shorepower = State(
        enter=["_set_valves_to_shore_power", "_enable_pump_control_shorepower"],
        exit="_disable_pump_control_shorepower",
    )
    propulsion = State(
        enter=["_set_valves_to_propulsion", "_enable_flow_balancing"],
        exit="_disable_flow_balancing",
    )

    check_shorepower = shorepower.from_(idle, cond="_shorepower_on") | idle.from_(
        shorepower, cond="not _shorepower_on"
    )
    check_thrusters = propulsion.from_(idle, cond="_propdrive_active") | idle.from_(
        propulsion, cond="not _propdrive_active"
    )


class DrivesControl(
    Control[
        DrivesSensorValues,
        DrivesControlValues,
        DrivesParameters,
        DrivesControlMode,
        DrivesControllerState,
    ]
):
    def __init__(
        self,
        parameters: DrivesParameters,
        time_fn: Callable[[], datetime],
    ) -> None:
        self._parameters = parameters
        self._time = time_fn
        self._current_values = DrivesControlValues.initial(self._time())

        # Starting with a mode set skips idle's enter actions: the first outputs are
        # the initial control values, and _deactivate_pump needs an active pump.
        self._state: str = _DrivesStateMachine.idle.value
        self._state_machine = _DrivesStateMachine(model=self, state_field="_state")
        self._init_controllers()

    def _init_controllers(self):
        self._heat_dump_controller = PidController[Ratio, Celsius](
            initial=self._current_values.drives_mix_exchanger.setpoint.value,
            setpoint=lambda: (
                self._parameters.propulsion_maximum_supply_temperature
                if self.mode.is_propulsion
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
            output_limits=(0.1, 1),
        )

        self._pump_controller_propulsion = PidController[Ratio, LMin](
            initial=self._current_values.drives_pump1.dutypoint.value,
            setpoint=0,  # gets overriden by flow balance controller
            tuning=lambda: self._parameters.pump_tuning,
            time_fn=self._time,
            output_limits=(0.1, 1),
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

        self._most_recently_active_pump: Literal["pump1", "pump2"] | None = None
        self._active_pump: Pump | None = None  # TODO: make into controller

        self._flow_balance_controller = FlowBalanceController(
            [
                self._current_values.drives_flowcontrol_propdrive_aft,
                self._current_values.drives_flowcontrol_propdrive_fwd,
            ],
            [self._aft_flow_controller, self._fwd_flow_controller],
            self._time,
            self._active_pump,
            self._pump_controller_propulsion,
        )

    @property
    def parameters(self) -> DrivesParameters:
        return self._parameters

    def update_parameters(self, parameters: DrivesParameters):
        self._parameters = parameters

    @property
    def mode(self) -> DrivesControlMode:
        return DrivesControlMode(mode=self._state)

    def initial(self) -> tuple[DrivesControlValues, DrivesControllerState]:
        timestamp = self._time()
        return (
            DrivesControlValues.initial(timestamp),
            DrivesControllerState.initial(timestamp),
        )

    def control(
        self, sensor_values: DrivesSensorValues
    ) -> tuple[DrivesControlValues, DrivesControllerState]:
        self._state_machine.check_shorepower(sensor_values)
        self._state_machine.check_thrusters(sensor_values)
        self._control_heat_dump(sensor_values)
        self._control_flow_balance(sensor_values)
        self._control_pump_shorepower(sensor_values)
        self._control_recovery_mix(sensor_values)

        if self.mode.is_shorepower:
            self._control_pump_shorepower(sensor_values)
        elif self.mode.is_propulsion:
            self._control_flow_balance(sensor_values)

        controller_state = DrivesControllerState(
            drives_heat_dump_controller=self._heat_dump_controller.values(),
            drives_recovery_mix_controller=self._recovery_mix_controller.values(),
            drives_pump_controller_shorepower=self._pump_controller_shorepower.values(),
            drives_pump_controller_propulsion=self._pump_controller_propulsion.values(),
            drives_aft_flow_controller=self._aft_flow_controller.values(),
            drives_fwd_flow_controller=self._fwd_flow_controller.values(),
            parameters=self._parameters,
            control_mode=self.mode,
        )

        return (self._current_values, controller_state)

    def _shorepower_on(self, sensor_values: DrivesSensorValues) -> bool:
        return any(
            (
                sensor_values.drives_shorepower1a.active.value,
                sensor_values.drives_shorepower1b.active.value,
                sensor_values.drives_shorepower2a.active.value,
                sensor_values.drives_shorepower2b.active.value,
            )
        )

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

        if self._most_recently_active_pump == "pump1":
            self._most_recently_active_pump = "pump2"
            self._active_pump = self._current_values.drives_pump2

        else:
            self._most_recently_active_pump = "pump1"
            self._active_pump = self._current_values.drives_pump1

        self._active_pump.on = Stamped(value=True, timestamp=self._time())

    def _deactivate_pump(self, sensor_values: DrivesSensorValues):
        if not self._active_pump:
            raise Warning("No pump active when deactivating")

        self._active_pump.on = Stamped(value=False, timestamp=self._time())
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
    DrivesControllerState,
    DrivesAlarms,
)
