from unittest import mock

from pydantic import Field

from tests.orchestration.simples import (
    SimpleControllerState,
    SimpleInOut,
    SimpleMode,
)
from thrs.classes.control import Control
from thrs.classes.machine_state_logger import (
    MachineStateLoggingServiceNoop,
    StateLogger,
)
from thrs.input_output.alarms import BaseAlarms
from thrs.input_output.base import Stamped, ThrsValues
from thrs.input_output.definitions.sensor import FlowSensor
from thrs.orchestration.module import Module


class ConfigurableParameters(ThrsValues):
    # Bounded so tests can exercise out-of-range/invalid persisted values.
    setpoint: float = Field(default=50.0, ge=0.0, le=100.0)


class ConfigurableAlarms(BaseAlarms[SimpleInOut, SimpleInOut, ConfigurableParameters]):
    pass


class ConfigurableControl(
    Control[
        SimpleInOut,
        SimpleInOut,
        ConfigurableParameters,
        SimpleMode,
        SimpleControllerState,
    ]
):
    def __init__(self, parameters: ConfigurableParameters) -> None:
        self._parameters = parameters
        self.state_logger: StateLogger = MachineStateLoggingServiceNoop()

    def initial(self) -> tuple[SimpleInOut, SimpleControllerState]:
        return (SimpleInOut.zero(), SimpleControllerState())

    def control(
        self, sensor_values: SimpleInOut
    ) -> tuple[SimpleInOut, SimpleControllerState]:
        return (sensor_values, SimpleControllerState())

    @property
    def parameters(self) -> ConfigurableParameters:
        return self._parameters

    @property
    def mode(self) -> SimpleMode | None:
        return None

    def update_parameters(self, parameters: ConfigurableParameters) -> None:
        self._parameters = parameters


type ConfigurableModule = Module[
    SimpleInOut,
    SimpleInOut,
    ConfigurableParameters,
    SimpleMode,
    SimpleControllerState,
]


def make_channels() -> mock.Mock:
    """Control channels that report nothing, so a module keeps its constructed state."""
    channels = mock.Mock()
    channels.get_sensor_values.return_value = None
    channels.get_parameters.return_value = None
    channels.get_manual_controls.return_value = None
    channels.get_automation_modes.return_value = None
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
    channels.send_manual_control = mock.AsyncMock()
    return channels


def make_module(
    name: str = "dhw", channels: mock.Mock | None = None
) -> ConfigurableModule:
    return Module(
        name,
        ConfigurableControl(ConfigurableParameters()),
        ConfigurableAlarms(),
        channels or make_channels(),
    )


def manual_values(flow: float) -> SimpleInOut:
    return SimpleInOut(
        go_with_the=FlowSensor(
            flow=Stamped.stamp(flow), temperature=Stamped.stamp(20.0)
        )
    )
