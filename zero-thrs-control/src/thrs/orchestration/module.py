from datetime import datetime
from typing import Callable, Mapping

from thrs.classes.control import Control, ControlResult
from thrs.control.base import ModuleDescription
from thrs.control.manual import ManualControl
from thrs.control.switching import SwitchingControl, SwitchingControlMode
from thrs.input_output.alarms import Alarm, BaseAlarms
from thrs.input_output.base import (
    CombinedValues,
    SimulationInputs,
    SimulationValues,
    ThrsValues,
)
from thrs.orchestration.connector import (
    DirectMqttMapping,
    ModuleMqttMapping,
    MqttMapping,
)
from thrs.simulation.io_mapping import CombinedIoMapping, IoMapping


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
                ManualControl(control.initial().values, time_fn), control
            )
            for name, control in modules.items()
        }
        self._time_fn = time_fn

    def initial(self) -> ControlResult[CombinedValues]:
        return ControlResult(
            values=CombinedValues(
                values={
                    name: module.initial().values
                    for name, module in self._modules.items()
                }
            ),
            timestamp=self._time_fn(),
        )

    def control(self, sensor_values: CombinedValues) -> ControlResult[CombinedValues]:
        results = {
            name: module.control(sensors)
            if (sensors := sensor_values.values.get(name, None))
            else module.initial()
            for name, module in self._modules.items()
        }
        return ControlResult(
            timestamp=self._time_fn(),
            values=CombinedValues(
                values={name: result.values for name, result in results.items()}
            ),
        )

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

    def mode_for(self, module: str) -> SwitchingControlMode[ThrsValues]:
        return self._modules[module].mode

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


class CombinedModule[I: SimulationInputs, O: SimulationValues]:
    """Combination of multiple modules into a single control/simulation unit

    Also contains the MQTT mapping for the combined modules.
    """

    def __init__(
        self,
        modules: dict[str, ModuleDescription],
        simulation_inputs_cls: type[I],
        simulation_outputs_cls: type[O],
        control_topic_suffix: str | None = None,
    ):
        self._modules = modules
        self._sensor_mqtt_mapping = ModuleMqttMapping(
            {module: desc.sensor_values_cls for module, desc in modules.items()}
        )
        self._control_mqtt_mapping = ModuleMqttMapping(
            {module: desc.control_values_cls for module, desc in modules.items()},
            topic_suffix=control_topic_suffix,
        )
        self._simulation_inputs_cls = simulation_inputs_cls
        self._simulation_outputs_cls = simulation_outputs_cls
        self._simulation_output_mapping = DirectMqttMapping(
            simulation_outputs_cls, topic="simulation/outputs"
        )

    def io_mapping(self) -> IoMapping:
        return CombinedIoMapping(
            {module: desc.sensor_values_cls for module, desc in self._modules.items()},
            self._simulation_outputs_cls,
        )

    @property
    def modules(self) -> list[str]:
        return list(self._modules.keys())

    @property
    def sensor_values_mqtt_mapping(self) -> MqttMapping[CombinedValues]:
        return self._sensor_mqtt_mapping

    @property
    def control_values_mqtt_mapping(self) -> MqttMapping[CombinedValues]:
        return self._control_mqtt_mapping

    @property
    def simulation_output_mqtt_mapping(self) -> MqttMapping[O]:
        return self._simulation_output_mapping

    @property
    def simulation_inputs_cls(self) -> type[I]:
        return self._simulation_inputs_cls

    @property
    def simulation_outputs_cls(self) -> type[O]:
        return self._simulation_outputs_cls

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
