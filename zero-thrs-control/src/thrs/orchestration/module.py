from datetime import datetime
from typing import Callable, Mapping

from thrs.classes.control import Control
from thrs.control.base import ModuleDescription
from thrs.control.manual import ManualControl
from thrs.control.switching import SwitchingControl
from thrs.input_output.alarms import Alarm, BaseAlarms
from thrs.input_output.base import (
    CombinedValues,
    SimulationInputs,
    ThrsValues,
)

type ModuleClassMap = Mapping[str, type[ThrsValues]]


class CombinedControl(
    Control[CombinedValues, CombinedValues, CombinedValues, CombinedValues]
):
    """Combination of sub controls for combined modules"""

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
        combined_controller_values = CombinedValues({})

        for name, module in self._modules.items():
            sensors = sensor_values.values.get(name, None)
            if sensors:
                control_value, controller_values = module.control(sensors)
            else:
                control_value, controller_values = module.initial()

            combined_control_values.values[name] = control_value
            combined_controller_values.values[name] = controller_values

        return (combined_control_values, combined_controller_values)

    @property
    def parameters(self) -> CombinedValues:
        return CombinedValues(
            values={name: module.parameters for name, module in self._modules.items()}
        )

    def update_parameters(self, parameters: CombinedValues):
        for name, params in parameters.values.items():
            self._modules[name].update_parameters(params)

    def update_parameters_for(self, module: str, parameters: ThrsValues):
        self._modules[module].update_parameters(parameters)

    def manual_controls(self, module: str, control_values: ThrsValues):
        self._modules[module].manual_controls(control_values)

    def set_automation_mode(self, module: str, automation: bool):
        self._modules[module].switch_mode("automatic" if automation else "manual")


class CombinedAlarms(BaseAlarms[CombinedValues, CombinedValues, CombinedValues]):
    """Combination of sub alarms for combined modules"""

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


class CombinedModule[I: SimulationInputs, O: ThrsValues]:
    """Combination of multiple modules into a single control/simulation unit

    Also contains the MQTT mapping for the combined modules.
    """

    def __init__(
        self,
        modules: dict[str, ModuleDescription],
        simulation_inputs_cls: type[I],
        simulation_outputs_cls: type[O],
    ):
        self._modules = modules
        self.sensor_values_clss: ModuleClassMap = {
            module: desc.sensor_values_cls for module, desc in modules.items()
        }
        self.control_values_clss: ModuleClassMap = {
            module: desc.control_values_cls for module, desc in modules.items()
        }
        self.controller_values_clss: ModuleClassMap = {
            module: desc.controller_values_cls for module, desc in modules.items()
        }
        self.simulation_inputs_cls = simulation_inputs_cls
        self.simulation_outputs_cls = simulation_outputs_cls

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
