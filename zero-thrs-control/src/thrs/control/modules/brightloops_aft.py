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


class BrightloopsAftControlMode(ThrsValues):
    mode: str


class BrightloopsAftParameters(ThrsValues):
    brightloop_return_temperature: Celsius
    brightloop_flow_setpoint: LMin
    warmup_mix_tuning: Tuning
    pump_tuning: Tuning


class BrightloopsAftSensorValues(ThrsValues):
    pump: sensor.Pump
    temperature_supply: sensor.TemperatureSensor
    temperature_return: sensor.TemperatureSensor
    pressure: sensor.PressureSensor
    mix: sensor.Valve
    flow_aft1: sensor.FlowSensor
    temperature_aft1_return: sensor.TemperatureSensor
    switch_aft1: sensor.Valve
    flow_aft2: sensor.FlowSensor
    temperature_aft2_return: sensor.TemperatureSensor
    switch_aft2: sensor.Valve
    flow_aft3: sensor.FlowSensor
    temperature_aft3_return: sensor.TemperatureSensor
    switch_aft3: sensor.Valve
    flow_aft4: sensor.FlowSensor
    temperature_aft4_return: sensor.TemperatureSensor
    switch_aft4: sensor.Valve
    aft1: sensor.Brightloop
    aft2: sensor.Brightloop
    aft3: sensor.Brightloop
    aft4: sensor.Brightloop

    @property
    def max_return_temperature_active_components(
        self,
    ) -> Celsius | None:
        return max(
            temperature
            for temperature in [
                self.temperature_aft1_return.temperature.value
                if self.flow_aft1.flow.value > 0.01
                else None,
                self.temperature_aft2_return.temperature.value
                if self.flow_aft2.flow.value > 0.01
                else None,
                self.temperature_aft3_return.temperature.value
                if self.flow_aft3.flow.value > 0.01
                else None,
                self.temperature_aft4_return.temperature.value
                if self.flow_aft4.flow.value > 0.01
                else None,
            ]
            if temperature is not None
        )

    @property
    def total_flow(self) -> LMin:
        return sum([
            self.flow_aft1.flow.value,
            self.flow_aft2.flow.value,
            self.flow_aft3.flow.value,
            self.flow_aft4.flow.value,
        ])


class BrightloopsAftControlValues(ThrsValues):
    pump: control.Pump
    mix: control.Valve
    switch_aft1: control.Valve
    switch_aft2: control.Valve
    switch_aft3: control.Valve
    switch_aft4: control.Valve


def _INITIAL_CONTROL_VALUES(timestamp: datetime) -> BrightloopsAftControlValues:
    return BrightloopsAftControlValues(
        pump=Pump(
            dutypoint=Stamped(value=0.0, timestamp=timestamp),
            on=Stamped(value=False, timestamp=timestamp),
        ),
        mix=Valve(setpoint=Stamped(value=Valve.MIXING_B_TO_AB, timestamp=timestamp)),
        switch_aft1=Valve(setpoint=Stamped(value=Valve.CLOSED, timestamp=timestamp)),
        switch_aft2=Valve(setpoint=Stamped(value=Valve.CLOSED, timestamp=timestamp)),
        switch_aft3=Valve(setpoint=Stamped(value=Valve.CLOSED, timestamp=timestamp)),
        switch_aft4=Valve(setpoint=Stamped(value=Valve.CLOSED, timestamp=timestamp)),
    )


class BrightloopsAftControl(
    Control[
        BrightloopsAftSensorValues,
        BrightloopsAftControlValues,
        BrightloopsAftParameters,
        BrightloopsAftControlMode,
    ]
):
    def __init__(
        self, parameters: BrightloopsAftParameters, time_fn: Callable[[], datetime]
    ) -> None:
        self._parameters = parameters
        self._time = time_fn
        self._current_values = _INITIAL_CONTROL_VALUES(self._time()).model_copy(
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
                "trigger": "_check_components_active",
                "source": "idle",
                "dest": "recovery",
                "conditions": self._component_active,
            },
            {
                "trigger": "_check_components_active",
                "source": "recovery",
                "dest": "idle",
                "conditions": lambda sensor_values: not self._component_active(
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
            initial=self._current_values.mix.setpoint.value,
            setpoint=lambda: self._parameters.brightloop_return_temperature,
            tuning=lambda: self._parameters.warmup_mix_tuning,
            time_fn=self._time,
        )

        self._pump_controller = Controller[Ratio, LMin](
            initial=self._current_values.pump.dutypoint.value,
            setpoint=0.0,  # Overwritten in control
            tuning=lambda: self._parameters.pump_tuning,
            time_fn=self._time,
        )

    @property
    def parameters(self) -> BrightloopsAftParameters:
        return self._parameters

    def update_parameters(self, parameters: BrightloopsAftParameters):
        self._parameters = parameters

    def modes(self) -> list[str]:
        return list(self._state_machine.states.keys())

    @property
    def initial_mode(self) -> BrightloopsAftControlMode:
        initial_mode: str = self._state_machine.initial  # type: ignore
        return BrightloopsAftControlMode(mode=initial_mode)

    @property
    def mode(self) -> BrightloopsAftControlMode:
        mode: str = self.state  # type: ignore
        return BrightloopsAftControlMode(mode=mode)

    def initial(self) -> ControlResult[BrightloopsAftControlValues]:
        return ControlResult(self._time(), _INITIAL_CONTROL_VALUES(self._time()))

    def _set_mix_to_a(self):
        self._current_values.mix.setpoint = Stamped(
            value=Valve.MIXING_A_TO_AB, timestamp=self._time()
        )

    def _component_active(self, sensor_values: BrightloopsAftSensorValues) -> bool:
        return any([
            sensor_values.aft1.active.value,
            sensor_values.aft2.active.value,
            sensor_values.aft3.active.value,
            sensor_values.aft4.active.value,
        ])

    def control(
        self, sensor_values: BrightloopsAftSensorValues
    ) -> ControlResult[BrightloopsAftControlValues]:
        self._check_components_active(sensor_values)  # type: ignore
        self._control_warmup_mix(sensor_values)
        self._control_switch_valves(sensor_values)
        self._control_flow(sensor_values)

        return ControlResult(self._time(), self._current_values)

    def _control_warmup_mix(self, sensor_values: BrightloopsAftSensorValues):
        self._current_values.mix.setpoint = Stamped(
            value=self._warmup_mix_controller(
                sensor_values.max_return_temperature_active_components
            ),
            timestamp=self._time(),
        )

    def _control_flow(self, sensor_values: BrightloopsAftSensorValues):
        self._pump_controller.setpoint = (
            self._parameters.brightloop_flow_setpoint
            * sum([
                sensor_values.aft1.active.value,
                sensor_values.aft2.active.value,
                sensor_values.aft3.active.value,
                sensor_values.aft4.active.value,
            ])
        )

        self._pump_controller(sensor_values.total_flow)

    def _control_switch_valves(self, sensor_values: BrightloopsAftSensorValues):
        valves_setpoints = [
            self._current_values.switch_aft1.setpoint,
            self._current_values.switch_aft2.setpoint,
            self._current_values.switch_aft3.setpoint,
            self._current_values.switch_aft4.setpoint,
        ]
        actives = [
            sensor_values.aft1.active.value,
            sensor_values.aft2.active.value,
            sensor_values.aft3.active.value,
            sensor_values.aft4.active.value,
        ]

        for setpoints, active in zip(valves_setpoints, actives):
            if setpoints.value == Valve.CLOSED and active:
                setpoints = Stamped(value=Valve.OPEN, timestamp=self._time())
            elif setpoints.value == Valve.OPEN and not active:
                setpoints = Stamped(value=Valve.CLOSED, timestamp=self._time())


class BrightloopsAftAlarms(BaseAlarms):
    pass
