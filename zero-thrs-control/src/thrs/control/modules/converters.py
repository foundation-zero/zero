from datetime import datetime
from typing import Callable

from transitions import Machine, State

from thrs.classes.control import Control, ControlResult

from thrs.control.controllers import Controller
from thrs.input_output.alarms import BaseAlarms
from thrs.input_output.base import Stamped, ThrsValues
from thrs.input_output.definitions import sensor
from thrs.input_output.definitions import control
from thrs.input_output.definitions.control import Pump, Valve
from thrs.input_output.definitions.units import Celsius, LMin, Ratio, Tuning


class ConvertersControlMode(ThrsValues):
    mode: str


class ConvertersParameters(ThrsValues):
    converter_return_temperature: Celsius
    converter_flow_setpoint: LMin
    warmup_mix_tuning: Tuning
    pump_tuning: Tuning


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
            temperature_sensor.temperature.value
            for temperature_sensor, flow_sensor in zip(
                self.converter_return_temperatures, self.flows
            )
            if flow_sensor.flow.value > 0.01
        )

    @property
    def total_flow(self) -> LMin:
        return sum([flow_sensor.flow.value for flow_sensor in self.flows])


class ConvertersControlValues(ThrsValues):
    pump: control.Pump
    mix: control.Valve
    switches: list[control.Valve]


def _INITIAL_CONTROL_VALUES(timestamp: datetime) -> ConvertersControlValues:
    return ConvertersControlValues(
        pump=Pump(
            dutypoint=Stamped(value=0.0, timestamp=timestamp),
            on=Stamped(value=False, timestamp=timestamp),
        ),
        mix=Valve(setpoint=Stamped(value=Valve.MIXING_B_TO_AB, timestamp=timestamp)),
        switches=[
            Valve(setpoint=Stamped(value=Valve.CLOSED, timestamp=timestamp)),
            Valve(setpoint=Stamped(value=Valve.CLOSED, timestamp=timestamp)),
            Valve(setpoint=Stamped(value=Valve.CLOSED, timestamp=timestamp)),
            Valve(setpoint=Stamped(value=Valve.CLOSED, timestamp=timestamp)),
        ],
    )


class ConvertersControl(
    Control[
        ConvertersSensorValues,
        ConvertersControlValues,
        ConvertersParameters,
        ConvertersControlMode,
    ]
):
    def __init__(
        self, parameters: ConvertersParameters, time_fn: Callable[[], datetime]
    ) -> None:
        self._parameters = parameters
        self._time = time_fn
        self.current_values = _INITIAL_CONTROL_VALUES(self._time()).model_copy(
            deep=True
        )

        self._states = [
            State(
                name="idle",
                on_enter=self._set_mix_to_a,
            ),
            State(
                name="recovery",
                on_enter=[
                    self._pump_controller.enable,
                    self._warmup_mix_controller.enable,
                ],
                on_exit=[
                    self._pump_controller.disable,
                    self._warmup_mix_controller.disable,
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

        self._warmup_mix_controller = Controller[Ratio, Celsius](
            initial=self.current_values.mix.setpoint.value,
            setpoint=lambda: self._parameters.converter_return_temperature,
            tuning=lambda: self._parameters.warmup_mix_tuning,
            time_fn=self._time,
        )

        self._pump_controller = Controller[Ratio, LMin](
            initial=self.current_values.pump.dutypoint.value,
            setpoint=0.0,  # Overwritten in control
            tuning=lambda: self._parameters.pump_tuning,
            time_fn=self._time,
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

    def initial(self) -> ControlResult[ConvertersControlValues]:
        return ControlResult(self._time(), _INITIAL_CONTROL_VALUES(self._time()))

    def _set_mix_to_a(self):
        self.current_values.mix.setpoint = Stamped(
            value=Valve.MIXING_A_TO_AB, timestamp=self._time()
        )

    def _converter_active(self, sensor_values: ConvertersSensorValues) -> bool:
        return any(converter.active for converter in sensor_values.converters)

    def control(
        self, sensor_values: ConvertersSensorValues
    ) -> ControlResult[ConvertersControlValues]:
        self._check_components_active(sensor_values)  # type: ignore
        self._control_warmup_mix(sensor_values)
        self._control_switch_valves(sensor_values)
        self._control_flow(sensor_values)

        return ControlResult(self._time(), self.current_values)

    def _control_warmup_mix(self, sensor_values: ConvertersSensorValues):
        self.current_values.mix.setpoint = Stamped(
            value=self._warmup_mix_controller(
                sensor_values.max_return_temperature_active_components
            ),
            timestamp=self._time(),
        )

    def _control_flow(self, sensor_values: ConvertersSensorValues):
        self._pump_controller.setpoint = self._parameters.converter_flow_setpoint * sum(
            converter.active.value for converter in sensor_values.converters
        )

        self._pump_controller(sensor_values.total_flow)

    def _control_switch_valves(self, sensor_values: ConvertersSensorValues):
        for switch, converter in zip(
            self.current_values.switches, sensor_values.converters
        ):
            if switch.setpoint.value == Valve.CLOSED and converter.active.value:
                switch.setpoint = Stamped(value=Valve.OPEN, timestamp=self._time())
            elif switch.setpoint.value == Valve.OPEN and not converter.active.value:
                switch.setpoint = Stamped(value=Valve.CLOSED, timestamp=self._time())


class ConvertersAlarms(BaseAlarms):
    pass
