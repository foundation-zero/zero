from unittest import mock

import pytest

from tests.helpers.modules import make_async_channels
from tests.orchestration.simples import simple_non_advisory_values
from thrs.classes.control import Control
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
def module_factory(mock_control, mock_alarms, mock_channels):
    def make_module(name: str = "test"):
        return Module(name, mock_control, mock_alarms, mock_channels)

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
