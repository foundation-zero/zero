from datetime import datetime
from unittest import mock

import pytest

from tests.helpers.modules import make_async_channels
from tests.orchestration.simples import simple_non_advisory_values
from thrs.classes.control import Control
from thrs.classes.machine_state_logger import MachineStateLoggingServiceNoop
from thrs.input_output.alarms import BaseAlarms
from thrs.input_output.base import Stamped
from thrs.input_output.definitions.system import AmcsControlMode, ControlMode
from thrs.orchestration.module import Module


@pytest.fixture
def mock_control():
    return mock.Mock(Control)


@pytest.fixture
def mock_alarms():
    alarms = mock.Mock(BaseAlarms)
    alarms.check.return_value = []
    return alarms


@pytest.fixture
def mock_channels():
    return make_async_channels()


@pytest.fixture
def mock_description(mock_control, mock_alarms):
    description = mock.Mock()
    description.control.return_value = mock_control
    description.alarms.return_value = mock_alarms
    return description


@pytest.fixture
def module_factory(mock_channels, mock_description):
    def make_module(name: str = "test"):
        return Module(
            name,
            description=mock_description,
            parameters=mock.Mock(),
            channels=mock_channels,
            time_fn=datetime.now,
            state_logger=MachineStateLoggingServiceNoop(),
        )

    return make_module


@pytest.fixture
def advisory_sensor_values():
    return mock.Mock(mode=AmcsControlMode(mode=Stamped.stamp(ControlMode.EXTERNAL)))


@pytest.fixture
def manual_values():
    return simple_non_advisory_values(flow=2.0)


@pytest.fixture
def local_sensor_values():
    return mock.Mock(mode=AmcsControlMode(mode=Stamped.stamp(ControlMode.LOCAL)))
