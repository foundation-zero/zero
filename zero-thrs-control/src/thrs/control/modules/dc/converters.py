from collections.abc import Callable
from datetime import datetime
from typing import Annotated

from statemachine import State, StateChart

from thrs.classes.control import Control
from thrs.control.controllers import PidController
from thrs.control.state import ControlMode
from thrs.input_output.base import Stamped, ThrsValues, component_meta
from thrs.input_output.definitions import control, sensor
from thrs.input_output.definitions.control import Valve
from thrs.input_output.definitions.controllers import PidControllerValues
from thrs.input_output.definitions.units import Celsius, LMin, Ratio, Tuning


class ConvertersControlMode(ControlMode):
    mode: str

    @property
    def is_idle(self) -> bool:
        return self.mode == "idle"

    @property
    def is_recovery(self) -> bool:
        return self.mode == "recovery"


class ConvertersParameters(ThrsValues):
    converter_return_temperature: Celsius
    converter_flow_setpoint: LMin
    warmup_mix_tuning: Tuning
    pump_tuning: Tuning


class ConvertersControllerState(ThrsValues):
    converters_pump_controller: Annotated[
        PidControllerValues, component_meta(component_type="pid_controller")
    ]
    converters_warmup_mix_controller: Annotated[
        PidControllerValues, component_meta(component_type="pid_controller")
    ]


class ConvertersSensorValues(ThrsValues):
    pump: sensor.Pump
    temperature_supply: sensor.TemperatureSensor
    temperature_return: sensor.TemperatureSensor
    pressure: sensor.PressureSensor
    mix: sensor.Valve
    flows: list[sensor.FlowSensor]
    switches: list[sensor.Valve]
    converters: list[sensor.Brightloop | sensor.Ugrid]
    converter_return_temperatures: list[sensor.TemperatureSensor]

    @property
    def max_return_temperature_active_components(
        self,
    ) -> Celsius | None:
        return max(
            (
                temperature_sensor.temperature.value
                for temperature_sensor, flow_sensor in zip(
                    self.converter_return_temperatures, self.flows, strict=False
                )
                if flow_sensor.flow.value > 0
            ),
            default=None,
        )

    @property
    def total_flow(self) -> LMin:
        return sum([flow_sensor.flow.value for flow_sensor in self.flows])


class ConvertersControlValues(ThrsValues):
    pump: control.Pump
    mix: control.Valve
    switches: list[control.Valve]


class _ConvertersStateMachine(StateChart["ConvertersControl"]):
    """Each event takes the first of its transitions whose condition holds."""

    # An error in a guard or action raises instead of becoming an unhandled event.
    catch_errors_as_events = False

    idle = State(initial=True, enter="_close_circuit")
    recovery = State(
        enter=["_enable_controllers", "_activate_pump"],
        exit=["_disable_controllers", "_deactivate_pump"],
    )

    check_converters_active = recovery.from_(
        idle, cond="_converter_active"
    ) | idle.from_(recovery, cond="not _converter_active")


class ConvertersControl(
    Control[
        ConvertersSensorValues,
        ConvertersControlValues,
        ConvertersParameters,
        ConvertersControlMode,
        ConvertersControllerState,
    ]
):
    def __init__(
        self,
        parameters: ConvertersParameters,
        time_fn: Callable[[], datetime],
        initial_control_values: ConvertersControlValues,
    ) -> None:
        self._parameters = parameters
        self._time = time_fn
        self._current_values = initial_control_values

        # Starting with a mode set skips idle's enter actions: the first outputs are
        # the initial control values.
        self._state: str = _ConvertersStateMachine.idle.value
        self._state_machine = _ConvertersStateMachine(model=self, state_field="_state")
        self._init_controllers()

    def _init_controllers(self):
        self._pump_controller = PidController[Ratio, LMin](
            initial=self._current_values.pump.dutypoint.value,
            setpoint=0.0,  # Overwritten in control
            tuning=lambda: self._parameters.pump_tuning,
            time_fn=self._time,
            output_limits=(0.1, 1),
        )

        self._warmup_mix_controller = PidController[Ratio, Celsius](
            initial=self._current_values.mix.setpoint.value,
            setpoint=lambda: self._parameters.converter_return_temperature,
            tuning=lambda: self._parameters.warmup_mix_tuning,
            time_fn=self._time,
        )

    @property
    def parameters(self) -> ConvertersParameters:
        return self._parameters

    def update_parameters(self, parameters: ConvertersParameters):
        self._parameters = parameters

    @property
    def mode(self) -> ConvertersControlMode:
        return ConvertersControlMode(mode=self._state)

    def initial(self) -> tuple[ConvertersControlValues, ConvertersControllerState]:
        return (
            self._current_values,
            ConvertersControllerState.initial(self._time()),
        )

    def _close_circuit(self):
        self._current_values.mix.setpoint = Stamped(
            value=Valve.MIXING_B_TO_AB, timestamp=self._time()
        )

    def _enable_controllers(self):
        self._pump_controller.enable()
        self._warmup_mix_controller.enable()

    def _disable_controllers(self):
        self._pump_controller.disable()
        self._warmup_mix_controller.disable()

    def _activate_pump(self, sensor_values: ConvertersSensorValues):
        self._current_values.pump.on = Stamped(value=True, timestamp=self._time())

    def _deactivate_pump(self, sensor_values: ConvertersSensorValues):
        self._current_values.pump.on = Stamped(value=False, timestamp=self._time())

    def _converter_active(self, sensor_values: ConvertersSensorValues) -> bool:
        return any(converter.active.value for converter in sensor_values.converters)

    def control(
        self, sensor_values: ConvertersSensorValues
    ) -> tuple[ConvertersControlValues, ConvertersControllerState]:
        self._state_machine.check_converters_active(sensor_values)
        self._control_warmup_mix(sensor_values)
        self._control_switch_valves(sensor_values)
        self._control_flow(sensor_values)

        return (
            self._current_values,
            ConvertersControllerState(
                converters_pump_controller=self._pump_controller.values(),
                converters_warmup_mix_controller=self._warmup_mix_controller.values(),
            ),
        )

    def _control_warmup_mix(self, sensor_values: ConvertersSensorValues):
        self._current_values.mix.setpoint = Stamped(
            value=self._warmup_mix_controller(
                sensor_values.max_return_temperature_active_components
            ),
            timestamp=self._time(),
        )

    def _control_flow(self, sensor_values: ConvertersSensorValues):
        # Control flow based on switch valves to prevent pumping against closed
        # valves, as well as having insufficient flow during the closing of valves
        # (when components are already inactive). Assuming possible flow is
        # approximately quadratic to valve opening.
        self._pump_controller.setpoint = self._parameters.converter_flow_setpoint * sum(
            switch.position_rel.value**2 for switch in sensor_values.switches
        )

        self._current_values.pump.dutypoint = Stamped(
            value=self._pump_controller(sensor_values.total_flow),
            timestamp=self._time(),
        )

    def _control_switch_valves(self, sensor_values: ConvertersSensorValues):
        for switch, converter in zip(
            self._current_values.switches, sensor_values.converters, strict=False
        ):
            if switch.setpoint.value == Valve.CLOSED and converter.active.value:
                switch.setpoint = Stamped(value=Valve.OPEN, timestamp=self._time())
            elif switch.setpoint.value == Valve.OPEN and not converter.active.value:
                switch.setpoint = Stamped(value=Valve.CLOSED, timestamp=self._time())
