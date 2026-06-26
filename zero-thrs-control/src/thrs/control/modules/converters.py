from datetime import datetime
from typing import Callable

from transitions import Machine, State

from thrs.classes.control import Control, ControlMode
from thrs.control.controllers import PidController
from thrs.input_output.base import Stamped, ThrsValues
from thrs.input_output.definitions import control, sensor
from thrs.input_output.definitions.control import Valve
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
    parameters: ConvertersParameters


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
                    self.converter_return_temperatures, self.flows
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
        self.current_values = initial_control_values

        self._pump_controller = PidController[Ratio, LMin](
            initial=self.current_values.pump.dutypoint.value,
            setpoint=0.0,  # Overwritten in control
            tuning=lambda: self._parameters.pump_tuning,
            time_fn=self._time,
        )

        self._warmup_mix_controller = PidController[Ratio, Celsius](
            initial=self.current_values.mix.setpoint.value,
            setpoint=lambda: self._parameters.converter_return_temperature,
            tuning=lambda: self._parameters.warmup_mix_tuning,
            time_fn=self._time,
        )

        self._states = [
            State(
                name="idle",
                on_enter=self._close_circuit,
            ),
            State(
                name="recovery",
                on_enter=[
                    lambda sensor_values: self._pump_controller.enable(),
                    lambda sensor_values: self._warmup_mix_controller.enable(),
                    self._activate_pump,
                ],
                on_exit=[
                    lambda sensor_values: self._pump_controller.disable(),
                    lambda sensor_values: self._warmup_mix_controller.disable(),
                    self._deactivate_pump,
                ],
            ),
        ]

        self._transitions = [
            {
                "trigger": "_check_converters_active",
                "source": "idle",
                "dest": "recovery",
                "conditions": self._converter_active,
            },
            {
                "trigger": "_check_converters_active",
                "source": "recovery",
                "dest": "idle",
                "conditions": lambda sensor_values: not self._converter_active(
                    sensor_values
                ),
            },
        ]

        self._state_machine = Machine(
            model=self,
            states=self._states,
            transitions=self._transitions,
            initial="idle",
        )

    @property
    def parameters(self) -> ConvertersParameters:
        return self._parameters

    def update_parameters(self, parameters: ConvertersParameters):
        self._parameters = parameters

    def modes(self) -> list[str]:
        return list(self._state_machine.states.keys())

    @property
    def initial_mode(self) -> ConvertersControlMode:
        initial_mode: str = self._state_machine.initial  # type: ignore
        return ConvertersControlMode(mode=initial_mode)

    @property
    def mode(self) -> ConvertersControlMode:
        mode: str = self.state  # type: ignore
        return ConvertersControlMode(mode=mode)

    def initial(self) -> tuple[ConvertersControlValues, ConvertersControllerState]:
        return (
            self.current_values,
            ConvertersControllerState(parameters=self._parameters),
        )

    def _close_circuit(self):
        self.current_values.mix.setpoint = Stamped(
            value=Valve.MIXING_B_TO_AB, timestamp=self._time()
        )

    def _activate_pump(self, sensor_values: ConvertersSensorValues):
        self.current_values.pump.on = Stamped(value=True, timestamp=self._time())

    def _deactivate_pump(self, sensor_values: ConvertersSensorValues):
        self.current_values.pump.on = Stamped(value=False, timestamp=self._time())

    def _converter_active(self, sensor_values: ConvertersSensorValues) -> bool:
        return any(converter.active.value for converter in sensor_values.converters)

    def control(
        self, sensor_values: ConvertersSensorValues
    ) -> tuple[ConvertersControlValues, ConvertersControllerState]:
        self._check_converters_active(sensor_values)  # type: ignore
        self._control_warmup_mix(sensor_values)
        self._control_switch_valves(sensor_values)
        self._control_flow(sensor_values)

        return (
            self.current_values,
            ConvertersControllerState(parameters=self._parameters),
        )

    def _control_warmup_mix(self, sensor_values: ConvertersSensorValues):
        self.current_values.mix.setpoint = Stamped(
            value=self._warmup_mix_controller(
                sensor_values.max_return_temperature_active_components
            ),
            timestamp=self._time(),
        )

    def _control_flow(self, sensor_values: ConvertersSensorValues):
        self._pump_controller.setpoint = (
            self._parameters.converter_flow_setpoint
            * sum(switch.position_rel.value**2 for switch in sensor_values.switches)
        )  # Control flow based on switch valves to prevent pumping against closed valves, as well as having insufficient flow during the closing of valves (when components are already inacive). Assuming possible flow is approximately quadratic to valve opening.

        self.current_values.pump.dutypoint = Stamped(
            value=self._pump_controller(sensor_values.total_flow),
            timestamp=self._time(),
        )

    def _control_switch_valves(self, sensor_values: ConvertersSensorValues):
        for switch, converter in zip(
            self.current_values.switches, sensor_values.converters
        ):
            if switch.setpoint.value == Valve.CLOSED and converter.active.value:
                switch.setpoint = Stamped(value=Valve.OPEN, timestamp=self._time())
            elif switch.setpoint.value == Valve.OPEN and not converter.active.value:
                switch.setpoint = Stamped(value=Valve.CLOSED, timestamp=self._time())
