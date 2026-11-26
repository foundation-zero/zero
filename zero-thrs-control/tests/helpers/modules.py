from datetime import datetime
from unittest import mock

from pydantic import Field

from tests.orchestration.simples import SimpleInOut, SimpleMode, simple_control_values
from thrs.classes.control import Control
from thrs.control.state import ControlModes, ControlState
from thrs.input_output.alarms import BaseAlarms
from thrs.input_output.base import ThrsValues
from thrs.orchestration.module import Module, ModuleDescription


class ConfigurableParameters(ThrsValues):
    # Bounded so tests can exercise out-of-range/invalid persisted values.
    setpoint: float = Field(default=50.0, ge=0.0, le=100.0)


class ConfigurableControllerState(
    ControlState[SimpleInOut, ConfigurableParameters, SimpleMode]
):
    pass


class ConfigurableAlarms(
    BaseAlarms[SimpleInOut, SimpleInOut, ConfigurableControllerState]
):
    pass


class ConfigurableControl(
    Control[
        SimpleInOut,
        SimpleInOut,
        ConfigurableParameters,
        SimpleMode,
        ConfigurableControllerState,
    ]
):
    def __init__(
        self,
        parameters: ConfigurableParameters,
        time_fn=None,
    ) -> None:
        self._parameters = parameters
        self._time_fn = time_fn or datetime.now
        self._current_values: SimpleInOut = SimpleInOut.zero()

    def initial(self) -> tuple[SimpleInOut, ConfigurableControllerState]:
        return (
            SimpleInOut.zero(),
            ConfigurableControllerState(parameters=ConfigurableParameters()),
        )

    def control(
        self, sensor_values: SimpleInOut
    ) -> tuple[SimpleInOut, ConfigurableControllerState]:
        return (
            sensor_values,
            ConfigurableControllerState(
                parameters=self._parameters, control_mode=self.mode
            ),
        )

    @property
    def parameters(self) -> ConfigurableParameters:
        return self._parameters

    @property
    def mode(self) -> SimpleMode | None:
        return None

    def update_parameters(self, parameters: ConfigurableParameters) -> None:
        self._parameters = parameters

    def update_controls(self, control_values: SimpleInOut) -> None:
        self._current_values.update_in_place(control_values)

    def reset(self) -> None:
        self._current_values = SimpleInOut.zero()


type ConfigurableModule = Module[
    SimpleInOut,
    SimpleInOut,
    ConfigurableParameters,
    SimpleMode,
    ConfigurableControllerState,
]


def make_channels() -> mock.Mock:
    """Control channels that report nothing, so a module keeps its constructed state."""
    channels = mock.Mock()
    channels.get_sensor_values.return_value = None
    channels.get_parameters.return_value = None
    channels.get_manual_controls.return_value = None
    channels.get_control_values_set.return_value = None
    channels.get_automation_modes.return_value = None
    channels.get_actuated_control_values.return_value = None
    return channels


def make_async_channels() -> mock.Mock:
    """Control channels with awaitable `send_*` methods, so `Module.tick()` can be
    called and inspected for exactly what would have been published over MQTT."""
    channels = make_channels()
    channels.send_computed_values = mock.AsyncMock()
    channels.send_control_values = mock.AsyncMock()
    channels.send_controller_state = mock.AsyncMock()
    channels.send_parameters = mock.AsyncMock()
    channels.send_control_modes = mock.AsyncMock()
    channels.send_automation_mode = mock.AsyncMock()
    channels.send_actuated_control_values = mock.AsyncMock()
    return channels


CONFIGURABLE_MODULE_DESCRIPTION = ModuleDescription(
    SimpleInOut,
    SimpleInOut,
    ConfigurableParameters,
    ConfigurableControl,
    ConfigurableControllerState,
    ConfigurableAlarms,
)


def make_module(
    name: str = "test",
    channels: mock.Mock | None = None,
    parameters: ConfigurableParameters | None = None,
    automation_mode: ControlModes = "manual",
) -> ConfigurableModule:
    return Module(
        name,
        description=CONFIGURABLE_MODULE_DESCRIPTION,
        channels=channels or make_async_channels(),
        time_fn=datetime.now,
        parameters=parameters,
        automation_mode=automation_mode,
    )


__all__ = [
    "make_async_channels",
    "make_channels",
    "make_module",
    "simple_control_values",
]
