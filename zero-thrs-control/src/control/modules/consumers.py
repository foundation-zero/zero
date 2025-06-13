from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field
from classes.control import Control, ControlResult
from control.controllers import (
    FlowDistributionController,
)
from input_output.base import Stamped
from input_output.definitions.control import Valve
from input_output.definitions.units import Ratio
from input_output.modules.consumers import ConsumersControlValues, ConsumersSensorValues


class ConsumersParameters(BaseModel):
    boosting_enabled: bool
    boosting_flow_ratio_setpoint: Annotated[Ratio, Field(ge=0.0, le=1.0)]
    fahrenheit_enabled: bool
    fahrenheit_flow_ratio_setpoint: Annotated[Ratio, Field(ge=0.0, le=1.0)]


_ZERO_TIME = datetime.fromtimestamp(0)
_INITIAL_CONTROL_VALUES = ConsumersControlValues(
    consumers_switch_fahrenheit_direct_supply=Valve(
        setpoint=Stamped(value=Valve.SWITCH_STRAIGHT, timestamp=_ZERO_TIME)
    ),
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
    consumers_switch_fahrenheit_direct_return=Valve(
        setpoint=Stamped(value=Valve.CLOSED, timestamp=_ZERO_TIME)
    ),
    consumers_switch_boosting=Valve(
        setpoint=Stamped(value=Valve.OPEN, timestamp=_ZERO_TIME)
    ),
)


class ConsumersControl(Control[ConsumersSensorValues, ConsumersControlValues]):
    def __init__(self, parameters: ConsumersParameters) -> None:
        self._parameters = parameters
        self._current_values = _INITIAL_CONTROL_VALUES.model_copy(deep=True)
        self._flow_controller = FlowDistributionController(
            [
                self._current_values.consumers_flowcontrol_boosting,
                self._current_values.consumers_flowcontrol_fahrenheit,
                self._current_values.consumers_flowcontrol_bypass,
            ]
        )

    def initial(self, time: datetime) -> ControlResult[ConsumersControlValues]:
        return ControlResult(time, self._current_values)

    def _control_distribution(
        self, sensor_values: ConsumersSensorValues, time: datetime
    ):
        actives = [
            self._parameters.boosting_enabled,
            self._parameters.fahrenheit_enabled,
        ]
        self._flow_controller.set_actives(
            [
                *actives,
                True,  # Bypass is always active
            ]
        )
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
        self._flow_controller.set_ratios(
            [
                *ratios,
                1 - sum(ratio for ratio in ratios if ratio is not None),
            ]
        )
        self._flow_controller(
            [
                sensor_values.consumers_flow_boosting.flow.value,
                sensor_values.consumers_flow_fahrenheit.flow.value,
                sensor_values.consumers_flow_bypass.flow.value,
            ],
            time,
        )

    def _control_switch_valve(
        self,
        switch_valve: Valve,
        enabled: bool,
        time: datetime,
    ):
        if enabled:
            if switch_valve.setpoint.value != Valve.OPEN:
                switch_valve.setpoint = Stamped(value=Valve.OPEN, timestamp=time)
        elif not enabled and switch_valve.setpoint.value != Valve.CLOSED:
            switch_valve.setpoint = Stamped(value=Valve.CLOSED, timestamp=time)

    def control(
        self, sensor_values: ConsumersSensorValues, time: datetime
    ) -> ControlResult:
        self._control_distribution(sensor_values, time)

        self._control_switch_valve(
            self._current_values.consumers_switch_boosting,
            self._parameters.boosting_enabled,
            time,
        )
        self._control_switch_valve(
            self._current_values.consumers_switch_fahrenheit_exchanger,
            self._parameters.fahrenheit_enabled,
            time,
        )

        return ControlResult(time, self._current_values)
