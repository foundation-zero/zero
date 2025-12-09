from datetime import datetime
from typing import Annotated, Callable

from pydantic import Field
from thrs.classes.control import Control, ControlResult
from thrs.control.controllers import (
    Controller,
    FlowDistributionController,
)
from thrs.input_output.alarms import BaseAlarms
from thrs.input_output.base import Stamped, ThrsValues
from thrs.input_output.definitions.control import Valve
from thrs.input_output.definitions.units import LMin, Ratio, Tuning
from thrs.input_output.modules.consumers import (
    ConsumersControlValues,
    ConsumersSensorValues,
)


class ConsumersParameters(ThrsValues):
    boosting_enabled: bool = True
    boosting_flow_ratio_setpoint: Annotated[Ratio, Field(ge=0.0, le=1.0)] = 0.3
    fahrenheit_enabled: bool = True
    fahrenheit_flow_ratio_setpoint: Annotated[Ratio, Field(ge=0.0, le=1.0)] = 0.3
    boosting_flow_balance_tuning: Tuning = (0.01, 0.001, 0)
    bypass_flow_balance_tuning: Tuning = (0.01, 0.001, 0)
    fahrenheit_flow_balance_tuning: Tuning = (0.01, 0.001, 0)


_ZERO_TIME = datetime.fromtimestamp(0)
_INITIAL_CONTROL_VALUES = ConsumersControlValues(
    consumers_flowcontrol_bypass=Valve(
        setpoint=Stamped(value=Valve.OPEN, timestamp=_ZERO_TIME)
    ),
    consumers_flowcontrol_boosting=Valve(
        setpoint=Stamped(value=Valve.OPEN, timestamp=_ZERO_TIME)
    ),
    consumers_flowcontrol_fahrenheit=Valve(
        setpoint=Stamped(value=Valve.OPEN, timestamp=_ZERO_TIME)
    ),
    consumers_switch_fahrenheit_exchanger=Valve(
        setpoint=Stamped(value=Valve.OPEN, timestamp=_ZERO_TIME)
    ),
    consumers_switch_boosting=Valve(
        setpoint=Stamped(value=Valve.OPEN, timestamp=_ZERO_TIME)
    ),
)


class ConsumersControl(
    Control[ConsumersSensorValues, ConsumersControlValues, ConsumersParameters]
):
    def __init__(
        self, parameters: ConsumersParameters, time_fn: Callable[[], datetime]
    ) -> None:
        self._parameters = parameters
        self._current_values = _INITIAL_CONTROL_VALUES.model_copy(deep=True)
        self._time = time_fn

        self._boosting_flow_controller = Controller[Ratio, LMin](
            _INITIAL_CONTROL_VALUES.consumers_flowcontrol_boosting.setpoint.value,
            0.0,
            parameters.boosting_flow_balance_tuning,
            self._time,
        )

        self._bypass_flow_controller = Controller[Ratio, LMin](
            _INITIAL_CONTROL_VALUES.consumers_flowcontrol_bypass.setpoint.value,
            0.0,
            parameters.bypass_flow_balance_tuning,
            self._time,
        )

        self._fahrenheit_flow_controller = Controller[Ratio, LMin](
            _INITIAL_CONTROL_VALUES.consumers_flowcontrol_fahrenheit.setpoint.value,
            0.0,
            parameters.fahrenheit_flow_balance_tuning,
            self._time,
        )

        self._flow_distribution_controller = FlowDistributionController(
            [
                self._current_values.consumers_flowcontrol_boosting,
                self._current_values.consumers_flowcontrol_fahrenheit,
                self._current_values.consumers_flowcontrol_bypass,
            ],
            [
                self._boosting_flow_controller,
                self._fahrenheit_flow_controller,
                self._bypass_flow_controller,
            ],
        )

    def initial(self) -> ControlResult[ConsumersControlValues]:
        return ControlResult(self._time(), self._current_values)

    def _control_flow_distribution(self, sensor_values: ConsumersSensorValues):
        actives = [
            self._parameters.boosting_enabled,
            self._parameters.fahrenheit_enabled,
            True,  # Bypass is always active
        ]

        self._flow_distribution_controller.set_active_valves(actives)

        ratios = [
            ratio if active else None
            for ratio, active in zip(
                [
                    self._parameters.boosting_flow_ratio_setpoint,
                    self._parameters.fahrenheit_flow_ratio_setpoint,
                ],
                actives,
            )
        ]
        self._flow_distribution_controller.set_ratios(
            [
                *ratios,
                1 - sum(ratio for ratio in ratios if ratio is not None),
            ]
        )
        self._flow_distribution_controller(
            [
                sensor_values.consumers_flow_boosting.flow.value,
                sensor_values.consumers_flow_fahrenheit.flow.value,
                sensor_values.consumers_flow_bypass.flow.value,
            ],
        )

    def _control_switch_valve(
        self,
        switch_valve: Valve,
        enabled: bool,
    ):
        if enabled:
            if switch_valve.setpoint.value != Valve.OPEN:
                switch_valve.setpoint = Stamped(
                    value=Valve.OPEN, timestamp=self._time()
                )
        elif not enabled and switch_valve.setpoint.value != Valve.CLOSED:
            switch_valve.setpoint = Stamped(value=Valve.CLOSED, timestamp=self._time())

    def control(self, sensor_values: ConsumersSensorValues) -> ControlResult:
        self._control_flow_distribution(sensor_values)

        self._control_switch_valve(
            self._current_values.consumers_switch_boosting,
            self._parameters.boosting_enabled,
        )
        self._control_switch_valve(
            self._current_values.consumers_switch_fahrenheit_exchanger,
            self._parameters.fahrenheit_enabled,
        )

        return ControlResult(self._time(), self._current_values)

    @staticmethod
    def modes() -> list[str]:
        return [""]

    @staticmethod
    def initial_mode() -> str:
        return ""

    @property
    def mode(self) -> str | None:
        return None

    @property
    def parameters(self) -> ConsumersParameters:
        return self._parameters

    def update_parameters(self, parameters: ConsumersParameters):
        pass


class ConsumersAlarms(BaseAlarms):
    pass
