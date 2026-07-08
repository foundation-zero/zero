from datetime import datetime
from typing import Callable, Mapping, cast

from thrs.classes.control import Control
from thrs.control.manual import ManualControl
from thrs.control.switching import (
    AutomationMode,
    SwitchingControl,
    SwitchingControlMode,
)
from thrs.input_output.alarms import Alarm, BaseAlarms
from thrs.input_output.base import (
    CombinedValues,
    ThrsValues,
)

type ModuleClassMap = Mapping[str, type[ThrsValues]]


class ModuleDescription[
    S: ThrsValues,
    C: ThrsValues,
    P: ThrsValues,
    M: ThrsValues,
    CV: ThrsValues,
]:
    """Description of a module with sensor values, control values, control parameters and control mode models and the control & alarm logic"""

    def __init__(
        self,
        sensor_values_cls: type[S],
        control_values_cls: type[C],
        parameters_cls: type[P],
        control: Callable[[P, Callable[[], datetime]], Control[S, C, P, M, CV]],
        control_mode_cls: type[M],
        controller_state_cls: type[CV],
        alarms: Callable[[], BaseAlarms[S, C, P]],
    ):
        self.sensor_values_cls = sensor_values_cls
        self.control_values_cls = control_values_cls
        self.parameters_cls = parameters_cls
        self.control_mode_cls = control_mode_cls
        self.controller_state_cls = controller_state_cls
        self.control = control
        self.alarms = alarms


class CombinedControl(
    Control[
        CombinedValues,
        CombinedValues,
        CombinedValues,
        CombinedValues,
        CombinedValues,
    ]
):
    """Combination of multiple controls into one control module"""

    def __init__(
        self,
        modules: Mapping[str, Control],
        time_fn: Callable[[], datetime],
    ):
        self._modules = {
            name: SwitchingControl(
                ManualControl(control.initial()[0], time_fn), control
            )
            for name, control in modules.items()
        }
        self._time_fn = time_fn

    def initial(self) -> tuple[CombinedValues, CombinedValues]:
        return self.control(CombinedValues({}))

    def control(
        self, sensor_values: CombinedValues
    ) -> tuple[CombinedValues, CombinedValues]:
        combined_control_values = CombinedValues({})
        combined_controller_state = CombinedValues({})

        for name, module in self._modules.items():
            sensors = sensor_values.values.get(name, None)
            if sensors:
                control_value, controller_state = module.control(sensors)
            else:
                control_value, controller_state = module.initial()

            combined_control_values.values[name] = control_value
            combined_controller_state.values[name] = controller_state

        return (combined_control_values, combined_controller_state)

    @property
    def parameters(self) -> CombinedValues:
        return CombinedValues(
            values={name: module.parameters for name, module in self._modules.items()}
        )

    @staticmethod
    def initial_mode():
        return ""

    @property
    def mode(self) -> CombinedValues | None:
        return CombinedValues(
            values={name: module.mode for name, module in self._modules.items()}
        )

    def update_parameters(self, parameters: CombinedValues):
        for name, params in parameters.values.items():
            self._modules[name].update_parameters(params)

    def update_manual_controls(self, module: str, control_values: ThrsValues):
        self._modules[module].update_manual_controls(control_values)

    @property
    def manual_controls(self) -> CombinedValues:
        return CombinedValues(
            values={
                name: module.manual_controls for name, module in self._modules.items()
            }
        )

    def update_automation_modes(self, combined_modes: CombinedValues):
        for module, mode in combined_modes.values.items():
            expected_mode = cast(AutomationMode, mode)
            self._modules[module].switch_mode(expected_mode)

    def set_automation_mode(self, module: str, automatic: bool):
        self._modules[module].switch_mode(
            AutomationMode(mode="automatic" if automatic else "manual")
        )


class CombinedAlarms(BaseAlarms[CombinedValues, CombinedValues, CombinedValues]):
    """Combination of multiple alarms into one alarm module"""

    def __init__(
        self, modules: Mapping[str, BaseAlarms[ThrsValues, ThrsValues, ThrsValues]]
    ):
        self._modules = dict(modules)

    def check(
        self,
        sensor_values: CombinedValues,
        control_values: CombinedValues,
        parameters: CombinedValues,
    ) -> list[Alarm]:
        if not sensor_values.values:
            return []
        return [
            alarm
            for name, module in self._modules.items()
            for alarm in module.check(
                sensor_values.values[name],
                control_values.values[name],
                parameters.values[name],
            )
        ]


class CombinedModule:
    """Combination of multiple control modules into a single control module"""

    def __init__(
        self,
        modules: dict[str, ModuleDescription],
    ):
        self._modules = modules
        self.sensor_values_clss: ModuleClassMap = {
            module: desc.sensor_values_cls for module, desc in modules.items()
        }
        self.control_values_clss: ModuleClassMap = {
            module: desc.control_values_cls for module, desc in modules.items()
        }
        self.controller_state_clss: ModuleClassMap = {
            module: desc.controller_state_cls for module, desc in modules.items()
        }
        self.parameters_clss: ModuleClassMap = {
            module: desc.parameters_cls for module, desc in modules.items()
        }
        self.control_modes_clss: ModuleClassMap = {
            module: SwitchingControlMode[desc.control_mode_cls]
            for module, desc in modules.items()
        }

    @property
    def modules(self) -> list[str]:
        return list(self._modules.keys())

    def control_values_for_module(self, module: str) -> type[ThrsValues]:
        return self._modules[module].control_values_cls

    def parameters_for_module(self, module: str) -> type[ThrsValues]:
        return self._modules[module].parameters_cls

    def control(
        self, parameters: CombinedValues, time_fn: Callable[[], datetime]
    ) -> CombinedControl:
        subs = {
            name: module.control(parameters.values[name], time_fn)
            for name, module in self._modules.items()
            if name in parameters.values
        }
        return CombinedControl(subs, time_fn)

    def alarms(self) -> CombinedAlarms:
        return CombinedAlarms(
            {name: module.alarms() for name, module in self._modules.items()}
        )
