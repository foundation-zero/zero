from collections.abc import Callable
from datetime import datetime

from thrs.classes.control import Control
from thrs.control.controllers import (
    FlowDistributionController,
    PidController,
)
from thrs.control.modules.consumers.io import (
    ConsumersControlValues,
    ConsumersSensorValues,
)
from thrs.control.modules.consumers.state import (
    ConsumersControllerState,
    ConsumersControlMode,
    ConsumersParameters,
)
from thrs.input_output.alarms import BaseAlarms
from thrs.input_output.base import Stamped
from thrs.input_output.definitions.control import Valve
from thrs.input_output.definitions.units import LMin, Ratio
from thrs.orchestration.module import ModuleDescription


def _INITIAL_CONTROL_VALUES(timestamp: datetime) -> ConsumersControlValues:  # noqa: N802
    return ConsumersControlValues(
        consumers_flowcontrol_bypass=Valve(
            setpoint=Stamped(value=Valve.OPEN, timestamp=timestamp)
        ),
        consumers_flowcontrol_dhw=Valve(
            setpoint=Stamped(value=Valve.OPEN, timestamp=timestamp)
        ),
        consumers_flowcontrol_adsorption=Valve(
            setpoint=Stamped(value=Valve.OPEN, timestamp=timestamp)
        ),
        consumers_switch_adsorption=Valve(
            setpoint=Stamped(value=Valve.OPEN, timestamp=timestamp)
        ),
        consumers_switch_dhw=Valve(
            setpoint=Stamped(value=Valve.OPEN, timestamp=timestamp)
        ),
    )


class ConsumersControl(
    Control[
        ConsumersSensorValues,
        ConsumersControlValues,
        ConsumersParameters,
        ConsumersControlMode,
        ConsumersControllerState,
    ]
):
    def __init__(
        self,
        parameters: ConsumersParameters,
        time_fn: Callable[[], datetime],
    ) -> None:
        self._parameters = parameters
        self._time = time_fn
        self._current_values = _INITIAL_CONTROL_VALUES(self._time()).model_copy(
            deep=True
        )

        self._init_controllers()

    def _init_controllers(self):
        self._dhw_flow_controller = PidController[Ratio, LMin](
            self._current_values.consumers_flowcontrol_dhw.setpoint.value,
            0.0,
            lambda: self._parameters.dhw_flow_balance_tuning,
            self._time,
        )

        self._bypass_flow_controller = PidController[Ratio, LMin](
            self._current_values.consumers_flowcontrol_bypass.setpoint.value,
            0.0,
            lambda: self._parameters.bypass_flow_balance_tuning,
            self._time,
        )

        self._adsorption_flow_controller = PidController[Ratio, LMin](
            self._current_values.consumers_flowcontrol_adsorption.setpoint.value,
            0.0,
            lambda: self._parameters.adsorption_flow_balance_tuning,
            self._time,
        )

        self._flow_distribution_controller = FlowDistributionController(
            [
                self._current_values.consumers_flowcontrol_dhw,
                self._current_values.consumers_flowcontrol_adsorption,
                self._current_values.consumers_flowcontrol_bypass,
            ],
            [
                self._dhw_flow_controller,
                self._adsorption_flow_controller,
                self._bypass_flow_controller,
            ],
        )

    def initial(self) -> tuple[ConsumersControlValues, ConsumersControllerState]:
        return (
            _INITIAL_CONTROL_VALUES(self._time()),
            ConsumersControllerState.zero(self._time()),
        )

    def _control_flow_distribution(self, sensor_values: ConsumersSensorValues):
        actives = [
            self._parameters.dhw_enabled,
            self._parameters.adsorption_enabled,
            True,  # Bypass is always active
        ]

        self._flow_distribution_controller.set_active_valves(actives)

        ratios = [
            ratio if active else None
            for ratio, active in zip(
                [
                    self._parameters.dhw_flow_ratio_setpoint,
                    self._parameters.adsorption_flow_ratio_setpoint,
                ],
                actives,
                strict=False,
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
                sensor_values.consumers_flow_dhw.flow.value,
                sensor_values.consumers_flow_adsorption.flow.value,
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

    def control(
        self, sensor_values: ConsumersSensorValues
    ) -> tuple[ConsumersControlValues, ConsumersControllerState]:
        self._control_flow_distribution(sensor_values)

        self._control_switch_valve(
            self._current_values.consumers_switch_dhw,
            self._parameters.dhw_enabled,
        )
        self._control_switch_valve(
            self._current_values.consumers_switch_adsorption,
            self._parameters.adsorption_enabled,
        )

        controller_state = ConsumersControllerState(
            consumers_dhw_flow_controller=self._dhw_flow_controller.values(),
            consumers_bypass_flow_controller=self._bypass_flow_controller.values(),
            consumers_adsorption_flow_controller=self._adsorption_flow_controller.values(),
            parameters=self._parameters,
            control_mode=self.mode,
        )

        return (self._current_values, controller_state)

    @property
    def mode(self) -> ConsumersControlMode:
        return ConsumersControlMode()

    @property
    def parameters(self) -> ConsumersParameters:
        return self._parameters

    def update_parameters(self, parameters: ConsumersParameters):
        self._parameters = parameters


class ConsumersAlarms(BaseAlarms):
    pass


CONSUMERS_MODULE_DESCRIPTION = ModuleDescription(
    ConsumersSensorValues,
    ConsumersControlValues,
    ConsumersParameters,
    ConsumersControl,
    ConsumersControllerState,
    ConsumersAlarms,
)
